# 🌸 Brainstorm para o Site de Gerenciamento de Estágios 🌸
 
## 🎀 Introdução
<p align = "justify">
O brainstorm é uma técnica de elicitação de requisitos que consiste em reunir a equipe e discutir sobre diversos tópicos gerais do projeto apresentados no documento problema de negócio. No brainstorm o diálogo é incentivado e críticas são evitadas para permitir que todos colaborem com suas próprias ideias.
</p>
 
## 🎀 Metodologia
<p align = "justify">
A equipe se reuniu para debater ideias gerais sobre o projeto presencialmente, começou 07/04/2026 e terminou [preencher],onde a equipe decidiu em conjunto as perguntas e as respostas foram transcritas para o documento.
</p>
 
## 🎀 Perguntas
 
### 💕 1. Qual o objetivo principal da aplicação?
 
<p align = "justify">
<b>Letícia</b> - Deve ser uma plataforma onde os coordenadores tenham mais facilidade para gerenciar estágio.
</p>
 
<b>Roger</b> - A plataforma deve fornecer um ambiente de gerenciamento de estágios para os coordenadores e alunos do IBMEC.
 
<b>João Gabriel</b> - O objetivo da aplicação é facilitar  e padronizar a formalização de contratos de estágio referentes aos alunos do IBMEC com empresas externas.
 
<b>Lucas</b> - O principal objetivo da aplicação é simplificar, organizar e facilitar o gerenciamento de estagios do IBMEC em um só lugar.
 
<b>Vinicius</b> - A plataforma deve gerenciar as documentações necessárias para aplicação à vaga de estágio.
</p>
 
---
 
### 💕 2. Como será o processo para cadastrar uma nova empresa?
 
<p align = "justify">
<b>Letícia</b> - Deve ser um processo prático e intuitivo onde a  empresa deve estar de acordo com a legislação e as normas requeridas pela IBMEC.
</p>
 
<b>Roger</b> - Deve ser simples e intuitivo mas que atenda todas a necessidades legais para o cadastro de uma empresa.
 
<b>João Gabriel</b> - Imagino uma tela de login exclusiva para a empresa, com campos específicos e direcionados com o que é importante para o cadastro da empresa e campos de validação de documentos.
 
<b>Lucas</b> - O processo deve validar o CNPJ, verificar se a empresa está de acordo com a legislação trabalhista, normas da IBMEC e normas do MEC e deve requerer aprovação dos coordenadores da IBMEC e conter informações importantes sobre a empresa.
 
<b>Vinicius</b> - Captar a visão geral sobre a empresa, valores da empresa, área de atuação, lugares onde a empresa é sediada.
</p>

--- 

### 💕 3. Como será a forma de adicionar vagas de estágios?(Desconsiderada)
 
<p align = "justify">
<b>Letícia</b> - A empresa deve fornecer todas as informações requeridas pelo sistema com base nas necessidades de cada curso.
</p>
 
<b>Roger</b> - O processo deve ser extenso para que não haja ambiguidade nos objetivos do estágio, tenha todas as informações que convenham para os interessados e ter autenticação não somente automática, como humana.
 
<b>João Gabriel</b> - Deve ser burocrático, com envio de documentações pertinentes à vaga de estágio, alinhada com os padrões do MEC e relacionado com os requerimentos pesquisados. Talvez com uma análise se vai ser aceito ou não em relação à documentação.
 
<b>Lucas</b> - Deverá ser um processo rígido, onde a empresa explicita o objetivo da vaga, a parte de documentos deve ser analisada, os representantes de curso devem autorizar ou não o cadastro de vaga e deverá estar de acordo com os requisitos.
 
<b>Vinicius</b> - Se tiver algum processo seletivo deverá informar como será o processo, a empresa deve informar características da vaga como carga horária, modalidade de trabalho, se é ou não presencial, localização(no caso de ser presencial), valor do salário e informações que seriam úteis para quem vai aplicar para a vaga.
</p>

> A pergunta foi desconsiderada para a elicitação de requisitos pois percebemos que as vagas não seriam encontradas pelo nosso sistema

---
 
### 💕 4. Como será o processo de aprovação do estágio?

<p align = "justify">
<b>Letícia</b> - O sistema deve validar os documentos requeridos, seguido da aprovação do coordenador e do professor responsável.
</p>
 
<b>Lucas</b> O coordenador e o professor responsável pelo aluno devem aprovar o estágio e supervisionar durante o período de atuação.
 
<b>João Gabriel</b> Deverá conectar os três atores importantes: Estudante, Empresa e Instituição de ensino. Imagino tendo o uso mínimo de papel, com toda a verificação feita pelo próprio site via PDFs junto de assinaturas digitais, junto do uso de `Termos de Compromisso` presentes nos sistma. Além disso, campos de status sobre o estagio (ex: em andamento, concluido, aprovado, pendente).
</p>
 
---
  
## 🎀 Requisitos elicitados

### 💕 Requisitos Funcionais 
 
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
|RF12| **Notificações**	O sistema deve notificar usuários sobre mudanças|
|RF13| **Histórico**	O sistema deve armazenar histórico completo com data e assinatura de usuário |
|RF14| **Reenvio de Documentos**	O sistema deve permitir correções e reenvios |
|RF15| **Cálculo de Horas**	O sistema deve contabilizar automaticamente horas |
|RF16| **Validação de Jornada**	O sistema deve verificar limites legais de carga horária|
|RF17| **Assinatura de Documentos**	O sistema deve permitir assinatura digital|
|RF18| **Abertura de Solicitação**	O aluno deve iniciar o processo informando a vaga que ele pretende preencher |
|RF19| **Filtros de Pesquisa** O sistema deve permitir filtros por curso, empresa, aluno, status, período e situação documental. |

### 💕 Requisitos Não funcionais 

|ID|Descrição|
|----|-------------|
|RNF01| **Segurança	Autenticação**	O sistema deve exigir autenticação segura para acesso às áreas protegidas.|
|RNF02| **Segurança	Proteção de Dados**	Os dados devem ser armazenados de forma segura|
|RNF03| **Desempenho	Escalabilidade**	O sistema deve suportar múltiplos usuários simultâneos |
|RNF04| **Usabilidade	Interface**	A interface e fluxo devem ser intuitivos e de fácil uso |
|RNF05| **Legal	Conformidade**	O sistema deve seguir a Lei 11.788/08|
|RNF06| **Disponibilidade	Sistema**	O sistema deve ter alta disponibilidade |
|RNF07| **Manutenibilidade	Código**	O sistema deve ser modular e de fácil manutenção|
|RNF08| **Extensibilidade	Arquitetura**	O sistema deve permitir futuras integrações|
|RNF09| **Controle de Acesso** O sistema deve permitir acesso à documentos e dados pessoais apenas a perfis autorizados. |
|RNF10| **Controle de Fluxo** O fluxo deve ser guiado por etapas, reduzindo erros de preenchimento.|
 
## 🎀 Conclusão
<p align = "justify">
Através da aplicação da técnica, foi possível elicitar alguns dos primeiros requisitos do projeto.
</p>

## 🎀 Referências Bibliográficas
 
> BARBOSA, S. D. J; DA SILVA, B. S. Interação humano-computador. Elsevier, 2010.<br/>
> [Brainstorm da Letícia Completo](https://docs.google.com/document/d/1eNMFFYWj68dkVEnu3udgYlSfP6tqbN3NqCS5GpkvDrg/edit?usp=sharing)
 
## 🎀 Autor(es)
| Data | Versão | Descrição | Autor(es) |
| -- | -- | -- | -- |
| 07/04/2026 | 1.0 | Criação do documento | Letícia Valladão, Roger Pires, Lucas Alcântara, João Gabriel de Oliveira |
| 11/04/2026 | 2.0 | Adicionado os requisitos | Letícia Valladão |

## 🎀 Dados do Documento
> id: Brainstorm-Estagios <br/> title: Brainstorm do Site para Gerenciamento de Estágios para a IBMEC
