"""Geração de PDFs para o sistema de estágios IBMEC RJ.

Funções exportadas:
  gerar_tce(processo)                      → io.BytesIO
  gerar_termo_realizacao(processo)         → io.BytesIO
  gerar_relatorio_estagio(processo, dados) → io.BytesIO
"""
import io
from datetime import date

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
