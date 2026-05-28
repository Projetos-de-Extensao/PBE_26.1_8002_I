from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CursoViewSet, EmpresaConcedenteViewSet, AlunoViewSet,
    CoordenadorViewSet, SupervisorEmpresaViewSet,
    DocumentoProcessoViewSet, ProcessoEstagioViewSet,
    RegisterView, LoginView, LogoutView,
)

router = DefaultRouter()
router.register(r'cursos',               CursoViewSet,             basename='curso')
router.register(r'empresas',             EmpresaConcedenteViewSet, basename='empresa')
router.register(r'alunos',               AlunoViewSet,             basename='aluno')
router.register(r'coordenadores',        CoordenadorViewSet,       basename='coordenador')
router.register(r'supervisores-empresa', SupervisorEmpresaViewSet, basename='supervisor-empresa')
router.register(r'documentos',           DocumentoProcessoViewSet, basename='documento')
router.register(r'processos-estagio',    ProcessoEstagioViewSet,   basename='processo-estagio')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/',    LoginView.as_view(),    name='auth-login'),
    path('auth/logout/',   LogoutView.as_view(),   name='auth-logout'),
]
