# Documento de Arquitetura de Software (DAS) — **Sistema de Gestão e Mediação de Estágios Obrigatórios - IBMEC RJ** 

## Introdução

### Proposta

Este documento tem como objetivo consolidar a elicitação inicial de requisitos do sistema, alinhando problema, escopo, funcionalidades, regras de negócio, restrições e requisitos não funcionais que deverão orientar análise, modelagem, desenvolvimento e validação.

### Escopo

O sistema deverá cobrir:

- Cadastro e autenticação dos atores (Aluno, Empresa e coordenadores/professores) do processo;
- Abertura de solicitação de estágio obrigatório;
- Submissão, armazenamento e versionamento de documentos;
- Geração ou registro do TCE e documentos correlatos;
- Validação acadêmica e institucional;
- Fluxo de aprovação por perfil;
- Acompanhamento do estágio por status, eventos, horas e relatórios;
- Gestão de pendências, aditivos, rescisão e encerramento;
- Notificações e histórico do processo;
- Status em tempo real do processo;
- Relatórios operacionais e gerenciais.

### Visão Geral

O projeto propõe uma plataforma web para centralizar a formalização, validação e acompanhamento dos estágios obrigatórios do IBMEC, conectando aluno, empresa concedente, coordenação/secretaria e professor orientador em um fluxo único, com rastreabilidade documental, regras acadêmicas por curso e menor dependência de processos manuais. A proposta técnica atual do projeto considera back-end em Django, banco relacional e uma API com motor de regras para validar exigências acadêmicas e operacionais.

Pela base normativa usada pelo grupo, o estágio deve ser tratado como **ato educativo supervisionado**, não apenas como vínculo administrativo. Isso impacta diretamente o sistema: a solução precisa considerar matrícula e frequência regulares, compatibilidade entre estágio e formação acadêmica, professor orientador, supervisor da concedente, documentação obrigatória, jornada compatível com aulas, acompanhamento institucional e controle da carga horária validada para integralização curricular.

## Representação Arquitetural

### Cliente-Servidor

O sistema utiliza o modelo Cliente-Servidor, onde o processamento é distribuído entre o fornecedor de um serviço (servidor) e o requerente do serviço (cliente). No contexto deste projeto, o servidor centraliza as regras de negócio acadêmicas e a persistência de dados, enquanto o cliente provê a interface para os diferentes perfis de usuários (Aluno, Empresa, Orientador e Coordenação).

**Cliente:**

- **View:** Interface desenvolvida para permitir que o **Aluno** inicie solicitações, envie documentos e tenha acesso ao status em tempo real, a **Empresa** envie documentos e a **Coordenação** realize validações. A interface é responsável por coletar os inputs (como o upload de documentos do **RF05**) e exibir o status do workflow (conforme o **RF09**).
    
**Servidor:**

- **Controller:** Atua como o ponto de entrada das requisições da API. Ele recebe as solicitações do frontend, gerencia a autenticação baseada em perfis (**RNF01**) e direciona as chamadas para os serviços corretos, retornando as respostas em formato compatível com a integração.

- **Service:** Camada onde reside o **Motor de Regras** mencionado na visão geral do projeto. É responsável pela lógica de negócio complexa, como validar se a jornada é compatível com as aulas, verificar se o aluno está apto para o estágio (**RF07**) e processar a mudança de estados do workflow (conforme o **RNF09**).

- **Model:** Gerencia a persistência das entidades no banco de dados relacional, garantindo a integridade transacional e mantendo a trilha de auditoria e o histórico de ações dos usuários (**RF13**).

## Objetivos de Arquitetura e Restrições

### Objetivos

- **Segurança:** O sistema deve garantir que o acesso a documentos e dados sensíveis seja restrito via autenticação e autorização baseada em perfis (RBAC), protegendo uploads e downloads contra acessos indevidos.
- **Persistência:** Utilização de um banco de dados relacional para garantir a integridade transacional das aprovações e o armazenamento do histórico completo de auditoria de cada processo de estágio.
- **Privacidade:** Tratamento de dados pessoais e documentos seguindo os princípios de minimização e necessidade, com retenção segura conforme as normas institucionais.
- **Middlewares:** Uso de middlewares no Backend para interceptar requisições, validando tokens de autenticação e garantindo que apenas usuários autorizados acessem rotas críticas antes de chegarem à lógica de negócio.
- **Desempenho:** As operações de consulta de processos e carregamento de listas devem responder em tempo adequado para o uso administrativo, com feedback visual (progress bar) durante o upload de documentos pesados.
- **Reusabilidade:** No Frontend, uso de componentes modulares para formulários e cards de status. No Backend, a lógica de validação acadêmica é centralizada em módulos/serviços reutilizáveis por diferentes tipos de curso.

### Restrições

**Tamanho da tela:** A aplicação deve ser responsiva, priorizando o uso em desktops para perfis administrativos e alunos, mas adaptável para visualização de status em dispositivos móveis.

**Portabilidade:** O sistema deve ser acessível via navegadores modernos, sem necessidade de instalação de plugins locais.

| IE | Edge  | Firefox | Chrome | Safari | Googlebot |
| -- | ----- | ------- | ------ | ------ | --------- |
| 11 | >= 14 | >= 52   | >= 49  | >= 10  | Sim       |

**Serviços:** Os serviços oferecidos dependem da disponibilidade da API Django e do serviço de armazenamento de arquivos (Media Storage) para os documentos.

**Acesso à internet:** A aplicação está limitada apenas à conexão com internet, não possuindo modo offline funcional devido à necessidade de validação de documentos em tempo real.

### Ferramentas Utilizadas

- **Python:** Linguagem de programação robusta utilizada no desenvolvimento do Back-end.
- **Django:** Framework web de alto nível para o desenvolvimento ágil da API e do motor de regras acadêmicas.
- **MySQL:** Banco de dados relacional utilizado para persistência e integridade dos dados.
- **Figma:** Ferramenta utilizada para o design de interface (UI) e prototipagem do fluxo do usuário.
- **Git/GitHub:** Sistema de controle de versão para colaboração do time e versionamento do código-fonte.

## Visão de Caso de Uso

> https://projetos-de-extensao.github.io/PBE_26.1_8002_I/Elaboracao/casos_de_uso/

## Visão de Implementação

A implementação do sistema segue o paradigma de Orientação a Objetos, utilizando o ORM (Object-Relational Mapping) do Django para mapear as classes de domínio para o banco de dados relacional. Abaixo, o Diagrama de Classes detalha a estrutura das entidades, seus atributos e os métodos principais que regem o ciclo de vida do estágio.

> https://projetos-de-extensao.github.io/PBE_26.1_8002_I/Elaboracao/diagrma_de_classes/

## Visão de Dados

A persistência utiliza um **banco de dados relacional** para garantir a integridade das transações (como a aprovação de um documento que altera o status do processo). O sistema gerencia não apenas dados textuais, mas também o versionamento e armazenamento de arquivos (PDFs) vinculados a cada etapa do estágio (**RF20**).

## Tamanho e Desempenho

O sistema é projetado para suportar múltiplos processos simultâneos sem perda de consistência (**RNF03**). As consultas de status e listagens são otimizadas para o uso administrativo diário, e o sistema de upload deve gerenciar arquivos de documentação sem travar a interface do usuário (**RNF03**).

## Qualidade

A qualidade é assegurada pela **rastreabilidade total** (cada alteração de status registra quem a fez e quando) e pela **validade normativa**. O sistema impede que processos avancem sem os documentos obrigatórios (**RF07**), reduzindo erros operacionais e garantindo que o IBMEC esteja sempre em conformidade com a Lei do Estágio.

## Autor(es)

| Data | Versão | Descrição | Autor(es) |
| -- | -- | -- | -- |
| 11/04/2026 | 1.0 | Criação do documento | Letícia Valladão |

## 🎀 Dados do Documento

> id: DAS-Estagios <br/> title: DAS do Site para Gerenciamento de Estágios para a IBMEC
