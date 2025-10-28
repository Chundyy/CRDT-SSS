# 🚀 Guia de Instalação - NetGuardian

Este guia descreve o processo completo de instalação do NetGuardian para novos utilizadores.

---

## 📋 Pré-requisitos

### Obrigatórios
- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **pip** (incluído com Python)
- **Git** (opcional, para clonar) - [Download](https://git-scm.com/)

### Opcionais
- **PostgreSQL 12+** (para produção) - [Download](https://www.postgresql.org/download/)
- **VS Code** (IDE recomendada) - [Download](https://code.visualstudio.com/)

---

## 🪟 Windows

### 1. Obter o Código

**Opção A: Download ZIP**
```powershell
# Extrair o ZIP para uma pasta
# Abrir PowerShell nessa pasta
cd C:\caminho\para\NetGuardian
```

**Opção B: Git Clone**
```powershell
git clone https://github.com/seu-usuario/NetGuardian.git
cd NetGuardian
```

### 2. Criar Ambiente Virtual
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Nota**: Se encontrar erro de execução de scripts, execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Instalar Dependências
```powershell
pip install -r requirements.txt
```

### 4. Configurar Ambiente
```powershell
# Copiar ficheiro de exemplo
Copy-Item .env.example .env

# Editar com Notepad
notepad .env
```

**Mínimo necessário no .env:**
```env
APP_SECRET_KEY=sua-chave-secreta-aleatoria-aqui
ENCRYPTION_KEY=sua-chave-encriptacao-aqui
LOCAL_STORAGE_PATH=./local_files
```

**Gerar chaves aleatórias:**
```powershell
python -c "import secrets; print('APP_SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_urlsafe(32))"
```

### 5. Inicializar Base de Dados
```powershell
python -c "from src.database.db_manager import DatabaseManager; db = DatabaseManager(); db.initialize_database()"
```

### 6. Executar Aplicação
```powershell
python main.py
```

---

## 🐧 Linux / macOS

### 1. Obter o Código
```bash
git clone https://github.com/seu-usuario/NetGuardian.git
cd NetGuardian
```

### 2. Criar Ambiente Virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

**Linux**: Se falhar a instalação do Pillow/Tkinter:
```bash
sudo apt-get update
sudo apt-get install python3-tk python3-dev
```

### 4. Configurar Ambiente
```bash
cp .env.example .env
nano .env  # ou vim, gedit, etc.
```

### 5. Gerar Chaves
```bash
python3 -c "import secrets; print('APP_SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_urlsafe(32))"
```

### 6. Inicializar Base de Dados
```bash
python3 -c "from src.database.db_manager import DatabaseManager; db = DatabaseManager(); db.initialize_database()"
```

### 7. Executar Aplicação
```bash
python3 main.py
```

---

## 🐘 Configuração PostgreSQL (Opcional)

### Windows
```powershell
# Instalar PostgreSQL
# Criar base de dados
psql -U postgres
CREATE DATABASE netguardian;
CREATE USER netguardian_user WITH PASSWORD 'senha_segura';
GRANT ALL PRIVILEGES ON DATABASE netguardian TO netguardian_user;
\q
```

### Configurar .env
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=netguardian
DB_USER=netguardian_user
DB_PASSWORD=senha_segura
```

---

## ✅ Verificar Instalação

### Teste Rápido
```powershell
# Verificar Python
python --version

# Verificar dependências
pip list

# Verificar estrutura
ls src/
```

### Primeiro Login
1. Execute `python main.py`
2. Clique em "Register"
3. Crie uma conta
4. Faça login
5. Teste upload de um ficheiro

---

## 🐛 Resolução de Problemas

### Erro: "No module named 'bcrypt'"
```powershell
pip install bcrypt
```

### Erro: "Permission denied" (Linux/macOS)
```bash
chmod +x main.py
```

### Erro: Tkinter não encontrado (Linux)
```bash
sudo apt-get install python3-tk
```

### Erro: "Database is locked" (SQLite)
- Use PostgreSQL para produção
- Ou: feche todas as instâncias da aplicação

### Erro: "Import Error"
```powershell
# Reinstalar todas as dependências
pip install --upgrade --force-reinstall -r requirements.txt
```

---

## 📚 Próximos Passos

Após instalação bem-sucedida:

1. **Leia o README.md** - Documentação completa
2. **Explore o src/crdt/README.md** - Sincronização CRDT
3. **Configure múltiplos dispositivos** - Teste sincronização
4. **Consulte use_case_diagram.md** - Casos de uso

---

## 💡 Dicas

### Desenvolvimento
```powershell
# Activar ambiente virtual sempre que abrir terminal
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # Linux/macOS

# Ver logs
Get-Content netguardian.log -Tail 50  # Windows
tail -f netguardian.log               # Linux/macOS
```

### Produção
- Use PostgreSQL em vez de SQLite
- Configure backup automático
- Use HTTPS para sincronização remota
- Monitore logs regularmente

---

## 🆘 Suporte

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/NetGuardian/issues)
- **Documentação**: [README.md](README.md)
- **Email**: suporte@netguardian.com

---

**Desenvolvido com ❤️ pela NetGuardian Team**  
**Versão**: 1.0.0 | **Data**: Outubro 2025
