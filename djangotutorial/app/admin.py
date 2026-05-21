from django.contrib import admin
from .models import (
    Usuario, Curso, Empresa,
    Aluno, Coordenador,
    SolicitacaoEstagio,
    TermoCompromisso, ApoliceSeguro, RelatorioEstagio,
    AssinaturaDigital,
)

admin.site.register(Usuario)
admin.site.register(Curso)
admin.site.register(Empresa)
admin.site.register(Aluno)
admin.site.register(Coordenador)
admin.site.register(SolicitacaoEstagio)
admin.site.register(TermoCompromisso)
admin.site.register(ApoliceSeguro)
admin.site.register(RelatorioEstagio)
admin.site.register(AssinaturaDigital)
