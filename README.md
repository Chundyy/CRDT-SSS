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
|                     |                      |
|                     |                      |
|                     |                      |

(Preencha com os nomes e contatos dos participantes)

---

Este projeto é distribuído sob a licença MIT. Consulte o arquivo LICENSE para mais informações.
