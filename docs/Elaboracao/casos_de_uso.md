---
id: diagrama_de_casos_de_uso
title: Diagrama de Casos de Uso
---

# Diagrama de Casos de Uso

## Objetivo

Este documento apresenta os Diagramas de Casos de Uso do Sistema de Gestão de Estágios do IBMEC RJ. O sistema tem como objetivo organizar, facilitar e automatizar o processo documental de estágio entre Aluno e Secretaria, considerando que o aluno já foi aprovado na vaga.

Os diagramas foram modelados de forma simples e didática, representando o ciclo básico do processo de estágio.

---

## Premissas de modelagem

- O sistema inicia após o aluno já ter sido aprovado em uma vaga de estágio.
- O foco está na gestão documental e acompanhamento do processo.
- Relacionamentos `<<include>>` representam ações obrigatórias.
- Relacionamentos `<<extend>>` representam fluxos alternativos ou opcionais.
- O sistema não é representado como ator.
- Diagramas simples, voltados para fácil compreensão.

---

## Visão geral dos casos de uso

| Fase | Casos de Uso |
|------|-------------|
| Acesso | Login |
| Início | Abrir Novo Processo |
| Documentação | Adicionar Documentos |
| Validação | Validar Contrato |
| Execução | Enviar Relatório |
| Monitoramento | Acompanhar Status |
| Comunicação | Notificações |
| Encerramento | Encerrar Processo |

---

# 1. Login

```puml
@startuml
left to right direction

actor Aluno
actor Coordenadores

rectangle "Sistema de Gestão de Estágios IBMEC RJ" {
  usecase "Fazer Login" as UC1
  usecase "Autenticar Credenciais" as UC2
  usecase "Exibir Erro de Login" as UC3
  usecase "Redefinir Senha (1º Acesso)" as UC4
}

Aluno -- UC1
Coordenadores -- UC1

UC1 ..> UC2 : <<include>>
UC3 ..> UC1 : <<extend>>
UC4 ..> UC1 : <<extend>>

@enduml

```

### Login

- Atores:
	- Aluno
	- Coordenação

- Pré-Condições:
	Usuário deve ter cadastrado

- Fluxo Básico:
    - 1. Usuário acessa a página inicial.
	- 2. Usuário informa credenciais.
	- 3. Sistema valida login.
  - 4. Sistema redireciona ao dashboard.

- Fluxos Alternativos:
	- Erro de login → exibe mensagem
	- Primeiro acesso → redefinição de senha

- Pós-Condições:
 Sessão autenticada iniciada e usuário direcionado ao sistema.
 
# 2. Novo Processo

```puml
  @startuml
left to right direction

actor Aluno
actor Secretaria

rectangle "Sistema de Gestão de Estágios IBMEC RJ" {

  usecase "Iniciar Processo de Estágio" as UC1
  usecase "Preencher Dados do Estágio" as UC2
  usecase "Anexar Documento (TCE)" as UC3
  usecase "Validar Informações" as UC4
  usecase "Exibir Erro de Arquivo" as UC5
  usecase "Exibir Erro de Campos Obrigatórios" as UC6

}

Aluno -- UC1
Secretaria -- UC1

UC1 ..> UC2 : <<include>>
UC1 ..> UC3 : <<include>>
UC1 ..> UC4 : <<include>>

UC5 ..> UC1 : <<extend>>
UC6 ..> UC1 : <<extend>>

@enduml

```
### Novo Processo

- Atores:
	- Aluno
	- Coordenação

- Pré-Condições:
	Usuário deve ter cadastrado

- Fluxo Básico:
    - 1. Usuário acessa a página inicial.
	- 2. Usuário informa credenciais.
	- 3. Sistema valida login.
  - 4. Sistema redireciona ao dashboard.

- Fluxos Alternativos:
	- Erro de login → exibe mensagem
	- Primeiro acesso → redefinição de senha

- Pós-Condições:
 Processo criado e armazenado com status "Pendente de Análise".

# 3. Add Documentos 

```puml
@startuml
left to right direction

actor Usuario

rectangle "Sistema de Gestão de Estágios IBMEC RJ" {

  usecase "Anexar Documentos (.pdf)" as UC1
  usecase "Selecionar Arquivo" as UC2
  usecase "Validar Arquivo (tipo e tamanho)" as UC3
  usecase "Exibir Erro de Tamanho" as UC4

}

Usuario -- UC1

UC1 ..> UC2 : <<include>>
UC1 ..> UC3 : <<include>>

UC4 ..> UC1 : <<extend>>

@enduml

```
### Adicionar Documentos
- Atores:
	- Aluno
	- Coordenação

- Pré-Condições:
	Processo existente.

- Fluxo Básico:
    - 1. Seleciona arquivo
	- 2. Valida arquivo
	- 3. Salva arquivo

- Fluxos Alternativos:
	- Arquivo inválido

- Pós-Condições:
	Documento anexado corretamente ao processo.
  
# 4. Validar Contrato 

```puml
@startuml
left to right direction

actor Secretaria

rectangle "Sistema de Gestão de Estágios IBMEC RJ" {

  usecase "Validar Contrato" as UC1
  usecase "Visualizar Contrato" as UC2
  usecase "Aprovar Contrato" as UC3
  usecase "Reprovar com Justificativa" as UC4
  usecase "Notificar Aluno" as UC5

}

Secretaria -- UC1

UC1 ..> UC2 : <<include>>
UC1 ..> UC3 : <<include>>
UC1 ..> UC5 : <<include>>

UC4 ..> UC1 : <<extend>>

@enduml

```
### Validar contrato
- Atores:
	- Coordenação


- Fluxo Básico:
    - 1. Seleciona contrato
	- 2. Analisa contrato
	- 3. Aprova contrato

- Fluxos Alternativos:
	- Reprovação com justificativa

- Pós-Condições:
	Contrato atualizado com status "Aprovado" ou "Reprovado" e aluno notificado.


# 5. Enviar Relatório

```puml
@startuml
left to right direction

actor Aluno

rectangle "Sistema de Gestão de Estágios IBMEC RJ" {

  usecase "Enviar Relatório de Horas" as UC1
  usecase "Preencher Dados do Relatório" as UC2
  usecase "Anexar Documento" as UC3
  usecase "Salvar Relatório" as UC4
  usecase "Registrar Envio Fora do Prazo" as UC5

}

Aluno -- UC1

UC1 ..> UC2 : <<include>>
UC1 ..> UC3 : <<include>>
UC1 ..> UC4 : <<include>>

UC5 ..> UC1 : <<extend>>

@enduml

```
### Enviar relatório

- Atores:
	- Aluno


- Fluxo Básico:
    - 1. Preenche o relatório
	- 2. Anexa arquivos
	- 3. Envia relatório
  - 4. Sistema valida e salva.

- Fluxos Alternativos:
	- Envio fora do prazo
	- Campos obrigatórios não preenchidos

  - Pós-Condições:
	Relatório salvo e status atualizado para "Aguardando Validação".


# 6. Acompanhar status

```puml
@startuml
left to right direction

actor Aluno
actor Secretaria

rectangle "Sistema de Gestão de Estágios IBMEC RJ" {

  usecase "Acompanhar Status do Processo" as UC1
  usecase "Visualizar Lista de Processos" as UC2
  usecase "Visualizar Detalhes do Processo" as UC3
  usecase "Exibir Mensagem Sem Processos" as UC4
  usecase "Fazer Download do Documento" as UC5

}

Aluno -- UC1
Secretaria -- UC1

UC1 ..> UC2 : <<include>>
UC1 ..> UC3 : <<include>>

UC4 ..> UC1 : <<extend>>
UC5 ..> UC1 : <<extend>>

@enduml

```

### Acompanhar status

- Atores:
	- Aluno
	- Coordenação

- Pré-Condições:
	Usuário deve estar logado

- Fluxo Básico:
    - 1. Usuário acessa a página visualizar status
	- 2. Visualiza listas e ocorrencias pendentes
	- 3. Acessa detalhes

- Fluxos Alternativos:
	- Sem processos
	- Download de documento

- Pós-Condições:
	Nenhuma alteração nos dados; apenas consulta realizada


# 7. Notificações

```puml
@startuml
left to right direction

actor Aluno
actor Secretaria

rectangle "Sistema de Gestão de Estágios IBMEC RJ" {

  usecase "Receber Notificações" as UC1
  usecase "Visualizar Notificações" as UC2
  usecase "Exibir Detalhe da Notificação" as UC3
  usecase "Exibir Sem Notificações" as UC4
  usecase "Acessar Processo Relacionado" as UC5

}

Aluno -- UC1
Secretaria -- UC1

UC1 ..> UC2 : <<include>>
UC1 ..> UC3 : <<include>>

UC4 ..> UC1 : <<extend>>
UC5 ..> UC1 : <<extend>>

@enduml

```

### Notificações

- Atores:
	- Aluno
	- Coordenação


- Fluxo Básico:
    - 1. Usuário acessa a página de notificações
	- 2. Visualiza notificações
	- 3. Abre a aba detalhes
  - 4. Sistema redireciona ao dashboard.

- Fluxos Alternativos:
	- Sem notificações
	- Acesso ao processo

- Pós-Condições:
	Notificações visualizadas pelo usuário

# 8. Encerrar Processo

```puml
@startuml
left to right direction

actor Aluno
actor Secretaria

rectangle "Sistema de Gestão de Estágios IBMEC RJ" {

  usecase "Finalizar Processo de Estágio" as UC1
  usecase "Verificar Requisitos para Encerramento" as UC2
  usecase "Registrar Encerramento" as UC3
  usecase "Notificar Usuário" as UC4
  usecase "Encerramento com Pendências" as UC5
  usecase "Gerar Termo de Encerramento" as UC6

}

Aluno -- UC1
Secretaria -- UC1

UC1 ..> UC2 : <<include>>
UC1 ..> UC3 : <<include>>
UC1 ..> UC4 : <<include>>

UC5 ..> UC1 : <<extend>>
UC6 ..> UC1 : <<extend>>

@enduml


```

### Encerrar Processo

- Atores:
	- Aluno
	- Coordenação

- Pré-Condições:
	Usuário deve ter concluído todas as etapas

- Fluxo Básico:
    - 1. Verifica requisitos
	- 2. Informa a conclusão do processo
	- 3. Encerra o processo
  - 4. Notifica o encerramento do processo

- Fluxos Alternativos:
	- Ainda há Pendências
	- Geração de termo de conclusão

- Pós-Condições:
	Processo encerrado e registrado no histórico