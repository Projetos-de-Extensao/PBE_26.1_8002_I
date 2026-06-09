# Requisitos Levantados
## Introdução
 Este documento apresenta os requisitos elicitados para a construção do sistema, definindo claramente as funcionalidades necessárias para atender aos três perfis principais de usuários: Aluno, Empresa e Coordenador. Os requisitos aqui descritos foram levantados para garantir que a plataforma ofereça:
- Acompanhamento de status em tempo real e interfaces intuitivas.
- Um motor de regras de negócio capaz de validar pré-requisitos acadêmicos específicos de cada curso e limites de carga horária.
- Gestão documental completa, incluindo a geração automática do Termo de Compromisso de Estágio (TCE), Planos de Atividades e controle de apólices de seguro.
Através deste levantamento, a equipe de desenvolvimento possui as diretrizes exatas do que deve ser implementado para entregar um sistema que reduza erros e otimize o tempo de resposta da coordenação.

## Requisitos Funcionais 

|ID|Descrição|
|----|-------------|
|RF01| **Autenticação Institucional**	O sistema deve permitir login via e-mail institucional|
|RF02| **Controle de Acesso**	O sistema deve possuir perfis distintos (Aluno, Coordenador, Empresa)|
|RF03| **Gestão de Privilégios** O sistema deve aplicar permissões diferentes por perfil, restringindo visualização, edição e validações |
|RF04| **Checklist Dinâmico**	O sistema deve validar requisitos específicos para cada curso |
|RF05| **Upload de Documentos**	O sistema deve permitir envio de arquivos|
|RF06| **Repositório de Templates**	O sistema deve fornecer modelos de documentos |
|RF07| **Validação Automática**	O sistema deve validar dados com base em regras legais/acadêmicas|
|RF08| **Análise automatizada**	O sistema deve analisar documentos e gerar score de conformidade|
|RF09| **Gestão de Status**	O sistema deve gerenciar estados do processo para acompanhamento em tempo real |
|RF10| **Aprovação/Reprovação**	O sistema valida e o coordenador tem a possibilidade de interferir na decisão caso necessário |
|RF11| **Justificativa Obrigatória**	O sistema deve exigir justificativa em caso de rejeição|
|RF12| **Histórico**	O sistema deve armazenar histórico completo com data e assinatura de usuário |
|RF13| **Reenvio de Documentos**	O sistema deve permitir correções e reenvios |
|RF14| **Cálculo de Horas**	O sistema deve contabilizar automaticamente horas |
|RF15| **Validação de Jornada**	O sistema deve verificar limites legais de carga horária|
|RF16| **Abertura de Solicitação**	O aluno deve iniciar o processo informando a vaga que ele pretende preencher |
|RF17| **Filtros de Pesquisa** O sistema deve permitir filtros por curso, empresa, aluno, status, período e situação documental. |
|RF18| **Armazenamento de documentos** O sistema deve armazenar e versionar os documentos vinculados a cada etapa do processo. |

## Requisitos Não-Funcionais 

|ID|Descrição|
|----|-------------|
|RNF01| **Segurança	Autenticação**	O sistema deve exigir autenticação segura para acesso às áreas protegidas.|
|RNF02| **Segurança	Proteção de Dados**	Os dados devem ser armazenados de forma segura|
|RNF03| **Desempenho	Escalabilidade**	O sistema deve suportar múltiplos usuários e processos simultâneos |
|RNF04| **Usabilidade	Interface**	A interface e fluxo devem ser intuitivos e de fácil uso |
|RNF05| **Legal	Conformidade**	O sistema deve seguir a Lei 11.788/08|
|RNF06| **Disponibilidade	Sistema**	O sistema deve ter alta disponibilidade |
|RNF07| **Manutenibilidade	Código**	O sistema deve ser modular e de fácil manutenção|
|RNF08| **Extensibilidade	Arquitetura**	O sistema deve permitir futuras integrações|
|RNF09| **Controle de Acesso** O sistema deve permitir acesso à documentos e dados pessoais apenas a perfis autorizados. |
|RNF10| **Controle de Fluxo** O fluxo deve ser guiado por etapas, reduzindo erros de preenchimento.|

## Regras de Negógio

|ID|Descrição|
|----|-------------|
|RN01| O sistema só deve permitir que o aluno realize login na plataforma se ele estiver devidamente matriculado na disciplina "Estágio Supervisionado" |
|RN02| O sistema deve impedir a aprovação do estágio caso a carga horária oferecida pela empresa seja incompatível com a quantidade mínima de horas exigida pelo curso do aluno |
|RN03| O sistema deve controlar a jornada de estágio e emitir um alerta/bloqueio se a carga horária informada ultrapassar os limites diários e semanais permitidos por lei |
|RN04| O sistema deve restringir e controlar o tempo máximo que um aluno pode estagiar em uma mesma empresa concedente |
|RN05| O estágio só poderá ter seu status alterado para "Aprovado" e ser iniciado após a validação de todos os requisitos legais obrigatórios, o que inclui a aprovação do TCE e a anexação de uma Apólice de Seguro válida |
|RN06| O sistema deve realizar uma validação prévia (automática) para verificar se as atividades propostas pela empresa têm relação com o curso do aluno, bloqueando atividades fora da área de formação, mediante análise baseada nos documentos do curso |
|RN07| O aluno não pode prosseguir com a formalização do estágio em uma empresa que não tenha sido previamente aprovada/homologada pela faculdade no sistema |
|RN08| Toda empresa cadastrada deve possuir, obrigatoriamente, os dados: CNPJ, Razão Social (Nome), Áreas com vagas disponíveis e Localização |

## Autor(es)
| Data | Versão | Descrição | Autor(es) |
| -- | -- | -- | -- |
| 15/04/2026 | 1.0 | Criação do documento | Letícia Valladão |
| 09/06/2026 | 1.1 | Remoção de RF12 (Notificações), RF17 (Assinatura Digital), RN02 (Pré-requisitos PPC) e RN08 (Notificações de atraso) — fora do escopo. Renumeração dos itens subsequentes. | Roger |


## Dados do Documento
> id: Requisitos-Estagios <br/> title: Elicitação de Requisitos do Site para Gerenciamento de Estágios para a IBMEC


