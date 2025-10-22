#!/usr/bin/env python3
"""
NetGuardian - Script de Setup Automático
Execute este script após clonar o repositório para configurar o ambiente
"""

import os
import sys
import subprocess
import secrets
from pathlib import Path

def print_header(text):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    print_header("🐍 A verificar versão do Python")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ é necessário!")
        print(f"   Versão actual: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detectado")
    return True

def create_venv():
    """Cria ambiente virtual"""
    print_header("📦 A criar ambiente virtual")
    
    if Path("venv").exists():
        print("⚠️  Ambiente virtual já existe. A saltar...")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Ambiente virtual criado com sucesso")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao criar ambiente virtual")
        return False

def get_venv_python():
    """Retorna o caminho para o Python do ambiente virtual"""
    if sys.platform == "win32":
        return Path("venv/Scripts/python.exe")
    return Path("venv/bin/python")

def install_dependencies():
    """Instala dependências"""
    print_header("📥 A instalar dependências")
    
    venv_python = get_venv_python()
    
    if not venv_python.exists():
        print("❌ Ambiente virtual não encontrado")
        return False
    
    try:
        print("A instalar pacotes do requirements.txt...")
        subprocess.run([
            str(venv_python), "-m", "pip", "install", "--upgrade", "pip"
        ], check=True)
        
        subprocess.run([
            str(venv_python), "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        
        print("✅ Dependências instaladas com sucesso")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências")
        return False

def create_env_file():
    """Cria ficheiro .env a partir do .env.example"""
    print_header("⚙️  A configurar ambiente")
    
    if Path(".env").exists():
        response = input("⚠️  Ficheiro .env já existe. Sobrescrever? (s/N): ")
        if response.lower() != 's':
            print("A manter ficheiro .env existente")
            return True
    
    # Gerar chaves aleatórias
    app_secret = secrets.token_urlsafe(32)
    encryption_key = secrets.token_urlsafe(32)
    
    env_content = f"""# NetGuardian - Configuração de Ambiente
# Gerado automaticamente em {Path(__file__).parent}

# Base de Dados (SQLite por defeito, configure PostgreSQL para produção)
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=netguardian
# DB_USER=postgres
# DB_PASSWORD=sua_senha

# Segurança (GERADO AUTOMATICAMENTE - NÃO PARTILHAR!)
APP_SECRET_KEY={app_secret}
ENCRYPTION_KEY={encryption_key}

# Armazenamento
LOCAL_STORAGE_PATH=./local_files
CLOUD_STORAGE_ENABLED=false
MAX_FILE_SIZE_MB=100

# Logging
LOG_LEVEL=INFO
LOG_FILE=netguardian.log
"""
    
    try:
        Path(".env").write_text(env_content, encoding='utf-8')
        print("✅ Ficheiro .env criado com chaves de segurança únicas")
        print("⚠️  IMPORTANTE: Não partilhe o ficheiro .env!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar .env: {e}")
        return False

def initialize_database():
    """Inicializa a base de dados"""
    print_header("🗄️  A inicializar base de dados")
    
    venv_python = get_venv_python()
    
    try:
        subprocess.run([
            str(venv_python), "-c",
            "from src.database.db_manager import DatabaseManager; "
            "db = DatabaseManager(); "
            "db.initialize_database(); "
            "print('Base de dados inicializada!')"
        ], check=True)
        
        print("✅ Base de dados inicializada com sucesso")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao inicializar base de dados")
        print("   Pode executar manualmente:")
        print("   python -c \"from src.database.db_manager import DatabaseManager; db = DatabaseManager(); db.initialize_database()\"")
        return False

def create_directories():
    """Cria directórios necessários"""
    print_header("📁 A criar directórios")
    
    directories = ["local_files", "logs"]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
            print(f"✅ Criado: {directory}/")
        else:
            print(f"⚠️  Já existe: {directory}/")
    
    return True

def print_instructions():
    """Imprime instruções finais"""
    print_header("🎉 Setup Concluído!")
    
    venv_activate = "venv\\Scripts\\Activate.ps1" if sys.platform == "win32" else "source venv/bin/activate"
    
    print("Para iniciar a aplicação:")
    print()
    print(f"  1. Activar ambiente virtual:")
    if sys.platform == "win32":
        print(f"     .\\venv\\Scripts\\Activate.ps1")
        print()
        print("     (Se encontrar erro, execute primeiro:)")
        print("     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser")
    else:
        print(f"     source venv/bin/activate")
    print()
    print(f"  2. Executar aplicação:")
    print(f"     python main.py")
    print()
    print("📚 Documentação:")
    print("   - README.md      - Documentação completa")
    print("   - INSTALL.md     - Guia de instalação detalhado")
    print("   - CONTRIBUTING.md - Como contribuir")
    print()
    print("🐛 Problemas? Consulte INSTALL.md ou abra uma issue no GitHub")
    print()
    print("Bom trabalho! 🛡️")

def main():
    """Função principal"""
    print("\n" + "="*60)
    print("  🛡️  NetGuardian - Setup Automático")
    print("="*60)
    
    # Verificar versão do Python
    if not check_python_version():
        sys.exit(1)
    
    # Criar ambiente virtual
    if not create_venv():
        sys.exit(1)
    
    # Instalar dependências
    if not install_dependencies():
        sys.exit(1)
    
    # Criar ficheiro .env
    if not create_env_file():
        sys.exit(1)
    
    # Criar directórios
    if not create_directories():
        sys.exit(1)
    
    # Inicializar base de dados
    initialize_database()  # Não bloqueia se falhar
    
    # Instruções finais
    print_instructions()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrompido pelo utilizador")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro inesperado: {e}")
        sys.exit(1)
