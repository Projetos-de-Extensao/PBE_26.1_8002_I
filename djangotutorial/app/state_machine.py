"""Máquina de estados de ProcessoEstagio.

Módulo puro Python — sem dependência de Django.
As constantes string devem casar com ProcessoEstagio.Status.values em app/models.py.
"""

# Constantes de status
RASCUNHO            = 'RASCUNHO'
PENDENTE            = 'PENDENTE'
APROVADO            = 'APROVADO'
REJEITADO           = 'REJEITADO'
CORRECAO_SOLICITADA = 'CORRECAO_SOLICITADA'
ATIVO               = 'ATIVO'
ENCERRADO           = 'ENCERRADO'
CANCELADO           = 'CANCELADO'

# Mapa de transições válidas: de qual estado pode-se ir para quais
TRANSICOES: dict[str, set[str]] = {
    RASCUNHO:            {PENDENTE, CANCELADO},
    PENDENTE:            {APROVADO, REJEITADO, CORRECAO_SOLICITADA, CANCELADO},
    APROVADO:            {ATIVO, CANCELADO},
    CORRECAO_SOLICITADA: {PENDENTE, CANCELADO},
    ATIVO:               {ENCERRADO, CANCELADO},
    REJEITADO:           set(),
    ENCERRADO:           set(),
    CANCELADO:           set(),
}

ESTADOS_TERMINAIS = frozenset({REJEITADO, ENCERRADO, CANCELADO})
ESTADOS_VIVOS     = frozenset({RASCUNHO, PENDENTE, APROVADO, CORRECAO_SOLICITADA, ATIVO})


def transicoes_validas(estado_atual: str) -> set[str]:
    """Retorna o conjunto de estados que podem ser alcançados a partir de `estado_atual`."""
    return TRANSICOES.get(estado_atual, set())


def pode_transicionar(de: str, para: str) -> bool:
    """True se a transição `de` → `para` é válida no fluxo do ProcessoEstagio."""
    return para in transicoes_validas(de)


def eh_terminal(estado: str) -> bool:
    """True se `estado` é terminal (REJEITADO, ENCERRADO, CANCELADO)."""
    return estado in ESTADOS_TERMINAIS
