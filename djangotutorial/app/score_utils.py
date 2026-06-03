"""Cálculo automático de score de conformidade para DocumentoProcesso."""
import io


def calcular_score_conformidade(arquivo, tipo_documento):
    """Analisa o PDF e retorna um float de 0.0 a 1.0.

    Critérios (cada um vale 0.2):
    1. PDF válido e legível
    2. Número de páginas adequado ao tipo
    3. Quantidade mínima de texto
    4. Tamanho do arquivo entre 10 KB e 10 MB
    5. Palavras-chave esperadas para o tipo
    """
    try:
        import PyPDF2
    except ImportError:
        arquivo.seek(0)
        return 0.0

    score = 0.0
    RELATORIOS = {'RELATORIO_PARCIAL', 'RELATORIO_FINAL'}

    try:
        arquivo.seek(0)
        conteudo = arquivo.read()
        tamanho = len(conteudo)
        reader = PyPDF2.PdfReader(io.BytesIO(conteudo))
        num_paginas = len(reader.pages)

        texto_total = ''
        for page in reader.pages:
            try:
                texto_total += (page.extract_text() or '')
            except Exception:
                pass
        palavras = texto_total.split()

        # Critério 1: PDF legível
        score += 0.2

        # Critério 2: Número de páginas adequado
        if tipo_documento in RELATORIOS:
            if num_paginas >= 3:
                score += 0.2
        else:
            if num_paginas >= 1:
                score += 0.2

        # Critério 3: Quantidade mínima de texto
        if tipo_documento in RELATORIOS:
            if len(palavras) >= 500:
                score += 0.2
        else:
            if len(palavras) >= 50:
                score += 0.2

        # Critério 4: Tamanho do arquivo razoável
        if 10 * 1024 <= tamanho <= 10 * 1024 * 1024:
            score += 0.2

        # Critério 5: Palavras-chave por tipo
        texto_lower = texto_total.lower()
        if tipo_documento in RELATORIOS:
            keywords = ['estágio', 'atividades', 'empresa']
            encontradas = sum(1 for kw in keywords if kw in texto_lower)
            if encontradas >= 2:
                score += 0.2
        elif tipo_documento == 'TCE':
            keywords = ['termo', 'compromisso', 'estágio']
            encontradas = sum(1 for kw in keywords if kw in texto_lower)
            if encontradas >= 2:
                score += 0.2
        else:
            score += 0.2

    except Exception:
        score = 0.2

    arquivo.seek(0)
    return round(min(score, 1.0), 2)
