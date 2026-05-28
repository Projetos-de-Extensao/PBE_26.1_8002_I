"""
Permissões customizadas para o sistema de gestão de estágios.

Hierarquia de acesso (mais permissivo → menos):
  Admin (is_superuser / is_staff) → tudo
  Coordenador                     → leitura + alterar-status das solicitações do seu curso
  Aluno                           → leitura + criação das próprias solicitações
  Não autenticado                 → negado
"""
from rest_framework import permissions


# ── helpers ──────────────────────────────────────────────────────────────────

def get_aluno(user):
    """Retorna o perfil Aluno vinculado ao usuário, ou None."""
    try:
        return user.aluno
    except Exception:
        return None


def get_coordenador(user):
    """Retorna o perfil Coordenador vinculado ao usuário, ou None."""
    try:
        return user.coordenador
    except Exception:
        return None


def is_admin(user):
    return bool(user and user.is_authenticated and (user.is_superuser or user.is_staff))


def get_supervisor(user):
    """Retorna SupervisorEmpresa vinculado ao user, ou None."""
    try:
        return user.supervisor_empresa
    except Exception:
        return None


# ── permissões ────────────────────────────────────────────────────────────────

class IsAluno(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and get_aluno(request.user) is not None


class IsCoordenador(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and get_coordenador(request.user) is not None


class IsSupervisorEmpresa(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and get_supervisor(request.user) is not None


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return is_admin(request.user)


class IsDonoDoProcesso(permissions.BasePermission):
    """Ownership de ProcessoEstagio: aluno do processo, supervisor da empresa, ou coordenador do curso do aluno."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        if is_admin(user):
            return True
        aluno = get_aluno(user)
        if aluno is not None and obj.aluno_id == aluno.pk:
            return True
        supervisor = get_supervisor(user)
        if supervisor is not None and obj.empresa_id == supervisor.empresa_id:
            return True
        coord = get_coordenador(user)
        if coord is not None:
            curso = getattr(obj.aluno, 'curso', None)
            if curso is not None and curso.coordenador_id == coord.pk:
                return True
        return False
