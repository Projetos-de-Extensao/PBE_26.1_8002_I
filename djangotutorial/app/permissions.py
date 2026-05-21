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


# ── permissões ────────────────────────────────────────────────────────────────

class SolicitacaoEstagioPermission(permissions.BasePermission):
    """
    Controle de acesso ao ViewSet de SolicitacaoEstagio.

    Aluno
      - list, retrieve, create  ✔  (queryset já filtra para as próprias)
      - update, partial_update  ✘
      - destroy                 ✘
      - alterar_status          ✘

    Coordenador
      - list, retrieve          ✔  (queryset já filtra para o seu curso)
      - alterar_status          ✔  (somente solicitações do seu curso)
      - create, update, destroy ✘

    Admin
      - tudo                    ✔

    Default: negado.
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

        # Usuário autenticado sem perfil reconhecido → nega por padrão
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if is_admin(user):
            return True

        aluno = get_aluno(user)
        if aluno is not None:
            # Aluno só acessa as próprias solicitações
            return obj.aluno_id == aluno.pk

        coordenador = get_coordenador(user)
        if coordenador is not None:
            # Coordenador só acessa solicitações de alunos do seu curso
            curso = getattr(obj.aluno, 'curso', None)
            return curso is not None and curso.coordenador_id == coordenador.pk

        return False
