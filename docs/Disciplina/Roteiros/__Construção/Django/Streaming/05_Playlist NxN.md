# 05 - Playlist -Relacionamento NxN

## Playlist

Para criar o modelo `Playlist` conforme a modelagem mencionada, ele deve ter relacionamentos com as classes `Content` e `User`. A `Playlist` representará uma coleção de conteúdos (áudios ou vídeos) que pertence a um usuário específico.

Abaixo está o código para definir o modelo `Playlist` no Django, assumindo que você já possui as classes `Content` e `User` configuradas.

### Modelo `Playlist`

```python
from django.db import models
from django.contrib.auth.models import User
from content_app.models import Content  # Assumindo que o modelo Content está no app 'content_app'

class Playlist(models.Model):
    title = models.CharField(max_length=255)  # Título da playlist
    description = models.TextField(blank=True, null=True)  # Descrição opcional da playlist
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')  # Proprietário da playlist
    contents = models.ManyToManyField(Content, related_name='playlists')  # Conteúdos incluídos na playlist
    created_at = models.DateTimeField(auto_now_add=True)  # Data de criação
    updated_at = models.DateTimeField(auto_now=True)  # Data de última atualização

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Playlist'
        verbose_name_plural = 'Playlists'

    def __str__(self):
        return self.title
```

### Explicação dos Campos

1. **`title`**: Nome da playlist.
2. **`description`**: Descrição opcional, para explicar o propósito da playlist ou a seleção de conteúdos.
3. **`user`**: Chave estrangeira que faz referência ao modelo `User`, representando o dono da playlist.
4. **`contents`**: Relacionamento `ManyToMany` com `Content`, permitindo que vários conteúdos sejam adicionados à playlist.
5. **`created_at`** e **`updated_at`**: Campos de data para registrar a criação e a última atualização da playlist.

---

Para tornar o modelo `Playlist` acessível via API REST no Django, vamos definir o **serializador**, as **views** e as **URLs** usando o Django REST Framework. Dessa forma, será possível criar, listar, atualizar e deletar playlists, além de adicionar ou remover conteúdos de uma playlist.

### 1. **Definindo o Serializador**

O serializador converte as instâncias do modelo `Playlist` para JSON e valida os dados recebidos.

Crie um arquivo `serializers.py` dentro do seu app, se ele ainda não existir.

#### `serializers.py`

```python
from rest_framework import serializers
from .models import Playlist
from content.models import Content

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ['id', 'title', 'file_url', 'thumbnail_url', 'content_type']

class PlaylistSerializer(serializers.ModelSerializer):
    contents = ContentSerializer(many=True, read_only=True)
    content_ids = serializers.PrimaryKeyRelatedField(
        queryset=Content.objects.all(), write_only=True, many=True, source='contents'
    )

    class Meta:
        model = Playlist
        fields = ['id', 'title', 'description', 'user', 'contents', 'content_ids', 'created_at']
        read_only_fields = ['user', 'created_at']

    def create(self, validated_data):
        content_data = validated_data.pop('contents', [])
        playlist = super().create(validated_data)
        playlist.contents.set(content_data)
        return playlist

    def update(self, instance, validated_data):
        content_data = validated_data.pop('contents', None)
        playlist = super().update(instance, validated_data)
        if content_data is not None:
            playlist.contents.set(content_data)
        return playlist
```

* **`contents`**: Serializa os conteúdos da playlist de forma detalhada.
* **`content_ids`**: Permite adicionar conteúdos à playlist usando IDs.
* **`user`**: É preenchido automaticamente na view com o usuário autenticado.

### 2. **Definindo as Views**

Vamos usar o **Django REST Framework ViewSets** para definir as operações de CRUD na `Playlist`.

Crie ou edite o arquivo `views.py` no seu app.

#### `views.py`

```python
from rest_framework import viewsets, permissions
from .models import Playlist
from .serializers import PlaylistSerializer

class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Permite que o usuário veja apenas suas próprias playlists
        return self.queryset.filter(user=self.request.user)
```

* **`perform_create`**: Define o usuário autenticado como proprietário da playlist.
* **`get_queryset`**: Filtra as playlists para mostrar apenas as pertencentes ao usuário autenticado.

### 3. **Definindo as URLs**

Crie ou edite o arquivo `urls.py` no seu app e configure as URLs para o endpoint `Playlist`.

#### `urls.py`

```python
#content_app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlaylistViewSet

router = DefaultRouter()
router.register(r'playlists', PlaylistViewSet, basename='playlist')

urlpatterns = [
    path('', include(router.urls)),
]
```

### 4. **Testando a API**

Com o Django REST Framework, você pode acessar e interagir com a API nos seguintes endpoints:

* `GET /api/playlists/` - Listar todas as playlists do usuário autenticado.
* `POST /api/playlists/` - Criar uma nova playlist (enviar `title`, `description` e `content_ids`).
* `GET /api/playlists/<id>/` - Obter detalhes de uma playlist específica.
* `PUT /api/playlists/<id>/` - Atualizar uma playlist existente (enviar `title`, `description`, e `content_ids`).
* `DELETE /api/playlists/<id>/` - Excluir uma playlist específica.


### 6. **Django Shell**

Com esse modelo, é possível realizar operações no Django Shell para criar playlists, adicionar conteúdos e verificar quais playlists pertencem a um usuário ou contêm um conteúdo específico.

```bash
python manage.py shell
```

```python
from content.models import Content
from myapp.models import Playlist  # Substitua 'myapp' pelo nome do seu app
from django.contrib.auth.models import User

# Criando um usuário para teste
user = User.objects.create(username="testuser")

# Criando alguns conteúdos
content1 = Content.objects.create(title="Video 1", file_url="https://example.com/video1.mp4")
content2 = Content.objects.create(title="Audio 1", file_url="https://example.com/audio1.mp3")

# Criando uma playlist e adicionando conteúdos
playlist = Playlist.objects.create(title="Minha Playlist", user=user)
playlist.contents.add(content1, content2)

# Verificando os conteúdos na playlist
for content in playlist.contents.all():
    print(content.title)
```

Com essa estrutura, você pode facilmente gerenciar playlists associadas a conteúdos e usuários.
