# CRDT-SSS

## Objetivo do Projeto

O projeto CRDT-SSS (Conflict-free Replicated Data Types - Secure Synchronization System) tem como objetivo implementar e demonstrar mecanismos de sincronização de dados distribuídos utilizando CRDTs, garantindo consistência eventual e tolerância a falhas em ambientes distribuídos. O sistema também explora aspectos de segurança, gestão de conflitos e integração com aplicações reais.

## Estrutura do Projeto

- **crdt-cluster/**: Implementação dos serviços de CRDT, scripts de gestão, configuração de logs e exemplos de dados.
  - `bin/`: Scripts e serviços principais (ex: `crdt_service.py`).
  - `config/`: Configurações de logging.
  - `data/`: Exemplos de dados utilizados.
  - `logs/`: Logs de execução.
  - `src/`: Implementação dos tipos CRDT básicos (G-Counter, G-Set, LWW, Two-Phase Set).
  - `sync_folder/`: Exemplos de sincronização para cada tipo de CRDT.

- **NetGuardian/**: Aplicação principal que utiliza CRDTs para sincronização segura de arquivos e dados.
  - `src/`: Código-fonte da aplicação, incluindo módulos de autenticação, CRDT, banco de dados, gerenciamento de arquivos, GUI e utilitários.
  - `config/`: Configurações da aplicação.
  - `main.py`: Ponto de entrada da aplicação.
  - `requirements.txt`: Dependências do projeto.
  - `README.md`, `INSTALL.md`, `QUICKSTART.md`: Documentação adicional.

- **TESTES/**: Testes e exemplos de integração, incluindo uma aplicação web (cloud-webapp) para demonstração dos CRDTs em ambiente web.

- **Vulnerabilidades/**: Documentação sobre vulnerabilidades e segurança relacionadas ao projeto.

## Funcionalidades Principais

- Implementação de múltiplos tipos de CRDT (G-Counter, G-Set, LWW, Two-Phase Set)
- Sincronização distribuída de dados
- Gerenciamento de conflitos de forma automática
- Interface gráfica para demonstração e testes (NetGuardian)
- Scripts para deploy e gestão dos serviços
- Exemplos de integração com aplicações web
- Documentação sobre segurança e vulnerabilidades

## Como Executar

1. **Pré-requisitos:**
   - Python 3.10+
   - Instalar dependências: `pip install -r NetGuardian/requirements.txt`

2. **Executar aplicação principal:**
   - Navegue até a pasta `NetGuardian/`
   - Execute: `python main.py`

3. **Executar serviços CRDT:**
   - Navegue até `crdt-cluster/bin/`
   - Execute: `python crdt_service.py`

4. **Testes Web (Opcional):**
   - Navegue até `TESTES/cloud-webapp/`
   - Instale dependências: `pnpm install` ou `npm install`
   - Execute: `pnpm dev` ou `npm run dev`

## Documentação

- Consulte os arquivos `README.md`, `INSTALL.md` e `QUICKSTART.md` em cada diretório para instruções detalhadas.
- Veja exemplos de uso e diagramas em `NetGuardian/use_case_diagram.md`.

## Participantes do Projeto

| Nome                | Email                |
|---------------------|----------------------|
|Gonçalo Leitao          |                      |
|                     |                      |
|                     |                      |

(Preencha com os nomes e contatos dos participantes)

## Deployment & Configuration (important notes)

This section collects operational details to run NetGuardian with the crdt-cluster in real environments.

1) Database
- NetGuardian must connect to a PostgreSQL server (no SQLite). Configure DB connection in `NetGuardian/src/database` settings or via environment variables.
- Ensure PostgreSQL is reachable from the client and that credentials are correct.

2) CRDT cluster sync folder
- The authoritative files are stored in the CRDT cluster sync folder, by default: `/opt/crdt-cluster/sync_folder/lww` on the server nodes.
- NetGuardian mirrors uploads to the CRDT cluster via SFTP to the node corresponding to the user's group.

3) SFTP / Node port mapping (per-group)
- Ports used to reach CRDT nodes must be configurable by environment or settings. Example config keys supported:
  - GROUP_CRDT_PORTS = {'PORTO': 51230, 'LISBOA': 51234}
  - or individual env vars: CRDT_SFTP_PORT_PORTO=51230, CRDT_SFTP_PORT_LISBOA=51234
- At login the app determines the group of the user (e.g. PORTO or LISBOA) and selects the corresponding port to open the SFTP connection.
- Example mapping used by the project: group_id == 2 -> PORTO, group_id == 3 -> LISBOA.

4) Authentication and passwords
- Passwords in the initial DB may be plaintext. The app now supports bcrypt hashing for production — configure to use bcrypt and migrate users by hashing passwords.
- If your DB currently stores plaintext, the authentication module can be configured to accept plaintext verification temporarily, but enable bcrypt for real deployments.

5) File handling behavior
- Uploads should write files into the CRDT sync folder on the node (SFTP). Re-uploads should overwrite the existing file (same logical id) instead of creating duplicates. If you see duplicates, check the local filename -> remote mapping (UUIDs) and the LWW tombstone logic.
- Deletion must be mirrored (tombstones) so other nodes do not reintroduce deleted files later; configure the LWW implementation to propagate deletions correctly.
- Any file type (binary or text) is supported. Ensure SFTP transfer uses binary mode (paramiko handles this automatically when transferring bytes).

6) Building and packaging
- Install dependencies: pip install -r NetGuardian/requirements.txt
- Example single-file build with PyInstaller (may require hooks for cryptography/paramiko/customtkinter):
  - pyinstaller --onefile NetGuardian/main.py
- On Windows you may need to bundle libmagic or remove python-magic if not available.

7) Troubleshooting
- SFTP timeouts (connection timed out / WinError 10060): check network routing, firewall rules, and that the SSH daemon is listening on the target port (5131/5132/51230/51234 etc).
- DB connection refused: confirm PostgreSQL is listening on network interfaces and allow remote connections (postgresql.conf and pg_hba.conf).
- If files you delete reappear later: check the LWW logic and that deletions are propagated as tombstones; ensure clocks/timestamps are consistent across nodes.
- If uploads create new files instead of overwriting: verify the app uses consistent logical IDs (UUIDs) for files and uses the same filename when re-uploading.

8) Environment variables recommended
- DATABASE_URL (or DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)
- GROUP_CRDT_PORTS (JSON) or CRDT_SFTP_PORT_PORTO and CRDT_SFTP_PORT_LISBOA
- LOG_LEVEL

If you want, I can update the code to: make CRDT ports read from environment/settings, implement bcrypt password hashing and migration, fix SFTP overwrite behaviour, and correct LWW delete propagation. Tell me which of these to do next.

---

Este projeto é distribuído sob a licença MIT. Consulte o arquivo LICENSE para mais informações.
