from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .models import (
    Usuario, Curso, Empresa, Aluno, Coordenador, SolicitacaoEstagio,
)
from .serializers import (
    UsuarioSerializer, CursoSerializer, EmpresaSerializer,
    AlunoSerializer, CoordenadorSerializer,
    SolicitacaoEstagioSerializer, CriarSolicitacaoSerializer,
    AlterarStatusSerializer,
)
from .permissions import (
    SolicitacaoEstagioPermission, get_aluno, get_coordenador, is_admin,
)


# ── ViewSets de entidades secundárias ─────────────────────────────────────────

class CursoViewSet(viewsets.ModelViewSet):
    serializer_class = CursoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if is_admin(user):
            return Curso.objects.all()
        coordenador = get_coordenador(user)
        if coordenador is not None:
            return Curso.objects.filter(coordenador=coordenador)
        return Curso.objects.all()

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'destroy'):
            from rest_framework.permissions import BasePermission

            class _SoCoordenadorOuAdmin(BasePermission):
                def has_object_permission(self_, request, view, obj):
                    if is_admin(request.user):
                        return True
                    coord = get_coordenador(request.user)
                    return coord is not None and obj.coordenador_id == coord.pk

            return [IsAuthenticated(), _SoCoordenadorOuAdmin()]
        return [IsAuthenticated()]


class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer


class AlunoViewSet(viewsets.ModelViewSet):
    queryset = Aluno.objects.select_related('usuario', 'curso').all()
    serializer_class = AlunoSerializer


class CoordenadorViewSet(viewsets.ModelViewSet):
    queryset = Coordenador.objects.select_related('usuario').all()
    serializer_class = CoordenadorSerializer


# ── SolicitacaoEstagio — ViewSet com RBAC completo ────────────────────────────

class SolicitacaoEstagioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, SolicitacaoEstagioPermission]

    def get_serializer_class(self):
        user = self.request.user
        if is_admin(user):
            return SolicitacaoEstagioSerializer
        if self.action == 'create' and get_aluno(user) is not None:
            return CriarSolicitacaoSerializer
        if self.action == 'alterar_status' and get_coordenador(user) is not None:
            return AlterarStatusSerializer
        return SolicitacaoEstagioSerializer

    def get_queryset(self):
        user = self.request.user
        if is_admin(user):
            return SolicitacaoEstagio.objects.select_related(
                'aluno__usuario', 'aluno__curso__coordenador__usuario', 'empresa',
            ).all()

        aluno = get_aluno(user)
        if aluno is not None:
            return SolicitacaoEstagio.objects.filter(aluno=aluno).select_related(
                'aluno__usuario', 'empresa',
            )

        coordenador = get_coordenador(user)
        if coordenador is not None:
            return SolicitacaoEstagio.objects.filter(
                aluno__curso__coordenador=coordenador,
            ).select_related('aluno__usuario', 'aluno__curso', 'empresa')

        return SolicitacaoEstagio.objects.none()

    def perform_create(self, serializer):
        aluno = get_aluno(self.request.user)
        if aluno is None:
            raise PermissionDenied('Apenas alunos podem criar solicitações de estágio.')
        serializer.save(aluno=aluno, status=SolicitacaoEstagio.Status.PENDENTE)

    @action(detail=True, methods=['post'], url_path='alterar-status')
    def alterar_status(self, request, pk=None):
        solicitacao = self.get_object()
        serializer = AlterarStatusSerializer(
            solicitacao, data=request.data, partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ── Auth ──────────────────────────────────────────────────────────────────────

class RegisterView(APIView):
    """
    Registra um novo usuário e cria o perfil correspondente.

    Tipos aceitos: aluno, coordenador, empresa

    Corpo comum:
      { "tipo": "...", "username": "...", "password": "...", "nome": "..." }

    Campos extras por tipo:
      aluno:       cpf, curso_id (obrigatório), rg, coeficiente_rendimento
      coordenador: departamento
      empresa:     cnpj, razao_social, areas_atuacao, localizacao, email_contato

    Retorna:
      { "token": "...", "id": 1, "tipo": "..." }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        tipo = data.get('tipo', '').lower()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        nome = data.get('nome', '').strip()

        # ── Validações básicas ────────────────────────────────────────────────
        if not username or not password:
            return Response(
                {'erro': 'username e password são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(password) < 8:
            return Response(
                {'erro': 'Senha deve ter no mínimo 8 caracteres'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if tipo not in ('aluno', 'coordenador', 'empresa'):
            return Response(
                {'erro': 'tipo deve ser "aluno", "coordenador" ou "empresa"'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Registro por tipo ─────────────────────────────────────────────────
        user = None
        try:
            if tipo == 'aluno':
                curso_id = data.get('curso_id')
                if not curso_id:
                    return Response(
                        {'erro': 'curso_id é obrigatório para alunos'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if not Curso.objects.filter(pk=curso_id).exists():
                    return Response(
                        {'erro': 'Curso não encontrado'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                user = Usuario.objects.create_user(
                    username=username, password=password,
                    tipo='aluno', nome=nome,
                    email_institucional=data.get('email_institucional', ''),
                )
                Aluno.objects.create(
                    usuario=user,
                    cpf=data.get('cpf', ''),
                    rg=data.get('rg', ''),
                    coeficiente_rendimento=data.get('coeficiente_rendimento', 0),
                    curso_id=curso_id,
                )

            elif tipo == 'coordenador':
                user = Usuario.objects.create_user(
                    username=username, password=password,
                    tipo='coordenador', nome=nome,
                    email_institucional=data.get('email_institucional', ''),
                )
                Coordenador.objects.create(
                    usuario=user,
                    departamento=data.get('departamento', ''),
                )

            elif tipo == 'empresa':
                cnpj = data.get('cnpj', '').strip()
                razao_social = data.get('razao_social', '').strip()
                if not cnpj or not razao_social:
                    return Response(
                        {'erro': 'cnpj e razao_social são obrigatórios para empresas'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                user = Usuario.objects.create_user(
                    username=username, password=password,
                    tipo='empresa', nome=nome,
                    email_institucional=data.get('email_institucional', ''),
                )
                Empresa.objects.create(
                    cnpj=cnpj,
                    razao_social=razao_social,
                    areas_atuacao=data.get('areas_atuacao', ''),
                    localizacao=data.get('localizacao', ''),
                    email_contato=data.get('email_contato', ''),
                )

        except Exception as e:
            # Se o usuário foi criado mas o perfil falhou, desfaz
            if user is not None:
                user.delete()
            return Response({'erro': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {'token': token.key, 'id': user.pk, 'tipo': tipo},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    Autentica username/senha e retorna token + dados do usuário.

    Corpo:   { "username": "...", "password": "..." }
    Retorna: { "token": "...", "tipo": "...", "nome": "...", "id": 1 }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '')
        password = request.data.get('password', '')
        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {'erro': 'Credenciais inválidas'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'tipo': user.tipo,
            'nome': user.nome,
            'id': user.pk,
        })


class LogoutView(APIView):
    """
    Invalida o token do usuário autenticado.
    Header: Authorization: Token <token>
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({'mensagem': 'Logout realizado com sucesso'})
