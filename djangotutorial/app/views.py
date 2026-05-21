from rest_framework import viewsets, status
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
    SolicitacaoEstagioSerializer, TermoCompromissoSerializer,
    ApoliceSeguroSerializer, RelatorioEstagioSerializer, AssinaturaDigitalSerializer,
)


# ── ViewSets CRUD ────────────────────────────────────────────────────────────

class CursoViewSet(viewsets.ModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return Curso.objects.all()
        try:
            coordenador = user.coordenador
            return Curso.objects.filter(coordenador=coordenador)
        except Exception:
            pass
        return Curso.objects.all()


class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer


class AlunoViewSet(viewsets.ModelViewSet):
    queryset = Aluno.objects.all()
    serializer_class = AlunoSerializer


class CoordenadorViewSet(viewsets.ModelViewSet):
    queryset = Coordenador.objects.all()
    serializer_class = CoordenadorSerializer


class SolicitacaoEstagioViewSet(viewsets.ModelViewSet):
    queryset = SolicitacaoEstagio.objects.all()
    serializer_class = SolicitacaoEstagioSerializer


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


# ── Auth manual (AllowAny explícito — sem token para acessar) ────────────────

class RegisterView(APIView):
    """
    Cria um Usuario e o perfil vinculado (Aluno ou Coordenador).
    Corpo: { "tipo": "aluno"|"coordenador", "username": ..., "password": ..., ...campos do perfil }
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
                Coordenador.objects.create(
                    usuario=user,
                    departamento=data.get('departamento', ''),
                )
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
