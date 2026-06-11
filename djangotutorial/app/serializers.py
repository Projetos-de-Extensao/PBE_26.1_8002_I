from rest_framework import serializers
from .models import (
    Usuario, Curso, EmpresaConcedente, Aluno, Coordenador,
    SupervisorEmpresa, ProcessoEstagio, DocumentoProcesso, LogDocumento,
    ModeloFormulario, AvaliacaoEmpresa, HistoricoStatusProcesso, TemplateDocumento,
)
from .state_machine import ESTADOS_VIVOS
from .permissions import get_aluno, get_supervisor


class UsuarioSerializer(serializers.ModelSerializer):
    """Whitelist explícito — nunca expor password, groups, user_permissions."""
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'nome', 'email_institucional', 'tipo']


class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = '__all__'


class EmpresaConcedenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmpresaConcedente
        fields = '__all__'


class AlunoListSerializer(serializers.ModelSerializer):
    """Listagens públicas a coord/admin — sem dados sensíveis (CPF/RG)."""
    usuario = UsuarioSerializer(read_only=True)
    curso_nome = serializers.CharField(source='curso.nome', read_only=True)

    class Meta:
        model = Aluno
        fields = [
            'id', 'usuario', 'curso', 'curso_nome',
            'periodo_atual', 'coeficiente_rendimento', 'matriculado_estagio',
        ]


class AlunoDetailSerializer(serializers.ModelSerializer):
    """O próprio aluno (ou admin) — inclui CPF/RG."""
    usuario = UsuarioSerializer(read_only=True)

    class Meta:
        model = Aluno
        fields = [
            'id', 'usuario', 'cpf', 'rg',
            'curso', 'periodo_atual', 'coeficiente_rendimento', 'matriculado_estagio',
        ]


# Alias mantido para compatibilidade com código que ainda importa AlunoSerializer
AlunoSerializer = AlunoListSerializer


class CoordenadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordenador
        fields = '__all__'


class SupervisorEmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupervisorEmpresa
        fields = '__all__'


class DocumentoProcessoSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    enviado_por_nome = serializers.SerializerMethodField()

    class Meta:
        model = DocumentoProcesso
        fields = '__all__'
        read_only_fields = ['enviado_por', 'data_upload', 'versao', 'observacoes', 'score_conformidade']

    def get_enviado_por_nome(self, obj):
        if obj.enviado_por_id:
            return obj.enviado_por.nome
        return None

    def validate_arquivo(self, value):
        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError('Apenas arquivos PDF são aceitos.')
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('O arquivo deve ter no máximo 10 MB.')
        return value

    def validate(self, data):
        request = self.context.get('request')
        if not request:
            return data
        user = request.user
        tipo = data.get('tipo')

        RELATORIOS = {DocumentoProcesso.Tipo.RELATORIO_PARCIAL, DocumentoProcesso.Tipo.RELATORIO_FINAL}
        if tipo in RELATORIOS:
            if get_aluno(user) is None:
                raise serializers.ValidationError(
                    {'tipo': 'Apenas alunos podem enviar relatórios.'}
                )

        if tipo == DocumentoProcesso.Tipo.AVALIACAO_EMPRESA:
            if get_supervisor(user) is None:
                raise serializers.ValidationError(
                    {'tipo': 'Apenas supervisores da empresa podem enviar avaliação.'}
                )

        if tipo == DocumentoProcesso.Tipo.TERMO_REALIZACAO:
            raise serializers.ValidationError(
                {'tipo': 'Termo de Realização é gerado automaticamente pelo sistema.'}
            )

        return data


class LogDocumentoSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.SerializerMethodField()

    class Meta:
        model = LogDocumento
        fields = '__all__'
        read_only_fields = ['documento', 'acao', 'usuario', 'data']

    def get_usuario_nome(self, obj):
        if obj.usuario:
            return obj.usuario.nome
        return None


class ModeloFormularioSerializer(serializers.ModelSerializer):
    curso_nome = serializers.CharField(source='curso.nome', read_only=True)
    criado_por_nome = serializers.SerializerMethodField()

    class Meta:
        model = ModeloFormulario
        fields = '__all__'
        read_only_fields = ['criado_por', 'criado_em', 'atualizado_em']

    def get_criado_por_nome(self, obj):
        if obj.criado_por:
            return obj.criado_por.usuario.nome
        return None

    def validate_secoes(self, value):
        TIPOS_VALIDOS = {
            'auto', 'checkbox_duplo', 'escala_3',
            'escala_1_4_multi', 'escala_1_4', 'texto_livre',
        }
        GRAFICOS_VALIDOS = {'radar', 'barras', 'barras_agrupadas', 'pizza', 'nenhum'}
        if not isinstance(value, list):
            raise serializers.ValidationError('secoes deve ser uma lista.')
        for i, secao in enumerate(value):
            if not isinstance(secao, dict):
                raise serializers.ValidationError(f'Seção {i} deve ser um objeto.')
            if 'id' not in secao:
                raise serializers.ValidationError(f'Seção {i} precisa de um campo id.')
            if 'tipo' not in secao:
                raise serializers.ValidationError(f'Seção {i} precisa de um campo tipo.')
            if secao['tipo'] not in TIPOS_VALIDOS:
                raise serializers.ValidationError(
                    f'Seção {i}: tipo inválido. Válidos: {sorted(TIPOS_VALIDOS)}'
                )
            if 'titulo' not in secao:
                raise serializers.ValidationError(f'Seção {i} precisa de um campo titulo.')
            if 'grafico' not in secao:
                raise serializers.ValidationError(f'Seção {i} precisa de um campo grafico.')
            if secao['grafico'] not in GRAFICOS_VALIDOS:
                raise serializers.ValidationError(
                    f'Seção {i}: grafico inválido. Válidos: {sorted(GRAFICOS_VALIDOS)}'
                )
            if secao['tipo'] not in ('auto', 'texto_livre') and 'itens' not in secao:
                raise serializers.ValidationError(
                    f'Seção {i} do tipo {secao["tipo"]} precisa de itens.'
                )
            if secao['tipo'] in ('checkbox_duplo', 'escala_1_4_multi') and 'colunas' not in secao:
                raise serializers.ValidationError(
                    f'Seção {i} do tipo {secao["tipo"]} precisa de colunas.'
                )
        return value


class ProcessoEstagioSerializer(serializers.ModelSerializer):
    """Leitura full."""
    class Meta:
        model = ProcessoEstagio
        fields = '__all__'


class CriarProcessoSerializer(serializers.ModelSerializer):
    """Criação por aluno. aluno/status/coordenador são preenchidos pelo servidor."""
    class Meta:
        model = ProcessoEstagio
        fields = [
            'id', 'empresa', 'horas_semanais',
            'data_inicio_prevista', 'data_fim_prevista', 'plano_atividades',
            'aluno', 'status', 'coordenador',
        ]
        read_only_fields = ['aluno', 'status', 'coordenador']

    def validate(self, data):
        # Data: fim > início
        if data['data_fim_prevista'] <= data['data_inicio_prevista']:
            raise serializers.ValidationError({
                'data_fim_prevista': 'Deve ser posterior à data de início.'
            })

        request = self.context.get('request')
        if request is None or not getattr(request.user, 'is_authenticated', False):
            raise serializers.ValidationError('Usuário não autenticado.')

        try:
            aluno = request.user.aluno
        except Exception:
            raise serializers.ValidationError('Apenas alunos podem criar processos de estágio.')

        # RN01: matriculado em estágio
        if not aluno.matriculado_estagio:
            raise serializers.ValidationError({
                'aluno': 'RN01: aluno deve estar com matrícula ativa em estágio supervisionado.'
            })

        # RN09: empresa aprovada pelo IBMEC
        empresa = data['empresa']
        if not empresa.aprovada_ibmec:
            raise serializers.ValidationError({
                'empresa': 'RN09: empresa não está aprovada pelo IBMEC.'
            })

        # RN03: jornada compatível com o curso
        horas = data['horas_semanais']
        if aluno.curso is not None and aluno.curso.carga_horaria_maxima_diaria:
            limite_curso = aluno.curso.carga_horaria_maxima_diaria * 5
            if horas > limite_curso:
                raise serializers.ValidationError({
                    'horas_semanais': f'RN03: excede o limite do curso ({limite_curso}h/semana).'
                })
        # Ceiling legal (Lei 11.788/08)
        if horas > 30:
            raise serializers.ValidationError({
                'horas_semanais': 'Limite legal de 30h semanais (Lei 11.788/08).'
            })

        # RN05 (estendida): só pode iniciar processo se TODOS os anteriores
        # estiverem CANCELADO. Qualquer outro estado (vivo ou encerrado)
        # bloqueia a abertura de um novo.
        if ProcessoEstagio.objects.filter(aluno=aluno).exclude(status='CANCELADO').exists():
            raise serializers.ValidationError(
                'Você já possui um processo de estágio em andamento. '
                'Só é possível iniciar novo processo se o anterior estiver cancelado.'
            )

        return data


class AlterarStatusSerializer(serializers.ModelSerializer):
    """Mudança de status. Apenas status e justificativa_rejeicao editáveis."""
    class Meta:
        model = ProcessoEstagio
        fields = ['status', 'justificativa_rejeicao']

    def validate(self, data):
        if data.get('status') == ProcessoEstagio.Status.REJEITADO:
            justif = data.get(
                'justificativa_rejeicao',
                self.instance.justificativa_rejeicao if self.instance else '',
            )
            if not justif or not justif.strip():
                raise serializers.ValidationError({
                    'justificativa_rejeicao': 'RN11: justificativa obrigatória ao rejeitar uma solicitação.'
                })
        return data


class AvaliacaoEmpresaSerializer(serializers.ModelSerializer):
    aluno_nome = serializers.SerializerMethodField()
    empresa_nome = serializers.CharField(source='empresa.razao_social', read_only=True)

    class Meta:
        model = AvaliacaoEmpresa
        fields = [
            'id', 'empresa', 'processo', 'nota', 'comentario',
            'anonimo', 'aluno_nome', 'empresa_nome', 'data_criacao', 'data_atualizacao',
        ]
        read_only_fields = ['empresa', 'data_criacao', 'data_atualizacao']
        # aluno_hash NUNCA exposto — controle interno de unicidade

    def get_aluno_nome(self, obj):
        if obj.anonimo:
            return None
        return obj.aluno.usuario.nome

    def validate_nota(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError('Nota deve ser entre 1 e 5.')
        return value

    def validate(self, data):
        request = self.context.get('request')
        if not request:
            return data
        aluno = get_aluno(request.user)
        if aluno is None:
            raise serializers.ValidationError('Apenas alunos podem avaliar empresas.')

        processo = data.get('processo')
        if processo:
            if processo.aluno_id != aluno.pk:
                raise serializers.ValidationError(
                    {'processo': 'Você só pode avaliar empresas de processos seus.'}
                )
            if processo.status != ProcessoEstagio.Status.ENCERRADO:
                raise serializers.ValidationError(
                    {'processo': 'Só é possível avaliar empresas de processos encerrados.'}
                )
            data['empresa'] = processo.empresa
        return data


class HistoricoStatusSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.CharField(source='usuario.nome', read_only=True, default=None)

    class Meta:
        model = HistoricoStatusProcesso
        fields = ['id', 'processo', 'status_anterior', 'status_novo', 'usuario', 'usuario_nome', 'data', 'observacao']
        read_only_fields = fields


class TemplateDocumentoSerializer(serializers.ModelSerializer):
    curso_nome = serializers.CharField(source='curso.nome', read_only=True, default=None)

    class Meta:
        model = TemplateDocumento
        fields = [
            'id', 'nome', 'descricao', 'arquivo', 'tipo', 'curso', 'curso_nome',
            'ativo', 'criado_em', 'atualizado_em',
        ]
        read_only_fields = ['criado_em', 'atualizado_em']
