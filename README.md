# CRDT-SSS

## Project Overview

CRDT-SSS (Conflict-free Replicated Data Types - Secure Synchronization System) demonstrates distributed data synchronization using CRDTs to achieve eventual consistency and fault tolerance. The project also explores security, conflict resolution, and integration with client applications.

## Project Structure

- crdt-cluster/: CRDT service implementation, management scripts, configuration and sample data.
  - bin/: Main service scripts (e.g. crdt_service.py).
  - config/: Logging and configuration files.
  - data/: Sample data.
  - logs/: Log files.
  - src/: CRDT implementations (G-Counter, G-Set, LWW, Two-Phase Set).
  - sync_folder/: Example sync folders for each CRDT type.

- NetGuardian/: Desktop application that uses CRDTs for secure file and data synchronization.
  - src/: Application source code (auth, CRDT client, DB, file management, GUI, utilities).
  - config/: Application configuration.
  - main.py: Application entry point.
  - requirements.txt: Python dependencies.

- TESTS/: Integration tests and examples, including a web demo application.

- Vulnerabilities/: Security documentation and notes.

## Main Features

- Multiple CRDT types implemented (G-Counter, G-Set, LWW, Two-Phase Set)
- Distributed synchronization and automatic conflict resolution
- Desktop GUI for testing and demonstration (NetGuardian)
- Scripts for deployment and service management
- Documentation about security and known issues

## How to Run

1. Prerequisites
   - Python 3.10 or newer
   - PostgreSQL server for NetGuardian (SQLite is not supported for production)

2. Install dependencies
   - python -m venv .venv
   - On Windows: .venv\Scripts\activate
   - pip install -r NetGuardian/requirements.txt

3. Run the desktop application
   - cd NetGuardian
   - python main.py

4. Run CRDT services
   - cd crdt-cluster/bin
   - python crdt_service.py

5. Optional web demo
   - cd TESTES/cloud-webapp
   - Install and run with pnpm or npm (see project README in the webapp folder)

## Deployment & Configuration

These notes explain how to run NetGuardian with a remote crdt-cluster in real environments.

Database
- NetGuardian requires PostgreSQL. Configure DB connection parameters either with environment variables (DATABASE_URL or DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME) or in the application's settings file.
- Ensure PostgreSQL accepts connections from the client host and credentials are correct.

CRDT cluster sync folder
- The authoritative files are stored in the CRDT cluster sync folder, commonly at: /opt/crdt-cluster/sync_folder/lww on the server nodes.
- NetGuardian mirrors uploads to the CRDT cluster using SFTP to the node that corresponds to the user's group.

SFTP / Node port mapping (per-group)
- Map groups to CRDT node SFTP ports via environment variables or settings. Example options:
  - GROUP_CRDT_PORTS = {"PORTO": 51230, "LISBOA": 51234}
  - Or individual env vars: CRDT_SFTP_PORT_PORTO=51230 and CRDT_SFTP_PORT_LISBOA=51234
- At login the application determines the user's group and uses the corresponding port for SFTP.
- Convention used in this project: group_id == 2 -> PORTO, group_id == 3 -> LISBOA

Authentication and passwords
- Initial database records may store plaintext passwords. For production, enable bcrypt hashing and migrate users to hashed passwords.
- The authentication module can be configured temporarily to accept plaintext passwords during migration.

File handling behavior
- Uploads should place files into the CRDT sync folder on the corresponding node via SFTP. Re-uploads must overwrite existing files (use the same logical ID/filename) rather than creating duplicates.
- Deletions must be mirrored using tombstones so deleted files are not reintroduced by other nodes. The LWW (Last-Write-Wins) implementation must correctly propagate deletions.
- All file types (binary and text) are supported — SFTP transfers are binary-safe when using paramiko to transfer bytes.

Building and packaging
- Install dependencies: pip install -r NetGuardian/requirements.txt
- Example PyInstaller build (single-file). Note: PyInstaller may require hooks for cryptography, paramiko and customtkinter:
  - pyinstaller --onefile NetGuardian/main.py
- On Windows, bundling python-magic may require native libmagic binaries; if unavailable, remove python-magic from requirements.

Troubleshooting
- SFTP timeouts (WinError 10060 / connection timed out): verify network, firewall, and that SSH daemon on the server listens on the configured port.
- Database connection refused: check PostgreSQL's listen_addresses and pg_hba.conf to allow remote connections, and confirm port and credentials.
- Deleted files reappearing: ensure LWW deletions are sent as tombstones and that timestamps/clock synchronization across nodes is consistent.
- Re-uploads creating new files: verify the app uses a stable logical ID (UUID) for each file and reuses it when overwriting.

Recommended environment variables
- DATABASE_URL (or DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)
- GROUP_CRDT_PORTS (JSON) or CRDT_SFTP_PORT_PORTO and CRDT_SFTP_PORT_LISBOA
- LOG_LEVEL

## Contributing

Please follow the CONTRIBUTING.md guidelines in the NetGuardian folder for development workflows and code style.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
