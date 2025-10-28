"""
Database Manager for NetGuardian
Handles PostgreSQL database connections
"""

import os
import logging
from typing import Optional, List, Dict, Any, Union
import re

# Try to import PostgreSQL driver
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except Exception:
    # make names available for static analysis; will error at runtime if used
    psycopg2 = None  # type: ignore
    RealDictCursor = None  # type: ignore
    POSTGRES_AVAILABLE = False

# Try to import dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    def load_dotenv():
        return None

# Load application Config via file path to avoid package import issues
import importlib.util
config_paths = [
    os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'settings.py'),  # NetGuardian/config/settings.py
    os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.py'),       # src/config/settings.py
]
settings_mod = None
for p in config_paths:
    p_abs = os.path.abspath(p)
    if os.path.exists(p_abs):
        spec = importlib.util.spec_from_file_location("config.settings", p_abs)
        if spec and spec.loader:
            settings_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(settings_mod)  # type: ignore
            break

if not settings_mod:
    raise FileNotFoundError(f"Could not find config/settings.py in expected locations: {config_paths}")

Config = settings_mod.Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages database connections and operations with PostgreSQL support.

    Attributes:
        connection: Active database connection
        host: PostgreSQL host address
        port: PostgreSQL port
        database: Database name
        username: Database user
        password: Database password
    """
    
    def __init__(self) -> None:
        """Initialize DatabaseManager with config from environment or defaults."""
        load_dotenv()
        self.connection: Optional[Any] = None
        self.host: str = Config.DB_HOST
        self.port: str = Config.DB_PORT
        self.database: str = Config.DB_NAME
        self.username: str = Config.DB_USER
        self.password: str = Config.DB_PASSWORD
    
    def connect(self) -> bool:
        """
        Establish database connection to PostgreSQL.
        
        Returns:
            bool: True if PostgreSQL connected, False otherwise
        """
        try:
            if not POSTGRES_AVAILABLE:
                logger.error("psycopg2 is not installed: PostgreSQL is required. Install psycopg2-binary.")
                raise RuntimeError("psycopg2 not installed, PostgreSQL required")

            # Attempt to connect to PostgreSQL; raise on failure
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password,
                cursor_factory=RealDictCursor
            )
            logger.info("PostgreSQL database connection established")
            return True
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}", exc_info=True)
            raise

    def disconnect(self) -> None:
        """Close active database connection."""
        if self.connection:
            try:
                self.connection.close()
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> Union[List[Dict[str, Any]], int]:
        """
        Execute a database query and return results.
        
        Args:
            query: SQL query string
            params: Query parameters tuple
            
        Returns:
            List of dicts for SELECT queries, row count for INSERT/UPDATE/DELETE
            
        Raises:
            Exception: Database operation errors
        """
        try:
            if not self.connection:
                # connect() will raise if connection cannot be established
                self.connect()

            # Always use PostgreSQL in production; no SQLite fallback
            return self._execute_postgres_query(query, params)

        except Exception as e:
            logger.error(f"PostgreSQL query execution failed: {e}", exc_info=True)
            self._rollback_connection()
            raise
    
    def _execute_postgres_query(self, query: str, params: Optional[tuple]) -> Any:
        """Execute query on PostgreSQL connection."""
        # Convert sqlite-style placeholders (?) to psycopg2-style (%s)
        q = query.replace('?', '%s')
        # Normalize common boolean comparisons for PostgreSQL: replace literal 0/1 with FALSE/TRUE
        # Handle case-insensitive occurrences like "is_deleted = 0" or "is_active=1"
        q = re.sub(r'(?i)\bis_deleted\s*=\s*0\b', 'is_deleted = FALSE', q)
        q = re.sub(r'(?i)\bis_deleted\s*=\s*1\b', 'is_deleted = TRUE', q)
        q = re.sub(r'(?i)\bis_active\s*=\s*0\b', 'is_active = FALSE', q)
        q = re.sub(r'(?i)\bis_active\s*=\s*1\b', 'is_active = TRUE', q)
        # If placeholders used (converted to %s), convert matching params for boolean columns
        p = params if params is not None else None
        if p is not None:
            # work with a mutable list
            try:
                plist = list(p)
                # For each boolean-column pattern using %s, find which %s index it maps to
                for m in re.finditer(r'(?i)(is_deleted|is_active)\s*=\s*%s', q):
                    # count how many %s occurrences are before this match -> index
                    idx = q[:m.start()].count('%s')
                    if idx < len(plist):
                        val = plist[idx]
                        if val in (0, '0'):
                            plist[idx] = False
                        elif val in (1, '1'):
                            plist[idx] = True
                p = tuple(plist)
            except Exception:
                p = params
        with self.connection.cursor() as cursor:
            cursor.execute(q, p)

            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                self.connection.commit()
                return cursor.rowcount
    
    def _rollback_connection(self) -> None:
        """Safely rollback transaction on error."""
        if self.connection:
            try:
                self.connection.rollback()
            except Exception as e:
                logger.error(f"Rollback failed: {e}")
    
    def initialize_database(self):
        """Create necessary tables if they don't exist"""
        try:
            # Ensure we can connect to PostgreSQL; raise on failure
            self.connect()

            # Create users table
            groups_table = """
            CREATE TABLE IF NOT EXISTS groups (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL
            );
            """

            users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                group_id INTEGER REFERENCES groups(id),
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                last_login TIMESTAMP
            );
            """
            
            # Create files table
            files_table = """
            CREATE TABLE IF NOT EXISTS files (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                filename VARCHAR(255) NOT NULL,
                original_name VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                file_size BIGINT NOT NULL,
                file_hash VARCHAR(64),
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_deleted BOOLEAN DEFAULT FALSE
            );
            """
            
            # Create sessions table for user sessions
            sessions_table = """
            CREATE TABLE IF NOT EXISTS sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                session_token VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT TRUE
            );
            """
            
            # CRDT: Create events table for event sourcing
            crdt_events_table = """
            CREATE TABLE IF NOT EXISTS crdt_events (
                id SERIAL PRIMARY KEY,
                event_id VARCHAR(255) UNIQUE NOT NULL,
                entity_id VARCHAR(255) NOT NULL,
                event_type VARCHAR(100) NOT NULL,
                data JSONB NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                node_id VARCHAR(255) NOT NULL,
                vector_clock JSONB NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_crdt_events_entity ON crdt_events(entity_id);
            CREATE INDEX IF NOT EXISTS idx_crdt_events_timestamp ON crdt_events(timestamp);
            CREATE INDEX IF NOT EXISTS idx_crdt_events_type ON crdt_events(event_type);
            """
            
            # CRDT: Create snapshots table for fast state recovery
            crdt_snapshots_table = """
            CREATE TABLE IF NOT EXISTS crdt_snapshots (
                entity_id VARCHAR(255) PRIMARY KEY,
                state JSONB NOT NULL,
                vector_clock JSONB NOT NULL,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_crdt_snapshots_updated ON crdt_snapshots(updated_at);
            """
            
            # CRDT: Create sync log for tracking synchronization
            crdt_sync_log_table = """
            CREATE TABLE IF NOT EXISTS crdt_sync_log (
                id SERIAL PRIMARY KEY,
                node_id VARCHAR(255) NOT NULL,
                last_sync TIMESTAMP NOT NULL,
                events_synced INTEGER DEFAULT 0,
                sync_direction VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_crdt_sync_node ON crdt_sync_log(node_id);
            """
            
            # ensure groups exists before users
            self.execute_query(groups_table)
            self.execute_query(users_table)
            # Ensure older installations get last_login column if missing
            try:
                self.execute_query("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login TIMESTAMP;")
            except Exception:
                # Non-fatal: some PostgreSQL versions may error on ALTER statement parsing in this context
                pass
            self.execute_query(files_table)
            self.execute_query(sessions_table)

            # Only create internal CRDT tables when configured to use internal CRDT
            if Config.APP_USE_INTERNAL_CRDT:
                self.execute_query(crdt_events_table)
                self.execute_query(crdt_snapshots_table)
                self.execute_query(crdt_sync_log_table)

            logger.info("Database tables initialized successfully (PostgreSQL)")

        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    # Note: SQLite fallback removed. PostgreSQL is required by design.
