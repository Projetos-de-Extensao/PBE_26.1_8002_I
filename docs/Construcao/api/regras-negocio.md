# Regras de Negócio — Rastreabilidade

Este documento mapeia cada **regra de negócio** (RN) implementada na API IBMEC Estágios ao **código que a aplica** e ao **teste automatizado que prova seu funcionamento**. A filosofia é simples: toda RN levantada na fase de elaboração precisa virar código testado e auditável. Quem ler este documento deve conseguir, em poucos cliques, sair da redação da regra no documento de requisitos, chegar à linha exata do `serializers.py`/`views.py` que a executa e confirmar que existe um teste com nome explícito provando aquela regra. As regras estão na PR #47 (issue #46) e foram derivadas do documento `docs/Elaboracao/Requisitos/Requisitos-Gerais.md`, da Lei 11.788/08 e das normas internas do IBMEC.

## Tabela mestre

| ID   | Regra (resumo)                                       | Fonte normativa                | Onde é validada                          | Teste que prova                                          | HTTP |
| ---- | ---------------------------------------------------- | ------------------------------ | ---------------------------------------- | -------------------------------------------------------- | ---- |
| RN01 | Aluno deve estar matriculado em estágio supervisionado | Regulamento IBMEC + RF04       | `CriarProcessoSerializer.validate`       | `test_aluno_nao_matriculado_400_rn01`                    | 400  |
| RN03 | Jornada compatível com a carga máxima do curso (PPC) | PPC do curso + Lei 11.788/08   | `CriarProcessoSerializer.validate`       | `test_horas_excedem_limite_curso_400_rn03`               | 400  |
| RN05 | Um único processo "vivo" por aluno por vez           | Regulamento IBMEC              | `CriarProcessoSerializer.validate`       | `test_aluno_com_processo_vivo_nao_cria_outro_400_rn05`   | 400  |
| RN09 | Empresa precisa estar aprovada pelo IBMEC            | Regulamento IBMEC              | `CriarProcessoSerializer.validate`       | `test_empresa_nao_aprovada_400_rn09`                     | 400  |
| RN11 | Justificativa obrigatória em rejeição                | RF11 de `Requisitos-Gerais.md` | `AlterarStatusSerializer.validate`       | `test_coord_rejeita_sem_justificativa_400_rn11`          | 400  |
| LEI  | Limite legal de 30h/semana                           | Lei 11.788/08 art. 10          | `CriarProcessoSerializer.validate`       | `test_horas_acima_limite_legal_30h_400`                  | 400  |
| DATA | `data_fim_prevista > data_inicio_prevista`           | Validação básica de domínio    | `CriarProcessoSerializer.validate`       | `test_data_fim_antes_inicio_400`                         | 400  |

Observação sobre nomenclatura: o documento `Requisitos-Gerais.md` lista o item de **justificativa obrigatória** como **RF11** (requisito funcional). No código, porém, ele aparece referenciado como `RN11` nas mensagens de erro e nos nomes dos testes, por convenção do time, já que se comporta como uma regra de validação de negócio. Este documento adota o nome **RN11** para manter consistência com o que aparece na API.

## Detalhes por regra

### RN01 — Aluno deve estar matriculado em estágio

**O que diz.** "O sistema só deve permitir que o aluno realize login na plataforma se ele estiver devidamente matriculado na disciplina 'Estágio Supervisionado'." (`Requisitos-Gerais.md`, RN01.) A implementação atual aplica a regra **na criação do processo** (e não no login), pois o login está aberto a alunos em geral; o que está bloqueado é abrir solicitação de estágio sem matrícula ativa.

**Por que existe.** Garante que apenas alunos com vínculo formal com a disciplina possam iniciar um processo de estágio. Evita estágios "fantasma" e protege a integridade acadêmica da supervisão.

**Onde está implementada.** `djangotutorial/app/serializers.py`, classe `CriarProcessoSerializer`, método `validate`.

```python
# RN01: matriculado em estágio
if not aluno.matriculado_estagio:
    raise serializers.ValidationError({
        'aluno': 'RN01: aluno deve estar com matrícula ativa em estágio supervisionado.'
    })
```

**Teste que prova.** `test_aluno_nao_matriculado_400_rn01` em `djangotutorial/app/tests.py`, classe `CriacaoProcessoTest`. Usa o `aluno_nao_matriculado` (criado no `setUp` com `matriculado_estagio=False`) e tenta `POST /api/processos-estagio/`.

**Resposta HTTP esperada.** `400 Bad Request`.

```json
{
  "aluno": ["RN01: aluno deve estar com matrícula ativa em estágio supervisionado."]
}
```

### RN03 — Jornada compatível com o curso

**O que diz.** "O sistema deve impedir a aprovação do estágio caso a carga horária oferecida pela empresa seja incompatível com a quantidade mínima de horas exigida pelo curso do aluno." (`Requisitos-Gerais.md`, RN03.) A implementação aqui é o **teto** por curso: cada curso define `carga_horaria_maxima_diaria` no model `Curso`, e o limite semanal é calculado como `5 × diária`.

**Por que existe.** O Projeto Pedagógico de cada curso define uma carga máxima compatível com a grade acadêmica. Engenharia, por exemplo, tem 6h/dia → 30h/semana no curso da base de testes. Aceitar mais do que isso comprometeria o desempenho acadêmico do aluno.

**Onde está implementada.** `djangotutorial/app/serializers.py`, `CriarProcessoSerializer.validate`.

```python
# RN03: jornada compatível com o curso
horas = data['horas_semanais']
if aluno.curso is not None and aluno.curso.carga_horaria_maxima_diaria:
    limite_curso = aluno.curso.carga_horaria_maxima_diaria * 5
    if horas > limite_curso:
        raise serializers.ValidationError({
            'horas_semanais': f'RN03: excede o limite do curso ({limite_curso}h/semana).'
        })
```

**Teste que prova.** `test_horas_excedem_limite_curso_400_rn03` em `tests.py`, classe `CriacaoProcessoTest`. Envia `horas_semanais=40` para um aluno cujo curso tem limite de 30.

**Resposta HTTP esperada.** `400 Bad Request`.

```json
{
  "horas_semanais": ["RN03: excede o limite do curso (30h/semana)."]
}
```

### RN05 — Um processo "vivo" por aluno

**O que diz.** "O sistema deve restringir e controlar o tempo máximo que um aluno pode estagiar em uma mesma empresa concedente." (`Requisitos-Gerais.md`, RN05.) A interpretação operacional para a entrega da PR #47 é mais conservadora: **enquanto houver um processo em estado vivo (`RASCUNHO`, `PENDENTE`, `APROVADO`, `CORRECAO_SOLICITADA` ou `ATIVO`) para o aluno, ele não pode abrir outro**.

**Por que existe.** Evita que um aluno acumule múltiplas solicitações simultâneas, fazendo o coordenador escolher entre elas. Força o aluno a explicitamente **cancelar** o processo anterior (ou aguardar encerramento) antes de tentar de novo.

**Onde está implementada.** `djangotutorial/app/serializers.py`, `CriarProcessoSerializer.validate`. O conjunto `ESTADOS_VIVOS` vem de `state_machine.py`.

```python
# RN05: 1 processo vivo por aluno
if ProcessoEstagio.objects.filter(aluno=aluno, status__in=ESTADOS_VIVOS).exists():
    raise serializers.ValidationError(
        'RN05: aluno já possui um processo de estágio em andamento. '
        'Cancele ou aguarde o encerramento antes de abrir outro.'
    )
```

**Teste que prova.** `test_aluno_com_processo_vivo_nao_cria_outro_400_rn05` em `tests.py`, classe `CriacaoProcessoTest`. Cria um processo `PENDENTE` direto via ORM e depois tenta abrir um segundo via API.

**Resposta HTTP esperada.** `400 Bad Request`.

```json
{
  "non_field_errors": [
    "RN05: aluno já possui um processo de estágio em andamento. Cancele ou aguarde o encerramento antes de abrir outro."
  ]
}
```

### RN09 — Empresa aprovada pelo IBMEC

**O que diz.** "O aluno não pode prosseguir com a formalização do estágio em uma empresa que não tenha sido previamente aprovada/homologada pela faculdade no sistema." (`Requisitos-Gerais.md`, RN09.)

**Por que existe.** Garante que apenas empresas previamente avaliadas e homologadas pelo IBMEC possam receber alunos. A homologação é manual (admin/coordenador via Django Admin) e fica registrada em `EmpresaConcedente.aprovada_ibmec=True`.

**Onde está implementada.** `djangotutorial/app/serializers.py`, `CriarProcessoSerializer.validate`.

```python
# RN09: empresa aprovada pelo IBMEC
empresa = data['empresa']
if not empresa.aprovada_ibmec:
    raise serializers.ValidationError({
        'empresa': 'RN09: empresa não está aprovada pelo IBMEC.'
    })
```

**Teste que prova.** `test_empresa_nao_aprovada_400_rn09` em `tests.py`, classe `CriacaoProcessoTest`. Usa `empresa_nao_aprovada` (criada no `setUp` com `aprovada_ibmec=False`).

**Resposta HTTP esperada.** `400 Bad Request`.

```json
{
  "empresa": ["RN09: empresa não está aprovada pelo IBMEC."]
}
```

### LEI — Lei 11.788/08, art. 10 (30h/semana)

**O que diz.** O art. 10 da Lei 11.788/08 fixa o **teto legal** de 30 horas semanais para estágio não-obrigatório de nível superior (4h/dia em casos especiais e 6h em casos gerais, somando no máximo 30h semanais). Veja `docs/Iniciacao/pesquisa-detalhes/legislacao_trabalhista.md`.

**Por que existe.** Cumprimento de obrigação legal (RNF05 — Conformidade). Nenhum curso pode autorizar mais do que isso, ainda que o PPC interno permitisse mais — a Lei tem precedência.

**Onde está implementada.** `djangotutorial/app/serializers.py`, `CriarProcessoSerializer.validate`, logo depois do bloco do RN03.

```python
# Ceiling legal (Lei 11.788/08)
if horas > 30:
    raise serializers.ValidationError({
        'horas_semanais': 'Limite legal de 30h semanais (Lei 11.788/08).'
    })
```

**Teste que prova.** `test_horas_acima_limite_legal_30h_400` em `tests.py`, classe `CriacaoProcessoTest`. Envia `horas_semanais=35`.

**Resposta HTTP esperada.** `400 Bad Request`.

```json
{
  "horas_semanais": ["Limite legal de 30h semanais (Lei 11.788/08)."]
}
```

### DATA — `data_fim_prevista > data_inicio_prevista`

**O que diz.** Validação básica de domínio: a data de término precisa ser **estritamente posterior** à data de início. Datas iguais também são rejeitadas, porque um estágio precisa ter duração maior que zero.

**Por que existe.** Evita estados de domínio inválidos no banco. É a primeira validação executada no método `validate`, antes de qualquer regra que dependa do contexto da requisição.

**Onde está implementada.** `djangotutorial/app/serializers.py`, `CriarProcessoSerializer.validate`.

```python
# Data: fim > início
if data['data_fim_prevista'] <= data['data_inicio_prevista']:
    raise serializers.ValidationError({
        'data_fim_prevista': 'Deve ser posterior à data de início.'
    })
```

**Teste que prova.** `test_data_fim_antes_inicio_400` em `tests.py`, classe `CriacaoProcessoTest`. Envia `data_inicio_prevista=2026-07-01` e `data_fim_prevista=2026-06-01`.

**Resposta HTTP esperada.** `400 Bad Request`.

```json
{
  "data_fim_prevista": ["Deve ser posterior à data de início."]
}
```

### RN11 — Justificativa obrigatória em rejeição

**O que diz.** "O sistema deve exigir justificativa em caso de rejeição." (`Requisitos-Gerais.md`, **RF11**, mapeado como RN11 no código.)

**Por que existe.** Decisões negativas que afetam o aluno precisam ser registradas com motivação clara, tanto para fins acadêmicos (o aluno precisa saber o que corrigir) quanto para fins de auditoria (a coordenação fica obrigada a justificar suas decisões).

**Onde está implementada.** `djangotutorial/app/serializers.py`, classe `AlterarStatusSerializer`, método `validate`. A validação só é disparada quando o `status` recebido é `REJEITADO`.

```python
def validate(self, data):
    if data.get('status') == ProcessoEstagio.Status.REJEITADO:
        justif = data.get(
            'justificativa_rejeicao',
            self.instance.justificativa_rejeicao if self.instance else '',
        )
        if not justif or not justif.strip():
            raise serializers.ValidationError({
                'justificativa_rejeicao': 'RN11: justificativa obrigatória ao rejeitar uma solicitação.'
            })
    return data
```

**Teste que prova.** `test_coord_rejeita_sem_justificativa_400_rn11` em `tests.py`, classe `AlterarStatusTest`. O coordenador autenticado envia `POST /api/processos-estagio/<id>/alterar_status/` com `{"status": "REJEITADO"}` sem `justificativa_rejeicao`.

**Resposta HTTP esperada.** `400 Bad Request`.

```json
{
  "justificativa_rejeicao": ["RN11: justificativa obrigatória ao rejeitar uma solicitação."]
}
```

## Validação de transições de status (state machine)

Não é uma "RN" do documento de requisitos, mas é uma regra **crítica de domínio**: o status de um processo só pode mudar seguindo o mapa de transições definido em `djangotutorial/app/state_machine.py`. Por exemplo, um processo em estado terminal (`REJEITADO`, `ENCERRADO`, `CANCELADO`) não pode mais transitar para nenhum outro estado.

**Onde está implementada.** `djangotutorial/app/views.py`, `ProcessoEstagioViewSet.alterar_status`, passo 1, junto com `state_machine.transicoes_validas`:

```python
validas = transicoes_validas(processo.status)
if novo_status not in validas:
    return Response({
        'status': f'Transição inválida: {processo.status} → {novo_status}.',
        'estado_atual': processo.status,
        'transicoes_validas': sorted(validas) if validas else [],
    }, status=drf_status.HTTP_400_BAD_REQUEST)
```

**Teste que prova.** `test_transicao_invalida_400_lista_validas` em `tests.py`, classe `AlterarStatusTest`. Cria um processo já `REJEITADO` e tenta movê-lo para `ATIVO`.

**Resposta HTTP esperada.** `400 Bad Request`, com `transicoes_validas` listando alternativas (vazio quando o estado atual é terminal).

```json
{
  "status": "Transição inválida: REJEITADO → ATIVO.",
  "estado_atual": "REJEITADO",
  "transicoes_validas": []
}
```

Veja [state-machine.md](state-machine.md) para o diagrama completo do fluxo e a tabela de transições válidas.

## RBAC: permissão por papel

Também não é uma "RN" listada nos requisitos, mas é uma regra **crítica de segurança**. A API impõe permissão por papel em duas camadas complementares:

**1. Queryset filtrado por papel** (`ProcessoEstagioViewSet.get_queryset`). Cada papel só "enxerga" um subconjunto dos processos:

- **Aluno** → apenas os próprios processos (`base.filter(aluno=aluno)`).
- **Supervisor de empresa** → apenas processos da sua empresa (`base.filter(empresa=supervisor.empresa)`).
- **Coordenador** → apenas processos de alunos dos cursos que coordena (`base.filter(aluno__curso__coordenador=coord)`).
- **Admin (superuser)** → todos os processos.

Isso significa que tentar acessar um processo "alheio" devolve **404** (o registro existe, mas o queryset do papel não o enxerga), e não 403 — defesa em profundidade por filtro.

**2. Validação de quem dispara qual transição** (`ProcessoEstagioViewSet.alterar_status`, passo 2). Após confirmar que a transição é válida no mapa de estados, a view checa **quem pode dispará-la**:

- **Aluno**: só pode `RASCUNHO → PENDENTE` (submeter) ou `* → CANCELADO` (cancelar) **no próprio processo**.
- **Coordenador**: pode disparar `APROVADO`, `REJEITADO`, `CORRECAO_SOLICITADA`, `ATIVO` e `ENCERRADO`, e apenas em processos de alunos dos cursos que coordena.
- **Admin**: pode disparar qualquer transição válida.

Violações desse contrato retornam **403 Forbidden** com `{"detail": "..."}`.

**Testes que provam.**

| Teste                                                | Classe                  | Verifica                                                                                  |
| ---------------------------------------------------- | ----------------------- | ----------------------------------------------------------------------------------------- |
| `test_aluno_lista_apenas_proprios`                   | `IsolamentoQuerysetTest`| Aluno só vê seus processos no `GET /api/processos-estagio/`.                              |
| `test_supervisor_lista_apenas_empresa_dele`          | `IsolamentoQuerysetTest`| Supervisor só vê processos da própria empresa.                                            |
| `test_coordenador_lista_apenas_cursos_dele`          | `IsolamentoQuerysetTest`| Coordenador só vê processos de alunos dos cursos que coordena.                            |
| `test_admin_lista_todos`                             | `IsolamentoQuerysetTest`| Admin vê todos os processos.                                                              |
| `test_aluno_nao_pode_alterar_processo_de_outro_403`  | `AlterarStatusTest`     | Aluno tentando mexer em processo de outro aluno → 403 ou 404.                             |
| `test_coord_de_outro_curso_403`                      | `AlterarStatusTest`     | Coordenador de outro curso tentando aprovar → 403 ou 404.                                 |
| `test_aluno_nao_pode_aprovar_proprio_400_ou_403`     | `AlterarStatusTest`     | Aluno tentando aprovar o próprio processo → 400 ou 403.                                   |

**Resposta HTTP esperada.** `403 Forbidden` quando a permission detecta a violação após a view recuperar o objeto; `404 Not Found` quando o queryset do papel já tinha filtrado o objeto antes (por isso vários testes aceitam ambos os códigos).

Veja a seção [Resumo de permissões por papel](endpoints.md#resumo-de-permissoes-por-papel) em `endpoints.md` para a matriz papel × verbo completa.

## Cobertura de testes

Total: **24 testes** em **4 classes**, organizados em `djangotutorial/app/tests.py`:

| Classe                     | # testes | Foco                                                                            |
| -------------------------- | -------- | ------------------------------------------------------------------------------- |
| `CriacaoProcessoTest`      | 8        | POST `/api/processos-estagio/`: RN01, RN03, RN05, RN09, LEI 30h, DATA, autenticação. |
| `IsolamentoQuerysetTest`   | 4        | GET `/api/processos-estagio/`: filtragem por papel (aluno, supervisor, coord, admin). |
| `AlterarStatusTest`        | 8        | POST `/api/processos-estagio/<id>/alterar_status/`: transições, RN11, RBAC.     |
| `StateMachineUnitTest`     | 4        | Unit tests puros do módulo `app.state_machine`.                                 |

Convenção dos nomes: sempre que o teste cobre uma regra com ID, o ID aparece no nome (`_rn01`, `_rn03`, `_rn05`, `_rn09`, `_rn11`). Isso garante rastreabilidade bidirecional: do código pro teste, e do teste pro requisito. Rodar a suíte:

```bash
cd djangotutorial
../.venv/bin/python manage.py test app -v 2
```

## Regras NÃO implementadas (fora do escopo desta entrega)

A PR #47 cobre o núcleo de validações que travam o pipeline básico do processo. Os RNs/RFs abaixo continuam no backlog e ficam como follow-up para próximas entregas:

- **RN02 — Pré-requisitos acadêmicos do PPC.** Hoje só validamos `matriculado_estagio`. Validar disciplinas concluídas, CR mínimo e período mínimo exige um motor de regras por curso (provavelmente um JSON no `Curso` ou um app dedicado). Fica como follow-up.
- **RN04 — Jornada diária + semanal combinadas.** O limite **legal** semanal (30h) já está; falta validar a jornada **diária** declarada e cruzá-la com o `carga_horaria_maxima_diaria` do curso. Hoje aceitamos só `horas_semanais` no payload. Fica como follow-up junto com o redesenho do payload.
- **RN06 — Bloqueio de aprovação sem TCE + apólice de seguro.** Depende dos models de documento e do fluxo de upload (`Pessoa 5`). Fica como follow-up — quando aterrissar, vira mais uma checagem no `AlterarStatusSerializer.validate` no caso `status=APROVADO`.
- **RN07 — Validação automática de área de atuação vs. curso.** Requer NLP/análise textual do `plano_atividades` ou taxonomia formal de áreas no `Curso`. Fica como follow-up de longo prazo (ligado a RF08 — análise automatizada).
- **RN08 — Notificações de atraso de relatórios.** Pré-requisito: model de relatório obrigatório + scheduler (Celery/cron). Não há infra de jobs ainda. Fica como follow-up.
- **RN10 — Campos obrigatórios da empresa.** Parcialmente coberto: `EmpresaConcedente` exige `cnpj`, `razao_social`, `areas_atuacao` e `localizacao` no model (constraint de banco). Falta uma validação explícita no `EmpresaConcedenteSerializer` com mensagens de erro padronizadas. Fica como follow-up.
- **RF18 — Abertura formal por escolha de vaga.** Parcialmente coberto: hoje o aluno descreve a oportunidade no `plano_atividades`, sem model `Vaga`. Quando entrar o catálogo de vagas, o `CriarProcessoSerializer` recebe `vaga_id` e a validação passa a vincular processo a vaga. Fica como follow-up.

## Autor(es)

| Data       | Versão | Descrição              | Autor(es)               |
| ---------- | ------ | ---------------------- | ----------------------- |
| 28/05/2026 | 1.0    | Criação do documento   | João Gabriel Teodósio   |
