# Manual do Usuário

> Tutorial de uso do sistema de gestão de estágios do IBMEC.

---

## 1. Visão Geral

O sistema centraliza todo o ciclo do estágio obrigatório: da abertura da solicitação, passando pela aprovação do coordenador e gestão de documentos, até o encerramento e avaliação da empresa. Todas as interações ocorrem via API REST, documentada e testável no **Swagger UI** em `/api/docs/`.

---

## 2. Perfis de Usuário

| Perfil | O que pode fazer |
|--------|-----------------|
| **Aluno** | Abrir processos, enviar documentos, preencher formulários de avaliação, avaliar empresa |
| **Coordenador** | Aprovar/rejeitar processos e documentos do seu curso, criar modelos de formulário |
| **Supervisor de Empresa** | Visualizar processos vinculados à sua empresa |
| **Secretaria / CASA / Reitor / Pró-Reitor** | Visão global de leitura de todos os processos e cursos |
| **Carreiras** | Acesso administrativo completo (exceto edição de formulários) |

---

## 3. Acesso ao Sistema

### 3.1 Execução local

```bash
# Clone o repositório
git clone https://github.com/Projetos-de-Extensao/PBE_26.1_8002_I.git
cd PBE_26.1_8002_I

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# Instale as dependências
pip install -r djangotutorial/requirements.txt

# Aplique as migrações e crie o superusuário
cd djangotutorial
python manage.py migrate
python manage.py createsuperuser

# (Opcional) Popule o banco com dados de exemplo
python populate_db.py

# Inicie o servidor
python manage.py runserver
```

Após iniciar, os endereços disponíveis são:

| URL | Descrição |
|-----|-----------|
| `http://127.0.0.1:8000/api/` | API navegável (DRF) |
| `http://127.0.0.1:8000/api/docs/` | Swagger UI — documentação interativa |
| `http://127.0.0.1:8000/api/redoc/` | ReDoc — documentação alternativa |
| `http://127.0.0.1:8000/admin/` | Painel administrativo Django |

---

## 4. Autenticação

### 4.1 Registro

`POST /api/auth/register/`

```json
{
  "tipo": "aluno",
  "username": "pedro.silva",
  "password": "SenhaSegura123",
  "nome": "Pedro Silva",
  "email_institucional": "pedro.silva@ibmec.edu.br",
  "matricula": "2024001",
  "cpf": "000.000.000-00",
  "rg": "1234567"
}
```

Tipos válidos: `aluno`, `coordenador`, `supervisor_empresa`, `secretaria`, `casa`, `reitor`, `pro_reitor`, `carreiras`.

### 4.2 Login

`POST /api/auth/login/`

```json
{
  "email_institucional": "pedro.silva@ibmec.edu.br",
  "password": "SenhaSegura123"
}
```

A resposta retorna um **token** de autenticação. Inclua-o em todas as requisições seguintes:

```
Authorization: Token <seu-token-aqui>
```

### 4.3 Logout

`POST /api/auth/logout/`  
Requer o cabeçalho `Authorization: Token <token>`. Invalida o token imediatamente.

### 4.4 Recuperação de Senha

1. `POST /api/auth/esqueci-senha/` — informe `email_institucional`.
2. `POST /api/auth/redefinir-senha/` — informe o token recebido por e-mail e a nova senha.

---

## 5. Tutorial: Aluno

### 5.1 Abrir um Processo de Estágio

`POST /api/processos-estagio/`

```json
{
  "empresa": 1,
  "supervisor": 2,
  "horas_semanais": 20,
  "data_inicio_prevista": "2026-07-01",
  "data_fim_prevista": "2026-12-31",
  "plano_atividades": "Desenvolvimento de software backend com Python/Django.",
  "valor_bolsa": 1200.00,
  "valor_auxilio_transporte": 300.00
}
```

O processo é criado no status **PENDENTE** e encaminhado para o coordenador.

> **Dica:** use `GET /api/empresas/` para listar as empresas aprovadas pelo IBMEC e obter o `id` correto.

### 5.2 Acompanhar Status do Processo

`GET /api/processos-estagio/{id}/`

Os status possíveis e seu significado:

| Status | Significado |
|--------|-------------|
| `RASCUNHO` | Salvo mas ainda não enviado |
| `PENDENTE` | Aguardando análise do coordenador |
| `CORRECAO_SOLICITADA` | Coordenador pediu ajustes — releia a justificativa |
| `APROVADO` | Aprovado pelo coordenador, aguardando início |
| `ATIVO` | Estágio em andamento |
| `ENCERRADO` | Estágio concluído |
| `REJEITADO` | Processo negado (ver `justificativa_rejeicao`) |
| `CANCELADO` | Cancelado pelo aluno ou coordenador |

### 5.3 Enviar Documentos

`POST /api/documentos/` (multipart/form-data)

| Campo | Valor |
|-------|-------|
| `processo` | ID do processo |
| `tipo` | `TCE`, `APOLICE`, `RELATORIO_PARCIAL`, `RELATORIO_FINAL`, `AVALIACAO_EMPRESA`, `TERMO_REALIZACAO` ou `OUTRO` |
| `arquivo` | Arquivo PDF/DOCX |
| `titulo` | Título opcional do documento |

### 5.4 Gerar TCE em PDF

`GET /api/processos-estagio/{id}/gerar-tce/`

Gera automaticamente o **Termo de Compromisso de Estágio** em PDF com os dados do processo. O arquivo pode ser baixado diretamente.

### 5.5 Preencher Formulário de Avaliação

`POST /api/processos-estagio/{id}/preencher-formulario/`

```json
{
  "respostas": {
    "questao_1": "Sim",
    "questao_2": 4,
    "questao_3": "Excelente ambiente de trabalho."
  }
}
```

### 5.6 Avaliar a Empresa

`POST /api/avaliar-empresa/`

```json
{
  "processo": 1,
  "nota": 5,
  "comentario": "Empresa com ótima estrutura e suporte ao estagiário.",
  "anonimo": true
}
```

- Nota de **1 a 5 estrelas**.  
- Se `anonimo: true`, a identidade do avaliador não é exposta.  
- Cada processo permite **uma única avaliação**.

Para verificar se já avaliou: `GET /api/avaliar-empresa/ja-avaliei/?processo={id}`

---

## 6. Tutorial: Coordenador

### 6.1 Listar Processos do Curso

`GET /api/processos-estagio/`

O coordenador visualiza automaticamente apenas os processos do seu curso.

### 6.2 Aprovar ou Rejeitar um Processo

`PATCH /api/processos-estagio/{id}/`

**Aprovar:**
```json
{ "status": "APROVADO" }
```

**Rejeitar:**
```json
{
  "status": "REJEITADO",
  "justificativa_rejeicao": "Empresa não cadastrada no IBMEC."
}
```

**Solicitar correção:**
```json
{
  "status": "CORRECAO_SOLICITADA",
  "justificativa_rejeicao": "Plano de atividades incompleto."
}
```

### 6.3 Validar Documentos

`PATCH /api/documentos/{id}/`

```json
{
  "status": "APROVADO",
  "observacoes": "TCE assinado e conforme."
}
```

Ou para rejeitar:
```json
{
  "status": "REJEITADO",
  "observacoes": "Assinatura do responsável legal ausente."
}
```

### 6.4 Criar Modelo de Formulário de Avaliação

`POST /api/modelos-formulario/`

```json
{
  "titulo": "Formulário Padrão — Ciência da Computação",
  "curso": 1,
  "secoes": [
    {
      "tipo": "escala_1_4",
      "titulo": "Qualidade do ambiente de trabalho",
      "itens": ["Infraestrutura", "Equipe", "Suporte técnico"]
    },
    {
      "tipo": "texto_livre",
      "titulo": "Comentários adicionais"
    }
  ]
}
```

### 6.5 Dashboard

| Endpoint | Descrição |
|----------|-----------|
| `GET /api/dashboard/processos/` | Visão geral dos processos por status |
| `GET /api/dashboard/estatisticas/` | Métricas agregadas do curso |
| `GET /api/dashboard/empresas/` | Ranking e avaliações de empresas parceiras |

---

## 7. Tutorial: Supervisor de Empresa

### 7.1 Visualizar Processos da Empresa

`GET /api/processos-estagio/`

O supervisor visualiza automaticamente apenas os processos vinculados à empresa onde está cadastrado.

### 7.2 Consultar Documentos

`GET /api/documentos/?processo={id}`

Lista todos os documentos de um processo específico.

---

## 8. Painel Administrativo

Acesse `http://127.0.0.1:8000/admin/` com um superusuário para:

- Cadastrar e editar **Empresas Concedentes** e aprovar/reprovar o vínculo com o IBMEC.
- Gerenciar **Cursos** e atribuir coordenadores.
- Criar e editar **Templates de Documentos** (TCE, Relatório, Avaliação).
- Consultar o **Histórico de Status** de qualquer processo.
- Ver **Logs de Documentos** com rastreabilidade completa de ações.

---

## 9. Fluxo Completo — Resumo Visual

```
Aluno abre processo
        │
        ▼
   [PENDENTE] ──────────────────────────────────────────────┐
        │                                                    │
        ▼ Coordenador analisa                               │
   ┌────┴──────────────────────────────┐                   │
   │                                   │                   │
   ▼                                   ▼                   ▼
[APROVADO]               [CORRECAO_SOLICITADA]        [REJEITADO]
   │                              │                    (terminal)
   │                              ▼
   │                         Aluno corrige
   │                              │
   │                              ▼
   │                         [PENDENTE]
   │
   ▼ Coordenador ativa
[ATIVO]
   │
   ▼ Estágio concluído
[ENCERRADO]
   (terminal)
```

Em qualquer etapa não-terminal, o processo pode ser **[CANCELADO]**.

---

## 10. Erros Comuns

| Código | Significado | O que fazer |
|--------|-------------|-------------|
| `401 Unauthorized` | Token ausente ou inválido | Faça login e inclua o token no cabeçalho |
| `403 Forbidden` | Sem permissão para esta ação | Verifique se seu perfil tem acesso a esta operação |
| `400 Bad Request` | Dados inválidos | Leia a mensagem de erro retornada — há validações de negócio |
| `404 Not Found` | Recurso não encontrado | Confirme o ID e se você tem acesso a este objeto |

Para a lista completa de códigos de erro da API, consulte [Códigos de Erro](../Construcao/api/erros.md).
