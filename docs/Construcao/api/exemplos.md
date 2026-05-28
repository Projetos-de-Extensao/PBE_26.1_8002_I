# Exemplos práticos — Walkthrough da API

Este documento é executável: cole os comandos sequencialmente em um shell `bash` para reproduzir o fluxo completo do sistema de estágios, desde o seed inicial até o encerramento de um processo. Todos os exemplos usam `curl` contra `http://localhost:8000` e armazenam os tokens em variáveis de shell (`$TOKEN_ALUNO`, `$TOKEN_COORD`) para que os comandos subsequentes funcionem sem edição manual.

## Pré-requisitos

Antes de começar, garanta que o ambiente está pronto:

- **Servidor rodando** em outra aba do terminal:
  ```bash
  uv run python djangotutorial/manage.py runserver
  ```
  O servidor sobe em `http://localhost:8000`.

- **Superuser criado** (para acessar o Django Admin, se quiser inspecionar o banco):
  ```bash
  uv run python djangotutorial/manage.py createsuperuser \
      --username admin --email admin@ibmec.edu.br
  ```

- **Migrations aplicadas**. O comando `runserver` aplica automaticamente na primeira execução; caso queira forçar:
  ```bash
  uv run python djangotutorial/manage.py migrate
  ```

- **`python3` no PATH** — usado pelos exemplos para extrair o token JSON da resposta.

- **`curl` no PATH** — qualquer versão recente serve.

Opcionalmente, instale `httpie` (`pip install httpie`) para os exemplos da seção 8 — não é obrigatório.

## Seed inicial via Django shell

Os exemplos assumem o seguinte estado no banco:

- 1 coordenador (`coord1` / departamento Engenharia)
- 1 curso (Eng. Software, `carga_horaria_maxima_diaria=6` → limite semanal de 30h)
- 1 empresa aprovada (Tech LTDA, `aprovada_ibmec=True`)
- 1 empresa NÃO aprovada (Não Aprovada LTDA, `aprovada_ibmec=False`)
- 1 aluno matriculado (`aluno1`, `matriculado_estagio=True`)
- 1 aluno NÃO matriculado (`aluno2`, `matriculado_estagio=False`)

Execute o bloco abaixo uma única vez para popular o banco. Ele imprime os IDs gerados ao final — anote-os, especialmente o `emp_ok.pk`, pois o `curl` de criação de processo precisa dele (geralmente `1` se o banco está limpo).

```bash
uv run python djangotutorial/manage.py shell <<'PY'
from app.models import Usuario, Coordenador, Curso, EmpresaConcedente, Aluno

cu = Usuario.objects.create_user(
    username='coord1', password='senha123',
    tipo='coordenador', nome='Coord Eng',
)
coord = Coordenador.objects.create(usuario=cu, departamento='Engenharia')

curso = Curso.objects.create(
    nome='Eng. Software',
    carga_horaria_maxima_diaria=6,
    coordenador=coord,
)

emp_ok = EmpresaConcedente.objects.create(
    cnpj='11.111.111/0001-11', razao_social='Tech LTDA',
    areas_atuacao='TI', localizacao='RJ',
    email_contato='rh@tech.com', aprovada_ibmec=True,
)
emp_no = EmpresaConcedente.objects.create(
    cnpj='22.222.222/0001-22', razao_social='Não Aprovada LTDA',
    areas_atuacao='X', localizacao='RJ',
    email_contato='x@x.com', aprovada_ibmec=False,
)

u1 = Usuario.objects.create_user(
    username='aluno1', password='senha123',
    tipo='aluno', nome='Aluno Um',
)
Aluno.objects.create(
    usuario=u1, cpf='111.111.111-11',
    curso=curso, matriculado_estagio=True,
)

u2 = Usuario.objects.create_user(
    username='aluno2', password='senha123',
    tipo='aluno', nome='Aluno Dois',
)
Aluno.objects.create(
    usuario=u2, cpf='222.222.222-22',
    curso=curso, matriculado_estagio=False,
)

print(f'OK: curso={curso.pk}, emp_ok={emp_ok.pk}, emp_no={emp_no.pk}')
PY
```

Saída esperada (os IDs podem variar se o banco já tinha dados):

```
OK: curso=1, emp_ok=1, emp_no=2
```

Daqui pra frente, os exemplos assumem `emp_ok=1` e `emp_no=2`. Se forem outros no seu ambiente, substitua nos comandos.

## Walkthrough 1 — Happy path completo

Fluxo do nascimento ao encerramento de um processo de estágio: aluno cria, coordenador aprova, ativa e por fim encerra. Execute na ordem.

### 4.1 Login do aluno (captura `$TOKEN_ALUNO`)

```bash
TOKEN_ALUNO=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "aluno1", "password": "senha123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")

echo "TOKEN_ALUNO=$TOKEN_ALUNO"
```

Resposta bruta da API:

```json
{
  "token": "9b8c7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f2a1b0c",
  "id": 5,
  "tipo": "aluno",
  "nome": "Aluno Um"
}
```

### 4.2 Aluno cria processo de estágio

O servidor preenche automaticamente `aluno`, `status=PENDENTE` e `coordenador` (do curso do aluno) — você só envia os dados do estágio em si.

```bash
curl -s -X POST http://localhost:8000/api/processos-estagio/ \
  -H "Authorization: Token $TOKEN_ALUNO" \
  -H "Content-Type: application/json" \
  -d '{
    "empresa": 1,
    "horas_semanais": 20,
    "data_inicio_prevista": "2026-07-01",
    "data_fim_prevista": "2026-12-31",
    "plano_atividades": "Desenvolvimento de APIs em Django."
  }' | python3 -m json.tool
```

Resposta esperada (`201 Created`):

```json
{
  "id": 1,
  "empresa": 1,
  "horas_semanais": 20,
  "data_inicio_prevista": "2026-07-01",
  "data_fim_prevista": "2026-12-31",
  "plano_atividades": "Desenvolvimento de APIs em Django.",
  "aluno": 1,
  "status": "PENDENTE",
  "coordenador": 1
}
```

Anote o `id` do processo retornado (assumimos `1` nos próximos passos).

### 4.3 Login do coordenador (captura `$TOKEN_COORD`)

```bash
TOKEN_COORD=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "coord1", "password": "senha123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")

echo "TOKEN_COORD=$TOKEN_COORD"
```

Resposta bruta:

```json
{
  "token": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0",
  "id": 1,
  "tipo": "coordenador",
  "nome": "Coord Eng"
}
```

### 4.4 Coordenador aprova o processo (`PENDENTE → APROVADO`)

```bash
curl -s -X POST http://localhost:8000/api/processos-estagio/1/alterar_status/ \
  -H "Authorization: Token $TOKEN_COORD" \
  -H "Content-Type: application/json" \
  -d '{"status": "APROVADO"}' | python3 -m json.tool
```

Resposta esperada (`200 OK`) — retorna o processo completo atualizado:

```json
{
  "id": 1,
  "status": "APROVADO",
  "aluno": 1,
  "empresa": 1,
  "coordenador": 1,
  "horas_semanais": 20,
  "data_inicio_prevista": "2026-07-01",
  "data_fim_prevista": "2026-12-31",
  "plano_atividades": "Desenvolvimento de APIs em Django.",
  "justificativa_rejeicao": ""
}
```

### 4.5 Coordenador ativa o processo (`APROVADO → ATIVO`)

Quando o aluno efetivamente começa o estágio, o coordenador muda o status para `ATIVO`.

```bash
curl -s -X POST http://localhost:8000/api/processos-estagio/1/alterar_status/ \
  -H "Authorization: Token $TOKEN_COORD" \
  -H "Content-Type: application/json" \
  -d '{"status": "ATIVO"}' | python3 -m json.tool
```

Resposta (`200 OK`):

```json
{
  "id": 1,
  "status": "ATIVO",
  "aluno": 1,
  "empresa": 1,
  "coordenador": 1,
  "horas_semanais": 20
}
```

### 4.6 Coordenador encerra o processo (`ATIVO → ENCERRADO`)

```bash
curl -s -X POST http://localhost:8000/api/processos-estagio/1/alterar_status/ \
  -H "Authorization: Token $TOKEN_COORD" \
  -H "Content-Type: application/json" \
  -d '{"status": "ENCERRADO"}' | python3 -m json.tool
```

Resposta (`200 OK`):

```json
{
  "id": 1,
  "status": "ENCERRADO",
  "aluno": 1,
  "empresa": 1,
  "coordenador": 1
}
```

`ENCERRADO` é um estado terminal — não há transições válidas a partir dele.

## Walkthrough 2 — Cenários de erro (regras de negócio)

Cada subseção dispara propositalmente uma regra de negócio para mostrar a resposta de erro. Reset o banco (seção 9) entre os walkthroughs 1 e 2 se quiser começar limpo, ou simplesmente cancele o processo criado antes de rodar os cenários de criação.

### 5.1 Aluno não matriculado tenta criar (RN01)

```bash
TOKEN_ALUNO2=$(curl -s -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "aluno2", "password": "senha123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")

curl -s -X POST http://localhost:8000/api/processos-estagio/ \
  -H "Authorization: Token $TOKEN_ALUNO2" \
  -H "Content-Type: application/json" \
  -d '{
    "empresa": 1,
    "horas_semanais": 20,
    "data_inicio_prevista": "2026-07-01",
    "data_fim_prevista": "2026-12-31",
    "plano_atividades": "Teste."
  }' | python3 -m json.tool
```

Resposta (`400 Bad Request`):

```json
{
  "aluno": [
    "RN01: aluno deve estar com matrícula ativa em estágio supervisionado."
  ]
}
```

### 5.2 Empresa não aprovada (RN09)

Usa o aluno1 (matriculado), mas aponta para a empresa não aprovada (`empresa=2`).

```bash
curl -s -X POST http://localhost:8000/api/processos-estagio/ \
  -H "Authorization: Token $TOKEN_ALUNO" \
  -H "Content-Type: application/json" \
  -d '{
    "empresa": 2,
    "horas_semanais": 20,
    "data_inicio_prevista": "2026-07-01",
    "data_fim_prevista": "2026-12-31",
    "plano_atividades": "Teste empresa não aprovada."
  }' | python3 -m json.tool
```

Resposta (`400 Bad Request`):

```json
{
  "empresa": [
    "RN09: empresa não está aprovada pelo IBMEC."
  ]
}
```

### 5.3 Horas semanais acima do limite do curso (RN03)

O curso Eng. Software tem `carga_horaria_maxima_diaria=6`, logo o limite semanal é `6 × 5 = 30h`. Envie `40h`:

```bash
curl -s -X POST http://localhost:8000/api/processos-estagio/ \
  -H "Authorization: Token $TOKEN_ALUNO" \
  -H "Content-Type: application/json" \
  -d '{
    "empresa": 1,
    "horas_semanais": 40,
    "data_inicio_prevista": "2026-07-01",
    "data_fim_prevista": "2026-12-31",
    "plano_atividades": "Teste excesso de horas."
  }' | python3 -m json.tool
```

Resposta (`400 Bad Request`):

```json
{
  "horas_semanais": [
    "RN03: excede o limite do curso (30h/semana)."
  ]
}
```

### 5.4 Horas acima do limite legal (Lei 11.788/08)

Mesmo se o curso permitisse, a Lei 11.788/08 fixa o teto em 30h semanais. Envie `35h` (que não dispara RN03 nesse curso porque o curso tem o mesmo limite, mas em cursos com limite maior dispararia a regra legal):

```bash
curl -s -X POST http://localhost:8000/api/processos-estagio/ \
  -H "Authorization: Token $TOKEN_ALUNO" \
  -H "Content-Type: application/json" \
  -d '{
    "empresa": 1,
    "horas_semanais": 35,
    "data_inicio_prevista": "2026-07-01",
    "data_fim_prevista": "2026-12-31",
    "plano_atividades": "Teste limite legal."
  }' | python3 -m json.tool
```

Resposta (`400 Bad Request`):

```json
{
  "horas_semanais": [
    "RN03: excede o limite do curso (30h/semana)."
  ]
}
```

Quando o limite do curso é maior que 30h, a mensagem retornada será `"Limite legal de 30h semanais (Lei 11.788/08)."`.

### 5.5 Data fim anterior à data início

```bash
curl -s -X POST http://localhost:8000/api/processos-estagio/ \
  -H "Authorization: Token $TOKEN_ALUNO" \
  -H "Content-Type: application/json" \
  -d '{
    "empresa": 1,
    "horas_semanais": 20,
    "data_inicio_prevista": "2026-07-01",
    "data_fim_prevista": "2026-06-01",
    "plano_atividades": "Teste data inválida."
  }' | python3 -m json.tool
```

Resposta (`400 Bad Request`):

```json
{
  "data_fim_prevista": [
    "Deve ser posterior à data de início."
  ]
}
```

### 5.6 Aluno já tem processo vivo (RN05)

Crie um processo válido primeiro (ver 4.2). Em seguida, tente criar outro:

```bash
curl -s -X POST http://localhost:8000/api/processos-estagio/ \
  -H "Authorization: Token $TOKEN_ALUNO" \
  -H "Content-Type: application/json" \
  -d '{
    "empresa": 1,
    "horas_semanais": 20,
    "data_inicio_prevista": "2027-01-01",
    "data_fim_prevista": "2027-06-30",
    "plano_atividades": "Segundo processo."
  }' | python3 -m json.tool
```

Resposta (`400 Bad Request`):

```json
{
  "non_field_errors": [
    "RN05: aluno já possui um processo de estágio em andamento. Cancele ou aguarde o encerramento antes de abrir outro."
  ]
}
```

### 5.7 Coordenador rejeita sem justificativa (RN11)

Assume um processo `PENDENTE` com `id=1`. A rejeição exige `justificativa_rejeicao` não vazia.

```bash
curl -s -X POST http://localhost:8000/api/processos-estagio/1/alterar_status/ \
  -H "Authorization: Token $TOKEN_COORD" \
  -H "Content-Type: application/json" \
  -d '{"status": "REJEITADO"}' | python3 -m json.tool
```

Resposta (`400 Bad Request`):

```json
{
  "justificativa_rejeicao": [
    "RN11: justificativa obrigatória ao rejeitar uma solicitação."
  ]
}
```

### 5.8 Coordenador rejeita com justificativa válida

```bash
curl -s -X POST http://localhost:8000/api/processos-estagio/1/alterar_status/ \
  -H "Authorization: Token $TOKEN_COORD" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "REJEITADO",
    "justificativa_rejeicao": "Plano de atividades incompatível com o curso."
  }' | python3 -m json.tool
```

Resposta (`200 OK`):

```json
{
  "id": 1,
  "status": "REJEITADO",
  "justificativa_rejeicao": "Plano de atividades incompatível com o curso.",
  "aluno": 1,
  "empresa": 1,
  "coordenador": 1
}
```

### 5.9 Transição inválida (`REJEITADO → ATIVO`)

`REJEITADO` é estado terminal. Qualquer tentativa de transição é bloqueada com o conjunto `transicoes_validas` vazio.

```bash
curl -s -X POST http://localhost:8000/api/processos-estagio/1/alterar_status/ \
  -H "Authorization: Token $TOKEN_COORD" \
  -H "Content-Type: application/json" \
  -d '{"status": "ATIVO"}' | python3 -m json.tool
```

Resposta (`400 Bad Request`):

```json
{
  "status": "Transição inválida: REJEITADO → ATIVO.",
  "estado_atual": "REJEITADO",
  "transicoes_validas": []
}
```

## Walkthrough 3 — Isolamento por papel

A API filtra o queryset de cada endpoint pelo papel do usuário autenticado. Os exemplos abaixo demonstram esse isolamento.

### 6.1 Aluno1 lista — vê só os próprios processos

```bash
curl -s -X GET http://localhost:8000/api/processos-estagio/ \
  -H "Authorization: Token $TOKEN_ALUNO" | python3 -m json.tool
```

Resposta (`200 OK`) — apenas processos cujo `aluno` é o aluno1:

```json
[
  {
    "id": 1,
    "status": "PENDENTE",
    "aluno": 1,
    "empresa": 1,
    "coordenador": 1,
    "horas_semanais": 20
  }
]
```

### 6.2 Coordenador lista — vê só processos dos cursos dele

```bash
curl -s -X GET http://localhost:8000/api/processos-estagio/ \
  -H "Authorization: Token $TOKEN_COORD" | python3 -m json.tool
```

Resposta (`200 OK`) — todos os processos cujo `aluno.curso.coordenador` é o coord1:

```json
[
  {
    "id": 1,
    "status": "PENDENTE",
    "aluno": 1,
    "empresa": 1,
    "coordenador": 1
  }
]
```

Se houver alunos em outros cursos com outros coordenadores, esses processos não aparecem aqui.

### 6.3 Aluno1 tenta alterar processo do aluno2

Crie um processo do aluno2 manualmente (via shell) ou matricule-o e crie via API. Em seguida, tente alterar pelo aluno1:

```bash
curl -s -o /dev/null -w "HTTP %{http_code}\n" \
  -X POST http://localhost:8000/api/processos-estagio/2/alterar_status/ \
  -H "Authorization: Token $TOKEN_ALUNO" \
  -H "Content-Type: application/json" \
  -d '{"status": "CANCELADO"}'
```

Resposta esperada:

```
HTTP 404
```

A API retorna `404 Not Found` porque o queryset filtrado do aluno1 não inclui o processo do aluno2 — do ponto de vista dele, o recurso não existe. Caso o processo esteja em escopo mas a ação não seja permitida, a resposta seria `403 Forbidden` com:

```json
{
  "detail": "Sem permissão neste processo."
}
```

### 6.4 Coordenador de outro curso tenta aprovar

Cenário coberto pelos testes em `app/tests.py::AlterarStatusTest::test_coord_de_outro_curso_403`. Se um coordenador de outro departamento tenta aprovar um processo cujo aluno não pertence aos seus cursos, a API responde:

```json
{
  "detail": "Processo não pertence a curso sob sua coordenação."
}
```

Status `403 Forbidden`. Esse cenário não é reproduzido neste walkthrough porque o seed só cria um coordenador — para reproduzi-lo, adicione um segundo coordenador e um segundo curso no shell.

## Via Swagger UI

Tudo o que foi demonstrado via `curl` pode ser feito pela interface gráfica do Swagger.

1. Abra `http://localhost:8000/api/docs/` no navegador.
2. Faça login (ou pegue um token via 4.1/4.3) e clique em **Authorize** no canto superior direito.
3. No campo do esquema `tokenAuth`, digite `Token <seu_token>` — atenção: a palavra é literalmente `Token` (com T maiúsculo) seguida de espaço e o valor do token. Não use `Bearer`.
4. Expanda qualquer endpoint, clique em **Try it out**, edite o JSON do body se necessário e clique em **Execute**. O Swagger mostra o `curl` equivalente, o status code e o JSON de resposta.
5. Para trocar de usuário (por exemplo, de aluno para coordenador), clique em **Authorize** novamente, use **Logout** no esquema atual e cole o token do outro usuário.

Vale notar que o Swagger UI suporta todos os endpoints documentados — incluindo `/api/auth/login/`, `/api/processos-estagio/`, `/api/processos-estagio/{id}/alterar_status/`, `/api/processos-estagio/{id}/documentos/` etc. Se preferir um ambiente totalmente clicável para explorar a API, use-o.

## Via httpie (alternativa mais legível)

`httpie` é uma alternativa moderna ao `curl` com saída colorida e sintaxe mais sucinta. Não está no `requirements.txt` do projeto — instale separadamente com `pip install httpie`.

Login:

```bash
http POST :8000/api/auth/login/ \
  username=aluno1 password=senha123
```

Criar processo (após capturar `$TOKEN`):

```bash
http POST :8000/api/processos-estagio/ \
  "Authorization:Token $TOKEN" \
  empresa:=1 \
  horas_semanais:=20 \
  data_inicio_prevista=2026-07-01 \
  data_fim_prevista=2026-12-31 \
  plano_atividades="APIs em Django"
```

Alterar status:

```bash
http POST :8000/api/processos-estagio/1/alterar_status/ \
  "Authorization:Token $TOKEN_COORD" \
  status=APROVADO
```

Os campos com `:=` são tratados como JSON nativo (números, booleanos, listas); os com `=` viram strings. Não esqueça das aspas em `"Authorization:Token $TOKEN"` — sem elas, o shell pode interpretar o `:` de forma errada.

## Reset do banco (se precisar começar do zero)

Se algum walkthrough deixou o banco em estado inconsistente, apague o SQLite e refaça migrations + seed:

```bash
rm djangotutorial/db.sqlite3
uv run python djangotutorial/manage.py migrate
uv run python djangotutorial/manage.py createsuperuser \
    --username admin --email admin@ibmec.edu.br
# Rode novamente o bloco de seed da seção 3
```

O `migrate` recria todas as tabelas. O `createsuperuser` pedirá a senha interativamente. Depois rode novamente o bloco de seed da seção 3 para repopular o banco com os usuários e cursos usados nos exemplos.

## Autor(es)

| Data | Versão | Descrição | Autor(es) |
| -- | -- | -- | -- |
| 28/05/2026 | 1.0 | Criação do documento | João Gabriel Teodósio |
