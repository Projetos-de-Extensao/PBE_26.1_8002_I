from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario, Curso, EmpresaConcedente,
    Aluno, Coordenador, SupervisorEmpresa,
    ProcessoEstagio, DocumentoProcesso,
)


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Formulário de CRIAÇÃO de usuário
    add_fieldsets = (
        ('Credenciais de Acesso', {
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Dados Pessoais', {
            'fields': ('nome', 'email_institucional'),
        }),
        ('Papel no Sistema', {
            'fields': ('tipo',),
        }),
    )

    # Formulário de EDIÇÃO de usuário
    fieldsets = (
        ('Credenciais de Acesso', {
            'fields': ('username',),
        }),
        ('Dados Pessoais', {
            'fields': ('nome', 'email_institucional'),
        }),
        ('Papel no Sistema', {
            'fields': ('tipo',),
        }),
        ('Controle de Acesso', {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
            'classes': ('collapse',),
        }),
    )

    # Colunas exibidas na listagem
    list_display = ('username', 'nome', 'tipo', 'email_institucional', 'is_active')
    list_filter = ('tipo', 'is_active', 'is_staff')
    search_fields = ('username', 'nome', 'email_institucional')


@admin.register(Coordenador)
class CoordenadorAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'departamento')
    search_fields = ('usuario__nome', 'usuario__username', 'departamento')


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = (
        '__str__', 'cpf', 'curso', 'coeficiente_rendimento', 'matriculado_estagio'
    )
    search_fields = ('usuario__nome', 'cpf')
    list_filter = ('curso', 'matriculado_estagio')


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = (
        'nome', 'coordenador',
        'carga_horaria_minima_total', 'carga_horaria_maxima_diaria',
    )
    search_fields = ('nome',)


@admin.register(EmpresaConcedente)
class EmpresaConcedenteAdmin(admin.ModelAdmin):
    list_display = ('razao_social', 'cnpj', 'aprovada_ibmec', 'email_contato')
    list_filter = ('aprovada_ibmec',)
    search_fields = ('razao_social', 'cnpj')


@admin.register(SupervisorEmpresa)
class SupervisorEmpresaAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'empresa', 'cargo')
    search_fields = ('usuario__nome',)


@admin.register(ProcessoEstagio)
class ProcessoEstagioAdmin(admin.ModelAdmin):
    list_display = (
        '__str__', 'status', 'horas_semanais',
        'data_inicio_prevista', 'data_fim_prevista',
    )
    list_filter = ('status', 'empresa__aprovada_ibmec')
    search_fields = ('aluno__usuario__nome', 'empresa__razao_social')


@admin.register(DocumentoProcesso)
class DocumentoProcessoAdmin(admin.ModelAdmin):
    list_display = ('processo', 'tipo', 'status', 'data_upload')
    list_filter = ('tipo', 'status')
