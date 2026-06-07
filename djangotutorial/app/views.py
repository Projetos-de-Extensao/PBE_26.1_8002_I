from rest_framework import viewsets, status as drf_status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .models import (
    Usuario, Curso, EmpresaConcedente, Aluno, Coordenador,
    SupervisorEmpresa, ProcessoEstagio, DocumentoProcesso,
)
from .serializers import (
    UsuarioSerializer, CursoSerializer, EmpresaConcedenteSerializer,
    AlunoSerializer, CoordenadorSerializer, SupervisorEmpresaSerializer,
    DocumentoProcessoSerializer,
    ProcessoEstagioSerializer, CriarProcessoSerializer, AlterarStatusSerializer,
)
from .permissions import (
    get_aluno, get_coordenador, get_supervisor, is_admin,
    IsAluno, IsCoordenador, IsSupervisorEmpresa, IsAdminOrReadOnly, IsDonoDoProcesso,
)
from .state_machine import (
    transicoes_validas,
    RASCUNHO, PENDENTE, APROVADO, REJEITADO,
    CORRECAO_SOLICITADA, ATIVO, ENCERRADO, CANCELADO,
)


# ── CRUDs ─────────────────────────────────────────────────────────────────────

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
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAuthenticated(), IsAdminOrReadOnly()]
        return [IsAuthenticated()]


class EmpresaConcedenteViewSet(viewsets.ModelViewSet):
    serializer_class = EmpresaConcedenteSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        qs = EmpresaConcedente.objects.all()
        aprovada = self.request.query_params.get('aprovada')
        if aprovada is not None:
            qs = qs.filter(aprovada_ibmec=aprovada.lower() in ('true', '1'))
        busca = self.request.query_params.get('busca')
        if busca:
            qs = qs.filter(razao_social__icontains=busca)
        return qs


class AlunoViewSet(viewsets.ModelViewSet):
    serializer_class = AlunoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base = Aluno.objects.select_related('usuario', 'curso')
        if is_admin(user):
            return base.all()
        aluno = get_aluno(user)
        if aluno is not None:
            return base.filter(pk=aluno.pk)
        coord = get_coordenador(user)
        if coord is not None:
            return base.filter(curso__coordenador=coord)
        return base.none()


class CoordenadorViewSet(viewsets.ModelViewSet):
    serializer_class = CoordenadorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base = Coordenador.objects.select_related('usuario')
        if is_admin(user):
            return base.all()
        coord = get_coordenador(user)
        if coord is not None:
            return base.filter(pk=coord.pk)
        return base.none()


class SupervisorEmpresaViewSet(viewsets.ModelViewSet):
    serializer_class = SupervisorEmpresaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base = SupervisorEmpresa.objects.select_related('usuario', 'empresa')
        if is_admin(user):
            return base.all()
        supervisor = get_supervisor(user)
        if supervisor is not None:
            return base.filter(pk=supervisor.pk)
        return base.none()


class DocumentoProcessoViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentoProcessoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base = DocumentoProcesso.objects.select_related(
            'processo__aluno', 'processo__empresa',
        )
        if is_admin(user):
            return base.all()
        aluno = get_aluno(user)
        if aluno is not None:
            return base.filter(processo__aluno=aluno)
        supervisor = get_supervisor(user)
        if supervisor is not None:
            return base.filter(processo__empresa=supervisor.empresa)
        coord = get_coordenador(user)
        if coord is not None:
            return base.filter(processo__aluno__curso__coordenador=coord)
        return base.none()

    def perform_create(self, serializer):
        serializer.save(enviado_por=self.request.user)


# ── CORE da issue #46: ProcessoEstagio ────────────────────────────────────────

class ProcessoEstagioViewSet(viewsets.ModelViewSet):
    """
    Aluno: cria e cancela; vê só os próprios processos.
    Coordenador: aprova/rejeita/encerra processos de alunos dos cursos que coordena.
    Supervisor da empresa: vê processos vinculados à sua empresa.
    Admin: acesso total.
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CriarProcessoSerializer
        if self.action == 'alterar_status':
            return AlterarStatusSerializer
        return ProcessoEstagioSerializer

    def get_queryset(self):
        user = self.request.user
        base = ProcessoEstagio.objects.select_related(
            'aluno__usuario', 'aluno__curso',
            'empresa', 'coordenador__usuario', 'supervisor',
        )
        if is_admin(user):
            return base.all()
        aluno = get_aluno(user)
        if aluno is not None:
            return base.filter(aluno=aluno)
        supervisor = get_supervisor(user)
        if supervisor is not None:
            return base.filter(empresa=supervisor.empresa)
        coord = get_coordenador(user)
        if coord is not None:
            return base.filter(aluno__curso__coordenador=coord)
        return ProcessoEstagio.objects.none()

    def perform_create(self, serializer):
        aluno = get_aluno(self.request.user)
        if aluno is None:
            raise PermissionDenied('Apenas alunos podem criar processos de estágio.')
        coordenador = (
            aluno.curso.coordenador
            if aluno.curso and aluno.curso.coordenador_id
            else None
        )
        serializer.save(
            aluno=aluno,
            status=ProcessoEstagio.Status.PENDENTE,
            coordenador=coordenador,
        )

    @action(detail=True, methods=['post'], url_path='alterar_status')
    def alterar_status(self, request, pk=None):
        processo = self.get_object()
        novo_status = request.data.get('status')

        if not novo_status:
            return Response(
                {'status': 'Campo "status" é obrigatório.'},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        # 1. Transição válida pelo mapa de estados?
        validas = transicoes_validas(processo.status)
        if novo_status not in validas:
            return Response({
                'status': f'Transição inválida: {processo.status} → {novo_status}.',
                'estado_atual': processo.status,
                'transicoes_validas': sorted(validas) if validas else [],
            }, status=drf_status.HTTP_400_BAD_REQUEST)

        # 2. Permissão por papel
        user = request.user
        if not is_admin(user):
            aluno = get_aluno(user)
            coord = get_coordenador(user)

            if aluno is not None:
                if aluno.pk != processo.aluno_id:
                    return Response(
                        {'detail': 'Sem permissão neste processo.'},
                        status=drf_status.HTTP_403_FORBIDDEN,
                    )
                permitido = (
                    (processo.status == RASCUNHO and novo_status == PENDENTE)
                    or novo_status == CANCELADO
                )
                if not permitido:
                    return Response(
                        {'detail': 'Ação não permitida para aluno neste contexto.'},
                        status=drf_status.HTTP_403_FORBIDDEN,
                    )
            elif coord is not None:
                curso = getattr(processo.aluno, 'curso', None)
                if curso is None or curso.coordenador_id != coord.pk:
                    return Response(
                        {'detail': 'Processo não pertence a curso sob sua coordenação.'},
                        status=drf_status.HTTP_403_FORBIDDEN,
                    )
                permitidas_coord = {APROVADO, REJEITADO, CORRECAO_SOLICITADA, ATIVO, ENCERRADO}
                if novo_status not in permitidas_coord:
                    return Response(
                        {'detail': 'Ação não permitida para coordenador.'},
                        status=drf_status.HTTP_403_FORBIDDEN,
                    )
            else:
                return Response(
                    {'detail': 'Sem permissão.'},
                    status=drf_status.HTTP_403_FORBIDDEN,
                )

        # 3. Validar via serializer (RN11) e persistir
        serializer = AlterarStatusSerializer(processo, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # 4. Retorna o processo full atualizado
        processo.refresh_from_db()
        return Response(ProcessoEstagioSerializer(processo).data)

    @action(detail=True, methods=['get'])
    def documentos(self, request, pk=None):
        processo = self.get_object()
        docs = processo.documentos.all().order_by('-data_upload')
        serializer = DocumentoProcessoSerializer(docs, many=True)
        return Response(serializer.data)


# ── Auth ──────────────────────────────────────────────────────────────────────

class RegisterView(APIView):
    """
    Cria Usuario + perfil vinculado conforme `tipo`.

    Body comum: tipo, username, password, nome, email_institucional

    Campos extras por tipo:
      aluno:              cpf (obrig.), rg, coeficiente_rendimento, curso_id, matriculado_estagio
      coordenador:        departamento (obrig.)
      supervisor_empresa: empresa_id (obrig.), cargo
    """
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        tipo = data.get('tipo', '').lower()
        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            return Response(
                {'erro': 'username e password são obrigatórios.'},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        if tipo == 'aluno':
            try:
                user = Usuario.objects.create_user(
                    username=username, password=password, tipo='aluno',
                    nome=data.get('nome', ''),
                    email_institucional=data.get('email_institucional', ''),
                )
                Aluno.objects.create(
                    usuario=user,
                    cpf=data.get('cpf', ''),
                    rg=data.get('rg', ''),
                    coeficiente_rendimento=data.get('coeficiente_rendimento', 0),
                    curso_id=data.get('curso_id'),
                    matriculado_estagio=bool(data.get('matriculado_estagio', False)),
                )
            except Exception as e:
                return Response({'erro': str(e)}, status=drf_status.HTTP_400_BAD_REQUEST)

        elif tipo == 'coordenador':
            departamento = (data.get('departamento') or '').strip()
            if not departamento:
                return Response(
                    {'erro': 'campo "departamento" é obrigatório para coordenador.'},
                    status=drf_status.HTTP_400_BAD_REQUEST,
                )
            try:
                user = Usuario.objects.create_user(
                    username=username, password=password, tipo='coordenador',
                    nome=data.get('nome', ''),
                    email_institucional=data.get('email_institucional', ''),
                )
                Coordenador.objects.create(usuario=user, departamento=departamento)
            except Exception as e:
                return Response({'erro': str(e)}, status=drf_status.HTTP_400_BAD_REQUEST)

        elif tipo == 'supervisor_empresa':
            empresa_id = data.get('empresa_id')
            if not empresa_id:
                return Response(
                    {'erro': 'campo "empresa_id" é obrigatório para supervisor_empresa.'},
                    status=drf_status.HTTP_400_BAD_REQUEST,
                )
            try:
                empresa = EmpresaConcedente.objects.get(pk=empresa_id)
            except EmpresaConcedente.DoesNotExist:
                return Response(
                    {'erro': 'EmpresaConcedente não encontrada.'},
                    status=drf_status.HTTP_400_BAD_REQUEST,
                )
            try:
                user = Usuario.objects.create_user(
                    username=username, password=password, tipo='supervisor_empresa',
                    nome=data.get('nome', ''),
                    email_institucional=data.get('email_institucional', ''),
                )
                SupervisorEmpresa.objects.create(
                    usuario=user, empresa=empresa,
                    cargo=data.get('cargo', ''),
                )
            except Exception as e:
                return Response({'erro': str(e)}, status=drf_status.HTTP_400_BAD_REQUEST)

        else:
            return Response(
                {'erro': 'tipo deve ser "aluno", "coordenador" ou "supervisor_empresa".'},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {'token': token.key, 'id': user.pk, 'tipo': tipo},
            status=drf_status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Autentica username/password e retorna token DRF + dados básicos do usuário."""
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '')
        password = request.data.get('password', '')
        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {'erro': 'Credenciais inválidas.'},
                status=drf_status.HTTP_401_UNAUTHORIZED,
            )
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'id': user.pk,
            'tipo': user.tipo,
            'nome': user.nome,
        })


class LogoutView(APIView):
    """Invalida o token do usuário autenticado."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
        except Exception:
            pass
        return Response({'mensagem': 'Logout realizado com sucesso.'})
