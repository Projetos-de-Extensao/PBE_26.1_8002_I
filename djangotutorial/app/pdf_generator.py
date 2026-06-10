"""Geração de PDFs para o sistema de estágios IBMEC RJ.

Funções exportadas:
  gerar_tce(processo)                      → io.BytesIO
  gerar_termo_realizacao(processo)         → io.BytesIO
  gerar_relatorio_estagio(processo, dados) → io.BytesIO
"""
import io
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


# ── helpers ────────────────────────────────────────────────────────────────────

_MESES = [
    '', 'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
    'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro',
]


def _data_extenso(d: date) -> str:
    return f'{d.day} de {_MESES[d.month]} de {d.year}'


def _make_doc(buffer):
    return SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2.5 * cm,
        leftMargin=2.5 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2.5 * cm,
    )


def _styles():
    base = getSampleStyleSheet()
    titulo = ParagraphStyle(
        'titulo_ibmec',
        parent=base['Title'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=18,
        spaceAfter=4,
    )
    subtitulo = ParagraphStyle(
        'subtitulo_ibmec',
        parent=base['Title'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=16,
        spaceAfter=12,
    )
    corpo = ParagraphStyle(
        'corpo_ibmec',
        parent=base['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        spaceAfter=8,
    )
    clausula = ParagraphStyle(
        'clausula_ibmec',
        parent=base['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=16,
        spaceBefore=10,
        spaceAfter=4,
    )
    return titulo, subtitulo, corpo, clausula


def _linha_assinatura(label, sublabel=''):
    data = [
        ['_' * 50],
        [label + (f'\n{sublabel}' if sublabel else '')],
    ]
    t = Table(data, colWidths=[14 * cm])
    t.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica'),
        ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    return t


# ── TCE ───────────────────────────────────────────────────────────────────────

def gerar_tce(processo):
    """Gera o Termo de Compromisso de Estágio (TCE) conforme Lei 11.788/08."""
    buffer = io.BytesIO()
    doc = _make_doc(buffer)
    titulo_st, subtitulo_st, corpo_st, clausula_st = _styles()

    sol = processo
    aluno = sol.aluno
    empresa = sol.empresa
    curso_nome = aluno.curso.nome if aluno.curso else '—'
    coord_nome = (
        processo.coordenador.usuario.nome
        if processo.coordenador
        else 'Coordenação de Estágios'
    )
    sup_nome = processo.supervisor.usuario.nome if processo.supervisor else 'Representante Legal'
    sup_cargo = processo.supervisor.cargo if processo.supervisor else ''
    assinante_empresa = empresa.responsavel_legal_nome or sup_nome

    elems = [
        Paragraph('IBMEC RJ', titulo_st),
        Paragraph('TERMO DE COMPROMISSO DE ESTÁGIO', subtitulo_st),
        Paragraph(
            'Pelo presente instrumento, e na melhor forma de direito, as partes abaixo '
            'identificadas celebram o presente Termo de Compromisso de Estágio (TCE), '
            'nos termos da Lei nº 11.788, de 25 de setembro de 2008.',
            corpo_st,
        ),
        Spacer(1, 0.3 * cm),

        Paragraph('DADOS DA INSTITUIÇÃO DE ENSINO', clausula_st),
        Paragraph('Instituição: IBMEC RJ', corpo_st),
        Paragraph('Endereço: Rio de Janeiro – RJ', corpo_st),

        Paragraph('DADOS DA EMPRESA CONCEDENTE', clausula_st),
        Paragraph(f'Razão Social: {empresa.razao_social}', corpo_st),
        Paragraph(f'CNPJ: {empresa.cnpj}', corpo_st),
        Paragraph(f'Endereço: {empresa.localizacao}', corpo_st),
        Paragraph(f'E-mail: {empresa.email_contato}', corpo_st),
    ]

    if empresa.responsavel_legal_nome:
        cargo_resp = f' — {empresa.responsavel_legal_cargo}' if empresa.responsavel_legal_cargo else ''
        elems.append(Paragraph(
            f'Responsável Legal: {empresa.responsavel_legal_nome}{cargo_resp}',
            corpo_st,
        ))

    if processo.supervisor:
        elems += [
            Paragraph(f'Supervisor(a): {sup_nome}', corpo_st),
            Paragraph(f'Cargo: {sup_cargo}', corpo_st),
        ]

    elems += [
        Paragraph('DADOS DO ESTAGIÁRIO', clausula_st),
        Paragraph(f'Nome: {aluno.usuario.nome}', corpo_st),
        Paragraph(f'CPF: {aluno.cpf}', corpo_st),
        Paragraph(f'RG: {aluno.rg or "—"}', corpo_st),
        Paragraph(f'Curso: {curso_nome}', corpo_st),
        Paragraph(f'E-mail Institucional: {aluno.usuario.email_institucional or "—"}', corpo_st),

        Paragraph(
            'CLÁUSULA 1ª — BASE LEGAL',
            clausula_st,
        ),
        Paragraph(
            'Este Termo de Compromisso de Estágio reger-se-á pela Lei nº 11.788, de 25 de '
            'setembro de 2008, e pelas normas de estágio do IBMEC RJ.',
            corpo_st,
        ),

        Paragraph('CLÁUSULA 2ª — JORNADA E VIGÊNCIA', clausula_st),
        Paragraph(
            f'As atividades de estágio serão cumpridas pelo(a) estagiário(a) em jornada de '
            f'{processo.horas_semanais} horas semanais, no período de '
            f'{processo.data_inicio_prevista} a {processo.data_fim_prevista}. '
            'A jornada deverá ser compatível com o horário escolar do(a) estagiário(a).',
            corpo_st,
        ),
    ]

    if processo.valor_bolsa is not None:
        elems.append(Paragraph(
            f'O(a) estagiário(a) receberá bolsa-auxílio mensal no valor de '
            f'R$ {processo.valor_bolsa:.2f}.',
            corpo_st,
        ))

    if processo.valor_auxilio_transporte is not None:
        elems.append(Paragraph(
            f'O(a) estagiário(a) receberá auxílio transporte mensal no valor de '
            f'R$ {processo.valor_auxilio_transporte:.2f}.',
            corpo_st,
        ))

    elems += [
        Paragraph('CLÁUSULA 3ª — INTERRUPÇÃO', clausula_st),
        Paragraph(
            'Constituem motivos para interrupção automática deste Termo: a conclusão ou '
            'abandono do curso; o trancamento de matrícula; o descumprimento das condições '
            'aqui estabelecidas.',
            corpo_st,
        ),

        Paragraph('CLÁUSULA 4ª — SEGURO', clausula_st),
        Paragraph(
            'Na vigência deste Termo, o(a) estagiário(a) estará coberto(a) por seguro contra '
            'acidentes pessoais, conforme apólice contratada pela empresa concedente, nos '
            'termos do Art. 9º, IV da Lei 11.788/08.',
            corpo_st,
        ),
        Paragraph(
            f'Nº da Apólice de Seguro: {processo.numero_seguro or "A definir"}',
            corpo_st,
        ),

        Paragraph('CLÁUSULA 5ª — VÍNCULO', clausula_st),
        Paragraph(
            'O presente estágio não gera vínculo empregatício de qualquer natureza entre '
            'o(a) estagiário(a) e a empresa concedente, nos termos do Art. 3º da Lei 11.788/08.',
            corpo_st,
        ),

        Paragraph('CLÁUSULA 6ª — OBRIGAÇÕES DA EMPRESA', clausula_st),
        Paragraph(
            'Caberá à empresa concedente: a) proporcionar atividades de aprendizagem '
            'compatíveis com a formação do(a) estagiário(a); b) oferecer condições de '
            'acompanhamento e supervisão; c) fornecer à instituição de ensino os subsídios '
            'necessários para supervisão e avaliação do estágio.',
            corpo_st,
        ),

        Paragraph('CLÁUSULA 7ª — OBRIGAÇÕES DO ESTAGIÁRIO', clausula_st),
        Paragraph(
            'Caberá ao(à) estagiário(a): a) cumprir com empenho a programação do estágio; '
            'b) observar as normas internas da empresa concedente; c) elaborar e entregar '
            'relatórios conforme prazos estabelecidos.',
            corpo_st,
        ),

        Paragraph('CLÁUSULA 8ª — PLANO DE ATIVIDADES', clausula_st),
        Paragraph('As atividades a serem desenvolvidas pelo(a) estagiário(a) são:', corpo_st),
        Paragraph(processo.plano_atividades, corpo_st),

        Paragraph('CLÁUSULA 9ª — FORO', clausula_st),
        Paragraph(
            'As partes elegem o foro da comarca do Rio de Janeiro — RJ para dirimir quaisquer '
            'questões oriundas deste instrumento.',
            corpo_st,
        ),

        Spacer(1, 0.5 * cm),
        Paragraph(
            'E, por estarem de inteiro e comum acordo, as partes assinam o presente '
            'instrumento em 3 (três) vias de igual teor.',
            corpo_st,
        ),
        Spacer(1, 1 * cm),

        _linha_assinatura('INSTITUIÇÃO DE ENSINO', f'Coordenador(a): {coord_nome}'),
        Spacer(1, 0.8 * cm),
        _linha_assinatura('EMPRESA CONCEDENTE', assinante_empresa),
        Spacer(1, 0.8 * cm),
        _linha_assinatura('ESTAGIÁRIO(A)', aluno.usuario.nome),
    ]

    if processo.professor_orientador:
        elems += [
            Spacer(1, 0.8 * cm),
            _linha_assinatura(
                'PROFESSOR(A) ORIENTADOR(A)',
                processo.professor_orientador.nome,
            ),
        ]

    doc.build(elems)
    buffer.seek(0)
    return buffer


# ── Termo de Realização ────────────────────────────────────────────────────────

def gerar_termo_realizacao(processo):
    """Gera o Termo de Realização de Estágio (Art. 9º, V — Lei 11.788/08)."""
    buffer = io.BytesIO()
    doc = _make_doc(buffer)
    titulo_st, subtitulo_st, corpo_st, clausula_st = _styles()

    aluno = processo.aluno
    empresa = processo.empresa
    curso_nome = aluno.curso.nome if aluno.curso else '—'
    coord_nome = (
        processo.coordenador.usuario.nome
        if processo.coordenador
        else 'Coordenação de Estágios'
    )
    sup_nome = (
        processo.supervisor.usuario.nome
        if processo.supervisor
        else 'representante da empresa'
    )
    hoje = _data_extenso(date.today())
    data_inicio = processo.data_inicio_real or processo.data_inicio_prevista
    data_fim = processo.data_fim_real or processo.data_fim_prevista

    elems = [
        Paragraph('IBMEC RJ', titulo_st),
        Paragraph('TERMO DE REALIZAÇÃO DE ESTÁGIO', subtitulo_st),

        Paragraph(
            f'Declaramos, para os devidos fins, que o(a) estudante '
            f'<b>{aluno.usuario.nome}</b>, CPF {aluno.cpf}, matriculado(a) no curso de '
            f'<b>{curso_nome}</b> do IBMEC RJ, realizou estágio obrigatório na empresa '
            f'<b>{empresa.razao_social}</b>, CNPJ {empresa.cnpj}, no período de '
            f'<b>{data_inicio}</b> a <b>{data_fim}</b>, '
            f'cumprindo jornada de <b>{processo.horas_semanais} horas semanais</b>, '
            f'sob a supervisão de {sup_nome}.',
            corpo_st,
        ),
    ]

    if processo.plano_atividades and processo.plano_atividades.strip():
        elems += [
            Paragraph(
                'Durante esse período, o(a) estagiário(a) realizou as seguintes atividades:',
                corpo_st,
            ),
            Paragraph(processo.plano_atividades, corpo_st),
        ]

    elems += [
        Spacer(1, 0.5 * cm),
        Paragraph(f'Rio de Janeiro, {hoje}.', corpo_st),
        Spacer(1, 1 * cm),

        _linha_assinatura(
            'EMPRESA CONCEDENTE',
            f'{empresa.razao_social} — CNPJ {empresa.cnpj}\n{sup_nome}',
        ),
        Spacer(1, 0.8 * cm),
        _linha_assinatura(
            'IBMEC RJ',
            f'Coordenação de Estágios\n{coord_nome}',
        ),
    ]

    if processo.professor_orientador:
        elems += [
            Spacer(1, 0.8 * cm),
            _linha_assinatura(
                'PROFESSOR(A) ORIENTADOR(A)',
                processo.professor_orientador.nome,
            ),
        ]

    doc.build(elems)
    buffer.seek(0)
    return buffer


# ── Relatório de Estágio (ABNT) ───────────────────────────────────────────────

def gerar_relatorio_estagio(processo, dados):
    """Gera o Relatório de Estágio (parcial ou final) no formato ABNT.

    dados (dict):
        tipo_relatorio           : "parcial" | "final"
        resumo                   : str
        introducao               : str
        apresentacao_empresa     : str (opcional)
        atividades_desenvolvidas : str
        analise_critica          : str
        conclusao                : str
    """
    buffer = io.BytesIO()
    titulo_st, subtitulo_st, corpo_st, clausula_st = _styles()

    aluno = processo.aluno
    empresa = processo.empresa
    curso_nome = aluno.curso.nome if aluno.curso else 'Não informado'
    ano_atual = date.today().year
    tipo = dados.get('tipo_relatorio', 'parcial').lower()
    eh_final = tipo == 'final'

    titulo_relatorio = (
        'RELATÓRIO FINAL DE ESTÁGIO SUPERVISIONADO'
        if eh_final
        else 'RELATÓRIO DE ESTÁGIO SUPERVISIONADO'
    )
    requisito_texto = 'requisito final' if eh_final else 'requisito parcial'

    orientador_nome = (
        processo.professor_orientador.nome
        if processo.professor_orientador
        else (
            processo.coordenador.usuario.nome
            if processo.coordenador
            else 'Coordenação de Estágios'
        )
    )
    sup_nome = (
        processo.supervisor.usuario.nome
        if processo.supervisor
        else 'Representante da Empresa'
    )
    coord_nome = (
        processo.coordenador.usuario.nome
        if processo.coordenador
        else 'Coordenação de Estágios'
    )
    data_inicio = processo.data_inicio_real or processo.data_inicio_prevista
    data_fim = processo.data_fim_real or processo.data_fim_prevista

    base = getSampleStyleSheet()
    recuo_st = ParagraphStyle(
        'recuo_abnt',
        parent=base['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        leftIndent=8 * cm,
        spaceAfter=8,
    )
    cabecalho_st = ParagraphStyle(
        'cabecalho_abnt',
        parent=base['Title'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=18,
        spaceAfter=6,
    )
    secao_st = ParagraphStyle(
        'secao_abnt',
        parent=base['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=18,
        spaceBefore=14,
        spaceAfter=6,
    )

    # ── Capa ──────────────────────────────────────────────────────────────
    capa = [
        Paragraph('IBMEC RJ', cabecalho_st),
        Paragraph(curso_nome, subtitulo_st),
        Spacer(1, 3 * cm),
        Paragraph(aluno.usuario.nome.upper(), cabecalho_st),
        Spacer(1, 3 * cm),
        Paragraph(titulo_relatorio, subtitulo_st),
        Spacer(1, 4 * cm),
        Paragraph('Rio de Janeiro', corpo_st),
        Paragraph(str(ano_atual), corpo_st),
    ]

    # ── Folha de Rosto ────────────────────────────────────────────────────
    folha_rosto = [
        Paragraph(aluno.usuario.nome.upper(), cabecalho_st),
        Spacer(1, 1 * cm),
        Paragraph(titulo_relatorio, subtitulo_st),
        Spacer(1, 1 * cm),
        Paragraph(
            f'Relatório apresentado ao IBMEC RJ como {requisito_texto} para aprovação '
            'na disciplina de Estágio Supervisionado.',
            recuo_st,
        ),
        Paragraph(f'Orientador(a): {orientador_nome}', recuo_st),
        Spacer(1, 4 * cm),
        Paragraph('Rio de Janeiro', corpo_st),
        Paragraph(str(ano_atual), corpo_st),
    ]

    # ── Conteúdo ──────────────────────────────────────────────────────────
    descricao_empresa = (
        f'Razão Social: {empresa.razao_social}\n'
        f'CNPJ: {empresa.cnpj}\n'
        f'Localização: {empresa.localizacao}\n'
        f'E-mail: {empresa.email_contato}'
    )
    if getattr(empresa, 'descricao', ''):
        descricao_empresa += f'\n\n{empresa.descricao}'
    complemento = dados.get('apresentacao_empresa', '').strip()
    if complemento:
        descricao_empresa += f'\n\n{complemento}'

    conteudo = [
        Paragraph('1. RESUMO', secao_st),
        Paragraph(dados.get('resumo', ''), corpo_st),

        Paragraph('2. INTRODUÇÃO', secao_st),
        Paragraph(dados.get('introducao', ''), corpo_st),

        Paragraph('3. APRESENTAÇÃO DA EMPRESA', secao_st),
        Paragraph(descricao_empresa.replace('\n', '<br/>'), corpo_st),

        Paragraph('4. PLANO DE ATIVIDADES', secao_st),
        Paragraph(processo.plano_atividades, corpo_st),

        Paragraph('5. ATIVIDADES DESENVOLVIDAS', secao_st),
        Paragraph(dados.get('atividades_desenvolvidas', ''), corpo_st),

        Paragraph('6. ANÁLISE CRÍTICA', secao_st),
        Paragraph(dados.get('analise_critica', ''), corpo_st),

        Paragraph('7. CONCLUSÃO', secao_st),
        Paragraph(dados.get('conclusao', ''), corpo_st),
    ]

    # ── Folha de Aprovação ────────────────────────────────────────────────
    folha_aprovacao = [
        Paragraph('FOLHA DE APROVAÇÃO', cabecalho_st),
        Spacer(1, 0.4 * cm),
        Paragraph(f'Aluno(a): {aluno.usuario.nome}', corpo_st),
        Paragraph(f'CPF: {aluno.cpf}', corpo_st),
        Paragraph(f'Curso: {curso_nome}', corpo_st),
        Paragraph(f'Período: {data_inicio} a {data_fim}', corpo_st),
        Paragraph(f'Empresa: {empresa.razao_social}', corpo_st),
        Paragraph(f'Supervisor(a): {sup_nome}', corpo_st),
        Spacer(1, 1 * cm),
        _linha_assinatura('PROFESSOR(A) ORIENTADOR(A) / COORDENADOR(A)', orientador_nome),
        Spacer(1, 0.8 * cm),
        _linha_assinatura('SUPERVISOR(A) DA EMPRESA', sup_nome),
        Spacer(1, 0.8 * cm),
        _linha_assinatura('COORDENADOR(A) DO CURSO', coord_nome),
    ]

    all_elems = (
        capa + [Spacer(1, 0.1 * cm)]
        + folha_rosto + [Spacer(1, 0.1 * cm)]
        + conteudo + [Spacer(1, 0.1 * cm)]
        + folha_aprovacao
    )

    doc = _make_doc(buffer)
    doc.build(all_elems)
    buffer.seek(0)
    return buffer


# ── Relatório de Avaliação (formulário dinâmico) ──────────────────────────────

_NOTA_LABEL = {1: '1 — Ruim', 2: '2 — Regular', 3: '3 — Bom', 4: '4 — Ótimo'}

_MESES_EXTENSO = [
    '', 'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
    'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro',
]


def _tabela_avaliacao(dados_tabela, col_widths, row_heights=None):
    """Cria Table com estilo padrão. Aceita Paragraph nas células para word-wrap."""
    t = Table(dados_tabela, colWidths=col_widths, rowHeights=row_heights, splitByRow=True)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    return t


# Estilos compartilhados para células de tabela com word-wrap
_TD_LEFT = ParagraphStyle(
    'td_left', fontName='Helvetica', fontSize=8, leading=10, alignment=0,
)
_TD_LEFT_BOLD = ParagraphStyle(
    'td_left_bold', fontName='Helvetica-Bold', fontSize=8, leading=10, alignment=0,
)
_TD_CENTER = ParagraphStyle(
    'td_center', fontName='Helvetica', fontSize=8, leading=10, alignment=1,
)
_TH = ParagraphStyle(
    'th', fontName='Helvetica-Bold', fontSize=8, leading=10, alignment=1,
)
_TD_DESC = ParagraphStyle(
    'td_desc', fontName='Helvetica-Oblique', fontSize=7, leading=9,
    alignment=0, textColor=colors.grey,
)


def _p(text, style=_TD_LEFT):
    """Envolve string em Paragraph (para word-wrap em células de tabela)."""
    if text is None:
        return ''
    return Paragraph(str(text), style)


def _kv_table(rows, usable_w):
    """Tabela 2x2 (label/valor) lado a lado, compatível com formato do PO."""
    col_label = 3.5 * cm
    col_val = (usable_w - 2 * col_label) / 2
    grid_rows = []
    for i in range(0, len(rows), 2):
        a = rows[i]
        b = rows[i + 1] if i + 1 < len(rows) else ('', '')
        grid_rows.append([
            _p(a[0], _TD_LEFT_BOLD), _p(a[1], _TD_LEFT),
            _p(b[0], _TD_LEFT_BOLD), _p(b[1], _TD_LEFT),
        ])
    t = Table(grid_rows, colWidths=[col_label, col_val, col_label, col_val])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    return t


def _kv_table_full(rows, usable_w):
    """Tabela 2 colunas (label / valor) ocupando largura total — usada para empresa."""
    col_label = 4.5 * cm
    col_val = usable_w - col_label
    body = [[_p(r[0], _TD_LEFT_BOLD), _p(r[1], _TD_LEFT)] for r in rows]
    t = Table(body, colWidths=[col_label, col_val])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    return t


def _texto_livre(label, valor, corpo_st):
    """Renderiza um campo de texto livre como label + parágrafo."""
    elems = []
    if label:
        elems.append(Paragraph(f'<b>{label}:</b>', corpo_st))
    if valor and str(valor).strip():
        elems.append(Paragraph(str(valor), corpo_st))
    else:
        elems.append(Paragraph('—', corpo_st))
    return elems


def _rodape_paginacao(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.grey)
    txt = f'Relatório de Estágio Supervisionado – Alunos    Página {doc.page} de {{nb}}'
    # ReportLab não tem total de páginas direto sem 2-pass; usamos placeholder visual
    # simplificado (somente página atual + total desconhecido seria feio). Por
    # simplicidade, mostramos só o número da página atual.
    txt_simples = f'Relatório de Estágio Supervisionado – Alunos    Página {doc.page}'
    canvas.drawRightString(A4[0] - 2.5 * cm, 1.2 * cm, txt_simples)
    canvas.restoreState()


def gerar_relatorio_avaliacao(processo, modelo, respostas):
    """Gera o PDF de Avaliação do Estágio no formato do docx oficial do PO."""
    buffer = io.BytesIO()
    doc = _make_doc(buffer)
    titulo_st, subtitulo_st, corpo_st, clausula_st = _styles()

    cabec_st = ParagraphStyle(
        'cabec_po', parent=corpo_st, fontName='Helvetica-Bold',
        fontSize=12, alignment=1, leading=15, spaceAfter=2,
    )
    cabec_sub_st = ParagraphStyle(
        'cabec_sub_po', parent=corpo_st, fontName='Helvetica',
        fontSize=8, alignment=1, leading=11, spaceAfter=4,
    )
    titulo_relatorio_st = ParagraphStyle(
        'titulo_relatorio_po', parent=corpo_st, fontName='Helvetica-Bold',
        fontSize=12, alignment=1, leading=15, spaceBefore=8, spaceAfter=8,
    )
    intro_st = ParagraphStyle(
        'intro_po', parent=corpo_st, fontSize=9, alignment=4, leading=12, spaceAfter=10,
    )
    secao_st = ParagraphStyle(
        'secao_po', parent=corpo_st, fontName='Helvetica-Bold',
        fontSize=11, leading=14, spaceBefore=14, spaceAfter=6,
    )
    secao_sub_st = ParagraphStyle(
        'secao_sub_po', parent=corpo_st, fontName='Helvetica-Oblique',
        fontSize=8, leading=11, textColor=colors.grey, spaceAfter=6,
    )

    aluno = processo.aluno
    empresa = processo.empresa
    curso_nome = aluno.curso.nome.upper() if aluno.curso else '—'
    data_inicio = processo.data_inicio_real or processo.data_inicio_prevista
    data_fim = processo.data_fim_real or processo.data_fim_prevista
    hoje = date.today()

    orientador_nome = (
        processo.professor_orientador.nome
        if getattr(processo, 'professor_orientador', None)
        else (
            processo.coordenador.usuario.nome
            if processo.coordenador
            else 'Coordenação de Estágios'
        )
    )
    sup_nome = processo.supervisor.usuario.nome if processo.supervisor else None

    semanas = max(1, (data_fim - data_inicio).days // 7) if data_inicio and data_fim else 0
    horas_totais = semanas * processo.horas_semanais

    usable_w = 16 * cm

    # ── Cabeçalho institucional ──────────────────────────────────────────
    elems = [
        Paragraph('CENTRO UNIVERSITÁRIO IBMEC', cabec_st),
        Paragraph(
            'Credenciada pela Portaria nº 223 de 14/03/2018 DOU 15/03/2018',
            cabec_sub_st,
        ),
        Spacer(1, 0.3 * cm),
        Paragraph('RELATÓRIO DE AVALIAÇÃO DO ESTÁGIO PELO ESTAGIÁRIO', titulo_relatorio_st),
        Paragraph(
            'O relatório de avaliação é um instrumento que tem por objetivo acompanhar o estágio. '
            'O preenchimento completo e correto auxiliará no acompanhamento realizado pelo '
            'Centro Universitário Ibmec.',
            intro_st,
        ),
    ]

    def render_data(d):
        return d.strftime('%d/%m/%Y') if d else '—'

    def render_money(v):
        return f'R$ {float(v):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.') if v is not None else '—'

    # ── Itera as seções do modelo ────────────────────────────────────────
    for secao in modelo.secoes:
        tipo = secao.get('tipo')
        titulo_secao = secao.get('titulo', '')
        sid = secao.get('id')
        itens = secao.get('itens', [])
        itens_detalhados = secao.get('itens_detalhados', [])
        colunas = secao.get('colunas', [])
        descricao = secao.get('descricao')
        valor = respostas.get(sid)
        texto_geral = respostas.get(f'{sid}_texto') if sid else None
        texto_pos = respostas.get(f'{sid}_texto_positivo') if sid else None
        texto_neg = respostas.get(f'{sid}_texto_negativo') if sid else None
        efetivacao = respostas.get(f'{sid}_efetivacao') if sid else None

        elems.append(Paragraph(titulo_secao, secao_st))
        if descricao:
            elems.append(Paragraph(descricao, secao_sub_st))

        # ── auto — seções 1 e 2 (dados do processo) ─────────────────────
        if tipo == 'auto' and sid == 'estagiario':
            rows = [
                ('Nome', aluno.usuario.nome),
                ('Matrícula', aluno.usuario.username),
                ('Curso', curso_nome),
                ('Semestre atual', f'{aluno.periodo_atual}º' if aluno.periodo_atual else '—'),
                ('Data de entrada', render_data(data_inicio)),
                ('Data de saída', render_data(data_fim)),
                ('Horas/semana', f'{processo.horas_semanais}'),
                ('Semanas trabalhadas', f'{semanas}'),
                ('Horas totais', f'{horas_totais}'),
                ('Remuneração média', render_money(processo.valor_bolsa)),
            ]
            elems.append(_kv_table(rows, usable_w))
        elif tipo == 'auto' and sid == 'empresa':
            telefone = '—'
            website = '—'
            email_gestor = empresa.email_contato or '—'
            gestor_nome = sup_nome or empresa.responsavel_legal_nome or '—'
            rows = [
                ['Empresa', empresa.razao_social],
                ['CNPJ', empresa.cnpj],
                ['Localização', empresa.localizacao or '—'],
                ['Telefone', telefone],
                ['Website', website],
                ['Gestor direto', gestor_nome],
                ['Email do gestor', email_gestor],
            ]
            elems.append(_kv_table_full(rows, usable_w))

        # ── checkbox_duplo (seção 3) ────────────────────────────────────
        elif tipo == 'checkbox_duplo':
            n_cols = max(1, len(colunas))
            col_w_first = 5.5 * cm
            col_w = (usable_w - col_w_first) / n_cols
            header = [_p('Item', _TH)] + [_p(c, _TH) for c in colunas]
            rows = [header]
            for item in itens:
                marcados = (valor or {}).get(item, []) if isinstance(valor, dict) else []
                rows.append(
                    [_p(item, _TD_LEFT)]
                    + [_p('✓' if c in marcados else '', _TD_CENTER) for c in colunas]
                )
            elems.append(_tabela_avaliacao(rows, [col_w_first] + [col_w] * n_cols))
            if secao.get('campo_texto'):
                elems.append(Spacer(1, 0.2 * cm))
                elems += _texto_livre(secao['campo_texto'], texto_geral, corpo_st)

        # ── escala_3 (seção 4) ──────────────────────────────────────────
        elif tipo == 'escala_3':
            opcoes = secao.get('opcoes', ['Suficiente', 'Insuficiente', 'Não utilizado'])
            n_op = max(1, len(opcoes))
            col_w_first = 8 * cm
            col_w = (usable_w - col_w_first) / n_op
            header = [_p('Disciplina', _TH)] + [_p(o, _TH) for o in opcoes]
            rows = [header]
            for item in itens:
                resp = (valor or {}).get(item) if isinstance(valor, dict) else None
                rows.append(
                    [_p(item, _TD_LEFT)]
                    + [_p('✓' if resp == o else '', _TD_CENTER) for o in opcoes]
                )
            elems.append(_tabela_avaliacao(rows, [col_w_first] + [col_w] * n_op))
            if secao.get('campo_texto'):
                elems.append(Spacer(1, 0.2 * cm))
                elems += _texto_livre(secao['campo_texto'], texto_geral, corpo_st)

        # ── escala_1_4_multi (seção 5) ──────────────────────────────────
        elif tipo == 'escala_1_4_multi':
            n_cols = max(1, len(colunas))
            col_w_first = 5 * cm
            col_w = (usable_w - col_w_first) / n_cols
            header = [_p('Software', _TH)] + [_p(c, _TH) for c in colunas]
            rows = [header]
            for item in itens:
                notas_item = (valor or {}).get(item, {}) if isinstance(valor, dict) else {}
                linha = [_p(item, _TD_LEFT)]
                for col in colunas:
                    n = notas_item.get(col) if isinstance(notas_item, dict) else None
                    linha.append(_p(str(n) if n is not None else '—', _TD_CENTER))
                rows.append(linha)
            elems.append(_tabela_avaliacao(rows, [col_w_first] + [col_w] * n_cols))
            if secao.get('campo_texto'):
                elems.append(Spacer(1, 0.2 * cm))
                elems += _texto_livre(secao['campo_texto'], texto_geral, corpo_st)

        # ── escala_1_4 (seções 6 e 7) ───────────────────────────────────
        elif tipo == 'escala_1_4':
            # Detalha descrição do item se houver itens_detalhados
            detalhes_map = {d.get('nome'): d.get('descricao', '') for d in itens_detalhados}
            rows = [[_p('Item', _TH), _p('Nota', _TH)]]
            for item in itens:
                nota_raw = (valor or {}).get(item) if isinstance(valor, dict) else None
                nota_str = _NOTA_LABEL.get(nota_raw, '—')
                if detalhes_map.get(item):
                    # Combina nome em bold + descrição em parágrafo único (Paragraph
                    # respeita <br/> e <font>).
                    cell_html = (
                        f'<font name="Helvetica-Bold" size="9">{item}</font><br/>'
                        f'<font size="7" color="grey">{detalhes_map[item]}</font>'
                    )
                    rows.append([Paragraph(cell_html, _TD_LEFT), _p(nota_str, _TD_CENTER)])
                else:
                    rows.append([_p(item, _TD_LEFT), _p(nota_str, _TD_CENTER)])
            elems.append(_tabela_avaliacao(rows, [11.5 * cm, 4.5 * cm]))
            # Campos extras de texto / efetivação (seção 7)
            extras = []
            if secao.get('campo_efetivacao'):
                extras.append(Spacer(1, 0.2 * cm))
                extras += _texto_livre('Há proposta de efetivação ao final do estágio?', efetivacao, corpo_st)
            if secao.get('campo_texto_positivo'):
                extras.append(Spacer(1, 0.2 * cm))
                extras += _texto_livre(secao['campo_texto_positivo'], texto_pos, corpo_st)
            if secao.get('campo_texto_negativo'):
                extras.append(Spacer(1, 0.2 * cm))
                extras += _texto_livre(secao['campo_texto_negativo'], texto_neg, corpo_st)
            elems += extras

        # ── texto_livre (legado) ────────────────────────────────────────
        elif tipo == 'texto_livre':
            elems += _texto_livre(None, valor, corpo_st)

    # ── Rodapé: data + assinaturas lado a lado ───────────────────────────
    elems += [
        Spacer(1, 1 * cm),
        Paragraph(f'Rio de Janeiro, {_data_extenso(hoje)}.', corpo_st),
        Spacer(1, 1.2 * cm),
    ]
    assinaturas = Table(
        [
            ['_' * 30, '_' * 30],
            [aluno.usuario.nome, orientador_nome],
            ['Aluno(a)', 'Professor responsável\npela supervisão do estágio'],
        ],
        colWidths=[usable_w / 2, usable_w / 2],
    )
    assinaturas.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elems.append(assinaturas)

    doc.build(elems, onFirstPage=_rodape_paginacao, onLaterPages=_rodape_paginacao)
    buffer.seek(0)
    return buffer
