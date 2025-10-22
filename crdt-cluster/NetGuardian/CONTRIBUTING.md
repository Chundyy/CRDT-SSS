# 🤝 Guia de Contribuição - NetGuardian

Obrigado pelo interesse em contribuir para o NetGuardian! Este documento explica como pode participar no desenvolvimento.

---

## 📋 Código de Conduta

- Seja respeitoso e profissional
- Aceite críticas construtivas
- Foque no que é melhor para a comunidade
- Mostre empatia com outros membros

---

## 🚀 Como Contribuir

### 1. Fork e Clone
```bash
# Fork no GitHub (clique no botão Fork)
git clone https://github.com/seu-usuario/NetGuardian.git
cd NetGuardian
git remote add upstream https://github.com/original-user/NetGuardian.git
```

### 2. Criar Branch
```bash
# Actualizar main
git checkout main
git pull upstream main

# Criar branch para a funcionalidade
git checkout -b feature/nome-da-funcionalidade
```

### 3. Fazer Alterações
```bash
# Fazer as alterações no código
# Testar localmente
python main.py

# Adicionar ficheiros
git add .
git commit -m "Add: Descrição clara da alteração"
```

### 4. Push e Pull Request
```bash
git push origin feature/nome-da-funcionalidade
```
Depois abra um Pull Request no GitHub.

---

## 📝 Convenções de Código

### Python (PEP 8)
```python
# Bom ✅
def calculate_total(items: List[Item]) -> float:
    """
    Calcula o total de itens.
    
    Args:
        items: Lista de itens a calcular
        
    Returns:
        float: Total calculado
    """
    return sum(item.price for item in items)

# Mau ❌
def calc(i):
    return sum(x.price for x in i)
```

### Docstrings
- Use docstrings em todas as funções públicas
- Siga formato Google/NumPy
- Inclua tipos (Args, Returns, Raises)

### Nomes
- **Funções/Métodos**: `snake_case`
- **Classes**: `PascalCase`
- **Constantes**: `UPPER_CASE`
- **Privados**: `_leading_underscore`

---

## 🧪 Testes

### Executar Testes
```bash
# Instalar pytest
pip install pytest pytest-cov

# Executar todos
pytest

# Com cobertura
pytest --cov=src

# Teste específico
pytest tests/test_auth.py::test_login
```

### Escrever Testes
```python
# tests/test_exemplo.py
import pytest
from src.auth.auth_manager import AuthManager

def test_register_user_success():
    """Teste de registo de utilizador bem-sucedido"""
    auth = AuthManager(db_mock)
    success, msg = auth.register_user("joao", "joao@test.com", "senha123")
    assert success is True
    assert "sucesso" in msg.lower()
```

---

## 🐛 Reportar Bugs

### Template de Issue
```markdown
## Descrição
Descrição clara do bug

## Passos para Reproduzir
1. Abrir aplicação
2. Clicar em '...'
3. Ver erro

## Comportamento Esperado
O que deveria acontecer

## Comportamento Actual
O que acontece

## Ambiente
- OS: Windows 11
- Python: 3.11
- Versão: 1.0.0

## Logs
```
[Cole os logs relevantes]
```
```

---

## ✨ Sugerir Funcionalidades

### Template de Feature Request
```markdown
## Problema
Descreva o problema que a funcionalidade resolve

## Solução Proposta
Como a funcionalidade funcionaria

## Alternativas
Outras formas de resolver

## Contexto Adicional
Screenshots, mockups, etc.
```

---

## 📦 Tipos de Contribuições

### 🐛 Bug Fixes
- Corrigir bugs existentes
- Adicionar testes para evitar regressão

### ✨ Novas Funcionalidades
- Discutir em Issue primeiro
- Seguir arquitectura existente
- Adicionar testes e documentação

### 📚 Documentação
- Melhorar README
- Adicionar exemplos
- Corrigir typos

### 🎨 UI/UX
- Melhorar interface
- Adicionar animações
- Optimizar layout

### 🔧 Refactoring
- Melhorar código existente
- Optimizar performance
- Remover código duplicado

---

## 🔍 Processo de Review

### Checklist antes de PR
- [ ] Código segue PEP 8
- [ ] Todos os testes passam
- [ ] Adicionados testes para novas funcionalidades
- [ ] Documentação actualizada
- [ ] Commit messages são claras
- [ ] Sem ficheiros sensíveis (.env, .key)

### Durante Review
- Responda aos comentários
- Faça alterações solicitadas
- Mantenha discussão profissional

---

## 📊 Commit Messages

### Formato
```
Tipo: Descrição curta (máx 50 chars)

Descrição detalhada (opcional, max 72 chars por linha)

Refs: #123
```

### Tipos
- `Add:` Nova funcionalidade
- `Fix:` Correcção de bug
- `Update:` Actualização de funcionalidade existente
- `Remove:` Remoção de código
- `Refactor:` Refactoring sem alterar funcionalidade
- `Docs:` Actualização de documentação
- `Test:` Adição/actualização de testes
- `Style:` Formatação, sem alteração de lógica

### Exemplos
```bash
git commit -m "Add: Sistema de notificações em tempo real"
git commit -m "Fix: Erro ao fazer upload de ficheiros grandes"
git commit -m "Docs: Actualizar guia de instalação para macOS"
```

---

## 🏗️ Arquitectura

### Estrutura de Módulos
```
src/
├── auth/          # Autenticação
├── crdt/          # CRDTs e sincronização
├── database/      # Acesso a dados
├── file_manager/  # Gestão de ficheiros
├── gui/           # Interface gráfica
└── utils/         # Utilitários
```

### Adicionar Novo Módulo
1. Criar pasta em `src/`
2. Adicionar `__init__.py`
3. Seguir padrões existentes
4. Documentar no README

---

## 🎯 Prioridades

### Alta Prioridade
- Correcção de bugs críticos
- Melhorias de segurança
- Correcção de perda de dados

### Média Prioridade
- Novas funcionalidades
- Melhorias de performance
- Refactoring

### Baixa Prioridade
- Melhorias cosméticas
- Optimizações menores
- Documentação adicional

---

## 💬 Comunicação

### Onde Discutir
- **Issues**: Bugs e feature requests
- **Pull Requests**: Discussão de código
- **Discussions**: Ideias gerais

### Línguas
- Português (preferencial)
- Inglês (aceitável)

---

## 📜 Licença

Ao contribuir, concorda que as suas contribuições serão licenciadas sob a licença MIT do projecto.

---

## 🙏 Reconhecimento

Todos os contribuidores serão adicionados ao ficheiro CONTRIBUTORS.md

---

**Obrigado por contribuir para o NetGuardian! 🛡️**
