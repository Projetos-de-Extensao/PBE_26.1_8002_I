# Erros — Convenções e Catálogo

Este documento descreve **como a API IBMEC Estágios devolve erros** ao cliente. A filosofia é simples: erros são úteis. Toda resposta de erro deve trazer (1) um código HTTP coerente com o tipo de problema, (2) uma mensagem em português orientada ao usuário ou ao desenvolvedor e, quando aplicável, (3) instruções para o cliente seguir adiante (ex.: lista de transições válidas, indicação de campo com problema). Não existe `500` "silencioso" — qualquer 500 é bug e precisa ser reportado.

## Códigos HTTP usados

| Código                         | Significado neste sistema                                                                                                            | Exemplo de body                                                                  |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------- |
| `200 OK`                       | `GET` bem-sucedido ou ação de mutação completada com sucesso (por exemplo `alterar_status` com transição válida).                    | objeto serializado do recurso                                                    |
| `201 Created`                  | `POST` criou um recurso (processo, usuário via `/api/auth/register/`).                                                               | objeto criado, incluindo `id`                                                    |
| `400 Bad Request`              | Validação falhou: RN violada, JSON malformado, transição de status inválida, justificativa vazia, campo faltando.                    | `{"detail": "..."}` ou `{"campo": ["msg"]}`                                      |
| `401 Unauthorized`             | Sem token ou token inválido/expirado.                                                                                                | `{"detail": "Authentication credentials were not provided."}`                    |
| `403 Forbidden`                | Token OK, mas o papel do usuário **não tem permissão** para a ação solicitada.                                                       | `{"detail": "Sem permissão neste processo."}`                                    |
| `404 Not Found`                | Recurso não existe **ou** o recurso existe mas o queryset do papel não o enxerga (defesa por filtro — ver `regras-negocio.md`).      | `{"detail": "Not found."}`                                                       |
| `500 Internal Server Error`    | Bug. Não deveria acontecer; reporte no canal do time com o `request id` e o payload usado.                                           | stack trace (somente em `DEBUG=True`)                                            |

Pontos importantes:

- **404 é também uma forma de proteção.** Quando um aluno tenta acessar `/api/processos-estagio/<id de outro aluno>/`, o queryset filtrado em `ProcessoEstagioViewSet.get_queryset` já remove esse objeto **antes** de o DRF rodar `get_object`. Resultado: o cliente vê `404`, não `403`. Isso é proposital — evita vazamento de informação sobre existência de recursos. Cobertura: `IsolamentoQuerysetTest` em `djangotutorial/app/tests.py`.
- **403 ocorre depois** do queryset, quando a permission da action (por exemplo `alterar_status`) detecta que o papel não pode disparar aquela transição específica. Cobertura: `test_aluno_nao_pode_aprovar_proprio_400_ou_403`, `test_coord_de_outro_curso_403`.

## Convenções de payload de erro

A API mistura **três formatos** de erro, dependendo de quem está lançando a exceção. Saber identificar cada um economiza tempo de debug.

### Erro de validação de campo (DRF padrão)

Quando o `ModelSerializer` (ou `Serializer`) lança `ValidationError({"campo": "msg"})`, o DRF responde com:

```json
{
  "campo": ["msg"]
}
```

Note que o valor é sempre uma **lista** de strings, mesmo que haja só uma mensagem. Esse é o formato mais comum em `POST /api/processos-estagio/` quando uma RN bate. Exemplo real (RN09):

```json
{
  "empresa": ["RN09: empresa não está aprovada pelo IBMEC."]
}
```

Quando o `ValidationError` é lançado sem chave de campo (ex.: RN05), o DRF agrupa em `non_field_errors`:

```json
{
  "non_field_errors": [
    "RN05: aluno já possui um processo de estágio em andamento. Cancele ou aguarde o encerramento antes de abrir outro."
  ]
}
```

### Erro genérico (DRF padrão)

Quando o DRF lança uma exceção sem contexto de campo — autenticação, permissão, recurso não encontrado, método não permitido — o formato é:

```json
{
  "detail": "mensagem"
}
```

Exemplos:

- `401`: `{"detail": "Authentication credentials were not provided."}`
- `403`: `{"detail": "Sem permissão neste processo."}` (custom da view `alterar_status`) ou `{"detail": "You do not have permission to perform this action."}` (DRF padrão)
- `404`: `{"detail": "Not found."}`

### Erro das auth views customizadas

As views `RegisterView` e `LoginView` em `djangotutorial/app/views.py` usam a chave `erro` (em vez de `detail`), por convenção do time:

```json
{
  "erro": "Credenciais inválidas."
}
```

Casos onde isso aparece:

- Falta `username`/`password` no `POST /api/auth/register/` → `400 + {"erro": "username e password são obrigatórios."}`
- `tipo` inválido no register → `400 + {"erro": "tipo deve ser 'aluno', 'coordenador' ou 'supervisor_empresa'."}`
- Coordenador sem `departamento` → `400 + {"erro": "campo \"departamento\" é obrigatório para coordenador."}`
- Supervisor sem `empresa_id` → `400 + {"erro": "campo \"empresa_id\" é obrigatório para supervisor_empresa."}`
- Login com credenciais erradas → `401 + {"erro": "Credenciais inválidas."}`

### Erro de transição inválida (custom)

Quando o cliente tenta mover o status para um estado inalcançável, a view `alterar_status` devolve um payload **estruturado** que ajuda o cliente a se corrigir:

```json
{
  "status": "Transição inválida: REJEITADO → ATIVO.",
  "estado_atual": "REJEITADO",
  "transicoes_validas": []
}
```

A chave `transicoes_validas` é uma **lista de estados alcançáveis** a partir do estado atual. Quando o processo está em estado terminal, a lista vem vazia (`[]`). Use esse payload para popular menus de "próxima ação" na UI sem hardcoded.

## Mensagens padronizadas por regra

| Regra      | Mensagem                                                                                                                              |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| RN01       | `RN01: aluno deve estar com matrícula ativa em estágio supervisionado.`                                                               |
| RN03       | `RN03: excede o limite do curso (Xh/semana).` (onde `X` é o limite calculado do curso)                                                |
| RN05       | `RN05: aluno já possui um processo de estágio em andamento. Cancele ou aguarde o encerramento antes de abrir outro.`                  |
| RN09       | `RN09: empresa não está aprovada pelo IBMEC.`                                                                                         |
| RN11       | `RN11: justificativa obrigatória ao rejeitar uma solicitação.`                                                                        |
| LEI 30h    | `Limite legal de 30h semanais (Lei 11.788/08).`                                                                                       |
| DATA       | `Deve ser posterior à data de início.`                                                                                                |

Essas mensagens **fazem parte do contrato** da API. Trocar texto requer atualização nos testes correspondentes (`test_*_rn01`, `test_*_rn03`, etc.) e neste documento. Se você precisar internacionalizar no futuro, use chaves estáveis (`error_code`) ao lado do `message`.

## Exemplos completos por rota

Esta seção traz pares **requisição → resposta** dos cenários de erro mais comuns, para servir de referência rápida quando você estiver depurando o cliente.

### POST `/api/processos-estagio/` — RN01

Aluno sem matrícula ativa tenta abrir processo.

```http
POST /api/processos-estagio/
Authorization: Token <token-aluno-nao-matriculado>
Content-Type: application/json

{"empresa": 1, "horas_semanais": 20, "data_inicio_prevista": "2026-07-01",
 "data_fim_prevista": "2026-12-31", "plano_atividades": "..."}
```

Resposta:

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{"aluno": ["RN01: aluno deve estar com matrícula ativa em estágio supervisionado."]}
```

### POST `/api/processos-estagio/<id>/alterar_status/` — RN11

Coordenador tenta rejeitar sem justificativa.

```http
POST /api/processos-estagio/42/alterar_status/
Authorization: Token <token-coordenador>
Content-Type: application/json

{"status": "REJEITADO"}
```

Resposta:

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{"justificativa_rejeicao": ["RN11: justificativa obrigatória ao rejeitar uma solicitação."]}
```

### POST `/api/processos-estagio/<id>/alterar_status/` — Transição inválida

Coordenador tenta reativar um processo já rejeitado.

```http
POST /api/processos-estagio/42/alterar_status/
{"status": "ATIVO"}
```

Resposta `400`:

```json
{"status": "Transição inválida: REJEITADO → ATIVO.",
 "estado_atual": "REJEITADO",
 "transicoes_validas": []}
```

### GET `/api/processos-estagio/<id-de-outro-aluno>/` — 404 por filtro

Aluno autenticado tenta abrir processo de outro aluno: `GET /api/processos-estagio/77/` retorna `404 Not Found` com `{"detail": "Not found."}` — o queryset filtra o objeto antes de o DRF rodar `get_object`.

## Como debugar erros

Algumas pistas práticas baseadas no que mais ocorre durante o desenvolvimento:

- **`404` quando esperava `403`**. Isso é o `get_queryset` do viewset filtrando o objeto antes da permission rodar. Confirme se o token autenticado pertence ao papel certo e se o objeto realmente "pertence" a esse papel (aluno dono, supervisor da mesma empresa, coordenador do mesmo curso). Veja `ProcessoEstagioViewSet.get_queryset` em `djangotutorial/app/views.py`.
- **`401` com token aparentemente válido**. Confirme o header: deve ser `Authorization: Token <key>` (com espaço, **sem** prefixo `Bearer`). DRF Token Auth não é JWT.
- **`400` em `alterar_status` mas sem mensagem clara**. O DRF empilha o erro do `serializer.is_valid(raise_exception=True)` em cima da resposta. Se houver `justificativa_rejeicao` no payload, o erro vem como `{"justificativa_rejeicao": ["..."]}`. Se for transição inválida, vem como `{"status": "...", "estado_atual": "...", "transicoes_validas": [...]}`. Os formatos são distintos.
- **`500` sem stack trace**. Em produção (`DEBUG=False`), o Django esconde a trace e devolve uma página HTML padrão. Olhe o terminal do `runserver` — é onde a exceção é impressa. Para reproduzir local, rode `manage.py check` antes para descartar erro de configuração.
- **Resposta JSON difícil de ler**. Use `curl -s ... | python3 -m json.tool` para formatar a saída no terminal. Para `httpie`, basta `http POST ...` que ele já formata.
- **Validação aparentemente "sumindo"**. Cheque a ordem em `CriarProcessoSerializer.validate`: a primeira regra que falha **interrompe** o método. Se você esperava ver RN05 mas viu RN01, é porque o aluno não estava matriculado e o validador parou antes.

## Padrões de DRF

O sistema segue, por padrão, as convenções do [Django REST Framework](https://www.django-rest-framework.org/api-guide/exceptions/):

- `401`/`403`/`404`/`405` saem do DRF "out of the box", via classes de exceção (`NotAuthenticated`, `PermissionDenied`, `NotFound`, `MethodNotAllowed`).
- `400` é **principalmente** customizado pela aplicação, via `serializers.ValidationError` ou retorno explícito de `Response(..., status=400)` nas actions.
- O renderizador padrão é JSON (`rest_framework.renderers.JSONRenderer`); a Browsable API também está habilitada em desenvolvimento e renderiza HTML quando o cliente envia `Accept: text/html`.

Para mais detalhes do contrato global de respostas, veja [o guia de exceções do DRF](https://www.django-rest-framework.org/api-guide/exceptions/) e as referências em [autenticacao.md](autenticacao.md) e na seção [Resumo de permissões por papel](endpoints.md#resumo-de-permissoes-por-papel) de `endpoints.md`.

## Autor(es)

| Data       | Versão | Descrição              | Autor(es)               |
| ---------- | ------ | ---------------------- | ----------------------- |
| 28/05/2026 | 1.0    | Criação do documento   | João Gabriel Teodósio   |
