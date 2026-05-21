# app/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CursoViewSet, EmpresaViewSet, AlunoViewSet, CoordenadorViewSet,
    SolicitacaoEstagioViewSet,
    RegisterView, LoginView, LogoutView,
)

router = DefaultRouter()
router.register(r'cursos', CursoViewSet, basename='curso')
router.register(r'empresas', EmpresaViewSet, basename='empresa')
router.register(r'alunos', AlunoViewSet, basename='aluno')
router.register(r'coordenadores', CoordenadorViewSet, basename='coordenador')
router.register(r'solicitacoes-estagio', SolicitacaoEstagioViewSet, basename='solicitacaoestagio')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
]