# PBE_26.1_8002_I

Projeto da disciplina voltado à gestão e otimização dos estágios obrigatórios do IBMEC. A proposta é centralizar a formalização, validação e acompanhamento do estágio em um único fluxo, conectando aluno, empresa concedente e coordenação com rastreabilidade documental, regras acadêmicas por curso e menos dependência de processos manuais.

## Participantes

- Lucas de Souza Alcantara
- João Gabriel Teodósio de Oliveira Lima
- Roger dos Santos Tavares Pires
- Letícia Rocha Valladão
- Vinícius Dias Lopes Machado Martinez

## Tecnologias usadas

- Python
- Django
- MySQL / banco de dados relacional
- MkDocs
- Material for MkDocs
- PlantUML

## Estrutura de pastas

```text
PBE_26.1_8002_I/
├── .github/workflows/   # automações e publicação
├── docs/                # documentação fonte do projeto
│   ├── Iniciacao/
│   ├── Elaboracao/
│   ├── Construcao/
│   ├── Transicao/
│   ├── assets/          # imagens e arquivos de apoio
│   └── css/             # estilos extras do MkDocs
├── site/                # saída gerada do build do MkDocs
├── mkdocs.yml           # configuração da documentação
├── requirements.txt     # dependências Python
└── README.md
```

## Instalação local — Documentação (MkDocs)

```bash
git clone https://github.com/Projetos-de-Extensao/PBE_26.1_8002_I.git
cd PBE_26.1_8002_I
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

Acesse a documentação local em `http://127.0.0.1:8000`.

---

## Instalação local — Back-end Django/DRF

### Pré-requisitos

- Python 3.9+

### Passos

```bash
# 1. Clone e entre na pasta
git clone https://github.com/Projetos-de-Extensao/PBE_26.1_8002_I.git
cd PBE_26.1_8002_I

# 2. Crie e ative o virtualenv
python3 -m venv .venv
source .venv/bin/activate          # Linux/macOS
# .venv\Scripts\activate           # Windows

# 3. Instale as dependências Django
pip install -r djangotutorial/requirements.txt

# 4. Aplique as migrações
cd djangotutorial
python manage.py migrate

# 5. Crie um superusuário para o admin
python manage.py createsuperuser

# 6. (Opcional) Popule o banco com dados de exemplo
python populate_db.py

# 7. Suba o servidor
python manage.py runserver
```

- Admin Django: `http://127.0.0.1:8000/admin/`
- API Browsable: `http://127.0.0.1:8000/api/`

### Endpoints de autenticação

| Método | URL | Descrição |
|--------|-----|-----------|
| POST | `/api/auth/register/` | Cria aluno ou coordenador, retorna token |
| POST | `/api/auth/login/` | Autentica e retorna token |
| POST | `/api/auth/logout/` | Invalida o token (requer `Authorization: Token <token>`) |

Exemplo de registro:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"tipo":"aluno","username":"teste","password":"senha123","nome":"Teste","email_institucional":"teste@ibmec.edu.br","matricula":"2024001","cpf":"000.000.000-00","rg":"0000000"}'
```

---

## Configurar login Microsoft (OAuth)

O sistema já tem a carcaça do OAuth Microsoft instalada (via `django-allauth`).
Para ativá-la, você precisa de um **App Registration** no Azure Active Directory.

### 1. Criar o App Registration

1. Acesse [portal.azure.com](https://portal.azure.com) e faça login com sua conta institucional.
2. Vá em **Azure Active Directory → App registrations → New registration**.
3. Nome: `IBMEC Estágios` (ou outro de sua escolha).
4. Tipos de conta suportados: *Accounts in this organizational directory only* (ou *Any Azure AD directory* para multi-tenant).
5. Redirect URI: `http://127.0.0.1:8000/accounts/microsoft/login/callback/` (tipo Web).
6. Clique em **Register**.

### 2. Obter as credenciais

- **Client ID**: na página do app, campo *Application (client) ID*.
- **Tenant ID**: campo *Directory (tenant) ID*.
- **Client Secret**: vá em *Certificates & secrets → New client secret*, copie o valor gerado.

### 3. Configurar o .env

```bash
cp .env.example .env
# Edite .env com os valores obtidos acima
```

```env
MICROSOFT_CLIENT_ID=seu-client-id-aqui
MICROSOFT_CLIENT_SECRET=seu-client-secret-aqui
MICROSOFT_TENANT_ID=seu-tenant-id-aqui
```

O servidor Django lê essas variáveis automaticamente via `os.getenv()`.
**Sem elas o app continua funcionando** — só o botão "Entrar com Microsoft" ficará sem efeito.
