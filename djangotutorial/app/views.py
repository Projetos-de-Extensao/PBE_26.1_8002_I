from rest_framework import viewsets, status as drf_status, filters
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate

from .models import (
    Usuario, Curso, EmpresaConcedente, Aluno, Coordenador,
    SupervisorEmpresa, ProcessoEstagio, DocumentoProcesso, LogDocumento,
    ModeloFormulario, AvaliacaoEmpresa, HistoricoStatusProcesso, TemplateDocumento,
)
from .serializers import (
    UsuarioSerializer, CursoSerializer, EmpresaConcedenteSerializer,
    AlunoListSerializer, AlunoDetailSerializer,
    CoordenadorSerializer, SupervisorEmpresaSerializer,
    DocumentoProcessoSerializer, LogDocumentoSerializer,
    ProcessoEstagioSerializer, CriarProcessoSerializer, AlterarStatusSerializer,
    ModeloFormularioSerializer, AvaliacaoEmpresaSerializer, HistoricoStatusSerializer,
    TemplateDocumentoSerializer,
)
from .score_utils import calcular_score_conformidade
from .permissions import (
    get_aluno, get_coordenador, get_supervisor, is_admin, is_administrativo, has_global_access, is_visao_global,
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
        if has_global_access(user):
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
    """
    Coordenador/admin podem criar/editar. Aluno também pode criar (cadastra
    a empresa do estágio). Após criação por aluno, dispara criação do
    supervisor e email com link de definição de senha.
    """
    serializer_class = EmpresaConcedenteSerializer

    def get_permissions(self):
        if self.action == 'create':
            # Qualquer usuário autenticado pode propor uma empresa
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsAdminOrReadOnly()]

    def get_queryset(self):
        qs = EmpresaConcedente.objects.all()
        aprovada = self.request.query_params.get('aprovada')
        if aprovada is not None:
            qs = qs.filter(aprovada_ibmec=aprovada.lower() in ('true', '1'))
        busca = self.request.query_params.get('busca')
        if busca:
            qs = qs.filter(razao_social__icontains=busca)
        return qs

    _CAMPOS_OBRIGATORIOS_EMPRESA = [
        'cnpj', 'razao_social', 'areas_atuacao', 'localizacao',
        'email_contato', 'descricao',
        'responsavel_legal_nome', 'responsavel_legal_cargo',
    ]

    def create(self, request, *args, **kwargs):
        # Aluno cadastrando empresa: exige TODOS os campos preenchidos.
        if get_aluno(request.user) is not None:
            faltando = [
                c for c in self._CAMPOS_OBRIGATORIOS_EMPRESA
                if not (request.data.get(c) or '').strip()
            ]
            if faltando:
                return Response(
                    {'erro': 'Todos os campos da empresa são obrigatórios.',
                     'campos_faltando': faltando},
                    status=drf_status.HTTP_400_BAD_REQUEST,
                )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        empresa = serializer.save()
        aluno_perfil = get_aluno(self.request.user)
        if aluno_perfil is None:
            return  # criação por coord/admin: não dispara fluxo de email
        # Cria Usuario+SupervisorEmpresa para que o gestor da empresa acesse o sistema
        from django.conf import settings as dj_settings
        from django.contrib.auth.tokens import PasswordResetTokenGenerator
        from django.core.mail import send_mail
        import secrets
        email_gestor = (empresa.email_contato or '').strip()
        if not email_gestor:
            return
        if Usuario.objects.filter(email_institucional=email_gestor).exists():
            return  # já existe; não recria
        senha_aleatoria = secrets.token_urlsafe(16)
        user_sup = Usuario.objects.create_user(
            username=email_gestor,
            email_institucional=email_gestor,
            password=senha_aleatoria,
            tipo='supervisor_empresa',
            nome=empresa.responsavel_legal_nome or empresa.razao_social,
        )
        SupervisorEmpresa.objects.create(
            usuario=user_sup, empresa=empresa,
            cargo=empresa.responsavel_legal_cargo or '',
        )
        token = PasswordResetTokenGenerator().make_token(user_sup)
        base = getattr(dj_settings, 'FRONTEND_BASE_URL', 'http://localhost:8000')
        link = f'{base}/redefinir-senha/?uid={user_sup.pk}&token={token}'
        nome_aluno = self.request.user.nome or self.request.user.email_institucional
        send_mail(
            'IBMEC Estágios — sua empresa foi cadastrada',
            f'Olá!\n\nA empresa {empresa.razao_social} foi cadastrada no sistema '
            f'de estágios do IBMEC pelo aluno {nome_aluno}.\n\n'
            'Clique no link abaixo para definir sua senha e acessar o painel:\n'
            f'{link}\n\n'
            'Equipe IBMEC Estágios.\n',
            dj_settings.DEFAULT_FROM_EMAIL,
            [email_gestor],
            fail_silently=True,
        )


class AlunoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base = Aluno.objects.select_related('usuario', 'curso')
        if has_global_access(user):
            return base.all()
        aluno = get_aluno(user)
        if aluno is not None:
            return base.filter(pk=aluno.pk)
        coord = get_coordenador(user)
        if coord is not None:
            return base.filter(curso__coordenador=coord)
        return base.none()

    def get_serializer_class(self):
        """Detail (com CPF/RG) só para admin ou para o próprio aluno acessando seu perfil.
        Listagens e visões de coordenador usam o List (sem dados sensíveis)."""
        user = self.request.user
        if self.action in ('retrieve', 'update', 'partial_update'):
            if has_global_access(user):
                return AlunoDetailSerializer
            aluno = get_aluno(user)
            if aluno is not None:
                # próprio aluno olhando seu cadastro
                obj_pk = self.kwargs.get(self.lookup_field or 'pk')
                if obj_pk and str(obj_pk) == str(aluno.pk):
                    return AlunoDetailSerializer
        return AlunoListSerializer


class CoordenadorViewSet(viewsets.ModelViewSet):
    serializer_class = CoordenadorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base = Coordenador.objects.select_related('usuario')
        if has_global_access(user):
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
        if has_global_access(user):
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
            'processo__aluno', 'processo__empresa', 'enviado_por',
        )

        # ── filtros opcionais ──────────────────────────────────────────────
        processo_id = self.request.query_params.get('processo')
        tipo = self.request.query_params.get('tipo')
        doc_status = self.request.query_params.get('status')
        if processo_id:
            base = base.filter(processo_id=processo_id)
        if tipo:
            base = base.filter(tipo=tipo)
        if doc_status:
            base = base.filter(status=doc_status)

        # ── isolamento por papel ──────────────────────────────────────────
        if has_global_access(user):
            return base
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
        # Tipo é opcional no upload — default 'OUTRO' quando o frontend só envia título livre.
        save_kwargs = {'enviado_por': self.request.user}
        if not serializer.validated_data.get('tipo'):
            save_kwargs['tipo'] = DocumentoProcesso.Tipo.OUTRO
        doc = serializer.save(**save_kwargs)
        score = calcular_score_conformidade(doc.arquivo, doc.tipo)
        doc.score_conformidade = score
        auto_aprovado = score >= 0.8
        if auto_aprovado:
            doc.status = DocumentoProcesso.StatusDoc.APROVADO
        doc.save(update_fields=['score_conformidade', 'status'])
        LogDocumento.objects.create(
            documento=doc,
            acao=LogDocumento.Acao.UPLOAD,
            usuario=self.request.user,
        )
        if auto_aprovado:
            LogDocumento.objects.create(
                documento=doc,
                acao=LogDocumento.Acao.APROVADO,
                usuario=self.request.user,
                comentario='Aprovado automaticamente por score de conformidade >= 0.8',
            )

    @action(detail=True, methods=['post'], url_path='validar')
    def validar(self, request, pk=None):
        """
        POST /api/documentos/{id}/validar/
        Body: { "status": "APROVADO" } ou { "status": "REJEITADO" }
        Apenas coordenador ou admin.
        """
        user = request.user
        if not (has_global_access(user) or get_coordenador(user) is not None):
            return Response(
                {'erro': 'Apenas coordenadores ou administradores podem validar documentos.'},
                status=drf_status.HTTP_403_FORBIDDEN,
            )

        doc = self.get_object()
        novo_status = request.data.get('status')
        if novo_status not in (
            DocumentoProcesso.StatusDoc.APROVADO,
            DocumentoProcesso.StatusDoc.REJEITADO,
        ):
            return Response(
                {'erro': 'Status deve ser APROVADO ou REJEITADO.'},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        comentario = request.data.get('comentario', None)
        doc.status = novo_status
        if comentario is not None:
            doc.observacoes = comentario
        doc.save()
        LogDocumento.objects.create(
            documento=doc,
            acao=novo_status,
            usuario=user,
            comentario=comentario,
        )
        return Response(self.get_serializer(doc).data)

    @action(detail=True, methods=['get'], url_path='logs')
    def logs(self, request, pk=None):
        """GET /api/documentos/{id}/logs/ — histórico de ações do documento."""
        doc = self.get_object()
        serializer = LogDocumentoSerializer(doc.logs.all(), many=True)
        return Response(serializer.data)


# ── ModeloFormulario ──────────────────────────────────────────────────────────

class ModeloFormularioViewSet(viewsets.ModelViewSet):
    """
    CRUD de modelos de formulário de avaliação.
    - Coordenador: cria e edita apenas para o seu curso
    - Admin: acesso total
    - Aluno: leitura dos modelos ativos do seu curso
    - Supervisor: leitura dos modelos ativos
    """
    serializer_class = ModeloFormularioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base = ModeloFormulario.objects.select_related('curso', 'criado_por__usuario')
        if has_global_access(user):
            return base.all()
        coord = get_coordenador(user)
        if coord is not None:
            return base.filter(curso__coordenador=coord)
        aluno = get_aluno(user)
        if aluno is not None and aluno.curso:
            return base.filter(curso=aluno.curso, ativo=True)
        supervisor = get_supervisor(user)
        if supervisor is not None:
            return base.filter(ativo=True)
        return ModeloFormulario.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        coord = get_coordenador(user)
        if coord is None and not is_admin(user):
            raise PermissionDenied('Apenas coordenadores e admins podem criar modelos de formulário.')
        if coord is not None:
            curso = serializer.validated_data.get('curso')
            if curso and curso.coordenador_id != coord.pk:
                raise PermissionDenied('Você só pode criar formulários para o seu curso.')
        serializer.save(criado_por=coord)

    def update(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        coord = get_coordenador(user)
        if not is_admin(user):
            if coord is None or instance.curso.coordenador_id != coord.pk:
                return Response(
                    {'erro': 'Você só pode editar formulários do seu curso.'},
                    status=drf_status.HTTP_403_FORBIDDEN,
                )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        instance = self.get_object()
        coord = get_coordenador(user)
        if not is_admin(user):
            if coord is None or instance.curso.coordenador_id != coord.pk:
                return Response(
                    {'erro': 'Você só pode excluir formulários do seu curso.'},
                    status=drf_status.HTTP_403_FORBIDDEN,
                )
        return super().destroy(request, *args, **kwargs)


# ── CORE da issue #46: ProcessoEstagio ────────────────────────────────────────

class ProcessoEstagioViewSet(viewsets.ModelViewSet):
    """
    Aluno: cria e cancela; vê só os próprios processos.
    Coordenador: aprova/rejeita/encerra processos de alunos dos cursos que coordena.
    Supervisor da empresa: vê processos vinculados à sua empresa.
    Admin: acesso total.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['aluno__usuario__nome', 'aluno__usuario__username']

    def get_serializer_class(self):
        if self.action == 'create':
            return CriarProcessoSerializer
        if self.action == 'alterar_status':
            return AlterarStatusSerializer
        return ProcessoEstagioSerializer

    def _filtrar_respostas_se_supervisor(self, data):
        """Supervisor não pode ver respostas_formulario do aluno (privacidade
        da avaliação). Anula o campo no payload para esse perfil."""
        user = self.request.user
        if get_supervisor(user) is not None and not has_global_access(user):
            if isinstance(data, list):
                for d in data:
                    if isinstance(d, dict):
                        d['respostas_formulario'] = None
            elif isinstance(data, dict):
                data['respostas_formulario'] = None
        return data

    def list(self, request, *args, **kwargs):
        resp = super().list(request, *args, **kwargs)
        resp.data = self._filtrar_respostas_se_supervisor(resp.data)
        return resp

    def retrieve(self, request, *args, **kwargs):
        resp = super().retrieve(request, *args, **kwargs)
        resp.data = self._filtrar_respostas_se_supervisor(resp.data)
        return resp

    def get_queryset(self):
        user = self.request.user
        base = ProcessoEstagio.objects.select_related(
            'aluno__usuario', 'aluno__curso',
            'empresa', 'coordenador__usuario', 'supervisor',
        )
        if has_global_access(user):
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
        if not has_global_access(user):
            aluno = get_aluno(user)
            coord = get_coordenador(user)

            if aluno is not None:
                if aluno.pk != processo.aluno_id:
                    return Response(
                        {'detail': 'Sem permissão neste processo.'},
                        status=drf_status.HTTP_403_FORBIDDEN,
                    )
                pode_cancelar = (
                    novo_status == CANCELADO
                    and processo.status in (RASCUNHO, PENDENTE)
                )
                permitido = (
                    (processo.status == RASCUNHO and novo_status == PENDENTE)
                    or pode_cancelar
                )
                if not permitido:
                    if novo_status == CANCELADO:
                        return Response(
                            {'detail': 'Aluno só pode cancelar processos com status RASCUNHO ou PENDENTE.'},
                            status=drf_status.HTTP_403_FORBIDDEN,
                        )
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

        # 3. RN05: APROVADO→ATIVO exige TCE aprovado
        if processo.status == APROVADO and novo_status == ATIVO:
            tem_tce_aprovado = DocumentoProcesso.objects.filter(
                processo=processo,
                tipo=DocumentoProcesso.Tipo.TCE,
                status=DocumentoProcesso.StatusDoc.APROVADO,
            ).exists()
            if not tem_tce_aprovado:
                return Response(
                    {'detail': 'RN05: é necessário que o TCE assinado esteja aprovado para ativar o estágio.'},
                    status=drf_status.HTTP_400_BAD_REQUEST,
                )

        # 4. Validar via serializer (RN11) e persistir
        status_anterior = processo.status
        serializer = AlterarStatusSerializer(processo, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # 5. Registrar no histórico de status
        HistoricoStatusProcesso.objects.create(
            processo=processo,
            status_anterior=status_anterior,
            status_novo=novo_status,
            usuario=request.user,
            observacao=request.data.get('observacao', ''),
        )

        processo.refresh_from_db()
        return Response(ProcessoEstagioSerializer(processo).data)

    @action(detail=True, methods=['get'])
    def documentos(self, request, pk=None):
        processo = self.get_object()
        docs = processo.documentos.all().order_by('-data_upload')
        serializer = DocumentoProcessoSerializer(docs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def historico(self, request, pk=None):
        processo = self.get_object()
        registros = processo.historico_status.all()
        serializer = HistoricoStatusSerializer(registros, many=True)
        return Response(serializer.data)


# ── Geração de PDF ───────────────────────────────────────────────────────────

class GerarPDFView(APIView):
    """
    GET /api/processos-estagio/{processo_id}/gerar-tce/
    GET /api/processos-estagio/{processo_id}/gerar-termo-realizacao/

    Retorna o PDF gerado como application/pdf.
    Permissão: aluno do processo, supervisor da empresa, coordenador do curso, ou admin.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, processo_id, tipo_documento):
        user = request.user
        try:
            processo = ProcessoEstagio.objects.select_related(
                'aluno__usuario',
                'aluno__curso__coordenador__usuario',
                'empresa',
                'supervisor__usuario',
                'coordenador__usuario',
            ).get(pk=processo_id)
        except ProcessoEstagio.DoesNotExist:
            return Response(
                {'erro': 'Processo não encontrado.'},
                status=drf_status.HTTP_404_NOT_FOUND,
            )

        if not has_global_access(user):
            aluno = get_aluno(user)
            supervisor = get_supervisor(user)
            coord = get_coordenador(user)
            tem_acesso = False
            if aluno is not None and processo.aluno_id == aluno.pk:
                tem_acesso = True
            elif supervisor is not None and processo.empresa_id == supervisor.empresa_id:
                tem_acesso = True
            elif coord is not None:
                curso = getattr(processo.aluno, 'curso', None)
                if curso is not None and curso.coordenador_id == coord.pk:
                    tem_acesso = True
            if not tem_acesso:
                return Response(
                    {'erro': 'Acesso negado.'},
                    status=drf_status.HTTP_403_FORBIDDEN,
                )

        if tipo_documento == 'tce':
            from .pdf_generator import gerar_tce
            buffer = gerar_tce(processo)
            filename = f'tce_processo_{processo_id}.pdf'
        elif tipo_documento == 'termo-realizacao':
            from .pdf_generator import gerar_termo_realizacao
            buffer = gerar_termo_realizacao(processo)
            filename = f'termo_realizacao_processo_{processo_id}.pdf'
        else:
            return Response(
                {'erro': 'Tipo de documento inválido.'},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        from django.http import HttpResponse
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class GerarRelatorioView(APIView):
    """
    POST /api/processos-estagio/{processo_id}/gerar-relatorio/

    Gera PDF do relatório de estágio (parcial ou final), salva como
    DocumentoProcesso e retorna o PDF.

    Apenas o aluno dono do processo pode chamar este endpoint.
    """
    permission_classes = [IsAuthenticated]

    _CAMPOS_OBRIGATORIOS = [
        'resumo', 'introducao', 'atividades_desenvolvidas',
        'analise_critica', 'conclusao',
    ]

    def post(self, request, processo_id):
        user = request.user
        try:
            processo = ProcessoEstagio.objects.select_related(
                'aluno__usuario',
                'aluno__curso__coordenador__usuario',
                'empresa',
                'supervisor__usuario',
                'coordenador__usuario',
                'professor_orientador',
            ).get(pk=processo_id)
        except ProcessoEstagio.DoesNotExist:
            return Response(
                {'erro': 'Processo não encontrado.'},
                status=drf_status.HTTP_404_NOT_FOUND,
            )

        aluno = get_aluno(user)
        if aluno is None or processo.aluno_id != aluno.pk:
            return Response(
                {'erro': 'Apenas o aluno do processo pode gerar o relatório.'},
                status=drf_status.HTTP_403_FORBIDDEN,
            )

        faltando = [c for c in self._CAMPOS_OBRIGATORIOS if not request.data.get(c, '').strip()]
        if faltando:
            return Response(
                {'erro': f'Campos obrigatórios ausentes: {", ".join(faltando)}.'},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        preview_raw = request.data.get('preview', False)
        is_preview = preview_raw in (True, 'true', 'True', '1', 1)

        dados = {
            'tipo_relatorio': request.data.get('tipo_relatorio', 'parcial'),
            'resumo': request.data.get('resumo', ''),
            'introducao': request.data.get('introducao', ''),
            'apresentacao_empresa': request.data.get('apresentacao_empresa', ''),
            'atividades_desenvolvidas': request.data.get('atividades_desenvolvidas', ''),
            'analise_critica': request.data.get('analise_critica', ''),
            'conclusao': request.data.get('conclusao', ''),
        }

        from .pdf_generator import gerar_relatorio_estagio
        buffer = gerar_relatorio_estagio(processo, dados)

        tipo_doc = (
            DocumentoProcesso.Tipo.RELATORIO_FINAL
            if dados['tipo_relatorio'] == 'final'
            else DocumentoProcesso.Tipo.RELATORIO_PARCIAL
        )
        tipo_nome = 'final' if dados['tipo_relatorio'] == 'final' else 'parcial'
        filename = f'relatorio_{tipo_nome}_processo_{processo_id}.pdf'

        from django.core.files.base import ContentFile
        from django.http import HttpResponse

        if not is_preview:
            doc_processo = DocumentoProcesso(
                processo=processo,
                tipo=tipo_doc,
                enviado_por=user,
                status=DocumentoProcesso.StatusDoc.PENDENTE,
            )
            doc_processo.arquivo.save(filename, ContentFile(buffer.getvalue()), save=True)
            LogDocumento.objects.create(
                documento=doc_processo,
                acao=LogDocumento.Acao.GERADO,
                usuario=user,
            )

        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


# ── Preenchimento de formulário avaliativo ────────────────────────────────────

class PreencherFormularioView(APIView):
    """
    POST /api/processos-estagio/{processo_id}/preencher-formulario/

    Aluno preenche o formulário avaliativo do seu processo.
    Body: { "tipo_relatorio": "parcial"|"final", "respostas": {...}, "preview": bool }

    - Se preview=False: salva respostas no processo, gera PDF, cria DocumentoProcesso + log
    - Se preview=True: gera e retorna PDF sem persistir nada
    - Apenas o aluno dono do processo pode chamar
    - 400 se o processo não tem modelo_formulario atribuído
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, processo_id):
        user = request.user
        try:
            processo = ProcessoEstagio.objects.select_related(
                'aluno__usuario', 'aluno__curso__coordenador__usuario',
                'empresa', 'supervisor__usuario', 'coordenador__usuario',
                'modelo_formulario', 'professor_orientador',
            ).get(pk=processo_id)
        except ProcessoEstagio.DoesNotExist:
            return Response(
                {'erro': 'Processo não encontrado.'},
                status=drf_status.HTTP_404_NOT_FOUND,
            )

        aluno = get_aluno(user)
        if aluno is None or processo.aluno_id != aluno.pk:
            return Response(
                {'erro': 'Acesso negado.'},
                status=drf_status.HTTP_403_FORBIDDEN,
            )

        if not processo.modelo_formulario:
            return Response(
                {'erro': 'Este processo não possui um formulário de avaliação atribuído. Contate o coordenador.'},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        tipo_relatorio = request.data.get('tipo_relatorio', 'parcial')
        if tipo_relatorio not in ('parcial', 'final'):
            return Response(
                {'erro': 'tipo_relatorio deve ser "parcial" ou "final".'},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        respostas = request.data.get('respostas', {})
        if not isinstance(respostas, dict):
            return Response(
                {'erro': 'respostas deve ser um objeto JSON.'},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        from .form_validator import validar_respostas
        erros = validar_respostas(processo.modelo_formulario.secoes, respostas)
        if erros:
            return Response({'erros_validacao': erros}, status=drf_status.HTTP_400_BAD_REQUEST)

        preview_raw = request.data.get('preview', False)
        is_preview = preview_raw in (True, 'true', 'True', '1', 1)

        from .pdf_generator import gerar_relatorio_avaliacao
        buffer = gerar_relatorio_avaliacao(processo, processo.modelo_formulario, respostas)

        tipo_doc = (
            DocumentoProcesso.Tipo.RELATORIO_PARCIAL
            if tipo_relatorio == 'parcial'
            else DocumentoProcesso.Tipo.RELATORIO_FINAL
        )
        filename = f'avaliacao_{tipo_relatorio}_processo_{processo_id}.pdf'

        if not is_preview:
            import datetime
            processo.respostas_formulario = {
                'preenchido_em': datetime.datetime.now().isoformat(),
                'tipo_relatorio': tipo_relatorio,
                'secoes': respostas,
            }
            processo.save(update_fields=['respostas_formulario'])

            from django.core.files.base import ContentFile
            doc_processo = DocumentoProcesso(
                processo=processo,
                tipo=tipo_doc,
                enviado_por=user,
                status=DocumentoProcesso.StatusDoc.PENDENTE,
            )
            doc_processo.arquivo.save(filename, ContentFile(buffer.getvalue()), save=True)
            LogDocumento.objects.create(
                documento=doc_processo,
                acao=LogDocumento.Acao.GERADO,
                usuario=user,
                comentario=f'Formulário de avaliação ({tipo_relatorio}) preenchido e gerado automaticamente.',
            )

        from django.http import HttpResponse
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


# ── Avaliação de empresa ─────────────────────────────────────────────────────

class AvaliacaoEmpresaViewSet(viewsets.ModelViewSet):
    """
    Aluno: cria/edita avaliação de empresa de processo ENCERRADO seu (1 por processo).
    Coordenador/Admin/Administrativo: leitura de todas as avaliações dos seus cursos.
    Empresa (supervisor): leitura das avaliações da sua empresa.
    """
    serializer_class = AvaliacaoEmpresaSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        base = AvaliacaoEmpresa.objects.select_related(
            'empresa', 'aluno__usuario', 'processo',
        )
        if has_global_access(user):
            return base.all()
        aluno = get_aluno(user)
        if aluno is not None:
            return base.filter(aluno=aluno)
        coord = get_coordenador(user)
        if coord is not None:
            return base.filter(processo__aluno__curso__coordenador=coord)
        supervisor = get_supervisor(user)
        if supervisor is not None:
            return base.filter(empresa=supervisor.empresa)
        return base.none()

    def perform_create(self, serializer):
        aluno = get_aluno(self.request.user)
        if aluno is None:
            raise PermissionDenied('Apenas alunos podem avaliar empresas.')
        serializer.save(aluno=aluno)

    def perform_update(self, serializer):
        aluno = get_aluno(self.request.user)
        if aluno is None or serializer.instance.aluno_id != aluno.pk:
            raise PermissionDenied('Apenas o autor da avaliação pode editá-la.')
        serializer.save()


class TemplateDocumentoViewSet(viewsets.ModelViewSet):
    """
    Coordenador/Admin: CRUD de templates de documentos.
    Aluno/Supervisor: somente leitura dos templates ativos.
    """
    serializer_class = TemplateDocumentoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base = TemplateDocumento.objects.select_related('curso')
        if has_global_access(user) or is_admin(user):
            return base.all()
        coord = get_coordenador(user)
        if coord is not None:
            return base.all()
        return base.filter(ativo=True)

    def perform_create(self, serializer):
        user = self.request.user
        if not has_global_access(user) and get_coordenador(user) is None:
            raise PermissionDenied('Apenas coordenadores ou administradores podem criar templates.')
        serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        if not has_global_access(user) and get_coordenador(user) is None:
            raise PermissionDenied('Apenas coordenadores ou administradores podem editar templates.')
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if not has_global_access(user) and get_coordenador(user) is None:
            raise PermissionDenied('Apenas coordenadores ou administradores podem excluir templates.')
        instance.delete()


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
        # Aceita 'email' (preferido) ou 'username' (compat) — o campo de auth é
        # email_institucional, e username é sincronizado por Usuario.save().
        email = (data.get('email') or data.get('email_institucional') or data.get('username') or '').strip()
        password = data.get('password', '')

        if not email or not password:
            return Response(
                {'erro': 'email e password são obrigatórios.'},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )
        username = email  # username sincronizado com email_institucional

        if tipo == 'aluno':
            try:
                user = Usuario.objects.create_user(
                    username=username, password=password, tipo='aluno',
                    nome=data.get('nome', ''),
                    email_institucional=email,
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
                    email_institucional=email,
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
                    email_institucional=email,
                )
                SupervisorEmpresa.objects.create(
                    usuario=user, empresa=empresa,
                    cargo=data.get('cargo', ''),
                )
            except Exception as e:
                return Response({'erro': str(e)}, status=drf_status.HTTP_400_BAD_REQUEST)

        elif tipo in Usuario.TIPOS_ADMINISTRATIVOS:
            try:
                user = Usuario.objects.create_user(
                    username=username, password=password, tipo=tipo,
                    nome=data.get('nome', ''),
                    email_institucional=email,
                )
            except Exception as e:
                return Response({'erro': str(e)}, status=drf_status.HTTP_400_BAD_REQUEST)

        else:
            tipos_validos = ', '.join(
                [c[0] for c in Usuario.TIPO_CHOICES]
            )
            return Response(
                {'erro': f'tipo inválido. Opções: {tipos_validos}'},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {'token': token.key, 'id': user.pk, 'tipo': tipo},
            status=drf_status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Autentica email_institucional + password. Aceita 'email' ou 'username'
    no payload (compat) e resolve via email_institucional."""
    permission_classes = [AllowAny]

    def post(self, request):
        identificador = (request.data.get('email') or request.data.get('username') or '').strip()
        password = request.data.get('password', '')
        user = None
        if identificador and password:
            # Username está sincronizado com email_institucional (save() do Usuario);
            # com USERNAME_FIELD='email_institucional', authenticate aceita o email
            # como `username=` no kwarg do backend.
            user = authenticate(request, username=identificador, password=password)
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
            'email': user.email_institucional,
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


# ── Esqueci minha senha / Redefinir ───────────────────────────────────────

class EsqueciSenhaView(APIView):
    """POST /api/auth/esqueci-senha/ — envia link de redefinição por email."""
    permission_classes = [AllowAny]

    def post(self, request):
        from django.conf import settings as dj_settings
        from django.contrib.auth.tokens import PasswordResetTokenGenerator
        from django.core.mail import send_mail
        email = (request.data.get('email') or '').strip()
        # Resposta sempre 200 para não vazar se o email existe ou não.
        if email:
            user = Usuario.objects.filter(email_institucional=email).first()
            if user is not None:
                token = PasswordResetTokenGenerator().make_token(user)
                base = getattr(dj_settings, 'FRONTEND_BASE_URL', 'http://localhost:8000')
                link = f'{base}/redefinir-senha/?uid={user.pk}&token={token}'
                send_mail(
                    'IBMEC Estágios — redefinição de senha',
                    f'Olá {user.nome},\n\nClique no link abaixo para redefinir '
                    f'sua senha no sistema de estágios IBMEC:\n\n{link}\n\n'
                    'Se você não solicitou esta redefinição, ignore este email.\n',
                    dj_settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=True,
                )
        return Response({'mensagem': 'Se o email estiver cadastrado, você receberá instruções.'})


class RedefinirSenhaView(APIView):
    """POST /api/auth/redefinir-senha/ — valida token e troca senha."""
    permission_classes = [AllowAny]

    def post(self, request):
        from django.contrib.auth.tokens import PasswordResetTokenGenerator
        uid = request.data.get('uid')
        token = request.data.get('token')
        nova = request.data.get('nova_senha') or ''
        if not uid or not token or not nova:
            return Response(
                {'erro': 'uid, token e nova_senha são obrigatórios.'},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )
        if len(nova) < 6:
            return Response(
                {'erro': 'Nova senha deve ter ao menos 6 caracteres.'},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = Usuario.objects.get(pk=uid)
        except Usuario.DoesNotExist:
            return Response({'erro': 'Token inválido.'}, status=drf_status.HTTP_400_BAD_REQUEST)
        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({'erro': 'Token inválido ou expirado.'}, status=drf_status.HTTP_400_BAD_REQUEST)
        user.set_password(nova)
        user.save(update_fields=['password'])
        return Response({'mensagem': 'Senha redefinida com sucesso.'})


# ── Avaliação anônima de empresa pelo aluno ─────────────────────────────────

def _gerar_aluno_hash(aluno_pk, empresa_pk):
    import hashlib
    from django.conf import settings
    raw = f'{aluno_pk}:{empresa_pk}:{settings.SECRET_KEY}'
    return hashlib.sha256(raw.encode()).hexdigest()


class AvaliarEmpresaView(APIView):
    """
    POST /api/avaliar-empresa/
    Body: { "empresa": int (opcional — deduz do processo), "nota": 1-5, "comentario": str opcional }

    Validações:
    - Apenas alunos com processo APROVADO/ATIVO/ENCERRADO
    - Empresa deve ser a do processo do aluno
    - Apenas 1 avaliação por aluno por empresa (via aluno_hash)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        aluno = get_aluno(request.user)
        if aluno is None:
            return Response(
                {'erro': 'Apenas alunos podem avaliar empresas.'},
                status=drf_status.HTTP_403_FORBIDDEN,
            )

        processo = ProcessoEstagio.objects.filter(
            aluno=aluno,
            status__in=['APROVADO', 'ATIVO', 'ENCERRADO'],
        ).select_related('empresa').first()
        if processo is None:
            return Response(
                {'erro': 'Você só pode avaliar a empresa vinculada ao seu processo de estágio.'},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        empresa_id = request.data.get('empresa')
        if empresa_id is not None and int(empresa_id) != processo.empresa_id:
            return Response(
                {'erro': 'Você só pode avaliar a empresa vinculada ao seu processo de estágio.'},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )
        empresa = processo.empresa

        h = _gerar_aluno_hash(aluno.pk, empresa.pk)
        if AvaliacaoEmpresa.objects.filter(aluno_hash=h).exists():
            return Response(
                {'erro': 'Você já avaliou esta empresa.'},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        nota = request.data.get('nota')
        comentario = (request.data.get('comentario') or '').strip()
        try:
            nota_int = int(nota)
            if nota_int < 1 or nota_int > 5:
                raise ValueError
        except (TypeError, ValueError):
            return Response(
                {'erro': 'Nota deve ser inteiro entre 1 e 5.'},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        AvaliacaoEmpresa.objects.create(
            empresa=empresa,
            aluno=None,
            processo=None,
            nota=nota_int,
            comentario=comentario,
            aluno_hash=h,
        )
        return Response(
            {'mensagem': 'Avaliação registrada anonimamente.'},
            status=drf_status.HTTP_201_CREATED,
        )


class JaAvalieiView(APIView):
    """GET /api/avaliar-empresa/ja-avaliei/?empresa={id}"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        aluno = get_aluno(request.user)
        if aluno is None:
            return Response(
                {'erro': 'Apenas alunos podem consultar.'},
                status=drf_status.HTTP_403_FORBIDDEN,
            )
        empresa_id = request.query_params.get('empresa')
        if not empresa_id:
            return Response(
                {'erro': 'Parâmetro "empresa" é obrigatório.'},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )
        h = _gerar_aluno_hash(aluno.pk, int(empresa_id))
        ja = AvaliacaoEmpresa.objects.filter(aluno_hash=h).exists()
        return Response({'ja_avaliou': ja})
