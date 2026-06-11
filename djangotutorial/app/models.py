from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    TIPO_CHOICES = [
        ('aluno', 'Aluno'),
        ('coordenador', 'Coordenador'),
        ('supervisor_empresa', 'Supervisor de Empresa'),
        ('secretaria', 'Secretaria'),
        ('casa', 'CASA'),
        ('reitor', 'Reitor'),
        ('pro_reitor', 'Pró-Reitor'),
        ('carreiras', 'Carreiras'),
    ]

    TIPOS_ADMINISTRATIVOS = frozenset({'reitor', 'pro_reitor', 'secretaria', 'carreiras'})

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='aluno',
    )
    nome = models.CharField(max_length=100)
    email_institucional = models.EmailField(unique=True)

    # Autenticação por email; username permanece no schema (exigência do
    # AbstractUser) mas é preenchido automaticamente a partir do email.
    USERNAME_FIELD = 'email_institucional'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        # Email é a identidade primária (USERNAME_FIELD); username continua no
        # schema do AbstractUser. Se um dos dois estiver vazio, herda do outro.
        # Se ambos estiverem preenchidos, mantém os valores como passados — isso
        # permite username livre (ex: 'pedro.reis') + email completo.
        if not self.email_institucional and self.username:
            self.email_institucional = self.username
        elif not self.username and self.email_institucional:
            self.username = self.email_institucional
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'


class Coordenador(models.Model):
    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name='coordenador'
    )
    departamento = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.usuario.nome

    class Meta:
        verbose_name = 'Coordenador'
        verbose_name_plural = 'Coordenadores'


class Curso(models.Model):
    nome = models.CharField(max_length=200)
    coordenador = models.ForeignKey(
        Coordenador,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cursos',
        verbose_name='Coordenador responsável',
    )
    carga_horaria_minima_total = models.PositiveIntegerField(
        default=0,
        help_text='Carga horária mínima total exigida para integralização (horas)',
    )
    carga_horaria_maxima_diaria = models.PositiveIntegerField(
        default=6,
        help_text='Limite diário de horas permitido pela legislação/PPC',
    )

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'


class EmpresaConcedente(models.Model):
    cnpj = models.CharField(max_length=18, unique=True)
    razao_social = models.CharField(max_length=200)
    areas_atuacao = models.TextField()
    localizacao = models.CharField(max_length=300)
    email_contato = models.EmailField()
    aprovada_ibmec = models.BooleanField(default=False)
    descricao = models.TextField(
        blank=True,
        help_text='Descrição da empresa, estrutura organizacional e principais atividades',
    )
    responsavel_legal_nome = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text='Nome do responsável legal da empresa (quem assina o TCE)',
    )
    responsavel_legal_cargo = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Cargo do responsável legal',
    )

    def __str__(self):
        return self.razao_social

    class Meta:
        verbose_name = 'Empresa Concedente'
        verbose_name_plural = 'Empresas Concedentes'


class SupervisorEmpresa(models.Model):
    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name='supervisor_empresa'
    )
    empresa = models.ForeignKey(
        EmpresaConcedente,
        on_delete=models.CASCADE,
        related_name='supervisores',
    )
    cargo = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return f'{self.usuario.nome} ({self.empresa.razao_social})'

    class Meta:
        verbose_name = 'Supervisor de Empresa'
        verbose_name_plural = 'Supervisores de Empresa'


class Aluno(models.Model):
    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name='aluno'
    )
    cpf = models.CharField(max_length=14, unique=True)
    rg = models.CharField(max_length=20, blank=True, default='')
    coeficiente_rendimento = models.DecimalField(
        max_digits=4, decimal_places=2, default=0,
        help_text='Coeficiente de rendimento do aluno (ex: 8.50)',
    )
    curso = models.ForeignKey(
        Curso,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='alunos',
    )
    periodo_atual = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text='Período acadêmico atual do aluno (1 a 12)',
        validators=[MinValueValidator(1), MaxValueValidator(12)],
    )
    matriculado_estagio = models.BooleanField(
        default=False,
        help_text='Indica se o aluno está formalmente matriculado em estágio',
    )

    def __str__(self):
        return self.usuario.nome

    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'


# Nota: model Empresa da PR #52 foi substituído por EmpresaConcedente (mais completo).
# SolicitacaoEstagio foi renomeado para ProcessoEstagio na PR #47.
class ProcessoEstagio(models.Model):
    class Status(models.TextChoices):
        RASCUNHO = 'RASCUNHO', 'Rascunho'
        PENDENTE = 'PENDENTE', 'Pendente'
        APROVADO = 'APROVADO', 'Aprovado'
        REJEITADO = 'REJEITADO', 'Rejeitado'
        CORRECAO_SOLICITADA = 'CORRECAO_SOLICITADA', 'Correção Solicitada'
        ATIVO = 'ATIVO', 'Ativo'
        ENCERRADO = 'ENCERRADO', 'Encerrado'
        CANCELADO = 'CANCELADO', 'Cancelado'

    aluno = models.ForeignKey(
        Aluno, on_delete=models.PROTECT, related_name='processos'
    )
    empresa = models.ForeignKey(
        EmpresaConcedente, on_delete=models.PROTECT, related_name='processos'
    )
    supervisor = models.ForeignKey(
        SupervisorEmpresa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processos',
    )
    coordenador = models.ForeignKey(
        Coordenador,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processos',
    )
    status = models.CharField(
        max_length=30, choices=Status.choices, default=Status.PENDENTE
    )
    horas_semanais = models.PositiveIntegerField()
    data_inicio_prevista = models.DateField()
    data_fim_prevista = models.DateField()
    plano_atividades = models.TextField()
    justificativa_rejeicao = models.TextField(blank=True, default='')
    professor_orientador = models.ForeignKey(
        'Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processos_orientados',
        help_text='Professor orientador do estágio pela instituição de ensino',
    )
    numero_seguro = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Número da apólice de seguro contra acidentes pessoais',
    )
    valor_bolsa = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Valor da bolsa mensal (obrigatório para estágio não obrigatório)',
    )
    valor_auxilio_transporte = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Valor do auxílio transporte mensal (obrigatório para estágio não obrigatório)',
    )
    data_inicio_real = models.DateField(
        blank=True,
        null=True,
        help_text='Data real de início do estágio',
    )
    data_fim_real = models.DateField(
        blank=True,
        null=True,
        help_text='Data real de término do estágio',
    )
    modelo_formulario = models.ForeignKey(
        'ModeloFormulario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processos',
        help_text='Modelo de formulário de avaliação atribuído a este processo',
    )
    respostas_formulario = models.JSONField(
        null=True,
        blank=True,
        help_text='Respostas do aluno ao formulário de avaliação',
    )

    def __str__(self):
        return f'Processo #{self.pk} — {self.aluno} @ {self.empresa} [{self.status}]'

    class Meta:
        verbose_name = 'Processo de Estágio'
        verbose_name_plural = 'Processos de Estágio'


class DocumentoProcesso(models.Model):
    class Tipo(models.TextChoices):
        TCE = 'TCE', 'Termo de Compromisso de Estágio'
        APOLICE = 'APOLICE', 'Apólice de Seguro'
        RELATORIO_PARCIAL = 'RELATORIO_PARCIAL', 'Relatório Parcial'
        RELATORIO_FINAL = 'RELATORIO_FINAL', 'Relatório Final'
        AVALIACAO_EMPRESA = 'AVALIACAO_EMPRESA', 'Avaliação da Empresa'
        TERMO_REALIZACAO = 'TERMO_REALIZACAO', 'Termo de Realização'
        OUTRO = 'OUTRO', 'Outro'

    class StatusDoc(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        APROVADO = 'APROVADO', 'Aprovado'
        REJEITADO = 'REJEITADO', 'Rejeitado'

    processo = models.ForeignKey(
        ProcessoEstagio, on_delete=models.CASCADE, related_name='documentos'
    )
    tipo = models.CharField(max_length=30, choices=Tipo.choices, default=Tipo.OUTRO)
    titulo = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text='Título livre do documento (ex: "Carta de apresentação", "Apólice 2026").',
    )
    arquivo = models.FileField(upload_to='documentos/')
    enviado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos_enviados',
    )
    data_upload = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=StatusDoc.choices, default=StatusDoc.PENDENTE
    )
    versao = models.PositiveIntegerField(default=1)
    observacoes = models.TextField(
        blank=True,
        null=True,
        help_text='Observações/parecer do coordenador ao validar o documento',
    )
    score_conformidade = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text='Score automático de conformidade (0.0 a 1.0)',
    )

    def __str__(self):
        label = self.titulo or self.get_tipo_display()
        return f'{label} v{self.versao} — Processo #{self.processo_id}'

    class Meta:
        verbose_name = 'Documento de Processo'
        verbose_name_plural = 'Documentos de Processo'


class LogDocumento(models.Model):
    class Acao(models.TextChoices):
        UPLOAD = 'UPLOAD', 'Upload'
        APROVADO = 'APROVADO', 'Aprovado'
        REJEITADO = 'REJEITADO', 'Rejeitado'
        EDITADO = 'EDITADO', 'Editado'
        GERADO = 'GERADO', 'Gerado pelo sistema'

    documento = models.ForeignKey(
        DocumentoProcesso,
        on_delete=models.CASCADE,
        related_name='logs',
    )
    acao = models.CharField(max_length=20, choices=Acao.choices)
    usuario = models.ForeignKey(
        'Usuario',
        on_delete=models.SET_NULL,
        null=True,
    )
    comentario = models.TextField(blank=True, null=True)
    data = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data']
        verbose_name = 'Log de Documento'
        verbose_name_plural = 'Logs de Documentos'

    def __str__(self):
        return f'{self.acao} - {self.documento} - {self.data}'


class ModeloFormulario(models.Model):
    curso = models.ForeignKey(
        'Curso',
        on_delete=models.CASCADE,
        related_name='modelos_formulario',
    )
    criado_por = models.ForeignKey(
        'Coordenador',
        on_delete=models.SET_NULL,
        null=True,
    )
    titulo = models.CharField(max_length=200)
    secoes = models.JSONField(
        default=list,
        help_text=(
            'Lista de seções do formulário. Tipos válidos: '
            'auto, checkbox_duplo, escala_3, escala_1_4_multi, escala_1_4, texto_livre.'
        ),
    )
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Modelo de Formulário'
        verbose_name_plural = 'Modelos de Formulário'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.titulo} — {self.curso.nome}'


class AvaliacaoEmpresa(models.Model):
    empresa = models.ForeignKey(
        EmpresaConcedente, on_delete=models.CASCADE, related_name='avaliacoes',
    )
    aluno = models.ForeignKey(
        Aluno, on_delete=models.CASCADE, related_name='avaliacoes_empresas',
    )
    processo = models.OneToOneField(
        ProcessoEstagio, on_delete=models.CASCADE, related_name='avaliacao_empresa',
    )
    nota = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comentario = models.TextField(blank=True, default='')
    anonimo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Avaliação de Empresa'
        verbose_name_plural = 'Avaliações de Empresas'
        constraints = [
            models.UniqueConstraint(
                fields=['processo'], name='unique_avaliacao_por_processo',
            ),
        ]

    def __str__(self):
        return f'Avaliação {self.nota}★ — {self.empresa.razao_social}'


class HistoricoStatusProcesso(models.Model):
    processo = models.ForeignKey(
        ProcessoEstagio, on_delete=models.CASCADE, related_name='historico_status',
    )
    status_anterior = models.CharField(max_length=30, choices=ProcessoEstagio.Status.choices)
    status_novo = models.CharField(max_length=30, choices=ProcessoEstagio.Status.choices)
    usuario = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True,
    )
    data = models.DateTimeField(auto_now_add=True)
    observacao = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Histórico de Status'
        verbose_name_plural = 'Históricos de Status'
        ordering = ['-data']

    def __str__(self):
        return f'{self.status_anterior} → {self.status_novo} — Processo #{self.processo_id}'


class TemplateDocumento(models.Model):
    class TipoTemplate(models.TextChoices):
        TCE = 'TCE', 'Termo de Compromisso de Estágio'
        RELATORIO = 'RELATORIO', 'Relatório'
        AVALIACAO = 'AVALIACAO', 'Avaliação'
        OUTRO = 'OUTRO', 'Outro'

    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, default='')
    arquivo = models.FileField(upload_to='templates-documentos/')
    tipo = models.CharField(max_length=20, choices=TipoTemplate.choices, default=TipoTemplate.OUTRO)
    curso = models.ForeignKey(
        Curso, on_delete=models.CASCADE, null=True, blank=True,
        related_name='templates_documentos',
    )
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Template de Documento'
        verbose_name_plural = 'Templates de Documentos'
        ordering = ['-criado_em']

    def __str__(self):
        return self.nome
