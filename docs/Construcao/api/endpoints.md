# Endpoints da API

A API IBMEC Estágios expõe **27 endpoints** organizados em **8 recursos** (3 de autenticação + 7 ViewSets REST registrados no `DefaultRouter`). Este documento traz a referência tabular dos recursos publicados pela PR [#47](https://github.com/Projetos-de-Extensao/PBE_26.1_8002_I/pull/47); para os contratos de payload exatos, **a fonte de verdade é o Swagger UI em `/api/docs/`**, gerado pelo `drf-spectacular` a partir dos serializers do código.

## Tabela mestre

Legenda de status: `✓ pronto` = entregue na PR #47 · `⚠ parcial` = caminho feliz pronto, faltam validações secundárias · `✗ não implementado` = previsto para entregas futuras.

| Método | URL | Quem pode | Descrição | Status |
| -- | -- | -- | -- | -- |
| POST | `/api/auth/register/` | Anônimo | Cria `Usuario` + perfil (`aluno`, `coordenador` ou `supervisor_empresa`) e devolve token DRF | ✓ pronto |
| POST | `/api/auth/login/` | Anônimo | Autentica username/password, retorna token + dados básicos | ✓ pronto |
| POST | `/api/auth/logout/` | Autenticado | Invalida o token do usuário corrente | ✓ pronto |
| GET | `/api/cursos/` | Autenticado | Lista cursos (coord vê só os seus, admin vê todos) | ✓ pronto |
| POST | `/api/cursos/` | Admin | Cria curso | ✓ pronto |
| GET | `/api/cursos/{id}/` | Autenticado | Detalha curso | ✓ pronto |
| PUT/PATCH | `/api/cursos/{id}/` | Admin | Atualiza curso | ✓ pronto |
| DELETE | `/api/cursos/{id}/` | Admin | Remove curso | ✓ pronto |
| GET | `/api/cursos/meus_alunos/` | Coordenador | Alunos do(s) curso(s) sob coordenação | ✗ não implementado |
| GET | `/api/cursos/processos_pendentes/` | Coordenador | Processos `PENDENTE` aguardando análise | ✗ não implementado |
| GET | `/api/empresas/` | Autenticado | Lista empresas concedentes (filtros `?aprovada=` e `?busca=`) | ✓ pronto |
| POST | `/api/empresas/` | Admin | Cadastra empresa concedente | ✓ pronto |
| GET | `/api/empresas/{id}/` | Autenticado | Detalha empresa | ✓ pronto |
| PUT/PATCH | `/api/empresas/{id}/` | Admin | Atualiza empresa | ✓ pronto |
| DELETE | `/api/empresas/{id}/` | Admin | Remove empresa | ✓ pronto |
| GET | `/api/empresas/meu_perfil/` | Supervisor de empresa | Empresa do supervisor logado | ✗ não implementado |
| GET/POST | `/api/alunos/` | Autenticado (isolado) | Lista/cria alunos com escopo por papel | ✓ pronto |
| GET/PUT/PATCH/DELETE | `/api/alunos/{id}/` | Autenticado (isolado) | CRUD por ID, respeitando isolamento | ✓ pronto |
| GET | `/api/alunos/meu_perfil/` | Aluno | Perfil próprio do aluno logado | ✗ não implementado |
| GET/POST | `/api/coordenadores/` | Autenticado (isolado) | Lista/cria coordenadores | ✓ pronto |
| GET/PUT/PATCH/DELETE | `/api/coordenadores/{id}/` | Autenticado (isolado) | CRUD por ID | ✓ pronto |
| GET/POST | `/api/supervisores-empresa/` | Autenticado (isolado) | Lista/cria supervisores | ✓ pronto |
| GET/PUT/PATCH/DELETE | `/api/supervisores-empresa/{id}/` | Autenticado (isolado) | CRUD por ID | ✓ pronto |
| GET/POST | `/api/documentos/` | Autenticado (isolado) | Lista/cria documentos | ⚠ parcial |
| GET/PUT/PATCH/DELETE | `/api/documentos/{id}/` | Autenticado (isolado) | CRUD por ID | ⚠ parcial |
| GET | `/api/processos-estagio/` | Autenticado (isolado) | Lista processos visíveis ao usuário | ✓ pronto |
| POST | `/api/processos-estagio/` | Aluno | Abre processo (`status=PENDENTE`, coord automático) | ✓ pronto |
| GET | `/api/processos-estagio/{id}/` | Dono / Coord / Supervisor / Admin | Detalha processo | ✓ pronto |
| PUT/PATCH | `/api/processos-estagio/{id}/` | Dono / Admin | Atualiza dados livres do processo | ✓ pronto |
| DELETE | `/api/processos-estagio/{id}/` | Admin | Remove processo | ✓ pronto |
| POST | `/api/processos-estagio/{id}/alterar_status/` | Conforme transição | Transição validada pela state machine | ✓ pronto |
| GET | `/api/processos-estagio/{id}/documentos/` | Autenticado (isolado) | Lista documentos do processo | ✓ pronto |
| POST | `/api/processos-estagio/{id}/gerar-tce/` | Coordenador | Gera PDF do Termo de Compromisso de Estágio | ✗ não implementado |
| POST | `/api/processos-estagio/{id}/gerar-termo-realizacao/` | Coordenador | Gera PDF do Termo de Realização | ✗ não implementado |

## Autenticação

A camada de autenticação usa token DRF (`rest_framework.authtoken`). Detalhes do header `Authorization: Token <chave>`, ciclo de vida do token e estrutura dos payloads de cadastro estão em [Autenticação](autenticacao.md).

### POST `/api/auth/register/`

Cria um `Usuario` + perfil vinculado conforme o campo `tipo` (`aluno`, `coordenador`, `supervisor_empresa`). Devolve token DRF pronto pra usar. Body comum: `tipo`, `username`, `password`, `nome`, `email_institucional`. Campos extras variam por tipo (CPF para aluno, departamento para coordenador, empresa_id para supervisor). Veja [Autenticação](autenticacao.md#post-apiauthregister).

### POST `/api/auth/login/`

Autentica username + password via `django.contrib.auth.authenticate` e devolve `{token, id, tipo, nome}`. Falha com `401 Unauthorized` se as credenciais não baterem. Veja [Autenticação](autenticacao.md#post-apiauthlogin).

### POST `/api/auth/logout/`

Apaga o token DRF do usuário corrente. Próximas requisições com aquele token retornam `401`. Veja [Autenticação](autenticacao.md#post-apiauthlogout).

## Processos de Estágio (foco da PR #47)

Recurso central da entrega. `ProcessoEstagioViewSet` aplica RBAC no `get_queryset` (cada papel só enxerga o que lhe pertence), troca de serializer conforme a ação e expõe duas `@action` customizadas.

### GET `/api/processos-estagio/`

Lista paginada dos processos visíveis ao usuário. O filtro implícito por papel é:

- **Aluno** — somente os próprios processos (`filter(aluno=aluno)`).
- **Supervisor de empresa** — processos da empresa em que está vinculado (`filter(empresa=supervisor.empresa)`).
- **Coordenador** — processos de alunos dos cursos que coordena (`filter(aluno__curso__coordenador=coord)`).
- **Admin** — todos.
- **Qualquer outro caso** — `.none()` (negação por default).

Permissões: `IsAuthenticated`. Os filtros de papel acontecem no queryset, não nas permissions.

### POST `/api/processos-estagio/`

Cria um processo. Apenas alunos podem chamar — se o usuário não tem perfil `Aluno`, o `perform_create` levanta `PermissionDenied`. O ViewSet seta automaticamente `aluno` = aluno logado, `status` = `PENDENTE` e `coordenador` = coordenador do curso do aluno (quando existir).

Payload de exemplo:

```json
{
  "empresa": 4,
  "supervisor": 7,
  "horas_semanais": 20,
  "data_inicio_prevista": "2026-06-15",
  "data_fim_prevista": "2026-12-15",
  "plano_atividades": "Desenvolvimento de microserviços em Python."
}
```

Resposta `201 Created`:

```json
{
  "id": 12,
  "aluno": 3,
  "empresa": 4,
  "supervisor": 7,
  "coordenador": 2,
  "status": "PENDENTE",
  "horas_semanais": 20,
  "data_inicio_prevista": "2026-06-15",
  "data_fim_prevista": "2026-12-15",
  "plano_atividades": "Desenvolvimento de microserviços em Python.",
  "justificativa_rejeicao": ""
}
```

Permissões: `IsAuthenticated` + perfil `Aluno` verificado em `perform_create`.

### GET `/api/processos-estagio/{id}/`

Detalha um processo. O acesso é validado duplamente: pelo queryset (papel) e pelo `get_object` (existência). Se o ID não está no queryset filtrado, o DRF responde `404 Not Found` — não vaza a existência de processos alheios.

Resposta `200 OK` traz o mesmo formato do `POST`, com os relacionamentos resolvidos por `select_related`.

### POST `/api/processos-estagio/{id}/alterar_status/`

Endpoint mais delicado da entrega. Executa quatro checagens em ordem antes de persistir:

1. **Transição válida** pelo mapa em `state_machine.py` (`transicoes_validas(processo.status)`).
2. **Permissão por papel** — aluno só pode `RASCUNHO→PENDENTE` ou `*→CANCELADO`; coordenador só pode emitir `APROVADO`, `REJEITADO`, `CORRECAO_SOLICITADA`, `ATIVO` ou `ENCERRADO`.
3. **Validação do serializer** `AlterarStatusSerializer` — exige justificativa quando `novo_status=REJEITADO` (RN11).
4. **Persistência** + refresh + retorno do processo serializado por inteiro.

Payload mínimo:

```json
{
  "status": "APROVADO"
}
```

Payload de rejeição (justificativa obrigatória):

```json
{
  "status": "REJEITADO",
  "justificativa_rejeicao": "Plano de atividades não condiz com o curso do aluno."
}
```

Resposta de erro em transição inválida (`400 Bad Request`):

```json
{
  "status": "Transição inválida: APROVADO → RASCUNHO.",
  "estado_atual": "APROVADO",
  "transicoes_validas": ["ATIVO", "CANCELADO", "REJEITADO"]
}
```

Veja o mapa completo em [Máquina de Estados](state-machine.md) e a lista de regras de negócio aplicadas em [Regras de Negócio](regras-negocio.md).

### GET `/api/processos-estagio/{id}/documentos/`

Lista todos os `DocumentoProcesso` vinculados ao processo, ordenados por `-data_upload`. Reutiliza o `DocumentoProcessoSerializer`. Permissões: o `get_object` aplica o filtro de papel; quem não tem visão do processo recebe `404`.

Resposta `200 OK`:

```json
[
  {
    "id": 18,
    "processo": 12,
    "tipo": "TCE",
    "arquivo": "/media/documentos/tce_12.pdf",
    "enviado_por": 5,
    "data_upload": "2026-05-27T14:32:11Z",
    "status": "PENDENTE",
    "versao": 1
  }
]
```

## Cursos

CRUD básico via `CursoViewSet`. Escrita (`POST`/`PUT`/`PATCH`/`DELETE`) exige `IsAdminOrReadOnly`; leitura é liberada para autenticados, mas o `get_queryset` filtra: coordenador vê apenas cursos onde é responsável (`filter(coordenador=coordenador)`), admin vê tudo.

Campos do modelo (referência rápida):

```python
nome: CharField
coordenador: ForeignKey(Coordenador, null=True)
carga_horaria_minima_total: PositiveIntegerField
carga_horaria_maxima_diaria: PositiveIntegerField (default=6)
```

Permissões resumidas:

| Ação | Aluno | Coordenador | Supervisor | Admin |
| -- | -- | -- | -- | -- |
| Listar/detalhar | ✓ (todos) | ✓ (só os seus) | ✓ (todos) | ✓ |
| Criar/editar/remover | ✗ | ✗ | ✗ | ✓ |

## Empresas Concedentes

`EmpresaConcedenteViewSet` com `IsAdminOrReadOnly`: qualquer autenticado lê, só admin escreve. Suporta **dois filtros via query string**:

| Parâmetro | Tipo | Comportamento |
| -- | -- | -- |
| `?aprovada=true` ou `?aprovada=false` | bool (aceita `true`/`1`) | Filtra por `aprovada_ibmec` |
| `?busca=texto` | string | `razao_social__icontains=texto` |

Exemplo combinando filtros:

```bash
GET /api/empresas/?aprovada=true&busca=tecnologia
```

Campos persistidos (RN10):

```python
cnpj: CharField unique
razao_social: CharField
areas_atuacao: TextField
localizacao: CharField
email_contato: EmailField
aprovada_ibmec: BooleanField (default=False)
```

## Alunos

`AlunoViewSet` aplica isolamento por papel no `get_queryset`:

- **Admin** — todos os alunos.
- **Aluno** — apenas o próprio registro (`filter(pk=aluno.pk)`).
- **Coordenador** — alunos dos cursos que coordena (`filter(curso__coordenador=coord)`).
- **Outros casos** — `.none()`.

A leitura usa `select_related('usuario', 'curso')` para evitar N+1 ao montar a listagem.

Resposta de exemplo (`GET /api/alunos/{id}/`):

```json
{
  "id": 3,
  "usuario": {
    "id": 11,
    "username": "joao.silva",
    "nome": "João Silva",
    "email_institucional": "joao.silva@ibmec.edu.br",
    "tipo": "aluno"
  },
  "cpf": "123.456.789-00",
  "rg": "12.345.678-9",
  "coeficiente_rendimento": "8.50",
  "curso": 2,
  "matriculado_estagio": true
}
```

## Coordenadores

`CoordenadorViewSet` segue o mesmo padrão: admin vê todos, coordenador vê só a si mesmo, outros papéis recebem `.none()`. Útil para coordenadores conferirem seu próprio cadastro e admins gerirem a equipe acadêmica.

## Supervisores de Empresa

`SupervisorEmpresaViewSet` com a mesma estrutura: admin vê todos, supervisor vê só a si mesmo, demais recebem `.none()`. O `select_related('usuario', 'empresa')` traz a empresa vinculada em uma query.

## Documentos

`DocumentoProcessoViewSet` gerencia os arquivos vinculados aos processos (`TCE`, `APOLICE`, `RELATORIO_PARCIAL`, `RELATORIO_FINAL`, `AVALIACAO_EMPRESA`, `TERMO_REALIZACAO`, `OUTRO`).

Isolamento por papel no queryset:

- **Aluno** — documentos dos próprios processos.
- **Supervisor de empresa** — documentos dos processos da empresa em que atua.
- **Coordenador** — documentos dos processos de alunos dos cursos sob coordenação.
- **Admin** — todos.

No `perform_create`, o ViewSet seta `enviado_por = request.user` automaticamente, garantindo trilha de auditoria (RF13) sem confiar em campo do cliente.

Status `⚠ parcial` porque o upload funciona, mas a validação de MIME e tamanho do arquivo (RF05 detalhado) é parte da entrega da Pessoa 5.

### Comportamento de filtros combinados

Quando o usuário tem mais de um perfil ativo (caso raro em produção, mas suportado pelo modelo), o `get_queryset` resolve a precedência nesta ordem em cada ViewSet:

1. `is_admin(user)` — se for admin, retorna tudo e sai.
2. `get_aluno(user)` — se houver perfil `Aluno`, filtra para o próprio aluno.
3. `get_supervisor(user)` — se houver perfil `SupervisorEmpresa`, filtra pela empresa.
4. `get_coordenador(user)` — se houver perfil `Coordenador`, filtra pelos cursos coordenados.
5. Nada bateu → `.none()`.

Ou seja, a ordem é: admin > aluno > supervisor > coordenador. Em produção, cada `Usuario` deve ter apenas um perfil — o admin Django facilita auditar inconsistências.

## Resumo de permissões por papel

Tabela cruzada para consulta rápida. Marcador `R` = leitura, `W` = escrita (criar/atualizar/remover), `–` = sem acesso.

| Recurso | Aluno | Coordenador | Supervisor | Admin |
| -- | -- | -- | -- | -- |
| `/api/cursos/` | R | R (só seus) | R | R+W |
| `/api/empresas/` | R | R | R | R+W |
| `/api/alunos/` | R (si) | R (alunos dos seus cursos) + W limitado | – | R+W |
| `/api/coordenadores/` | – | R (si) | – | R+W |
| `/api/supervisores-empresa/` | – | – | R (si) | R+W |
| `/api/documentos/` | R+W (próprios) | R (escopo) | R+W (escopo) | R+W |
| `/api/processos-estagio/` | R (próprios) + criar | R (escopo) + transições | R (escopo) | R+W |

A coluna "escopo" significa: documentos/processos do círculo de cursos (coordenador) ou da empresa (supervisor), nunca de terceiros.

## Documentação interativa

Para explorar payloads exatos, testar requisições com um botão "Try it out" e inspecionar o JSON OpenAPI bruto, acesse a documentação interativa servida pelo `drf-spectacular`:

- Swagger UI — [`/api/docs/`](http://localhost:8000/api/docs/)
- Redoc — [`/api/redoc/`](http://localhost:8000/api/redoc/)
- Schema OpenAPI 3 (JSON) — [`/api/schema/`](http://localhost:8000/api/schema/)

Tudo é gerado a partir dos ViewSets, Serializers e docstrings do código. Mudou o serializer? Recarregue o Swagger.

## Fora do escopo desta entrega

A PR #47 entrega a fatia vertical da Pessoa 1 (núcleo do `ProcessoEstagio`). Os itens abaixo estão planejados, mas **não existem ainda** e devem retornar `404 Not Found` se chamados:

- `GET /api/cursos/meus_alunos/` — agregação para o coordenador (Pessoa 2).
- `GET /api/cursos/processos_pendentes/` — fila de processos `PENDENTE` para o coordenador (Pessoa 2).
- `GET /api/alunos/meu_perfil/` — atalho do aluno logado (Pessoa 3).
- `GET /api/empresas/meu_perfil/` — atalho do supervisor de empresa logado (Pessoa 3).
- Upload com validação MIME/tamanho em `/api/documentos/` (Pessoa 5).
- `POST /api/processos-estagio/{id}/gerar-tce/` — gera o Termo de Compromisso de Estágio em PDF (Pessoa 5).
- `POST /api/processos-estagio/{id}/gerar-termo-realizacao/` — gera o Termo de Realização em PDF (Pessoa 5).

Esses endpoints serão abertos em PRs subsequentes, cada um com sua issue dedicada.

## Autor(es)

| Data | Versão | Descrição | Autor(es) |
| -- | -- | -- | -- |
| 28/05/2026 | 1.0 | Criação do documento | João Gabriel Teodósio |
