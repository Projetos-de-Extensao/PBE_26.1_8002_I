"""
Management command: seed_completo

Cenário grande de demonstração:
- 7 cursos × 10 alunos = 70 alunos
- Senha padrão fácil para todos: 'senha123'
- 3 documentos por aluno (TCE, Apólice, Carta de apresentação)
- 100% dos alunos com respostas_formulario preenchidas (notas variadas)
- Status de processo distribuído: ~50% ATIVO, ~25% ENCERRADO, ~15% PENDENTE, ~10% APROVADO
- Semestres variados: 2025.2, 2026.1, 2026.2
- 6 empresas e supervisores

Uso:
    python3 manage.py seed_completo            # pede confirmação
    python3 manage.py seed_completo --force    # sem confirmação
"""
import random
import unicodedata
from datetime import date, datetime, timedelta, time
from decimal import Decimal

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from app.models import (
    Usuario, Curso, EmpresaConcedente,
    Aluno, Coordenador, SupervisorEmpresa,
    ProcessoEstagio, DocumentoProcesso, LogDocumento,
    ModeloFormulario,
)


PASSWORD = 'senha123'
PDF_BYTES = (
    b'%PDF-1.4\n%mock seed_completo\n'
    b'1 0 obj <<>> endobj\n'
    b'trailer <<>>\nstartxref\n0\n%%EOF\n'
)


def slugify_nome(nome):
    """Converte 'João da Silva' em 'joao.silva' (sem acentos)."""
    nome_norm = unicodedata.normalize('NFKD', nome)
    s = ''.join(c for c in nome_norm if not unicodedata.combining(c))
    partes = [p for p in s.lower().split() if p not in {'da', 'de', 'do', 'das', 'dos'}]
    if len(partes) < 2:
        return partes[0] if partes else 'aluno'
    return f'{partes[0]}.{partes[-1]}'


# ── Cursos do cenário (slug → nome) ──────────────────────────────────────
CURSOS = [
    ('cdia',  'Ciência de Dados e Inteligência Artificial'),
    ('engs',  'Engenharia de Software'),
    ('arq',   'Arquitetura e Urbanismo'),
    ('dir',   'Direito'),
    ('adm',   'Administração'),
    ('pub',   'Comunicação Social – Publicidade e Propaganda'),
    ('engcv', 'Engenharia Civil'),
]


# ── 1 coordenador por curso ──────────────────────────────────────────────
COORDENADORES = [
    ('Prof. Dr. João Oliveira',       'joao.oliveira@ibmec.edu.br',      'cdia'),
    ('Prof. Dr. Lucas Costa',         'lucas.costa@ibmec.edu.br',        'engs'),
    ('Profa. Dra. Mariana Ribeiro',   'mariana.ribeiro@ibmec.edu.br',    'arq'),
    ('Profa. Dra. Beatriz Fernandes', 'beatriz.fernandes@ibmec.edu.br',  'dir'),
    ('Prof. Dr. Marcelo Tavares',     'marcelo.tavares@ibmec.edu.br',    'adm'),
    ('Prof. Dr. Fernando Lima',       'fernando.lima@ibmec.edu.br',      'pub'),
    ('Prof. Dr. Clayton Silva',       'clayton.silva@ibmec.edu.br',      'engcv'),
]


# ── 6 empresas ───────────────────────────────────────────────────────────
EMPRESAS = [
    {'razao_social': 'Tech Solutions Ltda',           'cnpj': '12.345.678/0001-90', 'areas_atuacao': 'Tecnologia · Desenvolvimento de Software',  'localizacao': 'Rio de Janeiro, RJ', 'email_contato': 'contato@techsolutions.com.br', 'responsavel_legal_nome': 'Roberto Mendes Cardoso',  'responsavel_legal_cargo': 'Diretor Executivo'},
    {'razao_social': 'Construtora Horizonte S.A.',    'cnpj': '23.456.789/0001-01', 'areas_atuacao': 'Construção Civil · Engenharia',            'localizacao': 'Rio de Janeiro, RJ', 'email_contato': 'rh@horizonte.com.br',          'responsavel_legal_nome': 'Cláudia Lima Vasconcellos','responsavel_legal_cargo': 'Presidente'},
    {'razao_social': 'Banco Capital Investimentos',   'cnpj': '34.567.890/0001-12', 'areas_atuacao': 'Finanças · Mercado de Capitais',            'localizacao': 'São Paulo, SP',      'email_contato': 'estagio@bancocapital.com.br',  'responsavel_legal_nome': 'Henrique Sampaio Marques','responsavel_legal_cargo': 'CEO'},
    {'razao_social': 'Agência Criativa Digital',      'cnpj': '45.678.901/0001-23', 'areas_atuacao': 'Marketing · Publicidade',                   'localizacao': 'Rio de Janeiro, RJ', 'email_contato': 'rh@agcriativa.com.br',         'responsavel_legal_nome': 'Patrícia Lobo Fernandes', 'responsavel_legal_cargo': 'CEO'},
    {'razao_social': 'Escritório Machado & Assoc.',   'cnpj': '56.789.012/0001-34', 'areas_atuacao': 'Advocacia · Direito Empresarial',           'localizacao': 'Rio de Janeiro, RJ', 'email_contato': 'contato@machadoassoc.adv.br',  'responsavel_legal_nome': 'José Machado Filho',      'responsavel_legal_cargo': 'Sócio Fundador'},
    {'razao_social': 'DataMind Analytics',            'cnpj': '89.012.345/0001-67', 'areas_atuacao': 'Dados · IA · BI',                           'localizacao': 'Rio de Janeiro, RJ', 'email_contato': 'rh@datamind.ai',               'responsavel_legal_nome': 'Letícia Sampaio Furtado', 'responsavel_legal_cargo': 'CEO'},
]


# 1 supervisor por empresa
SUPERVISORES = [
    ('Marcos Vinícius Santiago', 'marcos.santiago@techsolutions.com.br', 0, 'Diretor de Tecnologia'),
    ('Eliana Cristina Branco',   'eliana.branco@horizonte.com.br',       1, 'Engenheira Sênior'),
    ('Antonio Carlos Macedo',    'antonio.macedo@bancocapital.com.br',   2, 'Gerente de Operações'),
    ('Daniela Souza Rangel',     'daniela.rangel@agcriativa.com.br',     3, 'Diretora Criativa'),
    ('Roberto Almeida Pinto',    'roberto.pinto@machadoassoc.adv.br',    4, 'Sócio Advogado'),
    ('Mariana Tavares Coelho',   'mariana.tavares@datamind.ai',          5, 'Líder de Data Science'),
]


# ── Pools de nomes para gerar 70 alunos únicos ───────────────────────────
NOMES_M = [
    'Pedro', 'João', 'Lucas', 'Gabriel', 'Mateus', 'Felipe', 'Bruno', 'Rafael',
    'Thiago', 'Diego', 'Marcelo', 'Eduardo', 'Vinícius', 'Carlos', 'Henrique',
    'Daniel', 'Ricardo', 'Fernando', 'Roberto', 'André', 'Marcos', 'Antônio',
    'Paulo', 'Rodrigo', 'Leonardo', 'Caio', 'Igor', 'Erick', 'Davi', 'Murilo',
]
NOMES_F = [
    'Isabella', 'Fernanda', 'Camila', 'Letícia', 'Larissa', 'Mariana', 'Beatriz',
    'Amanda', 'Natália', 'Renata', 'Bianca', 'Sophia', 'Carolina', 'Juliana',
    'Patrícia', 'Manuela', 'Adriana', 'Daniela', 'Eliana', 'Ana', 'Vanessa',
    'Cláudia', 'Helena', 'Yasmin', 'Gabriela', 'Aline', 'Vitória', 'Eduarda',
    'Júlia', 'Sabrina',
]
SOBRENOMES = [
    'Silva', 'Santos', 'Oliveira', 'Pereira', 'Costa', 'Lima', 'Souza',
    'Carvalho', 'Almeida', 'Rodrigues', 'Ferreira', 'Martins', 'Ribeiro',
    'Gomes', 'Alves', 'Mendes', 'Castro', 'Cardoso', 'Tavares', 'Borges',
    'Reis', 'Nunes', 'Vieira', 'Andrade', 'Moreira', 'Sales', 'Pinto',
    'Fernandes', 'Marques', 'Cavalcanti', 'Barros', 'Lopes', 'Rocha',
    'Teixeira', 'Cunha', 'Faria', 'Macedo', 'Brito', 'Pinheiro', 'Aragão',
]


def gerar_70_nomes_unicos():
    """Combina primeiros nomes + sobrenomes para produzir 70 (nome, slug) únicos."""
    primeiros = NOMES_M + NOMES_F
    random.Random(99).shuffle(primeiros)
    sobrenomes_shuf = list(SOBRENOMES)
    random.Random(33).shuffle(sobrenomes_shuf)

    out = []
    slugs_usados = set()
    for p in primeiros:
        for s in sobrenomes_shuf:
            nome = f'{p} {s}'
            slug = slugify_nome(nome)
            if slug not in slugs_usados:
                out.append((nome, slug))
                slugs_usados.add(slug)
            if len(out) >= 70:
                break
        if len(out) >= 70:
            break
    return out


def fake_cpf(i):
    return f'{(100 + i):03d}.{(200 + i*3) % 1000:03d}.{(300 + i*5) % 1000:03d}-{(10 + i) % 100:02d}'


def fake_rg(i):
    return f'{(10 + i) % 100:02d}.{(100 + i*2) % 1000:03d}.{(200 + i*3) % 1000:03d}-{i % 10}'


# ── Seções de exemplo por curso ──────────────────────────────────────────
COMPETENCIAS = ['Visão', 'Adaptabilidade', 'Empatia', 'Comunicação']
EXPERIENCIA = ['Orientação do supervisor', 'Feedback do supervisor',
               'Condições de trabalho', 'Relacionamento com equipe']
FERRAMENTAS_POR_SLUG = {
    'cdia':  ['Python', 'SQL', 'Power BI', 'Git'],
    'engs':  ['Python', 'JavaScript', 'Docker', 'Git'],
    'arq':   ['AutoCAD', 'SketchUp', 'Revit', 'Photoshop'],
    'dir':   ['PJe', 'JusBrasil', 'Word', 'Excel'],
    'adm':   ['Excel', 'Power BI', 'SAP', 'PowerPoint'],
    'pub':   ['Photoshop', 'Illustrator', 'Premiere', 'Figma'],
    'engcv': ['AutoCAD', 'Revit', 'Excel', 'Project'],
}


def gerar_secoes_modelo(slug):
    return [
        {'id': 'competencias', 'tipo': 'escala_1_4',
         'titulo': 'Competências Comportamentais',
         'descricao': '1-ruim; 2-regular; 3-bom; 4-ótimo',
         'itens': COMPETENCIAS, 'grafico': 'radar'},
        {'id': 'ferramentas', 'tipo': 'escala_1_4_multi',
         'titulo': 'Utilização de Ferramentas',
         'descricao': '1-muito; 2-médio; 3-pouco; 4-nada',
         'itens': FERRAMENTAS_POR_SLUG.get(slug, FERRAMENTAS_POR_SLUG['adm']),
         'colunas': ['Pela empresa', 'Por você', 'Se sentiu apto'],
         'grafico': 'barras_agrupadas'},
        {'id': 'experiencia', 'tipo': 'escala_1_4',
         'titulo': 'Avaliação da Experiência',
         'descricao': '1-ruim; 2-regular; 3-bom; 4-ótimo',
         'itens': EXPERIENCIA, 'grafico': 'barras'},
        {'id': 'comentarios', 'tipo': 'texto_livre',
         'titulo': 'Comentários gerais', 'grafico': 'nenhum'},
    ]


COMENTARIOS_POOL = [
    'Experiência muito positiva, equipe acolhedora e supervisor presente.',
    'Desafios reais e aprendizado constante. Recomendaria a empresa.',
    'Boa cultura, processos bem definidos e oportunidade de crescimento.',
    'Atividades bem alinhadas à formação acadêmica.',
    'Ambiente colaborativo, com bastante autonomia.',
    'Acompanhamento próximo do supervisor; feedbacks construtivos.',
    'Tive contato com projetos relevantes do mercado.',
    'Bom equilíbrio entre estudo e estágio.',
]


def gerar_respostas_variadas(slug, aluno_idx):
    """Notas determinísticas por aluno_idx, com variação real entre alunos.

    A variação nas médias é o que faz os gráficos do dashboard mostrarem
    distribuição realista (não tudo igual)."""
    rnd = random.Random(2000 + aluno_idx)
    base = rnd.choice([2, 2, 3, 3, 3, 4])

    def nota(extra=0):
        return max(1, min(4, base + extra + rnd.randint(-1, 1)))

    return {
        'preenchido_em': date.today().isoformat(),
        'tipo_relatorio': 'parcial',
        'secoes': {
            'competencias': {it: nota() for it in COMPETENCIAS},
            'ferramentas': {
                it: {'Pela empresa': nota(), 'Por você': nota(), 'Se sentiu apto': nota()}
                for it in FERRAMENTAS_POR_SLUG.get(slug, FERRAMENTAS_POR_SLUG['adm'])
            },
            'experiencia': {it: nota(1 if aluno_idx % 4 == 0 else 0) for it in EXPERIENCIA},
            'comentarios': rnd.choice(COMENTARIOS_POOL),
        },
    }


def data_inicio_para_indice(i):
    """Distribui semestre de início pelos 70 alunos:
       ~30% em 2025.2, ~43% em 2026.1, ~27% em 2026.2."""
    rnd = random.Random(500 + i)
    if i < 21:        # 21 alunos em 2025.2
        return date(2025, rnd.choice([7, 8, 9, 10, 11, 12]), rnd.randint(1, 28))
    elif i < 51:      # 30 em 2026.1
        return date(2026, rnd.choice([1, 2, 3, 4, 5, 6]), rnd.randint(1, 28))
    else:             # 19 em 2026.2
        return date(2026, rnd.choice([7, 8, 9, 10, 11, 12]), rnd.randint(1, 28))


class Command(BaseCommand):
    help = 'Popula banco com cenário grande de demonstração (70 alunos).'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Sem confirmação')

    def handle(self, *args, **opts):
        if not opts['force']:
            self.stdout.write(self.style.WARNING(
                'Esta ação APAGA todos os dados (Usuario, Aluno, Curso, Empresa, Processo, etc.).'
            ))
            resp = input('Continuar? [y/N]: ')
            if resp.strip().lower() not in ('y', 'yes', 's', 'sim'):
                self.stdout.write('Cancelado.')
                return

        self.stdout.write('🧹 Limpando dados…')
        LogDocumento.objects.all().delete()
        DocumentoProcesso.objects.all().delete()
        ProcessoEstagio.objects.all().delete()
        ModeloFormulario.objects.all().delete()
        Aluno.objects.all().delete()
        SupervisorEmpresa.objects.all().delete()
        Curso.objects.update(coordenador=None)
        Coordenador.objects.all().delete()
        EmpresaConcedente.objects.all().delete()
        Curso.objects.all().delete()
        Usuario.objects.all().delete()

        self.stdout.write('👑 Superuser admin@ibmec.edu.br / admin')
        Usuario.objects.create_superuser(
            username='admin@ibmec.edu.br',
            email_institucional='admin@ibmec.edu.br',
            password='admin', tipo='coordenador', nome='Administrador IBMEC',
        )

        self.stdout.write(f'🎓 Cursos ({len(CURSOS)})…')
        cursos = {}
        for slug, nome in CURSOS:
            cursos[slug] = Curso.objects.create(
                nome=nome, carga_horaria_minima_total=300, carga_horaria_maxima_diaria=6,
            )

        self.stdout.write(f'👔 Coordenadores ({len(COORDENADORES)})…')
        coords = {}
        for nome, email, slug in COORDENADORES:
            u = Usuario.objects.create_user(
                username=email, email_institucional=email,
                password=PASSWORD, tipo='coordenador', nome=nome,
            )
            c = Coordenador.objects.create(usuario=u, departamento=cursos[slug].nome)
            cursos[slug].coordenador = c
            cursos[slug].save(update_fields=['coordenador'])
            coords[slug] = c

        self.stdout.write(f'🏢 Empresas ({len(EMPRESAS)})…')
        empresas = [EmpresaConcedente.objects.create(aprovada_ibmec=True, **d) for d in EMPRESAS]

        self.stdout.write(f'🧑‍💼 Supervisores ({len(SUPERVISORES)})…')
        supervisores = []
        for nome, email, emp_idx, cargo in SUPERVISORES:
            u = Usuario.objects.create_user(
                username=email, email_institucional=email,
                password=PASSWORD, tipo='supervisor_empresa', nome=nome,
            )
            supervisores.append(
                SupervisorEmpresa.objects.create(usuario=u, empresa=empresas[emp_idx], cargo=cargo)
            )

        self.stdout.write(f'📝 Modelos de formulário ({len(CURSOS)})…')
        modelos = {}
        for slug, nome in CURSOS:
            modelos[slug] = ModeloFormulario.objects.create(
                curso=cursos[slug], criado_por=coords[slug],
                titulo=f'Relatório de estágio - {nome}',
                secoes=gerar_secoes_modelo(slug),
                ativo=True,
            )

        # ── Gera 70 (nome, slug) e distribui 10 por curso ────────────────
        nomes70 = gerar_70_nomes_unicos()
        assert len(nomes70) == 70, f'Esperava 70 nomes, gerei {len(nomes70)}'

        self.stdout.write(f'👨‍🎓 Alunos (10 por curso × {len(CURSOS)} = 70)…')

        # Distribuição de status determinística (50/25/15/10)
        status_plan = ['ATIVO'] * 35 + ['ENCERRADO'] * 18 + ['PENDENTE'] * 10 + ['APROVADO'] * 7
        random.Random(77).shuffle(status_plan)

        contagem_por_curso = {slug: 0 for slug, _ in CURSOS}
        docs_total = 0
        com_respostas = 0

        for i, (slug_curso, _) in enumerate(CURSOS):
            nomes_curso = nomes70[i*10:(i+1)*10]
            for j, (nome, slug_user) in enumerate(nomes_curso):
                aluno_idx = i * 10 + j  # 0..69
                email = f'{slug_user}@aluno.ibmec.edu.br'
                rnd = random.Random(9000 + aluno_idx)

                # Cria Usuario + Aluno
                user = Usuario.objects.create_user(
                    username=slug_user,            # username derivado do nome (não do email)
                    email_institucional=email,
                    password=PASSWORD,
                    tipo='aluno',
                    nome=nome,
                )
                aluno = Aluno.objects.create(
                    usuario=user,
                    cpf=fake_cpf(aluno_idx),
                    rg=fake_rg(aluno_idx),
                    coeficiente_rendimento=Decimal(str(round(rnd.uniform(6.0, 9.5), 2))),
                    curso=cursos[slug_curso],
                    periodo_atual=rnd.randint(3, 10),
                    matriculado_estagio=True,
                )
                contagem_por_curso[slug_curso] += 1

                # ── Processo de estágio ──
                empresa = empresas[aluno_idx % len(empresas)]
                supervisor = supervisores[aluno_idx % len(supervisores)]
                coord = cursos[slug_curso].coordenador
                modelo = modelos[slug_curso]
                status = status_plan[aluno_idx]
                inicio = data_inicio_para_indice(aluno_idx)
                fim = inicio + timedelta(days=180)

                processo = ProcessoEstagio.objects.create(
                    aluno=aluno, empresa=empresa, supervisor=supervisor, coordenador=coord,
                    status=status,
                    horas_semanais=rnd.choice([20, 30]),
                    data_inicio_prevista=inicio, data_fim_prevista=fim,
                    plano_atividades=(
                        f'Atuação em projetos da área de '
                        f'{empresa.areas_atuacao.split("·")[0].strip()}.'
                    ),
                    valor_bolsa=Decimal(str(rnd.choice([1200, 1500, 1800, 2000, 2500, 3000]))),
                    valor_auxilio_transporte=Decimal('200') if aluno_idx % 2 == 0 else Decimal('0'),
                    modelo_formulario=modelo,
                    respostas_formulario=gerar_respostas_variadas(slug_curso, aluno_idx),
                    data_inicio_real=inicio if status in ('ATIVO', 'ENCERRADO') else None,
                    data_fim_real=fim if status == 'ENCERRADO' else None,
                )
                com_respostas += 1  # 100% têm respostas

                # ── 3 documentos para o aluno ──
                # 1) TCE (sempre aprovado)
                # 2) Apólice (≈70% aprovada, 30% pendente)
                # 3) Carta (status variado)
                docs_spec = [
                    ('Termo de Compromisso de Estágio', 'TCE',     'APROVADO'),
                    ('Apólice de Seguro',               'APOLICE', rnd.choices(['APROVADO', 'PENDENTE'], weights=[7, 3])[0]),
                    ('Carta de apresentação',           'OUTRO',   rnd.choices(['APROVADO', 'PENDENTE', 'REJEITADO'], weights=[5, 3, 2])[0]),
                ]
                for k, (titulo_doc, tipo_doc, status_doc) in enumerate(docs_spec):
                    doc = DocumentoProcesso.objects.create(
                        processo=processo,
                        titulo=titulo_doc,
                        tipo=tipo_doc,
                        status=status_doc,
                        enviado_por=user,
                        score_conformidade=round(rnd.uniform(0.6, 0.95), 2),
                        observacoes='Documento conferido pelo coordenador.' if status_doc == 'APROVADO' else None,
                    )
                    # Anexa um PDF placeholder (FileField precisa de save dedicado)
                    nome_arq = f'doc_{processo.id}_{tipo_doc.lower()}_{k}.pdf'
                    doc.arquivo.save(nome_arq, ContentFile(PDF_BYTES), save=True)

                    # data_upload tem auto_now_add — força com .update() para variar
                    dias_atras = rnd.randint(0, 180)
                    upload_dt = timezone.now() - timedelta(days=dias_atras)
                    DocumentoProcesso.objects.filter(pk=doc.pk).update(data_upload=upload_dt)

                    LogDocumento.objects.create(
                        documento=doc, acao=LogDocumento.Acao.UPLOAD, usuario=user,
                    )
                    if status_doc == 'APROVADO':
                        LogDocumento.objects.create(
                            documento=doc, acao=LogDocumento.Acao.APROVADO, usuario=coord.usuario,
                            comentario='Aprovado em conferência.',
                        )
                    elif status_doc == 'REJEITADO':
                        LogDocumento.objects.create(
                            documento=doc, acao=LogDocumento.Acao.REJEITADO, usuario=coord.usuario,
                            comentario='Documento ilegível — reenviar.',
                        )
                    docs_total += 1

        # ── Resumo ──────────────────────────────────────────────────────
        total_proc = ProcessoEstagio.objects.count()
        por_status = {}
        for p in ProcessoEstagio.objects.all():
            por_status[p.status] = por_status.get(p.status, 0) + 1

        self.stdout.write(self.style.SUCCESS('\n✅ Cenário grande populado!'))
        self.stdout.write(f'  Cursos:              {Curso.objects.count()}')
        self.stdout.write(f'  Coordenadores:       {Coordenador.objects.count()}')
        self.stdout.write(f'  Empresas:            {EmpresaConcedente.objects.count()}')
        self.stdout.write(f'  Supervisores:        {SupervisorEmpresa.objects.count()}')
        self.stdout.write(f'  Modelos formulário:  {ModeloFormulario.objects.count()}')
        self.stdout.write('')
        self.stdout.write('  ALUNOS POR CURSO:')
        for slug_curso, nome_curso in CURSOS:
            self.stdout.write(f'    {nome_curso:<55} {contagem_por_curso[slug_curso]}')
        self.stdout.write(f'  Total de alunos:     {Aluno.objects.count()}')
        self.stdout.write('')
        self.stdout.write(f'  Documentos criados:  {docs_total}')
        self.stdout.write(f'  Processos totais:    {total_proc}')
        self.stdout.write(f'  Com respostas:       {com_respostas}/{total_proc} (100%)')
        self.stdout.write(f'  Por status:          {por_status}')

        # 3 usernames de exemplo
        amostras = list(Aluno.objects.select_related('usuario', 'curso').order_by('?')[:3])
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('🔑 Logins de exemplo (senha senha123):'))
        for a in amostras:
            self.stdout.write(f'  username: {a.usuario.username:<30} | email: {a.usuario.email_institucional:<40} | curso: {a.curso.nome}')
        self.stdout.write('')
        self.stdout.write(f'  Coordenador: clayton.silva@ibmec.edu.br / senha123 (Eng. Civil)')
        self.stdout.write(f'  Admin: admin@ibmec.edu.br / admin')
