from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db.models import Q

from .models import (
    Usuario, Curso, Empresa, Aluno, Coordenador, SolicitacaoEstagio,
)
from .serializers import (
    UsuarioSerializer, CursoSerializer, EmpresaSerializer,
    AlunoSerializer, CoordenadorSerializer, PerfilAlunoSerializer,
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
    """
    Lista de empresas com filtros (Pessoa 3):
      - ?aprovada=true|false  → filtra por aprovada_ibmec
      - ?busca=tech           → busca parcial em razão social e áreas de atuação

    CNPJ e aprovada_ibmec são protegidos no update (ver EmpresaSerializer).

    PENDENTE (bloqueado pelo models.py): os endpoints de self-service da
    empresa — `meu_perfil` e `meus_processos` — dependem de um vínculo
    Empresa.usuario (OneToOne) e do tipo 'empresa' em Usuario.tipo, que ainda
    não existem no models.py. Quando o dono do models adicionar o vínculo,
    ativar o esqueleto abaixo (análogo ao AlunoViewSet):

        @action(detail=False, methods=['get', 'put', 'patch'], url_path='meu_perfil')
        def meu_perfil(self, request):
            empresa = get_empresa(request.user)   # helper a criar em permissions.py
            ...

        @action(detail=False, methods=['get'], url_path='meus_processos')
        def meus_processos(self, request):
            empresa = get_empresa(request.user)
            return Response(
                SolicitacaoEstagioSerializer(empresa.solicitacoes.all(), many=True).data
            )
    """
    serializer_class = EmpresaSerializer

    def get_queryset(self):
        qs = Empresa.objects.all()

        aprovada = self.request.query_params.get('aprovada')
        if aprovada is not None:
            qs = qs.filter(aprovada_ibmec=aprovada.lower() in ('true', '1', 'sim'))

        busca = self.request.query_params.get('busca')
        if busca:
            qs = qs.filter(
                Q(razao_social__icontains=busca) | Q(areas_atuacao__icontains=busca)
            )

        return qs


class AlunoViewSet(viewsets.ModelViewSet):
    """
    Isolamento de dados (Pessoa 3):
      - admin        → todos os alunos
      - coordenador  → apenas alunos dos seus cursos
      - aluno        → apenas ele mesmo
      - outros       → vazio (negação por padrão)
    """
    serializer_class = AlunoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        base = Aluno.objects.select_related('usuario', 'curso')
        user = self.request.user

        if is_admin(user):
            return base.all()

        coordenador = get_coordenador(user)
        if coordenador is not None:
            return base.filter(curso__coordenador=coordenador)

        aluno = get_aluno(user)
        if aluno is not None:
            return base.filter(pk=aluno.pk)

        return Aluno.objects.none()

    @action(detail=False, methods=['get', 'put', 'patch'], url_path='meu_perfil')
    def meu_perfil(self, request):
        """
        Perfil do aluno autenticado.
          GET            → dados do próprio aluno
          PUT / PATCH    → atualiza dados editáveis (CPF é imutável)
        """
        aluno = get_aluno(request.user)
        if aluno is None:
            raise PermissionDenied('Apenas alunos possuem perfil de aluno.')

        if request.method == 'GET':
            return Response(PerfilAlunoSerializer(aluno).data)

        serializer = PerfilAlunoSerializer(
            aluno, data=request.data, partial=(request.method == 'PATCH'),
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='meus_processos')
    def meus_processos(self, request):
        """
        Solicitações de estágio do aluno autenticado.
        Filtro opcional: ?status=PENDENTE (qualquer valor de SolicitacaoEstagio.Status).
        """
        aluno = get_aluno(request.user)
        if aluno is None:
            raise PermissionDenied('Apenas alunos possuem processos de estágio.')

        qs = aluno.solicitacoes.select_related('empresa', 'coordenador').all()

        status_filtro = request.query_params.get('status')
        if status_filtro:
            valores_validos = SolicitacaoEstagio.Status.values
            if status_filtro not in valores_validos:
                return Response(
                    {'status': f'Status inválido. Opções: {", ".join(valores_validos)}'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            qs = qs.filter(status=status_filtro)

        return Response(SolicitacaoEstagioSerializer(qs, many=True).data)


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
