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
    TermoCompromisso, ApoliceSeguro, RelatorioEstagio, AssinaturaDigital,
)
from .serializers import (
    UsuarioSerializer, CursoSerializer, EmpresaSerializer,
    AlunoSerializer, CoordenadorSerializer,
    SolicitacaoEstagioSerializer, CriarSolicitacaoSerializer,
    AlterarStatusSerializer, TermoCompromissoSerializer,
    ApoliceSeguroSerializer, RelatorioEstagioSerializer, AssinaturaDigitalSerializer,
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
        # Escrita só para admin ou coordenador do curso
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
    """
    RBAC aplicado em duas camadas:
      1. has_permission  → bloqueia ações inteiras por papel (SolicitacaoEstagioPermission)
      2. get_queryset    → filtra queryset por papel (negação por padrão: .none())
      3. has_object_perm → valida ownership no detalhe/update/delete
    """
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
            # Aluno vê apenas as próprias solicitações
            return SolicitacaoEstagio.objects.filter(aluno=aluno).select_related(
                'aluno__usuario', 'empresa',
            )

        coordenador = get_coordenador(user)
        if coordenador is not None:
            # Coordenador vê apenas solicitações de alunos do seu curso
            return SolicitacaoEstagio.objects.filter(
                aluno__curso__coordenador=coordenador,
            ).select_related('aluno__usuario', 'aluno__curso', 'empresa')

        # Nenhum perfil reconhecido → retorna vazio (negação por padrão)
        return SolicitacaoEstagio.objects.none()

    def perform_create(self, serializer):
        aluno = get_aluno(self.request.user)
        if aluno is None:
            raise PermissionDenied('Apenas alunos podem criar solicitações de estágio.')
        # Força aluno = usuário autenticado e status inicial = PENDENTE
        serializer.save(aluno=aluno, status=SolicitacaoEstagio.Status.PENDENTE)

    @action(detail=True, methods=['post'], url_path='alterar-status')
    def alterar_status(self, request, pk=None):
        """
        Endpoint exclusivo para coordenador alterar o status de uma solicitação.

        POST /api/solicitacoes-estagio/{id}/alterar-status/
        Body: { "status": "APROVADO" }
              { "status": "REJEITADO", "justificativa_rejeicao": "..." }
        """
        solicitacao = self.get_object()  # aciona has_object_permission
        serializer = AlterarStatusSerializer(
            solicitacao, data=request.data, partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# ── ViewSets de documentos ────────────────────────────────────────────────────

class TermoCompromissoViewSet(viewsets.ModelViewSet):
    queryset = TermoCompromisso.objects.all()
    serializer_class = TermoCompromissoSerializer


class ApoliceSeguroViewSet(viewsets.ModelViewSet):
    queryset = ApoliceSeguro.objects.all()
    serializer_class = ApoliceSeguroSerializer


class RelatorioEstagioViewSet(viewsets.ModelViewSet):
    queryset = RelatorioEstagio.objects.all()
    serializer_class = RelatorioEstagioSerializer


class AssinaturaDigitalViewSet(viewsets.ModelViewSet):
    queryset = AssinaturaDigital.objects.all()
    serializer_class = AssinaturaDigitalSerializer


# ── Auth manual ───────────────────────────────────────────────────────────────

class RegisterView(APIView):
    """
    Cria um Usuario e o perfil vinculado (Aluno ou Coordenador).
    Corpo: { "tipo": "aluno"|"coordenador", "username": ..., "password": ..., ...campos }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        tipo = data.get('tipo', '').lower()
        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            return Response(
                {'erro': 'username e password são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if tipo == 'aluno':
            try:
                user = Usuario.objects.create_user(
                    username=username,
                    password=password,
                    tipo='aluno',
                    nome=data.get('nome', ''),
                    email_institucional=data.get('email_institucional', ''),
                )
                Aluno.objects.create(
                    usuario=user,
                    cpf=data.get('cpf', ''),
                    rg=data.get('rg', ''),
                    coeficiente_rendimento=data.get('coeficiente_rendimento', 0),
                    curso_id=data.get('curso_id'),
                )
            except Exception as e:
                return Response({'erro': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        elif tipo == 'coordenador':
            try:
                user = Usuario.objects.create_user(
                    username=username,
                    password=password,
                    tipo='coordenador',
                    nome=data.get('nome', ''),
                    email_institucional=data.get('email_institucional', ''),
                )
                # Nota: campo 'departamento' removido do model atual;
                # criar perfil sem ele.
                Coordenador.objects.create(usuario=user)
            except Exception as e:
                return Response({'erro': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(
                {'erro': 'tipo deve ser "aluno" ou "coordenador"'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {'token': token.key, 'id': user.pk, 'tipo': tipo},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    Autentica username/senha e retorna token DRF.
    Corpo: { "username": ..., "password": ... }
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
        return Response({'token': token.key})


class LogoutView(APIView):
    """
    Invalida o token do usuário autenticado.
    Header: Authorization: Token <token>
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response({'mensagem': 'Logout realizado com sucesso'})
