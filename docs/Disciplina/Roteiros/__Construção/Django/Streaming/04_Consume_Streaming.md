# 04 - **Consume API**

## Introdução

- Para acessar a API criada no Django REST framework, siga os passos abaixo. A API está acessível através de rotas prefixadas por `api/` conforme configurado no arquivo `urls.py`. Você pode testar a API usando ferramentas como **Postman**, **Insomnia**, ou até mesmo **cURL** no terminal.

### 1. **URLs Principais da API**

Com base na configuração do roteamento, as URLs disponíveis são:

- **Listar todos os conteúdos**: `GET /api/contents/`
- **Criar um novo conteúdo**: `POST /api/contents/` 
- **Ver detalhes de um conteúdo específico**: `GET /api/contents/<id>/`
- **Atualizar um conteúdo**: `PUT /api/contents/<id>/` (Requer autenticação)
- **Deletar um conteúdo**: `DELETE /api/contents/<id>/` 

### 2. **Acessando via Navegador**

Se você estiver rodando o servidor de desenvolvimento do Django localmente, use o comando:

```bash
python manage.py runserver
```

Agora, você pode acessar a API via navegador (ou Postman) em:

- **[Listar](http://127.0.0.1:8000/api/contents/)** — para listar todos os conteúdos.

O Django REST framework oferece uma interface de navegação de API embutida. Se você acessar a API pelo navegador, verá uma interface amigável onde pode visualizar, criar, editar e excluir registros.

### 3. **Exemplos de Requisições**

#### a) **GET - Listar todos os conteúdos**

Você pode listar todos os conteúdos disponíveis com a seguinte requisição:

**Com cURL**:

```bash
curl -X GET http://127.0.0.1:8000/api/contents/
```

#### b) **POST - Criar um novo conteúdo**

Para criar um novo conteúdo, você precisa estar autenticado e fornecer os dados adequados:

**No Postman**:

1. Defina o método como `POST`.
2. No campo URL, insira `http://127.0.0.1:8000/api/contents/`.
3. Vá até a aba "Body" e selecione `raw` com o tipo `JSON`, e insira algo como:

   ```json
   {
       "title": "My Video",
       "description": "A video description",
       "file_url": "http://example.com/video.mp4",
       "thumbnail_url": "http://example.com/thumbnail.jpg",
       "content_type": "video",
       "is_public": true
   }
   ```

4. Envie a requisição.

#### c) **PUT - Atualizar um conteúdo**

**Com cURL**:

```bash
curl -X PUT http://127.0.0.1:8000/api/contents/<id>/ \
  -H "Content-Type: application/json" \
  -d '{
        "title": "Updated Video Title",
        "description": "Updated description"
      }'
```

#### d) **DELETE - Remover um conteúdo**

Para deletar um conteúdo:

**Com cURL**:

```bash
curl -X DELETE http://127.0.0.1:8000/api/contents/<id>/
```

### Resumo

1. Acesse a API via `http://127.0.0.1:8000/api/contents/`.
2. Use ferramentas como Postman ou cURL para testar os endpoints.
3. Adicione filtros ou funcionalidades adicionais conforme necessário.

Assim, a API está configurada e pronta para ser consumida por frontends, aplicativos móveis ou outras aplicações REST.
