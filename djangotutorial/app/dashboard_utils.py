"""Funções auxiliares para agregar dados de processos de estágio no dashboard."""


def calcular_semestre(data):
    """Dado um date, retorna string no formato '26.1' ou '26.2'."""
    if data is None:
        return None
    semestre = 1 if data.month <= 6 else 2
    return f'{str(data.year)[2:]}.{semestre}'


def agregar_escala_1_4(processos, secao_id):
    """Agrega notas de seção escala_1_4 nos processos com respostas.
    Retorna dict: { "item": {"media": float, "contagem": int} }
    """
    acum = {}
    for processo in processos:
        rf = processo.respostas_formulario
        if not rf:
            continue
        valor = rf.get('secoes', {}).get(secao_id)
        if not isinstance(valor, dict):
            continue
        for item, nota in valor.items():
            if isinstance(nota, bool) or not isinstance(nota, (int, float)):
                continue
            if not (1 <= nota <= 4):
                continue
            if item not in acum:
                acum[item] = {'soma': 0, 'contagem': 0}
            acum[item]['soma'] += nota
            acum[item]['contagem'] += 1
    return {
        item: {'media': round(v['soma'] / v['contagem'], 2), 'contagem': v['contagem']}
        for item, v in acum.items()
    }


def agregar_escala_1_4_multi(processos, secao_id, colunas):
    """Agrega notas de seção escala_1_4_multi.
    Retorna dict: { "item": { "coluna": {"media": float, "contagem": int} } }
    """
    acum = {}
    for processo in processos:
        rf = processo.respostas_formulario
        if not rf:
            continue
        valor = rf.get('secoes', {}).get(secao_id)
        if not isinstance(valor, dict):
            continue
        for item, notas in valor.items():
            if not isinstance(notas, dict):
                continue
            if item not in acum:
                acum[item] = {}
            for col, nota in notas.items():
                if isinstance(nota, bool) or not isinstance(nota, (int, float)):
                    continue
                if not (1 <= nota <= 4):
                    continue
                if col not in acum[item]:
                    acum[item][col] = {'soma': 0, 'contagem': 0}
                acum[item][col]['soma'] += nota
                acum[item][col]['contagem'] += 1
    return {
        item: {
            col: {'media': round(v['soma'] / v['contagem'], 2), 'contagem': v['contagem']}
            for col, v in cols.items()
        }
        for item, cols in acum.items()
    }


def agregar_escala_3(processos, secao_id, opcoes):
    """Agrega respostas de seção escala_3.
    Retorna dict: { "item": { "opcao": contagem_int } }
    """
    resultado = {}
    for processo in processos:
        rf = processo.respostas_formulario
        if not rf:
            continue
        valor = rf.get('secoes', {}).get(secao_id)
        if not isinstance(valor, dict):
            continue
        for item, opcao in valor.items():
            if item not in resultado:
                resultado[item] = {op: 0 for op in opcoes}
            if opcao in resultado[item]:
                resultado[item][opcao] += 1
    return resultado


def agregar_checkbox_duplo(processos, secao_id, colunas):
    """Agrega checkboxes de seção checkbox_duplo.
    Retorna dict: { "item": { "coluna": contagem_int } }
    """
    resultado = {}
    for processo in processos:
        rf = processo.respostas_formulario
        if not rf:
            continue
        valor = rf.get('secoes', {}).get(secao_id)
        if not isinstance(valor, dict):
            continue
        for item, marcados in valor.items():
            if item not in resultado:
                resultado[item] = {col: 0 for col in colunas}
            if isinstance(marcados, list):
                for col in marcados:
                    if col in resultado[item]:
                        resultado[item][col] += 1
    return resultado


def calcular_avaliacao_media(processos):
    """Média de todas as notas escala_1_4 e escala_1_4_multi dos processos."""
    soma = 0
    contagem = 0
    for processo in processos:
        rf = processo.respostas_formulario
        if not rf or not processo.modelo_formulario:
            continue
        secoes_resp = rf.get('secoes', {})
        for secao in processo.modelo_formulario.secoes:
            tipo = secao.get('tipo')
            sid = secao.get('id')
            if tipo == 'escala_1_4':
                valor = secoes_resp.get(sid)
                if isinstance(valor, dict):
                    for nota in valor.values():
                        if not isinstance(nota, bool) and isinstance(nota, (int, float)) and 1 <= nota <= 4:
                            soma += nota
                            contagem += 1
            elif tipo == 'escala_1_4_multi':
                valor = secoes_resp.get(sid)
                if isinstance(valor, dict):
                    for notas_item in valor.values():
                        if isinstance(notas_item, dict):
                            for nota in notas_item.values():
                                if not isinstance(nota, bool) and isinstance(nota, (int, float)) and 1 <= nota <= 4:
                                    soma += nota
                                    contagem += 1
    return round(soma / contagem, 2) if contagem > 0 else None
