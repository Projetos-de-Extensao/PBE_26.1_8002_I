from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    tipo = models.CharField(
        max_length=20,
        choices=[('aluno', 'Aluno'), ('coordenador', 'Coordenador')],
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

    def __str__(self):
        return self.usuario.nome

    class Meta:
        verbose_name = 'Coordenador'
        verbose_name_plural = 'Coordenadores'


class Curso(models.Model):
    nome = models.CharField(max_length=200)
    '''
    carga_horaria_minima_total = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Carga horária mínima total exigida para integralização (horas)',
    )
    carga_horaria_maxima_diaria = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Limite diário de horas permitido pela legislação/PPC',
    )
    '''
    coordenador = models.ForeignKey(
        Coordenador,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cursos_coordenados',
        verbose_name='Coordenador responsável',
    )

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'


class Aluno(models.Model):
    usuario = models.OneToOneField(
        Usuario, on_delete=models.CASCADE, related_name='aluno'
    )
    cpf = models.CharField(max_length=14, unique=True)
    rg = models.CharField(max_length=20, blank=True, default='')
    coeficiente_rendimento = models.DecimalField(max_digits=2, decimal_places=2, default=0)
    curso = models.ForeignKey(
        Curso, on_delete=models.PROTECT, related_name='alunos', null=True, blank=True
    )

    def __str__(self):
        return self.usuario.nome

    class Meta:
        verbose_name = 'Aluno'
        verbose_name_plural = 'Alunos'


class Empresa(models.Model):
    cnpj = models.CharField(max_length=18, unique=True)
    razao_social = models.CharField(max_length=200)
    areas_atuacao = models.TextField()
    localizacao = models.CharField(max_length=300)
    email_contato = models.EmailField()
    aprovada_ibmec = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return self.razao_social

    class Meta:
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'


class SolicitacaoEstagio(models.Model):
    class Status(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        APROVADO = 'APROVADO', 'Aprovado'
        REJEITADO = 'REJEITADO', 'Rejeitado'
        RETIFICACAO_SOLICITADA = 'RETIFICACAO_SOLICITADA', 'Retificação Solicitada'
        ATIVO = 'ATIVO', 'Ativo'
        ENCERRADO = 'ENCERRADO', 'Encerrado'

    aluno = models.ForeignKey(
        Aluno, on_delete=models.PROTECT, related_name='solicitacoes'
    )
    empresa = models.ForeignKey(
        Empresa, on_delete=models.PROTECT, related_name='solicitacoes'
    )
    coordenador = models.ForeignKey(
        Coordenador, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='solicitacoes'
    )
    status = models.CharField(
        max_length=30, choices=Status.choices, default=Status.PENDENTE
    )
    horas_semanais = models.PositiveIntegerField()
    data_inicio_prevista = models.DateField()
    data_fim_prevista = models.DateField()
    justificativa_rejeicao = models.TextField(blank=True, default='')

    def __str__(self):
        return f'Solicitação #{self.pk} — {self.aluno} @ {self.empresa} [{self.status}]'

    class Meta:
        verbose_name = 'Solicitação de Estágio'
        verbose_name_plural = 'Solicitações de Estágio'


class Documento(models.Model):
    class StatusDocumento(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        APROVADO = 'APROVADO', 'Aprovado'
        REJEITADO = 'REJEITADO', 'Rejeitado'

    arquivo = models.FileField(upload_to='documentos/')
    status = models.CharField(
        max_length=20, choices=StatusDocumento.choices, default=StatusDocumento.PENDENTE
    )
    versao = models.PositiveIntegerField(default=1)
    data_upload = models.DateTimeField(auto_now_add=True)
    solicitacao = models.ForeignKey(
        SolicitacaoEstagio,
        on_delete=models.CASCADE,
        related_name='%(class)s_set',
    )

    class Meta:
        abstract = True

