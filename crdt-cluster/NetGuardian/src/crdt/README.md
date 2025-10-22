# 🔄 CRDT Module - NetGuardian

## Módulo de CRDTs State-Based para Gerenciamento Distribuído de Arquivos

Este módulo implementa **Conflict-free Replicated Data Types (CRDTs)** para permitir sincronização multi-device com resolução automática de conflitos.

---

## 📦 Componentes

### 1. **VectorClock** (`vector_clock.py`)
- Rastreamento de causalidade entre eventos
- Detecta eventos concorrentes vs. causalmente relacionados
- Garante ordem correta de eventos distribuídos

### 2. **LWWRegister** (`lww_register.py`)
- Last-Write-Wins Register (CRDT state-based)
- Resolve conflitos usando timestamps + node_id
- Merge determinístico e comutativo

### 3. **EventStore** (`event_store.py`)
- Event sourcing com PostgreSQL
- Armazenamento append-only de eventos
- Snapshots para recuperação rápida
- Query por entidade, tipo, ou timestamp

### 4. **CRDTManager** (`crdt_manager.py`)
- API de alto nível para operações CRDT
- Gerencia registros LWW
- Coordena event store e sincronização
- Reconstrução de estado a partir de eventos

### 5. **SyncEngine** (`sync_engine.py`)
- Motor de sincronização entre nós
- Suporta pull, push, e bidirectional sync
- Tracking de status de sincronização
- Auto-sync periódico (configurável)

---

## 🚀 Quick Start

```python
from src.database.db_manager import DatabaseManager
from src.file_manager.crdt_file_handler import CRDTFileHandler

# Inicializar
db = DatabaseManager()
db.initialize_database()

# Criar handler
handler = CRDTFileHandler(
    db_manager=db,
    user_id=1,
    node_id="meu-laptop"
)

# Upload com CRDT tracking
success, msg = handler.upload_file("arquivo.pdf")

# Sincronizar com outro device
remote_events = [...]  # Do servidor
result = handler.sync_with_remote(remote_events)

# Ver status
status = handler.get_sync_status()
print(status)
```

---

## 🏗️ Arquitetura

```
┌──────────────────────────────────────┐
│        Application Layer             │
│    (CRDTFileHandler)                 │
└────────────┬─────────────────────────┘
             │
┌────────────▼─────────────────────────┐
│         CRDT Manager                 │
│  ┌──────────────┐  ┌──────────────┐ │
│  │ LWW Register │  │ VectorClock  │ │
│  └──────────────┘  └──────────────┘ │
│  ┌──────────────┐  ┌──────────────┐ │
│  │  EventStore  │  │  SyncEngine  │ │
│  └──────────────┘  └──────────────┘ │
└────────────┬─────────────────────────┘
             │
┌────────────▼─────────────────────────┐
│       PostgreSQL Database            │
│  • crdt_events                       │
│  • crdt_snapshots                    │
│  • crdt_sync_log                     │
└──────────────────────────────────────┘
```

---

## 📊 Schema do Banco de Dados

### `crdt_events`
```sql
CREATE TABLE crdt_events (
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
```

### `crdt_snapshots`
```sql
CREATE TABLE crdt_snapshots (
    entity_id VARCHAR(255) PRIMARY KEY,
    state JSONB NOT NULL,
    vector_clock JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### `crdt_sync_log`
```sql
CREATE TABLE crdt_sync_log (
    id SERIAL PRIMARY KEY,
    node_id VARCHAR(255) NOT NULL,
    last_sync TIMESTAMP NOT NULL,
    events_synced INTEGER DEFAULT 0,
    sync_direction VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🔄 Como Funciona

### 1. **Criação de Estado**
```python
crdt.create_file_state("file_1", {
    'filename': 'doc.pdf',
    'size': 1024
})
```
- Cria LWWRegister com vector clock
- Gera evento 'file_created'
- Persiste no event store
- Salva snapshot

### 2. **Atualização**
```python
crdt.update_file_state("file_1", {
    'size': 2048
})
```
- Incrementa vector clock
- Atualiza timestamp
- Gera evento 'file_updated'
- Merge automático se necessário

### 3. **Sincronização**
```python
# Pull de eventos remotos
events = [...]  # Do servidor
merged = crdt.sync_from_remote(events)

# Push de eventos locais
local_events = crdt.get_changes_since(last_sync)
```
- Compara vector clocks
- Merge automático usando LWW
- Resolve conflitos deterministicamente

### 4. **Resolução de Conflitos**

**Cenário:**
- Device A: edita às 10:00
- Device B: edita às 10:05 (sem saber de A)

**Resolução:**
```
if timestamp_B > timestamp_A:
    winner = B
elif timestamp_B == timestamp_A:
    winner = max(node_id_A, node_id_B)  # Determinístico
```

---

## 🎯 Propriedades CRDT

### ✅ **Comutatividade**
```
merge(A, B) = merge(B, A)
```

### ✅ **Associatividade**
```
merge(merge(A, B), C) = merge(A, merge(B, C))
```

### ✅ **Idempotência**
```
merge(A, A) = A
```

### ✅ **Convergência**
Todos os nós que recebem os mesmos eventos convergem para o mesmo estado.

---

## 📈 Performance

### Otimizações:
- **Snapshots**: Estados salvos periodicamente
- **Índices**: Em entity_id, timestamp, event_type
- **Batch Operations**: Processar múltiplos eventos de uma vez
- **Cache**: Registros ativos em memória

### Benchmarks (estimados):
- **Create**: ~10ms
- **Update**: ~5ms
- **Sync 100 events**: ~50ms
- **Rebuild from events**: ~100ms (1000 eventos)

---

## 🔧 Configuração

### PostgreSQL (Local)
```bash
# .env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=netguardian
DB_USER=postgres
DB_PASSWORD=senha
```

### PostgreSQL (Ubuntu Server)
```bash
# .env
DB_HOST=192.168.1.100
DB_PORT=5432
DB_NAME=netguardian
DB_USER=netguardian_user
DB_PASSWORD=senha_segura
```

---

## 🧪 Testes

Execute os exemplos:
```bash
cd examples
python crdt_examples.py
```

Opções:
1. Operações Básicas
2. Sincronização Multi-Device
3. Resolução de Conflitos
4. Event Sourcing
5. Monitoramento de Status

---

## 📝 API Reference

### CRDTManager

```python
# Criar estado
create_file_state(file_id: str, metadata: dict) -> bool

# Atualizar estado
update_file_state(file_id: str, updates: dict) -> bool

# Delete (tombstone)
delete_file_state(file_id: str) -> bool

# Obter estado atual
get_file_state(file_id: str) -> dict

# Sincronizar
sync_from_remote(events: List[Event]) -> int

# Obter mudanças
get_changes_since(since: datetime) -> List[Event]

# Reconstruir
rebuild_state_from_events(file_id: str) -> LWWRegister
```

### SyncEngine

```python
# Pull sync
pull_sync(remote_events: List[Event]) -> dict

# Push sync
push_sync(since: datetime = None) -> dict

# Bidirectional
bidirectional_sync(remote_events, since) -> dict

# Status
get_sync_status() -> dict

# Resolver conflitos
resolve_conflicts(entity_id: str) -> bool
```

---

## 🐛 Troubleshooting

### Problema: Conflitos não resolvem
**Solução:**
```python
handler.resolve_conflicts(file_id)
```

### Problema: Estado inconsistente
**Solução:**
```python
register = crdt.rebuild_state_from_events(file_id)
crdt.registers[file_id] = register
```

### Problema: Sincronização lenta
**Soluções:**
- Usar snapshots mais frequentes
- Processar eventos em batch
- Otimizar índices do banco

---

## 📚 Referências

- [CRDT Tech](https://crdt.tech/)
- [Shapiro et al. - CRDTs Paper](https://hal.inria.fr/inria-00555588/document)
- [Vector Clocks Explained](https://en.wikipedia.org/wiki/Vector_clock)
- [Event Sourcing - Martin Fowler](https://martinfowler.com/eaaDev/EventSourcing.html)

---

## 🤝 Contribuindo

Para adicionar novos tipos de CRDT:

1. Implementar em novo arquivo (ex: `g_counter.py`)
2. Seguir interface: `set()`, `get()`, `merge()`
3. Adicionar testes
4. Atualizar `__init__.py`

---

## 📄 Licença

Este módulo faz parte do NetGuardian.

---

**Criado em:** Outubro 2025  
**Versão:** 1.0.0  
**Autor:** NetGuardian Team
