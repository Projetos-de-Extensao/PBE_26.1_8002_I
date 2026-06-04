"""Validação das respostas do aluno contra a estrutura de um ModeloFormulario."""


def validar_respostas(secoes, respostas):
    """Retorna lista de strings de erro (vazia se tudo ok).

    Tipos suportados:
    - escala_1_4       : {"item": nota_int_1_4}
    - escala_1_4_multi : {"item": {"coluna": nota_int_1_4}}
    - escala_3         : {"item": "opcao_string"}
    - checkbox_duplo   : {"item": ["coluna1", ...]}
    - texto_livre      : "string"
    - auto             : ignorado
    """
    erros = []

    for secao in secoes:
        tipo = secao.get('tipo')
        sid = secao.get('id')

        if tipo == 'auto':
            continue

        if sid not in respostas:
            continue

        valor = respostas[sid]

        if tipo == 'escala_1_4':
            itens = secao.get('itens', [])
            if not isinstance(valor, dict):
                erros.append(f'Seção "{sid}": esperado dict com notas por item.')
                continue
            for item in itens:
                if item not in valor:
                    continue
                nota = valor[item]
                if isinstance(nota, bool) or not isinstance(nota, int) or nota < 1 or nota > 4:
                    erros.append(
                        f'Seção "{sid}", item "{item}": nota deve ser inteiro entre 1 e 4, recebido {nota!r}.'
                    )

        elif tipo == 'escala_1_4_multi':
            itens = secao.get('itens', [])
            colunas = secao.get('colunas', [])
            if not isinstance(valor, dict):
                erros.append(f'Seção "{sid}": esperado dict com notas por item e coluna.')
                continue
            for item in itens:
                if item not in valor:
                    continue
                notas_item = valor[item]
                if not isinstance(notas_item, dict):
                    erros.append(f'Seção "{sid}", item "{item}": esperado dict com colunas.')
                    continue
                for col, nota in notas_item.items():
                    if col not in colunas:
                        erros.append(f'Seção "{sid}", item "{item}": coluna "{col}" não está no modelo.')
                    if isinstance(nota, bool) or not isinstance(nota, int) or nota < 1 or nota > 4:
                        erros.append(
                            f'Seção "{sid}", item "{item}", coluna "{col}": '
                            f'nota deve ser inteiro entre 1 e 4, recebido {nota!r}.'
                        )

        elif tipo == 'escala_3':
            itens = secao.get('itens', [])
            opcoes = secao.get('opcoes', ['Suficiente', 'Insuficiente', 'Não utilizado'])
            if not isinstance(valor, dict):
                erros.append(f'Seção "{sid}": esperado dict com opção por item.')
                continue
            for item in itens:
                if item not in valor:
                    continue
                opcao = valor[item]
                if opcao not in opcoes:
                    erros.append(
                        f'Seção "{sid}", item "{item}": opção "{opcao}" inválida. Válidas: {opcoes}.'
                    )

        elif tipo == 'checkbox_duplo':
            colunas = secao.get('colunas', [])
            if not isinstance(valor, dict):
                erros.append(f'Seção "{sid}": esperado dict com lista de colunas por item.')
                continue
            for item, marcados in valor.items():
                if not isinstance(marcados, list):
                    erros.append(f'Seção "{sid}", item "{item}": esperado lista de colunas marcadas.')
                    continue
                for col in marcados:
                    if col not in colunas:
                        erros.append(f'Seção "{sid}", item "{item}": coluna "{col}" não está no modelo.')

        elif tipo == 'texto_livre':
            if not isinstance(valor, str):
                erros.append(
                    f'Seção "{sid}": esperado string para texto livre, recebido {type(valor).__name__}.'
                )

    return erros
