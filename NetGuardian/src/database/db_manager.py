"""
Database Manager for NetGuardian
Handles PostgreSQL and SQLite database connections with automatic fallback
"""

import os
import sqlite3
import logging
from typing import Optional, List, Dict, Any, Union

# Try to import PostgreSQL driver
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

# Try to import dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from config.settings import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages database connections and operations with PostgreSQL/SQLite support.
    
    Automatically falls back to SQLite if PostgreSQL is unavailable.
    
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
        self.connection: Optional[Union[psycopg2.extensions.connection, sqlite3.Connection]] = None
        self.host: str = Config.DB_HOST
        self.port: str = Config.DB_PORT
        self.database: str = Config.DB_NAME
        self.username: str = Config.DB_USER
        self.password: str = Config.DB_PASSWORD
    
    def connect(self) -> bool:
        """
        Establish database connection to PostgreSQL.
        
        Returns:
            bool: True if PostgreSQL connected, False to trigger SQLite fallback
        """
        try:
            if not POSTGRES_AVAILABLE:
                logger.warning("psycopg2 not installed, using SQLite fallback")
                return False
                
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
            
        except psycopg2.OperationalError as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected database connection error: {e}", exc_info=True)
            return False
    
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
                self.connect()
            
            # Check if we're using SQLite or PostgreSQL
            is_sqlite = hasattr(self.connection, 'row_factory')
            
            if is_sqlite:
                return self._execute_sqlite_query(query, params)
            else:
                return self._execute_postgres_query(query, params)
                
        except sqlite3.Error as e:
            logger.error(f"SQLite query execution failed: {e}")
            self._rollback_connection()
            raise
        except psycopg2.Error as e:
            logger.error(f"PostgreSQL query execution failed: {e}")
            self._rollback_connection()
            raise
        except Exception as e:
            logger.error(f"Unexpected query execution error: {e}", exc_info=True)
            self._rollback_connection()
            raise
    
    def _execute_sqlite_query(self, query: str, params: Optional[tuple]) -> Union[List[Dict[str, Any]], int]:
        """Execute query on SQLite connection."""
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()
        cursor.execute(query, params or ())
        
        if query.strip().upper().startswith('SELECT'):
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        else:
            self.connection.commit()
            return cursor.rowcount
    
    def _execute_postgres_query(self, query: str, params: Optional[tuple]) -> Union[List[Dict[str, Any]], int]:
        """Execute query on PostgreSQL connection."""
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            
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
            if not self.connect():
                logger.warning("Using fallback SQLite database")
                self._create_sqlite_fallback()
                return
            
            # Create users table
            users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
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
            
            self.execute_query(users_table)
            self.execute_query(files_table)
            self.execute_query(sessions_table)

            # Only create internal CRDT tables when configured to use internal CRDT
            if Config.APP_USE_INTERNAL_CRDT:
                self.execute_query(crdt_events_table)
                self.execute_query(crdt_snapshots_table)
                self.execute_query(crdt_sync_log_table)

            logger.info("Database tables initialized successfully (with CRDT support)")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            self._create_sqlite_fallback()
    
    def _create_sqlite_fallback(self):
        """Create SQLite fallback database for local development"""
        import sqlite3
        
        try:
            self.connection = sqlite3.connect('netguardian.db')
            self.connection.row_factory = sqlite3.Row
            
            # Create tables with SQLite syntax
            users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            );
            """
            
            files_table = """
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                filename TEXT NOT NULL,
                original_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                file_hash TEXT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_deleted BOOLEAN DEFAULT 0
            );
            """
            
            sessions_table = """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                is_active BOOLEAN DEFAULT 1
            );
            """
            
            # CRDT tables for SQLite
            crdt_events_table = """
            CREATE TABLE IF NOT EXISTS crdt_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT UNIQUE NOT NULL,
                entity_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                data TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                node_id TEXT NOT NULL,
                vector_clock TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            crdt_events_index1 = """
            CREATE INDEX IF NOT EXISTS idx_crdt_events_entity ON crdt_events(entity_id)
            """
            
            crdt_events_index2 = """
            CREATE INDEX IF NOT EXISTS idx_crdt_events_timestamp ON crdt_events(timestamp)
            """
            
            crdt_snapshots_table = """
            CREATE TABLE IF NOT EXISTS crdt_snapshots (
                entity_id TEXT PRIMARY KEY,
                state TEXT NOT NULL,
                vector_clock TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            crdt_sync_log_table = """
            CREATE TABLE IF NOT EXISTS crdt_sync_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_id TEXT NOT NULL,
                last_sync TIMESTAMP NOT NULL,
                events_synced INTEGER DEFAULT 0,
                sync_direction TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            
            cursor = self.connection.cursor()
            cursor.execute(users_table)
            cursor.execute(files_table)
            cursor.execute(sessions_table)
            if Config.APP_USE_INTERNAL_CRDT:
                cursor.execute(crdt_events_table)
                cursor.execute(crdt_events_index1)
                cursor.execute(crdt_events_index2)
                cursor.execute(crdt_snapshots_table)
                cursor.execute(crdt_sync_log_table)
            self.connection.commit()
            
            logger.info("SQLite fallback database initialized (with CRDT support)")
            
        except Exception as e:
            logger.error(f"SQLite fallback failed: {e}")
            raise