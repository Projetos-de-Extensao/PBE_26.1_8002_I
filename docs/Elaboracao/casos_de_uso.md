---
id: diagrama_de_casos_de_uso
title: Diagrama de Casos de Uso
---

# Diagrama de Casos de Uso

## Objetivo

Este documento apresenta os Diagramas de Casos de Uso do Sistema de Gestão e Mediação de Estágios Obrigatórios do IBMEC RJ. A modelagem foi derivada do arquivo `documento_elicitacao_requisitos_estagio_ibmec.md` e do documento de especificação de casos de uso. Os diagramas foram divididos por fase do ciclo de vida do processo para manter a legibilidade dos atores e dos casos de uso.

## Premissas de modelagem

- O escopo cobre exclusivamente o fluxo de estágio obrigatório.
- Os diagramas foram separados em sete visões correspondentes ao ciclo de vida: Visão Geral, Cadastro e Regularização, Submissão Documental, Validação e Aprovação, Monitoramento, Encerramento e Relatórios e Auditoria.
- Relacionamentos `<<include>>` representam dependências obrigatórias entre casos de uso.
- Relacionamentos `<<extend>>` representam fluxos condicionais ou opcionais.
- Atores que não participam de uma fase não aparecem naquele diagrama, mantendo o foco visual.
- `Coordenacao/Secretaria` é tratada como um único ator até validação formal do papel junto ao cliente.

## Visão geral dos diagramas propostos

| Visão | Foco | Atores envolvidos |
| --- | --- | --- |
| Visão 0 — Geral | Mapa completo de atores e grupos de UC | Todos |
| Visão 1 — Cadastro | Abertura do processo e regularização | Aluno, Empresa/Supervisor, Coord./Secretaria |
| Visão 2 — Documentos | Submissão e controle documental | Aluno, Empresa/Supervisor |
| Visão 3 — Validação | Análise, parecer e aprovação | Prof. Orientador, Coord./Secretaria |
| Visão 4 — Monitoramento | Acompanhamento do estágio ativo | Aluno, Empresa/Supervisor, Prof. Orientador |
| Visão 5 — Encerramento | Relatório final e conclusão | Aluno, Empresa/Supervisor, Prof. Orientador, Coord./Secretaria |
| Visão 6 — Auditoria | Relatórios operacionais e trilha | Coord./Secretaria |

---

## Visão 0. Mapa geral de casos de uso

Visão panorâmica que posiciona os quatro atores e os grupos funcionais do sistema, sem detalhar os relacionamentos internos de cada fase.

```plantuml
@startuml visao_0_mapa_geral

left to right direction

skinparam DefaultFontName Arial
skinparam DefaultFontSize 12
skinparam shadowing false
skinparam backgroundColor white

skinparam actor {
  BackgroundColor white
  BorderColor black
  FontColor black
}
skinparam usecase {
  BackgroundColor white
  BorderColor black
  FontColor black
  FontSize 12
}
skinparam rectangle {
  BackgroundColor white
  BorderColor black
  FontColor black
  FontSize 14
}
skinparam ArrowColor black
skinparam ArrowFontColor black
skinparam ArrowFontSize 11

actor "Aluno"                  as ALU
actor "Empresa / Supervisor"   as EMP
actor "Prof. Orientador"       as ORI
actor "Coordenacao/Secretaria" as COO

rectangle "Sistema de Gestao de Estagios IBMEC RJ" {
  usecase "Cadastro e\nRegularizacao"  as G1
  usecase "Submissao\nDocumental"      as G2
  usecase "Validacao e\nAprovacao"     as G3
  usecase "Monitoramento\ndo Estagio"  as G4
  usecase "Encerramento\ndo Processo"  as G5
  usecase "Relatorios\ne Auditoria"    as G6
}

ALU -- G1
ALU -- G2
ALU -- G4
ALU -- G5

EMP -- G1
EMP -- G2
EMP -- G4
EMP -- G5

ORI -- G3
ORI -- G4
ORI -- G5

COO -- G1
COO -- G3
COO -- G4
COO -- G5
COO -- G6

@enduml
```

### Leitura da visão

- A visão geral serve como índice visual: cada elipse representa um grupo de casos de uso detalhado nas visões seguintes.
- Todos os atores aparecem simultaneamente para evidenciar as fronteiras de responsabilidade de cada perfil.
- Os relacionamentos `<<include>>` e `<<extend>>` são detalhados nas visões específicas de cada fase.

---

## Visão 1. Cadastro e regularização

Cobre a abertura do processo de estágio, a validação de pré-condições acadêmicas, o cadastro da empresa e a parametrização das regras por curso.

```plantuml
@startuml visao_1_cadastro_regularizacao

left to right direction

skinparam DefaultFontName Arial
skinparam DefaultFontSize 12
skinparam shadowing false
skinparam backgroundColor white

skinparam actor {
  BackgroundColor white
  BorderColor black
  FontColor black
}
skinparam usecase {
  BackgroundColor white
  BorderColor black
  FontColor black
  FontSize 12
}
skinparam rectangle {
  BackgroundColor white
  BorderColor black
  FontColor black
  FontSize 14
}
skinparam ArrowColor black
skinparam ArrowFontColor black
skinparam ArrowFontSize 11

actor "Aluno"                  as ALU
actor "Empresa / Supervisor"   as EMP
actor "Coordenacao/Secretaria" as COO

rectangle "Cadastro e Regularizacao" {
  usecase "Autenticar\nno Sistema"             as UC_AUTH
  usecase "Abrir Solicitacao\nde Estagio"      as UC_ABRIR
  usecase "Validar Pre-condicoes\nAcademicas"  as UC_PREC
  usecase "Registrar Plano\nde Atividades"     as UC_PLANO
  usecase "Cadastrar Empresa\nConcedente"      as UC_EMP
  usecase "Validar Situacao\nda Empresa"       as UC_VEMP
  usecase "Cadastrar Supervisor\nda Empresa"   as UC_SUP
  usecase "Parametrizar Regras\npor Curso"     as UC_REGRAS
  usecase "Visualizar Painel\nde Pendencias"   as UC_PAINEL
}

ALU -- UC_AUTH
ALU -- UC_ABRIR
ALU -- UC_EMP
ALU -- UC_PLANO
ALU -- UC_PAINEL

EMP -- UC_AUTH
EMP -- UC_EMP
EMP -- UC_SUP
EMP -- UC_PAINEL

COO -- UC_AUTH
COO -- UC_REGRAS
COO -- UC_PAINEL

UC_ABRIR .> UC_AUTH  : <<include>>
UC_ABRIR .> UC_PREC  : <<include>>
UC_ABRIR .> UC_PLANO : <<include>>
UC_ABRIR .> UC_EMP   : <<include>>

UC_EMP .> UC_VEMP : <<include>>
UC_EMP .> UC_SUP  : <<include>>

@enduml
```

### Leitura da visão

- `Abrir Solicitacao de Estagio` agrega obrigatoriamente quatro dependências: autenticação, pré-condições, plano de atividades e cadastro de empresa.
- `Validar Pre-condicoes Academicas` é executado pelo sistema automaticamente e verifica matrícula e frequência regulares (RN-02).
- `Validar Situacao da Empresa` verifica se a concedente possui situação documental e institucional apta, conforme RN-11.
- `Parametrizar Regras por Curso` é exclusivo da Coordenação/Secretaria, pois as regras variam por PPC e DCN (RN-04).

---

## Visão 2. Submissão documental

Cobre o envio, versionamento e validação de documentos, incluindo a geração ou registro do TCE e a correção de documentos devolvidos.

```plantuml
@startuml visao_2_submissao_documental

left to right direction

skinparam DefaultFontName Arial
skinparam DefaultFontSize 12
skinparam shadowing false
skinparam backgroundColor white

skinparam actor {
  BackgroundColor white
  BorderColor black
  FontColor black
}
skinparam usecase {
  BackgroundColor white
  BorderColor black
  FontColor black
  FontSize 12
}
skinparam rectangle {
  BackgroundColor white
  BorderColor black
  FontColor black
  FontSize 14
}
skinparam ArrowColor black
skinparam ArrowFontColor black
skinparam ArrowFontSize 11

actor "Aluno"                as ALU
actor "Empresa / Supervisor" as EMP

rectangle "Submissao Documental" {
  usecase "Autenticar\nno Sistema"              as UC_AUTH
  usecase "Enviar\nDocumentos"                  as UC_UPDOC
  usecase "Validar Obrigatoriedade\nDocumental" as UC_VALDOC
  usecase "Gerar e\nRegistrar TCE"              as UC_TCE
  usecase "Consultar Status\ndos Documentos"    as UC_STSDOC
  usecase "Corrigir e Reenviar\nDocumentos"     as UC_CORRDOC
}

ALU -- UC_AUTH
ALU -- UC_UPDOC
ALU -- UC_TCE
ALU -- UC_CORRDOC
ALU -- UC_STSDOC

EMP -- UC_AUTH
EMP -- UC_TCE
EMP -- UC_STSDOC

UC_UPDOC   .> UC_AUTH   : <<include>>
UC_UPDOC   .> UC_VALDOC : <<include>>
UC_TCE     .> UC_UPDOC  : <<include>>
UC_CORRDOC .> UC_UPDOC  : <<extend>>

@enduml
```

### Leitura da visão

- `Enviar Documentos` sempre inclui `Validar Obrigatoriedade Documental`, garantindo que documentos obrigatórios por etapa não sejam ignorados (RF-16, RF-21).
- `Gerar e Registrar TCE` inclui `Enviar Documentos` porque o TCE é tratado como um documento do processo com versionamento próprio (RF-19).
- `Corrigir e Reenviar Documentos` estende `Enviar Documentos` — só ocorre quando um documento foi rejeitado ou marcado como pendente (RF-17, RF-18).
- Tanto o Aluno quanto a Empresa participam do fluxo documental, pois o TCE exige participação de ambas as partes.

---

## Visão 3. Validação e aprovação

Cobre a análise da documentação, a validação da aderência acadêmica pelo professor orientador, a emissão de pareceres e o fluxo de aprovação ou devolução pela coordenação.

```plantuml
@startuml visao_3_validacao_aprovacao

left to right direction

skinparam DefaultFontName Arial
skinparam DefaultFontSize 12
skinparam shadowing false
skinparam backgroundColor white

skinparam actor {
  BackgroundColor white
  BorderColor black
  FontColor black
}
skinparam usecase {
  BackgroundColor white
  BorderColor black
  FontColor black
  FontSize 12
}
skinparam rectangle {
  BackgroundColor white
  BorderColor black
  FontColor black
  FontSize 14
}
skinparam ArrowColor black
skinparam ArrowFontColor black
skinparam ArrowFontSize 11

actor "Prof. Orientador"       as ORI
actor "Coordenacao/Secretaria" as COO

rectangle "Validacao e Aprovacao" {
  usecase "Autenticar\nno Sistema"             as UC_AUTH
  usecase "Analisar Documentacao\ndo Processo" as UC_ANALDOC
  usecase "Validar Aderencia\nAcademica"       as UC_ADER
  usecase "Emitir Parecer\nou Pendencia"       as UC_PARECER
  usecase "Devolver Processo\npara Correcao"   as UC_DEV
  usecase "Aprovar\nEstagio"                   as UC_APROV
  usecase "Rejeitar\nEstagio"                  as UC_REJ
}

ORI -- UC_AUTH
ORI -- UC_ADER
ORI -- UC_PARECER

COO -- UC_AUTH
COO -- UC_ANALDOC
COO -- UC_PARECER
COO -- UC_DEV
COO -- UC_APROV
COO -- UC_REJ

UC_ANALDOC .> UC_AUTH    : <<include>>
UC_ADER    .> UC_AUTH    : <<include>>
UC_APROV   .> UC_ANALDOC : <<include>>
UC_APROV   .> UC_ADER    : <<include>>

UC_DEV .> UC_PARECER : <<extend>>
UC_REJ .> UC_PARECER : <<extend>>

@enduml
```

### Leitura da visão

- `Aprovar Estagio` inclui obrigatoriamente `Analisar Documentacao do Processo` e `Validar Aderencia Academica` — a aprovação só é possível após ambas as validações (RF-27, RN-10).
- `Devolver Processo para Correcao` e `Rejeitar Estagio` estendem `Emitir Parecer ou Pendencia`, pois ambos são desdobramentos condicionais do parecer negativo (RF-25, RF-26).
- O Professor Orientador é responsável exclusivo pela validação acadêmica; a Coordenação/Secretaria é responsável pela análise institucional e pela decisão final de aprovação.

---

## Visão 4. Monitoramento do estágio

Cobre o acompanhamento do estágio ativo: controle de jornada e carga horária, envio de relatórios periódicos, avaliações de desempenho, pareceres periódicos e eventos de aditivo e rescisão.

```plantuml
@startuml visao_4_monitoramento

left to right direction

skinparam DefaultFontName Arial
skinparam DefaultFontSize 12
skinparam shadowing false
skinparam backgroundColor white

skinparam actor {
  BackgroundColor white
  BorderColor black
  FontColor black
}
skinparam usecase {
  BackgroundColor white
  BorderColor black
  FontColor black
  FontSize 12
}
skinparam rectangle {
  BackgroundColor white
  BorderColor black
  FontColor black
  FontSize 14
}
skinparam ArrowColor black
skinparam ArrowFontColor black
skinparam ArrowFontSize 11

actor "Aluno"                  as ALU
actor "Empresa / Supervisor"   as EMP
actor "Prof. Orientador"       as ORI
actor "Coordenacao/Secretaria" as COO

rectangle "Monitoramento do Estagio" {
  usecase "Autenticar\nno Sistema"              as UC_AUTH
  usecase "Acompanhar Status\ndo Processo"      as UC_STATUS
  usecase "Controlar Jornada\ne Carga Horaria"  as UC_CH
  usecase "Enviar Relatorios\nPeriodicos"       as UC_RELPER
  usecase "Enviar Avaliacao\nde Desempenho"     as UC_AVAL
  usecase "Emitir Parecer\nAcademico Periodico" as UC_PARPER
  usecase "Receber\nNotificacoes"               as UC_NOTIF
  usecase "Registrar Aditivo\nde Estagio"       as UC_ADIT
  usecase "Registrar Rescisao\nAntecipada"      as UC_RESC
}

ALU -- UC_AUTH
ALU -- UC_STATUS
ALU -- UC_CH
ALU -- UC_RELPER
ALU -- UC_NOTIF

EMP -- UC_AUTH
EMP -- UC_AVAL
EMP -- UC_NOTIF

ORI -- UC_AUTH
ORI -- UC_STATUS
ORI -- UC_PARPER
ORI -- UC_RELPER
ORI -- UC_NOTIF

COO -- UC_AUTH
COO -- UC_STATUS
COO -- UC_ADIT
COO -- UC_RESC
COO -- UC_NOTIF

UC_RELPER .> UC_AUTH   : <<include>>
UC_RELPER .> UC_STATUS : <<include>>
UC_CH     .> UC_STATUS : <<include>>

UC_AVAL   .> UC_RELPER : <<extend>>
UC_PARPER .> UC_RELPER : <<extend>>
UC_ADIT   .> UC_STATUS : <<extend>>
UC_RESC   .> UC_STATUS : <<extend>>

@enduml
```

### Leitura da visão

- `Enviar Relatorios Periodicos` inclui `Acompanhar Status do Processo` porque o envio só é válido com o estágio em status **Ativo** (RF-37).
- `Enviar Avaliacao de Desempenho` e `Emitir Parecer Academico Periodico` estendem `Enviar Relatorios Periodicos` — são eventos complementares opcionais atrelados ao ciclo de relatórios (RF-38, RF-39).
- `Registrar Aditivo de Estagio` e `Registrar Rescisao Antecipada` estendem `Acompanhar Status do Processo` — são eventos excepcionais que alteram o curso do processo ativo (RN-12).
- `Receber Notificacoes` é compartilhado por todos os atores, pois o sistema dispara alertas de pendências, prazos e mudanças de status para todos os perfis envolvidos (RF-49).

---

## Visão 5. Encerramento do processo

Cobre o envio do relatório final, a anexação do termo de realização, as avaliações finais, o parecer institucional e o registro do encerramento com cálculo de carga horária.

```plantuml
@startuml visao_5_encerramento

left to right direction

skinparam DefaultFontName Arial
skinparam DefaultFontSize 12
skinparam shadowing false
skinparam backgroundColor white

skinparam actor {
  BackgroundColor white
  BorderColor black
  FontColor black
}
skinparam usecase {
  BackgroundColor white
  BorderColor black
  FontColor black
  FontSize 12
}
skinparam rectangle {
  BackgroundColor white
  BorderColor black
  FontColor black
  FontSize 14
}
skinparam ArrowColor black
skinparam ArrowFontColor black
skinparam ArrowFontSize 11

actor "Aluno"                  as ALU
actor "Empresa / Supervisor"   as EMP
actor "Prof. Orientador"       as ORI
actor "Coordenacao/Secretaria" as COO

rectangle "Encerramento do Processo" {
  usecase "Autenticar\nno Sistema"                   as UC_AUTH
  usecase "Enviar Relatorio\nFinal"                  as UC_RELFIN
  usecase "Anexar Termo\nde Realizacao"              as UC_TERMO
  usecase "Registrar Avaliacao\nFinal do Supervisor" as UC_AVALFIN
  usecase "Emitir Parecer\nFinal Institucional"      as UC_PARFIN
  usecase "Calcular Carga Horaria\np/ Integralizacao" as UC_CALCCH
  usecase "Registrar\nEncerramento"                  as UC_ENCERRAR
  usecase "Consultar Historico\ndo Processo"         as UC_HIST
}

ALU -- UC_AUTH
ALU -- UC_RELFIN
ALU -- UC_HIST

EMP -- UC_AUTH
EMP -- UC_TERMO
EMP -- UC_AVALFIN

ORI -- UC_AUTH
ORI -- UC_PARFIN
ORI -- UC_HIST

COO -- UC_AUTH
COO -- UC_ENCERRAR
COO -- UC_HIST

UC_ENCERRAR .> UC_AUTH   : <<include>>
UC_ENCERRAR .> UC_CALCCH : <<include>>
UC_ENCERRAR .> UC_RELFIN : <<include>>
UC_ENCERRAR .> UC_PARFIN : <<include>>

UC_TERMO   .> UC_ENCERRAR : <<extend>>
UC_AVALFIN .> UC_ENCERRAR : <<extend>>

@enduml
```

### Leitura da visão

- `Registrar Encerramento` é o UC central desta fase e inclui obrigatoriamente: autenticação, cálculo de carga horária, relatório final e parecer final institucional (RF-47, RF-48).
- `Anexar Termo de Realizacao` e `Registrar Avaliacao Final do Supervisor` estendem o encerramento — são documentos complementares exigidos conforme regras do curso (RF-45, RF-46).
- `Calcular Carga Horaria p/ Integralizacao` é executado automaticamente pelo sistema para verificar se a carga mínima foi atingida antes de permitir a conclusão (RN-08).
- `Consultar Historico do Processo` está disponível para todos os atores ao final, garantindo rastreabilidade e auditabilidade completa do ciclo (RF-58).