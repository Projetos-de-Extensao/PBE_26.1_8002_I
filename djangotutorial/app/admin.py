from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario, Curso, Empresa,
    Aluno, Coordenador,
    SolicitacaoEstagio,
    TermoCompromisso, ApoliceSeguro, RelatorioEstagio,
    AssinaturaDigital,
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
    search_fields = ('usuario__nome', 'usuario__username')


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'cpf', 'curso', 'coeficiente_rendimento')
    search_fields = ('usuario__nome', 'cpf')
    list_filter = ('curso',)


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'coordenador')
    search_fields = ('nome',)


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('razao_social', 'cnpj', 'aprovada_ibmec', 'email_contato')
    list_filter = ('aprovada_ibmec',)
    search_fields = ('razao_social', 'cnpj')


@admin.register(SolicitacaoEstagio)
class SolicitacaoEstagioAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status', 'horas_semanais', 'data_inicio_prevista', 'data_fim_prevista')
    list_filter = ('status',)
    search_fields = ('aluno__usuario__nome', 'empresa__razao_social')


@admin.register(TermoCompromisso)
class TermoCompromissoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status', 'versao', 'data_upload')
    list_filter = ('status',)


@admin.register(ApoliceSeguro)
class ApoliceSeguroAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status', 'data_vencimento', 'versao')
    list_filter = ('status',)


@admin.register(RelatorioEstagio)
class RelatorioEstagioAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'status', 'periodo_referencia', 'versao')
    list_filter = ('status',)


@admin.register(AssinaturaDigital)
class AssinaturaDigitalAdmin(admin.ModelAdmin):
    list_display = ('signatario_nome', 'signatario_perfil', 'data_assinatura', 'ip_address')
    list_filter = ('signatario_perfil',)
