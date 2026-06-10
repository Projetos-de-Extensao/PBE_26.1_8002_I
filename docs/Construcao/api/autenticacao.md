# Autenticação

A API IBMEC Estágios utiliza autenticação por **token** baseada em `rest_framework.authtoken` (DRF Token Authentication). Não há sessão, nem cookie, nem CSRF: cada cliente obtém um token via registro ou login e o envia no header `Authorization` em todas as requisições subsequentes. O token é opaco, persistente até logout, e está vinculado a um único `Usuario`.

## Visão geral

Pseudo-fluxo do ciclo de autenticação:

```
Cliente ─► POST /api/auth/register/  ─► 201 { token, id, tipo }
              │
              └─ ou, se já tem conta:
                 POST /api/auth/login/ ─► 200 { token, id, tipo, nome }
                                                │
                                                ▼
Cliente ─► (toda request seguinte)
           Header: Authorization: Token <key>
                                                │
                                                ▼
Cliente ─► POST /api/auth/logout/    ─► 200 { mensagem }
           (invalida o token atual)
```

Enquanto o token estiver válido, ele é a credencial única do cliente. Não há expiração automática; a invalidação acontece em `logout` ou por ação administrativa.

## Tipos de usuário

O campo `tipo` em `Usuario` define o papel do ator no sistema e direciona qual perfil (`Aluno`, `Coordenador`, `SupervisorEmpresa`) é criado em conjunto. Administradores não usam `tipo`: são `Usuario` com `is_staff=True` e/ou `is_superuser=True`, criados via `python manage.py createsuperuser`.

| `tipo` | Quem é | O que faz no sistema |
| --- | --- | --- |
| `aluno` | Estudante do IBMEC matriculado em estágio obrigatório | Cria processos de estágio, anexa documentos, acompanha decisões, cancela o próprio processo |
| `coordenador` | Coordenador acadêmico de um ou mais cursos | Aprova, rejeita, solicita correção, ativa e encerra processos dos alunos dos cursos sob sua coordenação |
| `supervisor_empresa` | Profissional da empresa concedente | Visualiza processos vinculados à sua empresa; ações de acompanhamento ficam fora do escopo desta entrega |
| _admin_ (sem `tipo`) | Usuário com `is_staff=True`, criado via `createsuperuser` | Acesso total a todos os recursos e a qualquer transição da máquina de estados |

## POST /api/auth/register/

Cria simultaneamente o `Usuario` e o perfil correspondente ao `tipo`, e devolve um token pronto para uso.

- **Auth requerida:** não (`AllowAny`).
- **Content-Type:** `application/json`.

### Body comum (todos os tipos)

| Campo | Tipo | Obrigatório | Observação |
| --- | --- | --- | --- |
| `tipo` | string | sim | `aluno`, `coordenador` ou `supervisor_empresa` |
| `username` | string | sim | Identificador único de login |
| `password` | string | sim | Senha em texto plano (será hasheada pelo Django) |
| `nome` | string | recomendado | Nome civil do usuário |
| `email_institucional` | string (email) | recomendado | Email institucional do usuário |

### Campos extras por tipo

#### `tipo = "aluno"`

| Campo | Tipo | Obrigatório | Observação |
| --- | --- | --- | --- |
| `cpf` | string | sim | Único na base de alunos |
| `rg` | string | não | Texto livre |
| `coeficiente_rendimento` | decimal | não | Default `0` |
| `curso_id` | int (FK `Curso`) | não | Recomendado para que o sistema atribua coordenador automaticamente ao criar processo |
| `matriculado_estagio` | bool | não | Default `false` |

#### `tipo = "coordenador"`

| Campo | Tipo | Obrigatório | Observação |
| --- | --- | --- | --- |
| `departamento` | string | sim | Não pode ser vazio |

#### `tipo = "supervisor_empresa"`

| Campo | Tipo | Obrigatório | Observação |
| --- | --- | --- | --- |
| `empresa_id` | int (FK `EmpresaConcedente`) | sim | Deve referenciar empresa existente |
| `cargo` | string | não | Texto livre |

### Resposta de sucesso

`201 Created`:

```json
{
  "token": "c2f1a9d4e3b8...",
  "id": 17,
  "tipo": "aluno"
}
```

### Erros comuns

`400 Bad Request`:

```json
{ "erro": "username e password são obrigatórios." }
```

```json
{ "erro": "campo \"departamento\" é obrigatório para coordenador." }
```

```json
{ "erro": "campo \"empresa_id\" é obrigatório para supervisor_empresa." }
```

```json
{ "erro": "EmpresaConcedente não encontrada." }
```

```json
{ "erro": "tipo deve ser \"aluno\", \"coordenador\" ou \"supervisor_empresa\"." }
```

Erros de integridade de banco (`username` duplicado, `cpf` duplicado, etc.) também retornam `400` com a mensagem da exceção em `erro`.

### Exemplos curl

Aluno:

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "tipo": "aluno",
    "username": "ana.lima",
    "password": "senha-forte-123",
    "nome": "Ana Lima",
    "email_institucional": "ana.lima@al.ibmec.edu.br",
    "cpf": "123.456.789-00",
    "curso_id": 1,
    "coeficiente_rendimento": 8.4
  }'
```

Coordenador:

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "tipo": "coordenador",
    "username": "prof.souza",
    "password": "senha-forte-123",
    "nome": "Carlos Souza",
    "email_institucional": "carlos.souza@ibmec.edu.br",
    "departamento": "Computação"
  }'
```

Supervisor de empresa:

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "tipo": "supervisor_empresa",
    "username": "marcia.acme",
    "password": "senha-forte-123",
    "nome": "Márcia Pereira",
    "email_institucional": "marcia@acme.com",
    "empresa_id": 3,
    "cargo": "Gerente de RH"
  }'
```

## POST /api/auth/login/

Autentica `username`/`password` e devolve o token persistente do usuário (cria um, se ainda não existir).

- **Auth requerida:** não (`AllowAny`).

### Body

```json
{
  "username": "ana.lima",
  "password": "senha-forte-123"
}
```

### Resposta de sucesso

`200 OK`:

```json
{
  "token": "c2f1a9d4e3b8...",
  "id": 17,
  "tipo": "aluno",
  "nome": "Ana Lima"
}
```

### Erro

`401 Unauthorized`:

```json
{ "erro": "Credenciais inválidas." }
```

### Exemplo curl

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "ana.lima", "password": "senha-forte-123"}'
```

## POST /api/auth/logout/

Invalida o token do usuário autenticado, removendo-o da base. O mesmo usuário receberá outro token na próxima chamada a `login` ou `register`.

- **Auth requerida:** sim (`IsAuthenticated`).
- **Header obrigatório:** `Authorization: Token <key>`.

### Resposta de sucesso

`200 OK`:

```json
{ "mensagem": "Logout realizado com sucesso." }
```

A view captura silenciosamente o caso em que o token já foi removido, retornando a mesma mensagem.

### Exemplo curl

```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Token c2f1a9d4e3b8..."
```

## Usando o token em requests

Toda rota protegida exige o header:

```
Authorization: Token <key>
```

Note o prefixo literal `Token` (com letra maiúscula), seguido de espaço e da chave devolvida pelo `register`/`login`. Não use `Bearer`.

Exemplo de listagem de processos de estágio autenticada como aluno:

```bash
curl -X GET http://localhost:8000/api/processos-estagio/ \
  -H "Authorization: Token c2f1a9d4e3b8..." \
  -H "Accept: application/json"
```

Requisições sem o header (ou com token inválido/inexistente) retornam `401 Unauthorized`. Requisições com token válido mas sem permissão para o recurso retornam `403 Forbidden`.

## Permissões por papel (resumo)

Cada papel tem um conjunto típico de ações autorizadas pelas classes em `app/permissions.py` e pela lógica de `ProcessoEstagioViewSet`. O detalhamento por endpoint está em [`endpoints.md`](endpoints.md).

| Papel | Ações típicas |
| --- | --- |
| Aluno | Cria o próprio processo de estágio, lista/visualiza os próprios processos e documentos, envia documentos, cancela o próprio processo |
| Coordenador | Lista cursos sob sua coordenação, lista processos dos alunos desses cursos, aprova/rejeita/solicita correção/ativa/encerra esses processos |
| Supervisor de empresa | Lista processos vinculados à sua `EmpresaConcedente`, consulta documentos desses processos |
| Admin | Acesso irrestrito a todos os recursos e a qualquer transição da máquina de estados |

## OAuth Microsoft

A carcaça do `django-allauth` (com provider Microsoft) está instalada em `mysite/settings.py` como preparação para integração futura ao Azure AD do IBMEC. Porém o App Registration correspondente não está configurado: não há `client_id`/`client_secret` válidos, nem callback registrado no portal Azure. Por isso, autenticação via conta institucional Microsoft está **fora do escopo desta entrega** — a única autenticação operacional é o fluxo Token Auth descrito acima.

## Autor(es)

| Data | Versão | Descrição | Autor(es) |
| -- | -- | -- | -- |
| 28/05/2026 | 1.0 | Criação do documento | João Gabriel Teodósio |
