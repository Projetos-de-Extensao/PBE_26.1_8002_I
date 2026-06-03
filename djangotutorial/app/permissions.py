"""
Permissões customizadas para o sistema de gestão de estágios.

Hierarquia de acesso (mais permissivo → menos):
  Admin (is_superuser / is_staff) → tudo
  Coordenador                     → leitura + alterar-status das solicitações do seu curso
  Aluno                           → leitura + criação das próprias solicitações
  Empresa                         → acesso às próprias solicitações vinculadas
  Não autenticado                 → negado
"""
from rest_framework import permissions


# ── helpers ───────────────────────────────────────────────────────────────────

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


# ── 5 classes de permissão (responsabilidade: feat/auth-e-permissoes) ─────────

class IsAluno(permissions.BasePermission):
    """Permite acesso somente se o usuário autenticado for do tipo aluno."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and get_aluno(request.user) is not None
        )


class IsCoordenador(permissions.BasePermission):
    """Permite acesso somente se o usuário autenticado for do tipo coordenador."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and get_coordenador(request.user) is not None
        )


class IsEmpresa(permissions.BasePermission):
    """Permite acesso somente se o usuário autenticado for do tipo empresa."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.tipo == 'empresa'
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Admin faz tudo; demais usuários autenticados só leitura."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if is_admin(request.user):
            return True
        return request.method in permissions.SAFE_METHODS


class IsDonoDoProcesso(permissions.BasePermission):
    """
    Verifica se o usuário é dono do processo:
      - Aluno do processo
      - Empresa vinculada ao processo
      - Coordenador do curso do aluno
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if is_admin(user):
            return True

        # Aluno dono do processo
        aluno = get_aluno(user)
        if aluno is not None and obj.aluno_id == aluno.pk:
            return True

        # Empresa do processo (compara pelo email de contato)
        if user.tipo == 'empresa':
            if obj.empresa.email_contato == user.email_institucional:
                return True

        # Coordenador do curso do aluno
        coordenador = get_coordenador(user)
        if coordenador is not None:
            curso = getattr(obj.aluno, 'curso', None)
            if curso is not None and curso.coordenador_id == coordenador.pk:
                return True

        return False


# ── permissão de SolicitacaoEstagio (mantida da main) ────────────────────────

class SolicitacaoEstagioPermission(permissions.BasePermission):
    """
    Controle de acesso ao ViewSet de SolicitacaoEstagio.

    Aluno      → list, retrieve, create
    Coordenador → list, retrieve, alterar_status
    Admin      → tudo
    Default    → negado
    """

    _ALUNO_ACTIONS = frozenset({'list', 'retrieve', 'create'})
    _COORD_ACTIONS = frozenset({'list', 'retrieve', 'alterar_status'})

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if is_admin(user):
            return True

        action = getattr(view, 'action', None)

        if get_aluno(user) is not None:
            return action in self._ALUNO_ACTIONS

        if get_coordenador(user) is not None:
            return action in self._COORD_ACTIONS

        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if is_admin(user):
            return True

        aluno = get_aluno(user)
        if aluno is not None:
            return obj.aluno_id == aluno.pk

        coordenador = get_coordenador(user)
        if coordenador is not None:
            curso = getattr(obj.aluno, 'curso', None)
            return curso is not None and curso.coordenador_id == coordenador.pk

        return False
