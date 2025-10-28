# CRDT-SSS

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE) [![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/) [![Repo size](https://img.shields.io/github/repo-size/fwfg/CRDT-SSS?label=repo%20size)]()

## Project Overview

CRDT-SSS (Conflict-free Replicated Data Types - Secure Synchronization System) demonstrates distributed data synchronization using CRDTs to achieve eventual consistency and fault tolerance. The project also explores security, conflict resolution, and integration with client applications.

> Quick highlight: this repo contains state-based CRDT implementations, a desktop client (NetGuardian), packaging helpers, and demo web front-ends.

---

## Table of Contents

- [Project Structure](#project-structure-summary)
- [Quick Start](#quick-start)
- [CRDT_STATE_BASED](#crdt_state_based-details)
- [NetGuardian (desktop)](#netguardian-desktop-application)
- [NetGuardian_APP](#netguardian_app-packaging--helpers)
- [NetGuardian_Web](#netguardian_web-web-demos)
- [Vulnerabilidades (security notes)](#vulnerabilidades-security-notes)
- [Environment variables](#environment-variables)
- [Contributing & License](#contributing--license)

---

## Project Structure (summary)

- CRDT_STATE_BASED/: State-based CRDT implementations, service scripts, configuration and example sync folders.
- NetGuardian/: Desktop application that uses CRDTs for secure file and data synchronization (source code, GUI, auth, DB and utilities).
- NetGuardian_APP/: Packaging, installation helpers, scripts and additional app resources for building the desktop distribution.
- NetGuardian_Web/: Two Next.js webapp versions (v1 and v2) used for demos and web-based clients.
- crdt-cluster/: Example CRDT service and cluster scripts (see folder for service code and sync examples).
- Vulnerabilidades/: Security documents and vulnerability notes.


## Quick Start

> **Note:** these commands are minimal examples for local development on Windows. Adjust paths and env vars for your platform.

<details>
<summary><strong>Setup Python environment & run desktop app</strong></summary>

```powershell
# create & activate venv (Windows)
python -m venv .venv
.venv\Scripts\activate
pip install -r NetGuardian/requirements.txt
python NetGuardian/main.py
```

```bash
# run CRDT service (example)
cd CRDT_STATE_BASED/bin
python crdt_service.py
```

</details>

> **Tip:** open Vulnerabilidades/ first to review security notes before running services.


## CRDT_STATE_BASED (details)

Path: CRDT_STATE_BASED/

Purpose: Reference state-based CRDT implementations and a simple service to run them locally for tests and demonstrations.

Key files and folders:
- bin/
  - crdt_service.py — entry script for a minimal CRDT service used in examples and local testing.
  - create_service.sh, management.sh — helper scripts to create/manage service instances (Unix shells provided).
- config/
  - logging_simple.conf — basic logging configuration used by the service.
- data/
  - data.md — notes and sample data layout for CRDTs stored by the service.
- logs/
  - logs.md — notes about logging and common log locations.
- src/
  - base_crdt.py — common base class and helpers for state-based CRDTs.
  - crdt_types/ — implementations of CRDT types (g_counter, g_set, lww, two_phase_set).
- sync_folder/ — example folders used to emulate the sync directories for each CRDT type.


## NetGuardian (desktop application)

Path: NetGuardian/

Purpose: Desktop client that integrates with CRDT storage to upload, download and synchronize files across nodes. Includes authentication, DB management, GUI and file handling modules.

Key items:
- main.py — application entry point.
- requirements.txt — Python dependencies.
- config/settings.py — DB connection, CRDT ports mapping.
- src/ (api, auth, crdt, database, file_manager, gui, utils)


## NetGuardian_APP (packaging & helpers)

Path: NetGuardian_APP/

Contents: Packaging helpers, installers, scripts and docs (INSTALL.md, QUICKSTART.md, README.md), plus example packaged release.


## NetGuardian_Web (web demos)

Path: NetGuardian_Web/

Contents: Two Next.js demo apps (netguardian-webapp.v1 and v2). Use pnpm or npm to install and run the dev server.


## Vulnerabilidades (security notes)

Path: Vulnerabilidades/

Contents: security analysis documents (e.g., netguardiancrdt.pdf) and notes describing vulnerabilities and mitigations. Review before deploying.

> ⚠️ Security warning: do not deploy without addressing plaintext password storage, SFTP/DB network access, and proper tombstone handling in CRDTs.


## Environment variables

A short reference of commonly used env vars:

| Variable | Purpose | Example |
|---|---:|---|
| DATABASE_URL | Database connection (preferred) | postgresql://user:pass@host:5432/dbname |
| GROUP_CRDT_PORTS | JSON map of group->SFTP port | {"PORTO":51230,"LISBOA":51234} |
| CRDT_SFTP_PORT_PORTO | Per-group SFTP port (alternative) | 51230 |
| LOG_LEVEL | Logging verbosity | INFO, DEBUG |


## Contributing & License

Please follow CONTRIBUTING.md guidelines present in NetGuardian/ and NetGuardian_APP/ for development workflows and code style.

This project is licensed under the MIT License. See the LICENSE file for details.

---

If you want, I can:
- add a small demo GIF or screenshots (you provide images),
- translate the README to Portuguese, or
- add badges for CI/coverage if you provide the service links.
