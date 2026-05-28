from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    TIPO_CHOICES = [
        ('aluno', 'Aluno'),
        ('coordenador', 'Coordenador'),
        ('supervisor_empresa', 'Supervisor de Empresa'),
    ]

    tipo = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='aluno',
    )
    nome = models.CharField(max_length=100)
    email_institucional = models.EmailField(blank=True, default='')

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'


class Coordenador(models.Model):
    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name='coordenador'
    )
    departamento = models.CharField(max_length=100)

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
        related_name='cursos_coordenados',
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
        max_digits=4, decimal_places=2, default=0
    )
    curso = models.ForeignKey(
        Curso,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='alunos',
    )
    matriculado_estagio = models.BooleanField(default=False)

    def __str__(self):
        return self.usuario.nome

    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'


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
    tipo = models.CharField(max_length=30, choices=Tipo.choices)
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

    def __str__(self):
        return f'{self.get_tipo_display()} v{self.versao} — Processo #{self.processo_id}'

    class Meta:
        verbose_name = 'Documento de Processo'
        verbose_name_plural = 'Documentos de Processo'
