Sprint 0
Objetivo: criação da estrutura do projeto, CI, designs base e linha de base de segurança.
Ricardo e Gonçalo


Desenhar o esquema da base de dados e criar migrações para as entidades principais (ficheiros, utilizadores, metadados CRDT).
Criar o esqueleto do módulo CRDT (interfaces LWW, interface de persistência de estado).
Entregáveis: scripts de migração da BD, esqueleto do módulo CRDT, documento de arquitetura.
Concluído quando: as migrações correm localmente; o esquema foi revisto; as interfaces CRDT estão documentadas.


Tiago e Fabiano


Criar a estrutura inicial da aplicação desktop NetGuardian (abordagem Electron ou PyInstaller) e o shell básico de UI.
Integrar a aplicação com o backend de desenvolvimento (endpoint fictício).
Entregáveis: repositório da aplicação, package.json / requirements.txt, instruções de execução.
Concluído quando: a aplicação arranca, liga-se ao API fictício e o build CI é aprovado.


André e Diogo


Criar o modelo de ameaças e lista de verificação de segurança; plano inicial de pentest (incluir cenário de ransomware).
Configurar verificações de segurança no CI (SAST, verificação de dependências).
Entregáveis: documento de modelo de ameaças, tarefas de segurança adicionadas ao CI.
Concluído quando: a checklist foi revista e pelo menos uma análise estática está configurada.

------------------------------------------------------------------------------------------

Sprint 1
Objetivo: implementar a lógica CRDT, APIs do backend, funcionalidades base da aplicação e testes de segurança iniciais.

Ricardo e Gonçalo


Implementar a lógica CRDT LWW e persistência atómica de estado (classe de armazenamento separada).
Implementar APIs de backend para listar/sincronizar ficheiros e expor endpoints CRDT.
Entregáveis: módulo CRDT funcional, endpoints API, testes unitários CRDT.
Concluído quando: testes unitários CRDT passam; respostas da API validadas segundo o spec.


Tiago e Fabiano


Implementar upload/download de ficheiros, visualização do estado de sincronização na app e ligação ao backend real.
Integrar o build do front-end na aplicação desktop.
Entregáveis: app capaz de enviar/receber ficheiros e mostrar o estado de sincronização.
Concluído quando: upload/download testado de ponta a ponta em Windows; pipeline de empacotamento funcional.


André & Diogo


Executar testes de vulnerabilidade (cenário de ransomware) em staging; reforçar armazenamento e backups.
Validar configuração segura de SFTP, gestão de segredos e permissões de ficheiros.
Entregáveis: relatório de pentest, tickets de correção, teste de backup/restore.
Concluído quando: falhas críticas/maiores registadas e atribuídas; correções básicas implementadas.

------------------------------------------------------------------------------------------

Sprint 2
Objetivo: Finalizar funcionalidades, corrigir problemas de segurança, QA, criar executável/instalador para Windows.

Ricardo e Gonçalo


Otimizar índices da BD, finalizar casos limite de resolução de conflitos CRDT, adicionar testes de integração.
Entregáveis: migração otimizada da BD, conjunto de testes de integração, documentação do comportamento CRDT.
Concluído quando: testes de integração passam; desempenho medido e documentado.


Tiago e Fabiano


Finalizar o empacotamento: gerar executável/instalador Windows (Electron ou PyInstaller), incluir dependências.
Polir UX e corrigir bugs; criar artefacto de lançamento e testar instalação em VM limpa.
Entregáveis: instalador assinado ou executável único, notas de versão, job de empacotamento no CI.
Concluído quando: o instalador instala e corre numa VM Windows limpa; testes básicos de fumo passam.


André e Diogo


Re-testar o sistema após correções, executar checklist red team completa (incluindo mitigação de ransomware) e produzir relatório final de segurança.
Implementar monitorização/alertas para operações suspeitas em ficheiros.
Entregáveis: relatório final de segurança, configuração de monitorização, correções críticas resolvidas.
Concluído quando: não há vulnerabilidades críticas em aberto; alertas de monitorização demonstrados.
