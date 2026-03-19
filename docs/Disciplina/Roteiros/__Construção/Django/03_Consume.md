# Acessando a API do Django REST Framework

Para acessar sua API usando os endpoints do DRF e o Postman, siga estes passos:

## Endpoints Disponíveis

Considerando a estrutura proposta anteriormente, seus endpoints principais serão:

- `GET /api/produtos/` - Lista todos os produtos
- `POST /api/produtos/` - Cria um novo produto
- `GET /api/produtos/<id>/` - Detalhes de um produto específico
- `PUT /api/produtos/<id>/` - Atualiza um produto
- `PATCH /api/produtos/<id>/` - Atualização parcial de um produto
- `DELETE /api/produtos/<id>/` - Remove um produto
- `GET /api/produtos/disponiveis/` - Lista produtos disponíveis
- `GET /api/produtos/baratos/` - Lista produtos com preço < 1000

### Acessando via Navegador (DRF UI)

1.Execute o servidor de desenvolvimento:

```bash
   python manage.py runserver
```

2.Acesse os endpoints no navegador:

- [http://localhost:8000/api/produtos/](http://localhost:8000/api/produtos/)]
- [http://localhost:8000/api/produtos/1/](http://localhost:8000/api/produtos/1/)
- [http://localhost:8000/api/produtos/disponiveis/](http://localhost:8000/api/produtos/disponiveis/)

3.A interface web do DRF permitirá:

- Visualização dos dados em formato navegável
- Teste de métodos GET diretamente
- Formulário para testar POST, PUT, PATCH e DELETE

### Acessando via Postman

#### 1. Configurando o Postman

- Abra o Postman
- Crie uma nova coleção (opcional, mas recomendado)
- Configure o ambiente (opcional) com variável `base_url` = `http://localhost:8000/api`

#### 2. Exemplos de Requisições

##### GET - Listar todos os produtos

- **Método**: GET
- **URL**: `{{base_url}}/produtos/`
- **Headers**:
  - `Content-Type: application/json`
- **Body**: Nenhum

##### POST - Criar novo produto

- **Método**: POST
- **URL**: `{{base_url}}/produtos/`
- **Headers**:
  - `Content-Type: application/json`
- **Body** (raw, JSON):

```json
  {
      "nome": "Novo Produto",
      "preco": 99.90,
      "descricao": "Descrição do novo produto",
      "disponivel": true
  }
```

##### GET - Detalhes de um produto específico

- **Método**: GET
- **URL**: `{{base_url}}/produtos/1/` (onde 1 é o ID do produto)
- **Headers**:
  - `Content-Type: application/json`
- **Body**: Nenhum

##### PUT - Atualizar um produto completo

- **Método**: PUT
- **URL**: `{{base_url}}/produtos/1/`
- **Headers**:
  - `Content-Type: application/json`
- **Body** (raw, JSON):

```json
  {
      "nome": "Produto Atualizado",
      "preco": 129.90,
      "descricao": "Nova descrição",
      "disponivel": false
  }
```

##### PATCH - Atualização parcial

- **Método**: PATCH
- **URL**: `{{base_url}}/produtos/1/`
- **Headers**:
  - `Content-Type: application/json`
- **Body** (raw, JSON):

```json
  {
      "preco": 149.90
  }
```

##### DELETE - Remover um produto

- **Método**: DELETE
- **URL**: `{{base_url}}/produtos/1/`
- **Headers**:
  - `Content-Type: application/json`
- **Body**: Nenhum

##### GET - Produtos disponíveis

- **Método**: GET
- **URL**: `{{base_url}}/produtos/disponiveis/`
- **Headers**:
  - `Content-Type: application/json`
- **Body**: Nenhum

##### GET - Produtos baratos

- **Método**: GET
- **URL**: `{{base_url}}/produtos/baratos/`
- **Headers**:
  - `Content-Type: application/json`
- **Body**: Nenhum

#### 3. Dicas para Uso no Postman

- **Salve as requisições**: Crie uma coleção para seu projeto e salve cada endpoint como uma requisição diferente

- **Use variáveis de ambiente**: Configure variáveis como `base_url` para facilitar a mudança entre ambientes

- **Teste os status codes**:
  - 200 OK para GET bem-sucedido
  - 201 Created para POST bem-sucedido
  - 400 Bad Request para dados inválidos
  - 404 Not Found para recursos não existentes

- **Exporte a coleção**: Você pode exportar como JSON e compartilhar com sua equipe

### Solução de Problemas Comuns

#### 1. Erro 403 Forbidden

- **Causa**: Permissões ainda estão ativas
- **Solução**: Verifique `DEFAULT_PERMISSION_CLASSES` no `settings.py` e defina como `AllowAny`

#### 2. Erro 415 Unsupported Media Type

- **Causa**: Header `Content-Type` incorreto
- **Solução**: Sempre inclua `Content-Type: application/json`

#### 3. Dados não aparecem após POST

- **Causa**: Pode ser um problema com o banco de dados em memória durante testes
- **Solução**: Verifique se você está usando `python manage.py runserver` e não fechou o terminal

#### 4. Campos obrigatórios faltando

- **Causa**: Campos required no serializer não foram fornecidos
- **Solução**: Verifique a resposta de erro para ver quais campos são obrigatórios

## Exemplo Completo de Requisição no Postman

- **Configuração inicial**:
  - Abra o Postman
  - Clique em "New Request"
  - Selecione o método HTTP desejado (GET, POST, etc)
  - Digite a URL: `http://localhost:8000/api/produtos/`

- **Para POST/PUT/PATCH**:
  - Vá para a aba "Body"
  - Selecione "raw"
  - Escolha "JSON" no dropdown
  - Cole o JSON com os dados

- **Enviando a requisição**:
  - Clique em "Send"
  - Verifique o status code na resposta
  - Visualize os dados retornados na aba "Body" da resposta

Com esses passos, você poderá testar completamente sua API Django REST Framework tanto pelo navegador (usando a interface web do DRF) quanto pelo Postman, sem a necessidade de configurar autenticação.
