# 🛡️ NetGuardian

**Sistema Desktop de Gestão de Ficheiros em Nuvem com Sincronização Distribuída**

Um sistema avançado de gestão de ficheiros com suporte a múltiplos dispositivos, resolução automática de conflitos utilizando CRDTs (Conflict-free Replicated Data Types), e interface inspirada no Adobe Creative Cloud.

---

## 📋 Índice

- [Características](#-características)
- [Tecnologias](#-tecnologias)
- [Arquitetura](#-arquitetura)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Utilização](#-utilização)
- [Estrutura do Projecto](#-estrutura-do-projecto)
- [Módulos](#-módulos)
- [API Reference](#-api-reference)
- [Contribuir](#-contribuir)
- [Licença](#-licença)

---

## ✨ Características

### 🔐 Autenticação & Segurança
- ✅ Sistema de login/registo robusto
- ✅ Hash de passwords com bcrypt
- ✅ Gestão de sessões com tokens
- ✅ Encriptação de ficheiros sensíveis
- ✅ Validação de entrada e protecção contra SQL injection

### 📁 Gestão de Ficheiros
- ✅ Upload e download de ficheiros
- ✅ Organização por categorias (Documentos, Imagens, Vídeos, etc.)
- ✅ Pesquisa e filtros avançados
- ✅ Visualização em grid com cards estilizados
- ✅ Suporte a múltiplos tipos de ficheiro
- ✅ Limite de tamanho configurável

### 🔄 Sincronização Distribuída (CRDT)
- ✅ Sincronização multi-dispositivo
- ✅ Resolução automática de conflitos
- ✅ Event sourcing para auditoria
- ✅ Vector clocks para causalidade
- ✅ LWW (Last-Write-Wins) Register
- ✅ Suporte a operações offline

### 🎨 Interface Moderna
- ✅ Design inspirado no Adobe CC
- ✅ Tema dark com cores profissionais
- ✅ Layout responsivo e intuitivo
- ✅ Dashboard com estatísticas
- ✅ Hero banner personalizado
- ✅ Animações e transições suaves

---

## 🛠️ Tecnologias

### Backend
- **Python 3.8+** - Linguagem principal
- **SQLite/PostgreSQL** - Base de dados
- **bcrypt** - Hash de passwords
- **cryptography** - Encriptação de ficheiros
- **python-dotenv** - Gestão de variáveis de ambiente

### Frontend
- **Tkinter** - Interface gráfica desktop
- **Pillow (PIL)** - Processamento de imagens

### CRDT & Sincronização
- **Custom CRDT Implementation** - LWW Register, Vector Clocks
- **Event Sourcing** - Rastreamento de alterações
- **PostgreSQL JSONB** - Armazenamento de eventos

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                        GUI Layer (Tkinter)                       │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ LoginWindow │  │ MainWindow   │  │ Dashboard            │  │
│  └─────────────┘  └──────────────┘  └──────────────────────┘  │
└────────────┬────────────────────────────────────────────────────┘
             │
┌────────────▼─────────────────────────────────────────────────────┐
│                      Business Logic Layer                         │
│  ┌──────────────┐  ┌───────────────┐  ┌────────────────────┐   │
│  │ AuthManager  │  │ FileHandler   │  │ CRDTFileHandler    │   │
│  └──────────────┘  └───────────────┘  └────────────────────┘   │
└────────────┬──────────────────────────────────────────────────────┘
             │
┌────────────▼─────────────────────────────────────────────────────┐
│                         CRDT Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ CRDTManager  │  │ SyncEngine   │  │ EventStore           │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │ LWWRegister  │  │ VectorClock  │                            │
│  └──────────────┘  └──────────────┘                            │
└────────────┬──────────────────────────────────────────────────────┘
             │
┌────────────▼─────────────────────────────────────────────────────┐
│                      Data Access Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ DBManager    │  │ Encryption   │  │ Helpers              │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└────────────┬──────────────────────────────────────────────────────┘
             │
┌────────────▼─────────────────────────────────────────────────────┐
│                    Database (SQLite/PostgreSQL)                   │
│  • users            • files              • crdt_events           │
│  • sessions         • file_versions      • crdt_snapshots        │
│                                          • crdt_sync_log          │
└───────────────────────────────────────────────────────────────────┘
```

---

## 📥 Instalação

### Pré-requisitos
- Python 3.8 ou superior
- pip (gestor de pacotes Python)
- PostgreSQL 12+ (opcional, para produção)

### Passo a Passo

1. **Clone o repositório**
```powershell
git clone https://github.com/seu-usuario/NetGuardian.git
cd NetGuardian
```

2. **Crie um ambiente virtual**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Instale as dependências**
```powershell
pip install -r requirements.txt
```

Caso não exista `requirements.txt`, instale manualmente:
```powershell
pip install bcrypt cryptography python-dotenv pillow psycopg2-binary
```

4. **Configure as variáveis de ambiente**
```powershell
# Copie o arquivo .env.example
Copy-Item .env.example .env

# Edite o .env com suas configurações
notepad .env
```

5. **Inicialize a base de dados**
```powershell
python -c "from src.database.db_manager import DatabaseManager; db = DatabaseManager(); db.initialize_database()"
```

6. **Execute a aplicação**
```powershell
python main.py
```

---

## ⚙️ Configuração

### Arquivo `.env`

Crie um arquivo `.env` na raiz do projeto:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=netguardian
DB_USER=postgres
DB_PASSWORD=sua_senha_aqui

# Application Settings
APP_SECRET_KEY=sua-chave-secreta-aleatoria-aqui
ENCRYPTION_KEY=sua-chave-de-criptografia-aqui

# File Storage
LOCAL_STORAGE_PATH=./local_files
CLOUD_STORAGE_ENABLED=true
MAX_FILE_SIZE_MB=100

# Logging
LOG_LEVEL=INFO
```

### Configurações Adicionais

As configurações podem ser ajustadas em `config/settings.py`:

- **Cores do tema**: `Config.COLORS`
- **Categorias de ficheiro**: `Config.FILE_CATEGORIES`
- **Validações**: `ValidationRules`
- **Mensagens de UI**: `UIConstants`
- **Layout**: Dimensões da janela, sidebar, cards, etc.

---

## 🚀 Utilização

### Primeira Execução

1. **Inicie a aplicação**
   ```powershell
   python main.py
   ```

2. **Registe uma conta**
   - Clique em "Register"
   - Preencha username, email e password
   - Faça login

3. **Faça upload de ficheiros**
   - Clique em "Upload File"
   - Seleccione um ficheiro
   - O ficheiro será automaticamente categorizado

### Sincronização Multi-Device

#### Dispositivo 1 (Portátil Principal)
```python
from src.file_manager.crdt_file_handler import CRDTFileHandler
from src.database.db_manager import DatabaseManager

db = DatabaseManager()
handler = CRDTFileHandler(db, user_id=1, node_id="portatil-principal")

# Upload ficheiro
success, msg = handler.upload_file("documento.pdf")
print(msg)

# Obter eventos para sincronizar
events = handler.get_local_changes_since(last_sync_time)
# Enviar 'events' para o servidor/outro dispositivo
```

#### Dispositivo 2 (Desktop Casa)
```python
handler2 = CRDTFileHandler(db, user_id=1, node_id="desktop-casa")

# Receber eventos do Dispositivo 1
remote_events = [...]  # Eventos do servidor

# Sincronizar
result = handler2.sync_with_remote(remote_events)
print(f"Sincronizados: {result['synced']} eventos")
```

### Operações Básicas via API

```python
# Upload
success, message = handler.upload_file("/path/to/file.pdf")

# Listar ficheiros
files = handler.list_user_files()
for file in files:
    print(f"{file['filename']} - {file['size']} bytes")

# Pesquisar
results = handler.search_files("relatório")

# Download
success, path = handler.download_file(file_id=123)

# Eliminar
success, message = handler.delete_file(file_id=123)

# Estado da sincronização
status = handler.get_sync_status()
print(status)
```

---

## 📂 Estrutura do Projecto

```
NetGuardian/
├── main.py                      # Ponto de entrada da aplicação
├── encryption.key               # Chave de encriptação (não fazer commit!)
├── .env                         # Variáveis de ambiente (não fazer commit!)
├── requirements.txt             # Dependências Python
├── README.md                    # Este ficheiro
├── use_case_diagram.md         # Diagramas de caso de uso
│
├── config/                      # Configurações
│   ├── __init__.py
│   └── settings.py             # Configuração centralizada
│
├── src/                        # Código fonte principal
│   ├── __init__.py
│   │
│   ├── auth/                   # Autenticação
│   │   ├── __init__.py
│   │   └── auth_manager.py    # Login, registro, sessões
│   │
│   ├── crdt/                   # CRDTs e Sincronização
│   │   ├── __init__.py
│   │   ├── crdt_manager.py    # Gestor CRDT
│   │   ├── event_store.py     # Event sourcing
│   │   ├── lww_register.py    # Last-Write-Wins Register
│   │   ├── vector_clock.py    # Vector clocks
│   │   ├── sync_engine.py     # Motor de sincronização
│   │   └── README.md          # Documentação CRDT
│   │
│   ├── database/               # Base de dados
│   │   ├── __init__.py
│   │   └── db_manager.py      # Gestor SQLite/PostgreSQL
│   │
│   ├── file_manager/           # Gestão de ficheiros
│   │   ├── __init__.py
│   │   ├── file_handler.py    # Handler básico
│   │   └── crdt_file_handler.py  # Handler com CRDT
│   │
│   ├── gui/                    # Interface gráfica
│   │   ├── __init__.py
│   │   ├── login_window.py    # Tela de login
│   │   ├── main_window.py     # Janela principal
│   │   └── dashboard.py       # Dashboard
│   │
│   └── utils/                  # Utilitários
│       ├── __init__.py
│       ├── encryption.py      # Encriptação de ficheiros
│       └── helpers.py         # Funções auxiliares
│
└── local_files/                # Armazenamento local de ficheiros
    └── user_{id}/             # Pasta por utilizador
```

---

## 🧩 Módulos

### 1. Authentication (`src/auth/`)
Gere a autenticação de utilizadores com segurança robusta.

**Principais Classes:**
- `AuthManager`: Login, registo, validação de sessões

**Recursos:**
- Hash de password com bcrypt
- Tokens de sessão seguros
- Validação de entrada
- Gestão de sessões activas

### 2. CRDT (`src/crdt/`)
Implementação completa de CRDTs para sincronização distribuída.

**Principais Classes:**
- `CRDTManager`: API de alto nível para CRDTs
- `LWWRegister`: Last-Write-Wins Register
- `VectorClock`: Rastreamento de causalidade
- `EventStore`: Persistência de eventos
- `SyncEngine`: Motor de sincronização

**Ver documentação completa:** [`src/crdt/README.md`](src/crdt/README.md)

### 3. Database (`src/database/`)
Abstracção de base de dados com suporte a SQLite e PostgreSQL.

**Principais Classes:**
- `DatabaseManager`: Operações CRUD, transacções, migrations

### 4. File Manager (`src/file_manager/`)
Gestão de ficheiros local e em nuvem.

**Principais Classes:**
- `FileHandler`: Operações básicas de ficheiro
- `CRDTFileHandler`: Handler com suporte CRDT

### 5. GUI (`src/gui/`)
Interface gráfica moderna com Tkinter.

**Principais Classes:**
- `LoginWindow`: Ecrã de autenticação
- `MainWindow`: Janela principal da aplicação
- `Dashboard`: Dashboard com estatísticas

### 6. Utils (`src/utils/`)
Utilitários e helpers.

**Principais Módulos:**
- `encryption.py`: Encriptação de ficheiros
- `helpers.py`: Funções auxiliares

---

## 📚 API Reference

### AuthManager

```python
# Registo
success, message = auth_manager.register_user(
    username="joao",
    email="joao@example.com",
    password="senha123"
)

# Login
success, message = auth_manager.login_user(
    username="joao",
    password="senha123"
)

# Logout
auth_manager.logout_user()

# Verificar autenticação
if auth_manager.is_authenticated():
    user = auth_manager.get_current_user()
    print(f"Autenticado como: {user['username']}")
```

### FileHandler

```python
# Upload
success, msg = handler.upload_file("/path/to/ficheiro.pdf")

# Listar
files = handler.list_user_files(category="documents")

# Pesquisar
results = handler.search_files("termo de busca")

# Download
success, path = handler.download_file(file_id=1)

# Eliminar
success, msg = handler.delete_file(file_id=1)
```

### CRDTFileHandler

```python
# Todas as operações do FileHandler, mais:

# Sincronizar com remoto
result = handler.sync_with_remote(remote_events)

# Obter alterações locais
events = handler.get_local_changes_since(timestamp)

# Estado da sincronização
status = handler.get_sync_status()

# Resolver conflitos
handler.resolve_conflicts(file_id)
```

### DatabaseManager

```python
# Executar query
result = db.execute_query(
    "SELECT * FROM users WHERE username = ?",
    ("joao",)
)

# Insert/Update/Delete
db.execute_query(
    "INSERT INTO files (user_id, filename) VALUES (?, ?)",
    (1, "doc.pdf")
)

# Transacção
with db.transaction():
    db.execute_query(...)
    db.execute_query(...)
```

---

## 🧪 Testes

### Executar Testes Unitários

```powershell
# Instalar pytest
pip install pytest pytest-cov

# Executar todos os testes
pytest

# Com cobertura
pytest --cov=src --cov-report=html

# Teste específico
pytest tests/test_auth.py
```

### Testes Manuais

1. **Teste de Autenticação**
   - Registar novo utilizador
   - Login com credenciais válidas
   - Login com credenciais inválidas
   - Logout

2. **Teste de Upload**
   - Upload de ficheiro pequeno
   - Upload de ficheiro grande
   - Upload de tipo não suportado

3. **Teste de Sincronização**
   - Criar ficheiro no Dispositivo 1
   - Sincronizar com Dispositivo 2
   - Editar em ambos (conflito)
   - Verificar resolução automática

---

## 🐛 Troubleshooting

### Erro: "No module named 'bcrypt'"
```powershell
pip install bcrypt
```

### Erro: Database locked (SQLite)
- Utilize PostgreSQL para produção
- Ou aumente o timeout do SQLite em `db_manager.py`

### Erro: Tkinter não encontrado (Linux)
```bash
sudo apt-get install python3-tk
```

### Sincronização não está a funcionar
1. Verifique os logs em `netguardian.log`
2. Confirme que ambos os dispositivos estão a usar a mesma base de dados
3. Execute: `handler.resolve_conflicts(file_id)`

### Performance lenta
1. Utilize PostgreSQL em vez de SQLite
2. Crie índices na base de dados:
   ```sql
   CREATE INDEX idx_files_user ON files(user_id);
   CREATE INDEX idx_events_entity ON crdt_events(entity_id);
   ```
3. Aumente a frequência de snapshots CRDT

---

## 🤝 Contribuir

Contribuições são bem-vindas! Siga estes passos:

1. **Fork o projeto**
2. **Crie uma branch** (`git checkout -b feature/NovaFuncionalidade`)
3. **Commit suas mudanças** (`git commit -m 'Add: Nova funcionalidade'`)
4. **Push para a branch** (`git push origin feature/NovaFuncionalidade`)
5. **Abra um Pull Request**

### Directrizes

- Siga PEP 8 para código Python
- Adicione docstrings a todas as funções
- Escreva testes para novas funcionalidades
- Actualize a documentação conforme necessário

---

## 📊 Roadmap

- [ ] Suporte a partilha de ficheiros entre utilizadores
- [ ] Integração com serviços de nuvem (Google Drive, Dropbox)
- [ ] Aplicação móvel (React Native)
- [ ] API REST para terceiros
- [ ] Versionamento avançado de ficheiros
- [ ] Pré-visualização de ficheiros na interface
- [ ] Suporte a pastas/directórios
- [ ] Encriptação end-to-end
- [ ] Modo offline completo
- [ ] Sincronização em tempo real via WebSockets

---

## 📄 Licença

Este projeto é licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 👥 Autores

**NetGuardian Team**
- Desenvolvido como projeto acadêmico/profissional
- Outubro 2025

---

## 🙏 Agradecimentos

- [CRDT Tech](https://crdt.tech/) - Conceitos de CRDTs
- [Adobe Creative Cloud](https://www.adobe.com/) - Inspiração de design
- Comunidade Python - Bibliotecas fantásticas

---

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/NetGuardian/issues)
- **Email**: suporte@netguardian.com
- **Documentação**: [Wiki do Projecto](https://github.com/seu-usuario/NetGuardian/wiki)

---

## 📈 Estado do Projecto

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Versão Actual:** 1.0.0  
**Última Actualização:** Outubro 2025

---

<div align="center">
  <strong>🛡️ NetGuardian - Os seus ficheiros, seguros e sincronizados 🛡️</strong>
</div>
