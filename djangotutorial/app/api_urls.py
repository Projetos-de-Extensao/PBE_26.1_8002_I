from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CursoViewSet, EmpresaConcedenteViewSet, AlunoViewSet,
    CoordenadorViewSet, SupervisorEmpresaViewSet,
    DocumentoProcessoViewSet, ProcessoEstagioViewSet,
    ModeloFormularioViewSet,
    GerarPDFView, GerarRelatorioView, PreencherFormularioView,
    RegisterView, LoginView, LogoutView,
)
from .views_dashboard import (
    DashboardProcessosView, DashboardEstatisticasView, DashboardEmpresasView,
)

router = DefaultRouter()
router.register(r'cursos',               CursoViewSet,             basename='curso')
router.register(r'empresas',             EmpresaConcedenteViewSet, basename='empresa')
router.register(r'alunos',               AlunoViewSet,             basename='aluno')
router.register(r'coordenadores',        CoordenadorViewSet,       basename='coordenador')
router.register(r'supervisores-empresa', SupervisorEmpresaViewSet, basename='supervisor-empresa')
router.register(r'documentos',           DocumentoProcessoViewSet, basename='documento')
router.register(r'processos-estagio',    ProcessoEstagioViewSet,   basename='processo-estagio')
router.register(r'modelos-formulario',   ModeloFormularioViewSet,  basename='modelo-formulario')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/',    LoginView.as_view(),    name='auth-login'),
    path('auth/logout/',   LogoutView.as_view(),   name='auth-logout'),
    path(
        'processos-estagio/<int:processo_id>/gerar-tce/',
        GerarPDFView.as_view(),
        {'tipo_documento': 'tce'},
        name='gerar-tce',
    ),
    path(
        'processos-estagio/<int:processo_id>/gerar-termo-realizacao/',
        GerarPDFView.as_view(),
        {'tipo_documento': 'termo-realizacao'},
        name='gerar-termo-realizacao',
    ),
    path(
        'processos-estagio/<int:processo_id>/gerar-relatorio/',
        GerarRelatorioView.as_view(),
        name='gerar-relatorio',
    ),
    path(
        'processos-estagio/<int:processo_id>/preencher-formulario/',
        PreencherFormularioView.as_view(),
        name='preencher-formulario',
    ),
    path('dashboard/processos/',     DashboardProcessosView.as_view(),    name='dashboard-processos'),
    path('dashboard/estatisticas/',  DashboardEstatisticasView.as_view(), name='dashboard-estatisticas'),
    path('dashboard/empresas/',      DashboardEmpresasView.as_view(),     name='dashboard-empresas'),
]
