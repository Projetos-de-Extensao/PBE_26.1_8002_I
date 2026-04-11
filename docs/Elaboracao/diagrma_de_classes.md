---
id: diagrama_de_classes
title: Diagrama de Classes
---

# Diagrama de Classes

## Objetivo

Este documento apresenta o modelo de classes conceitual do Sistema de Gestão e Mediação de Estágios Obrigatórios do IBMEC RJ. A modelagem foi derivada do arquivo `documento_elicitacao_requisitos_estagio_ibmec.md` e, nesta fase de elaboração, mostra apenas classes e relacionamentos UML, sem atributos e sem métodos.

## Premissas de modelagem

- O recorte considera somente o fluxo de estágio obrigatório.
- As classes foram organizadas em três blocos para manter legibilidade: identidade e atores, núcleo do processo e acompanhamento/auditoria.
- Estados, permissões detalhadas e campos internos não aparecem como classes neste momento.
- `CoordenacaoSecretaria` foi mantida como uma única classe até a validação do papel exato de coordenação e secretaria junto ao cliente.
- TCE, convênio, termo de realização e demais artefatos legais continuam representados por `Documento` e `TipoDocumento`, evitando especializações prematuras.

## Visão geral das classes propostas

| Bloco | Classes |
| --- | --- |
| Identidade e atores | `Usuario`, `Perfil`, `Aluno`, `ProfessorOrientador`, `CoordenacaoSecretaria`, `SupervisorEmpresa`, `EmpresaConcedente`, `Curso`, `RegraCurso` |
| Núcleo do processo | `ProcessoEstagio`, `PlanoAtividades`, `Documento`, `TipoDocumento`, `Aprovacao`, `Pendencia`, `HistoricoStatus`, `Aditivo`, `Rescisao` |
| Acompanhamento e governança | `RegistroCargaHoraria`, `RelatorioPeriodico`, `RelatorioFinal`, `AvaliacaoDesempenho`, `ParecerAcademico`, `Notificacao`, `LogAuditoria` |

## Visão 1. Identidade, atores e contexto acadêmico

Para reduzir cruzamentos, padronizar a escala visual e evitar rótulos sobre linhas, a visão de identidade foi dividida em recortes menores com layout mais controlado.

### Visão 1A. Hierarquia de usuários e perfis

```puml
@startuml
top to bottom direction
hide empty members
skinparam classAttributeIconSize 0
skinparam linetype polyline
skinparam nodesep 70
skinparam ranksep 70
skinparam Padding 20
skinparam ArrowFontSize 12

class Perfil
abstract class Usuario
class Aluno
class ProfessorOrientador
class CoordenacaoSecretaria
class SupervisorEmpresa

Usuario "1..*" -- "1..*" Perfil : assume
Usuario <|-- Aluno
Usuario <|-- ProfessorOrientador
Usuario <|-- CoordenacaoSecretaria
Usuario <|-- SupervisorEmpresa

Perfil -[hidden]- Usuario
Aluno -[hidden]- ProfessorOrientador
ProfessorOrientador -[hidden]- CoordenacaoSecretaria
CoordenacaoSecretaria -[hidden]- SupervisorEmpresa
@enduml
```

### Visão 1B. Contexto acadêmico e institucional

```puml
@startuml
top to bottom direction
hide empty members
skinparam classAttributeIconSize 0
skinparam linetype polyline
skinparam nodesep 70
skinparam ranksep 70
skinparam Padding 20
skinparam ArrowFontSize 12

class Aluno
class ProfessorOrientador
class CoordenacaoSecretaria
class Curso
class RegraCurso
class EmpresaConcedente
class SupervisorEmpresa

Aluno "1" --> "1" Curso : matricula
ProfessorOrientador "0..*" --> "0..*" Curso : atua
CoordenacaoSecretaria "0..*" --> "0..*" Curso : administra
Curso "1" o-- "1..*" RegraCurso : regras
EmpresaConcedente "1" o-- "1..*" SupervisorEmpresa : designa

Aluno -[hidden]- ProfessorOrientador
ProfessorOrientador -[hidden]- CoordenacaoSecretaria
Curso -[hidden]- EmpresaConcedente
RegraCurso -[hidden]- SupervisorEmpresa
@enduml
```

### Leitura da visão

- `Aluno`, `ProfessorOrientador`, `CoordenacaoSecretaria` e `SupervisorEmpresa` continuam como especializações de `Usuario`, mas agora aparecem isolados do contexto acadêmico para facilitar leitura.
- `Perfil` permanece separado para refletir o requisito de permissões por papel e permitir evolução futura do controle de acesso.
- `EmpresaConcedente` foi separada da hierarquia de usuários porque é uma organização do domínio, não uma conta base do sistema.
- `Curso` e `RegraCurso` ficaram em um diagrama próprio para evidenciar as regras acadêmicas sem poluir a visão de autenticação.

## Visão 2. Núcleo do processo de estágio

O núcleo do processo foi reorganizado em recortes mais curtos para manter a mesma legibilidade visual entre os blocos e reduzir desvio das setas.

### Visão 2A. Abertura do processo e regra acadêmica

```puml
@startuml
left to right direction
hide empty members
skinparam classAttributeIconSize 0
skinparam linetype polyline
skinparam nodesep 70
skinparam ranksep 70
skinparam Padding 20
skinparam ArrowFontSize 12

class Aluno
class ProcessoEstagio
class RegraCurso

Aluno "1" --> "0..*" ProcessoEstagio : inicia
ProcessoEstagio "1" --> "1" RegraCurso : aplica
@enduml
```

### Visão 2B. Vínculos institucionais do processo

```puml
@startuml
left to right direction
hide empty members
skinparam classAttributeIconSize 0
skinparam linetype polyline
skinparam nodesep 70
skinparam ranksep 70
skinparam Padding 20
skinparam ArrowFontSize 12

class ProcessoEstagio
class EmpresaConcedente
class SupervisorEmpresa
class ProfessorOrientador

ProcessoEstagio "1" --> "1" EmpresaConcedente : empresa
ProcessoEstagio "1" --> "1" SupervisorEmpresa : supervisor
ProcessoEstagio "1" --> "1" ProfessorOrientador : orientador

EmpresaConcedente -[hidden]down- SupervisorEmpresa
SupervisorEmpresa -[hidden]down- ProfessorOrientador
@enduml
```

### Visão 2C. Estrutura documental do processo

```puml
@startuml
left to right direction
hide empty members
skinparam classAttributeIconSize 0
skinparam linetype polyline
skinparam nodesep 70
skinparam ranksep 70
skinparam Padding 20
skinparam ArrowFontSize 12

class ProcessoEstagio
class PlanoAtividades
class Documento
class TipoDocumento

ProcessoEstagio "1" *-- "1" PlanoAtividades : plano
ProcessoEstagio "1" *-- "0..*" Documento : documentos
Documento "0..*" --> "1" TipoDocumento : tipo

PlanoAtividades -[hidden]down- TipoDocumento
@enduml
```

### Visão 2D. Aprovação e pendências

```puml
@startuml
left to right direction
hide empty members
skinparam classAttributeIconSize 0
skinparam linetype polyline
skinparam nodesep 70
skinparam ranksep 70
skinparam Padding 20
skinparam ArrowFontSize 12

abstract class Usuario
class ProcessoEstagio
class Aprovacao
class Pendencia

Usuario "1" --> "0..*" Aprovacao : emite
Usuario "1" --> "0..*" Pendencia : registra
ProcessoEstagio "1" *-- "0..*" Aprovacao : aprovacoes
ProcessoEstagio "1" *-- "0..*" Pendencia : pendencias

Usuario -[hidden]- ProcessoEstagio
Aprovacao -[hidden]down- Pendencia
@enduml
```

### Visão 2E. Histórico e encerramento

```puml
@startuml
left to right direction
hide empty members
skinparam classAttributeIconSize 0
skinparam linetype polyline
skinparam nodesep 70
skinparam ranksep 70
skinparam Padding 20
skinparam ArrowFontSize 12

class ProcessoEstagio
class HistoricoStatus
class Aditivo
class Rescisao

ProcessoEstagio "1" *-- "0..*" HistoricoStatus : historico
ProcessoEstagio "1" *-- "0..*" Aditivo : aditivos
ProcessoEstagio "1" *-- "0..1" Rescisao : rescisao

HistoricoStatus -[hidden]down- Aditivo
Aditivo -[hidden]down- Rescisao
@enduml
```

### Leitura da visão

- `ProcessoEstagio` continua como agregado principal, mas os relacionamentos foram separados por intenção: abertura, vínculos institucionais, documentação, aprovação e encerramento.
- `PlanoAtividades`, `Documento` e `TipoDocumento` ficaram em um recorte dedicado para destacar a estrutura documental sem misturar atores externos.
- `Aprovacao`, `Pendencia`, `HistoricoStatus`, `Aditivo` e `Rescisao` foram repartidos em blocos menores para reduzir cruzamentos e sobreposição de rótulos.
- O layout foi padronizado com setas mais curtas, rótulos menores e caminhos menos tortuosos.

## Visão 3. Acompanhamento, encerramento e rastreabilidade

O acompanhamento posterior à aprovação também foi padronizado para manter escala semelhante entre os blocos e evitar diferenças excessivas de tamanho visual.

### Visão 3A. Registro de horas e entregas do aluno

```puml
@startuml
left to right direction
hide empty members
skinparam classAttributeIconSize 0
skinparam linetype polyline
skinparam nodesep 70
skinparam ranksep 70
skinparam Padding 20
skinparam ArrowFontSize 12

class Aluno
class ProcessoEstagio
class RegistroCargaHoraria
class RelatorioPeriodico
class RelatorioFinal

Aluno "1" --> "0..*" RelatorioPeriodico : submete
Aluno "1" --> "0..1" RelatorioFinal : entrega
ProcessoEstagio "1" *-- "0..*" RegistroCargaHoraria : controla
ProcessoEstagio "1" *-- "0..*" RelatorioPeriodico : recebe
ProcessoEstagio "1" *-- "0..1" RelatorioFinal : encerra

Aluno -[hidden]- ProcessoEstagio
RegistroCargaHoraria -[hidden]down- RelatorioPeriodico
RelatorioPeriodico -[hidden]down- RelatorioFinal
@enduml
```

### Visão 3B. Avaliações e pareceres

```puml
@startuml
left to right direction
hide empty members
skinparam classAttributeIconSize 0
skinparam linetype polyline
skinparam nodesep 70
skinparam ranksep 70
skinparam Padding 20
skinparam ArrowFontSize 12

class ProcessoEstagio
class SupervisorEmpresa
class ProfessorOrientador
class AvaliacaoDesempenho
class ParecerAcademico

SupervisorEmpresa "1" --> "0..*" AvaliacaoDesempenho : emite
ProfessorOrientador "1" --> "0..*" ParecerAcademico : emite
ProcessoEstagio "1" *-- "0..*" AvaliacaoDesempenho : consolida
ProcessoEstagio "1" *-- "0..*" ParecerAcademico : consolida

SupervisorEmpresa -[hidden]down- ProfessorOrientador
AvaliacaoDesempenho -[hidden]down- ParecerAcademico
@enduml
```

### Visão 3C. Tipos documentais do acompanhamento

```puml
@startuml
top to bottom direction
hide empty members
skinparam classAttributeIconSize 0
skinparam linetype polyline
skinparam nodesep 70
skinparam ranksep 70
skinparam Padding 20
skinparam ArrowFontSize 12

class Documento
class RelatorioPeriodico
class RelatorioFinal
class AvaliacaoDesempenho
class ParecerAcademico

Documento <|-- RelatorioPeriodico
Documento <|-- RelatorioFinal
Documento <|-- AvaliacaoDesempenho
Documento <|-- ParecerAcademico

RelatorioPeriodico -[hidden]- RelatorioFinal
RelatorioFinal -[hidden]- AvaliacaoDesempenho
AvaliacaoDesempenho -[hidden]- ParecerAcademico
@enduml
```

### Visão 3D. Notificações e auditoria

```puml
@startuml
left to right direction
hide empty members
skinparam classAttributeIconSize 0
skinparam linetype polyline
skinparam nodesep 70
skinparam ranksep 70
skinparam Padding 20
skinparam ArrowFontSize 12

abstract class Usuario
class ProcessoEstagio
class Notificacao
class LogAuditoria

Usuario "1" --> "0..*" Notificacao : recebe
Usuario "1" --> "0..*" LogAuditoria : gera
ProcessoEstagio "1" *-- "0..*" Notificacao : dispara
ProcessoEstagio "1" *-- "0..*" LogAuditoria : audita

Usuario -[hidden]- ProcessoEstagio
Notificacao -[hidden]- LogAuditoria
@enduml
```

### Leitura da visão

- `RegistroCargaHoraria`, `RelatorioPeriodico` e `RelatorioFinal` foram mantidos juntos porque representam o acompanhamento operacional do aluno.
- `AvaliacaoDesempenho` e `ParecerAcademico` ficaram em um recorte separado para destacar os emissores distintos e evitar sobreposição com relatórios do aluno.
- As especializações de `Documento` foram agrupadas em um diagrama próprio, mais simples, para deixar a herança clara sem cruzar setas com o restante do fluxo.
- `Notificacao` e `LogAuditoria` ganharam um recorte independente para representar a camada institucional sem poluir as relações de acompanhamento.

## Decisões de modelagem que ainda dependem de validação

- Confirmar se `CoordenacaoSecretaria` deve ser quebrada em duas classes distintas.
- Validar se `SupervisorEmpresa` é o único representante autenticado da empresa ou se haverá um papel adicional para cadastro institucional.
- Decidir se `Convenio` ou `TermoCooperacao` precisam virar classes próprias em vez de permanecerem como tipos documentais.
- Refinar se `Aprovacao` continuará genérica ou se será desdobrada em classes mais específicas de análise institucional e análise acadêmica.
- Verificar se `RegistroCargaHoraria` será um lançamento manual recorrente ou uma consolidação derivada de relatórios.

## Síntese

O modelo proposto posiciona `ProcessoEstagio` como centro do domínio e distribui o restante das classes entre três preocupações principais: identidade dos atores, formalização do processo e acompanhamento auditável do estágio. Esse recorte é suficiente para orientar a próxima etapa de detalhamento do back-end sem antecipar atributos, métodos ou decisões de persistência que ainda dependem de validação com o cliente.
