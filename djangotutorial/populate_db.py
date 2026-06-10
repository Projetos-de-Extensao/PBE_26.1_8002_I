"""
Script de população do banco com dados realistas IBMEC.

Modos de execução:
    python3 populate_db.py                        # standalone
    python3 manage.py shell < populate_db.py      # via Django shell
"""
import os
import sys
import random
from datetime import date, timedelta
from decimal import Decimal

# ── Django setup (idempotente — funciona standalone e via shell) ─────────
try:
    from django.apps import apps as _apps
    if not _apps.ready:
        raise RuntimeError('apps not ready')
except Exception:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    _here = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    if _here not in sys.path:
        sys.path.insert(0, _here)
    import django
    django.setup()

from app.models import (
    Usuario, Curso, EmpresaConcedente,
    Aluno, Coordenador, SupervisorEmpresa,
    ProcessoEstagio, DocumentoProcesso, LogDocumento,
    ModeloFormulario,
)

random.seed(42)  # determinístico

PASSWORD = 'ibmec2026'

# ── DADOS ───────────────────────────────────────────────────────────────

CURSOS = [
    ('Administração', 'adm'),
    ('Arquitetura e Urbanismo', 'arq'),
    ('Ciência de Dados e Inteligência Artificial', 'cdia'),
    ('Ciências Econômicas', 'eco'),
    ('Publicidade e Propaganda', 'pub'),
    ('Direito', 'dir'),
    ('Engenharia da Computação', 'engc'),
    ('Engenharia de Produção', 'engp'),
    ('Engenharia de Software', 'engs'),
    ('Relações Internacionais', 'ri'),
]

# (curso_idx, username, nome, departamento)
COORDENADORES = [
    (0, 'carlos.almeida',    'Carlos Eduardo Almeida',     'Administração'),
    (1, 'mariana.ribeiro',   'Mariana Santos Ribeiro',     'Arquitetura'),
    (2, 'joao.oliveira',     'João Pedro Oliveira',        'Computação'),
    (3, 'patricia.carvalho', 'Patricia Mendes Carvalho',   'Economia'),
    (4, 'fernando.lima',     'Fernando Augusto Lima',      'Comunicação'),
    (5, 'beatriz.fernandes', 'Beatriz Cardoso Fernandes',  'Direito'),
    (6, 'ricardo.pereira',   'Ricardo Souza Pereira',      'Computação'),
    (7, 'camila.silva',      'Camila Rodrigues Silva',     'Engenharia'),
    (8, 'lucas.costa',       'Lucas Martins Costa',        'Computação'),
    (9, 'adriana.vieira',    'Adriana Pinheiro Vieira',    'Relações Internacionais'),
]

# (curso_idx, username, nome) — 2 por curso
ALUNOS = [
    (0, 'gabriel.silva',     'Gabriel Henrique Silva'),
    (0, 'sofia.andrade',     'Sofia Maria Andrade'),
    (1, 'fernanda.castro',   'Fernanda Oliveira Castro'),
    (1, 'rafael.borges',     'Rafael Lima Borges'),
    (2, 'pedro.reis',        'Pedro Vinícius Reis'),
    (2, 'isabella.nunes',    'Isabella Cristina Nunes'),
    (3, 'bruno.cavalcanti',  'Bruno Sales Cavalcanti'),
    (3, 'larissa.moura',     'Larissa Helena Moura'),
    (4, 'mateus.domingues',  'Mateus Alves Domingues'),
    (4, 'camilla.teixeira',  'Camilla Barbosa Teixeira'),
    (5, 'vinicius.ramos',    'Vinícius Aparecido Ramos'),
    (5, 'julia.couto',       'Júlia Beatriz Couto'),
    (6, 'thiago.pacheco',    'Thiago Mendes Pacheco'),
    (6, 'beatriz.aragao',    'Beatriz Souza Aragão'),
    (7, 'andre.macedo',      'André Costa Macedo'),
    (7, 'mariana.faria',     'Mariana Lucena Faria'),
    (8, 'felipe.brito',      'Felipe Carvalho Brito'),
    (8, 'renata.vieira',     'Renata Lopes Vieira'),
    (9, 'eduardo.monteiro',  'Eduardo Tavares Monteiro'),
    (9, 'manuela.barros',    'Manuela Coelho Barros'),
]

EMPRESAS = [
    {
        'razao_social': 'Tech Solutions Ltda',
        'cnpj': '12.345.678/0001-90',
        'areas_atuacao': 'Tecnologia · Desenvolvimento de Software · Dados',
        'localizacao': 'Rio de Janeiro, RJ',
        'email_contato': 'contato@techsolutions.com.br',
        'responsavel_legal_nome': 'Roberto Mendes Cardoso',
        'responsavel_legal_cargo': 'Diretor Executivo',
        'descricao': 'Empresa de tecnologia com foco em soluções de software para setores financeiro e educacional.',
    },
    {
        'razao_social': 'Construtora Horizonte S.A.',
        'cnpj': '23.456.789/0001-01',
        'areas_atuacao': 'Construção Civil · Engenharia · Projetos Estruturais',
        'localizacao': 'Rio de Janeiro, RJ',
        'email_contato': 'rh@horizonte.com.br',
        'responsavel_legal_nome': 'Cláudia Lima Vasconcellos',
        'responsavel_legal_cargo': 'Presidente',
        'descricao': 'Construtora atuante em obras residenciais e comerciais no estado do RJ.',
    },
    {
        'razao_social': 'Banco Capital Investimentos',
        'cnpj': '34.567.890/0001-12',
        'areas_atuacao': 'Finanças · Mercado de Capitais · Wealth Management',
        'localizacao': 'São Paulo, SP',
        'email_contato': 'estagio@bancocapital.com.br',
        'responsavel_legal_nome': 'Henrique Sampaio Marques',
        'responsavel_legal_cargo': 'CEO',
        'descricao': 'Banco de investimentos focado em wealth management e operações de M&A.',
    },
    {
        'razao_social': 'Agência Criativa Digital',
        'cnpj': '45.678.901/0001-23',
        'areas_atuacao': 'Marketing · Publicidade · Comunicação Digital',
        'localizacao': 'Rio de Janeiro, RJ',
        'email_contato': 'rh@agcriativa.com.br',
        'responsavel_legal_nome': 'Patrícia Lobo Fernandes',
        'responsavel_legal_cargo': 'CEO',
        'descricao': 'Agência full-service focada em marketing digital e branding.',
    },
    {
        'razao_social': 'Escritório Machado & Associados',
        'cnpj': '56.789.012/0001-34',
        'areas_atuacao': 'Advocacia · Direito Empresarial · Contencioso',
        'localizacao': 'Rio de Janeiro, RJ',
        'email_contato': 'contato@machadoassoc.adv.br',
        'responsavel_legal_nome': 'José Machado Filho',
        'responsavel_legal_cargo': 'Sócio Fundador',
        'descricao': 'Escritório de advocacia full-service com atuação em direito empresarial.',
    },
    {
        'razao_social': 'Global Trade Consultoria',
        'cnpj': '67.890.123/0001-45',
        'areas_atuacao': 'Comércio Exterior · Logística Internacional',
        'localizacao': 'Rio de Janeiro, RJ',
        'email_contato': 'rh@globaltrade.com.br',
        'responsavel_legal_nome': 'Ana Paula Aguiar',
        'responsavel_legal_cargo': 'Diretora de Operações',
        'descricao': 'Consultoria em comércio exterior e estratégias de internacionalização.',
    },
]

# (empresa_idx, username, nome, cargo)
SUPERVISORES = [
    (0, 'marcos.santiago',  'Marcos Vinícius Santiago',   'Diretor de Tecnologia'),
    (1, 'eliana.branco',    'Eliana Cristina Branco',     'Engenheira Sênior'),
    (2, 'antonio.macedo',   'Antonio Carlos Macedo',      'Gerente de Operações'),
    (3, 'daniela.rangel',   'Daniela Souza Rangel',       'Diretora Criativa'),
    (4, 'roberto.pinto',    'Roberto Almeida Pinto',      'Sócio Advogado'),
    (5, 'vanessa.cardoso',  'Vanessa Lima Cardoso',       'Gerente de Comércio Exterior'),
]


def fake_cpf(i):
    return f'{(100 + i):03d}.{(200 + i * 3) % 1000:03d}.{(300 + i * 5) % 1000:03d}-{(10 + i) % 100:02d}'


def fake_rg(i):
    return f'{(10 + i) % 100:02d}.{(100 + i * 2) % 1000:03d}.{(200 + i * 3) % 1000:03d}-{i % 10}'


# ── Definições por curso para as seções 3, 4 e 5 ───────────────────────────

# Seção 3 — Área de Atuação (itens)
AREAS_POR_CURSO = {
    'arq': [
        'Interiores residenciais', 'Interiores comerciais',
        'Edificações residenciais', 'Edificações comerciais',
        'Edificações turismo/lazer', 'Edificações de saúde',
        'Edificações industriais', 'Restauração/patrimônio',
        'Projeto urbano', 'Planejamento urbano',
        'Paisagismo', 'Meio ambiente',
        'Projetos complementares (elétrica/hidro)',
        'Projetos complementares (gás/incêndio)',
        'Projetos complementares (estrutural)',
    ],
    'cdia': [
        'Análise exploratória de dados', 'Engenharia de dados / ETL',
        'Machine Learning supervisionado', 'Machine Learning não supervisionado',
        'Deep Learning / redes neurais', 'NLP / processamento de linguagem',
        'Computer Vision', 'Estatística aplicada',
        'Visualização e BI', 'MLOps / deploy de modelos',
    ],
    'engs': [
        'Backend / APIs', 'Frontend web', 'Mobile',
        'DevOps / CI/CD', 'Banco de dados',
        'Cloud / infraestrutura', 'Arquitetura de software',
        'Qualidade / testes automatizados', 'Segurança de aplicações',
        'UX / Design de produto',
    ],
    'engc': [
        'Hardware / sistemas embarcados', 'Redes de computadores',
        'Sistemas operacionais', 'Segurança / criptografia',
        'Cloud / infraestrutura', 'Backend / APIs',
        'Banco de dados', 'IoT', 'Inteligência artificial',
    ],
    'engp': [
        'PCP (planejamento e controle)', 'Qualidade',
        'Lean / melhoria contínua', 'Logística',
        'Gestão de projetos', 'Gestão da cadeia de suprimentos',
        'Custos', 'Manutenção', 'Ergonomia / segurança do trabalho',
        'Sustentabilidade',
    ],
    'adm': [
        'Gestão de pessoas', 'Recrutamento e seleção',
        'Finanças corporativas', 'Controladoria',
        'Marketing', 'Vendas', 'Operações', 'Logística',
        'Estratégia', 'Inteligência de mercado',
    ],
    'eco': [
        'Macroeconomia', 'Microeconomia', 'Econometria',
        'Mercado financeiro', 'Análise de risco',
        'Pesquisa econômica', 'Política pública',
        'Comércio internacional', 'Setor público',
    ],
    'pub': [
        'Planejamento de campanha', 'Criação / direção de arte',
        'Redação publicitária', 'Mídia paga', 'Mídias sociais',
        'Branding', 'Conteúdo', 'Atendimento / contas',
        'Audiovisual', 'Métricas / performance',
    ],
    'dir': [
        'Direito civil', 'Direito empresarial', 'Direito trabalhista',
        'Direito tributário', 'Direito penal', 'Direito administrativo',
        'Direito do consumidor', 'Contencioso', 'Consultivo',
        'Compliance / LGPD',
    ],
    'ri': [
        'Política externa', 'Comércio exterior',
        'Cooperação internacional', 'Diplomacia',
        'Organismos internacionais', 'Análise de cenários',
        'Negociação internacional', 'Geopolítica',
        'Direito internacional', 'Inteligência de mercado',
    ],
}

# Seção 4 — Aplicação do Conhecimento (disciplinas)
DISCIPLINAS_POR_CURSO = {
    'arq': [
        'Disciplinas de Projeto', 'Disciplinas de Teoria e História',
        'Disciplinas de Estruturas',
        'Disciplinas de Técnicas (conforto, ecologia, materiais)',
        'Disciplinas de Instalações (hidrossanitárias, elétricas)',
        'Disciplinas de Desenho a mão',
    ],
    'cdia': [
        'Estatística e Probabilidade', 'Cálculo / Álgebra Linear',
        'Programação (Python)', 'Banco de Dados',
        'Machine Learning', 'Visualização de Dados',
        'Metodologia de pesquisa',
    ],
    'engs': [
        'Algoritmos e Estrutura de Dados', 'Programação',
        'Engenharia de Software', 'Banco de Dados',
        'Redes', 'Sistemas Distribuídos', 'Gestão de Projetos',
    ],
    'engc': [
        'Algoritmos', 'Programação', 'Sistemas Digitais',
        'Redes', 'Sistemas Operacionais',
        'Eletrônica', 'Cálculo / Física',
    ],
    'engp': [
        'Pesquisa Operacional', 'Estatística e Qualidade',
        'PCP', 'Logística', 'Cálculo / Física',
        'Gestão de Projetos', 'Gestão de Pessoas',
    ],
    'adm': [
        'Gestão de Pessoas', 'Finanças', 'Marketing',
        'Contabilidade', 'Estratégia', 'Operações',
        'Direito Empresarial',
    ],
    'eco': [
        'Macroeconomia', 'Microeconomia', 'Econometria',
        'Estatística', 'Cálculo', 'Finanças',
        'História Econômica',
    ],
    'pub': [
        'Teoria da Comunicação', 'Redação Publicitária',
        'Criação / Direção de Arte', 'Mídia',
        'Pesquisa de Mercado', 'Branding',
        'Audiovisual',
    ],
    'dir': [
        'Direito Civil', 'Direito Empresarial', 'Direito Trabalhista',
        'Direito Constitucional', 'Direito Processual',
        'Teoria Geral do Direito', 'Direito Tributário',
    ],
    'ri': [
        'Teoria das Relações Internacionais', 'Política Externa Brasileira',
        'Economia Internacional', 'Direito Internacional',
        'História Contemporânea', 'Negociação',
        'Análise de Conjuntura',
    ],
}

# Seção 5 — Softwares (itens). Cada um é nivelado em básico/avançado quando faz sentido.
SOFTWARES_POR_CURSO = {
    'arq': [
        'Word básico', 'Word avançado',
        'Excel básico', 'Excel avançado',
        'AutoCAD básico', 'AutoCAD avançado',
        'SketchUp básico', 'SketchUp avançado',
        'VRay básico', 'VRay avançado',
        'Revit básico', 'Revit avançado',
        'Google Earth', 'QGIS', 'Promob', 'ArchiCAD',
    ],
    'cdia': [
        'Python básico', 'Python avançado',
        'SQL básico', 'SQL avançado',
        'R / Stata', 'Git', 'Power BI', 'Tableau',
        'Docker', 'AWS / GCP', 'Excel avançado',
    ],
    'engs': [
        'Python', 'JavaScript / TypeScript', 'Java / Kotlin',
        'SQL', 'Git', 'Docker', 'Kubernetes',
        'AWS / Azure / GCP', 'Linux',
    ],
    'engc': [
        'C / C++', 'Python', 'Java', 'SQL',
        'Linux', 'Git', 'Docker', 'Wireshark', 'VHDL / Verilog',
    ],
    'engp': [
        'Excel básico', 'Excel avançado', 'Power BI',
        'MS Project', 'AutoCAD', 'SAP', 'Minitab',
        'Python (análise de dados)',
    ],
    'adm': [
        'Excel básico', 'Excel avançado',
        'Power BI', 'SAP', 'Word', 'PowerPoint',
        'CRM (Salesforce, HubSpot)',
    ],
    'eco': [
        'Excel básico', 'Excel avançado',
        'R / Stata', 'Python', 'Bloomberg',
        'EViews', 'Power BI',
    ],
    'pub': [
        'Photoshop', 'Illustrator', 'InDesign',
        'After Effects', 'Premiere', 'Figma',
        'Meta Ads / Google Ads',
    ],
    'dir': [
        'Processo Eletrônico (PJe)', 'JusBrasil',
        'LexML', 'Word', 'Excel',
        'CRM jurídico',
    ],
    'ri': [
        'Excel', 'Word', 'PowerPoint',
        'Bloomberg', 'Inglês avançado', 'Espanhol',
    ],
}

ITENS_COMPORTAMENTAIS_DETALHADOS = [
    {'nome': 'Visão',         'descricao': 'Olhar estratégico, leitura de cenários, compreensão das circunstâncias e interpretação de regras e sistemas.'},
    {'nome': 'Adaptabilidade','descricao': 'Capacidade de aprendizagem, abertura para inovar, coragem de explorar novos processos.'},
    {'nome': 'Centralidade',  'descricao': 'Autoconhecimento, controle emocional, resiliência e autoestima.'},
    {'nome': 'Empatia',       'descricao': 'Interação em grupos, comunicação efetiva, respeito mútuo e honestidade.'},
]
ITENS_COMPORTAMENTAIS = [d['nome'] for d in ITENS_COMPORTAMENTAIS_DETALHADOS]

ITENS_EXPERIENCIA = [
    'Atividades vs formação acadêmica',
    'Orientação do supervisor',
    'Feedback do supervisor',
    'Condições de trabalho',
    'Remuneração vs mercado',
    'Relacionamento com equipe',
    'Sua produtividade',
    'Indicaria a empresa',
]

# Compat: ferramentas_por_curso e aplicacao_por_curso continuam exportados
def ferramentas_por_curso(slug):
    return SOFTWARES_POR_CURSO.get(slug, ['Excel', 'Word', 'PowerPoint', 'Outlook', 'Teams'])

def aplicacao_por_curso(slug):
    return DISCIPLINAS_POR_CURSO.get(slug, ['Disciplina 1', 'Disciplina 2', 'Disciplina 3'])


def gerar_modelo_secoes(slug):
    """Modelo de formulário alinhado ao docx oficial do PO — 7 seções."""
    return [
        {
            'id': 'estagiario',
            'tipo': 'auto',
            'titulo': '1. Estagiário / Aluno',
            'itens': [
                'Nome', 'Matrícula', 'Curso', 'Semestre atual',
                'Data de entrada', 'Data de saída',
                'Horas/semana', 'Semanas trabalhadas',
                'Horas totais', 'Remuneração média mensal',
            ],
            'grafico': 'nenhum',
        },
        {
            'id': 'empresa',
            'tipo': 'auto',
            'titulo': '2. Concedente / Empresa',
            'itens': ['Empresa', 'Telefone', 'Website', 'Gestor direto', 'Email do gestor'],
            'grafico': 'nenhum',
        },
        {
            'id': 'area_atuacao',
            'tipo': 'checkbox_duplo',
            'titulo': '3. Área de Atuação',
            'itens': AREAS_POR_CURSO.get(slug, AREAS_POR_CURSO['adm']),
            'colunas': [
                'Atuação da empresa: Obra',
                'Atuação da empresa: Projeto',
                'Sua atuação: Obra',
                'Sua atuação: Projeto',
            ],
            'grafico': 'barras_agrupadas',
            'campo_texto': 'Descreva as principais atividades desenvolvidas no seu estágio',
        },
        {
            'id': 'aplicacao_conhecimento',
            'tipo': 'escala_3',
            'titulo': '4. Avaliação da Aplicação do Conhecimento',
            'descricao': 'Escolha se foi: Suficiente, Insuficiente ou Não utilizado',
            'itens': DISCIPLINAS_POR_CURSO.get(slug, DISCIPLINAS_POR_CURSO['adm']),
            'opcoes': ['Suficiente', 'Insuficiente', 'Não utilizado'],
            'grafico': 'barras',
            'campo_texto': 'Comentário sobre a aplicabilidade do conhecimento acadêmico',
        },
        {
            'id': 'softwares',
            'tipo': 'escala_1_4_multi',
            'titulo': '5. Utilização de Softwares',
            'descricao': '1-muito; 2-médio; 3-pouco; 4-nada',
            'itens': SOFTWARES_POR_CURSO.get(slug, SOFTWARES_POR_CURSO['adm']),
            'colunas': ['Pela empresa', 'Por você', 'Se sentiu apto'],
            'grafico': 'barras_agrupadas',
            'campo_texto': 'Descreva sua experiência com o uso de softwares no estágio',
        },
        {
            'id': 'comportamental',
            'tipo': 'escala_1_4',
            'titulo': '6. Inteligência Comportamental',
            'descricao': '1-ruim; 2-regular; 3-bom; 4-ótimo',
            'itens_detalhados': ITENS_COMPORTAMENTAIS_DETALHADOS,
            'itens': ITENS_COMPORTAMENTAIS,
            'grafico': 'radar',
        },
        {
            'id': 'experiencia',
            'tipo': 'escala_1_4',
            'titulo': '7. Avaliação da Experiência',
            'descricao': '1-ruim; 2-regular; 3-bom; 4-ótimo',
            'itens': ITENS_EXPERIENCIA,
            'grafico': 'barras',
            'campo_efetivacao': True,
            'campo_texto_positivo': 'Pontos positivos sobre sua experiência',
            'campo_texto_negativo': 'Pontos negativos sobre sua experiência',
        },
    ]


def gerar_respostas(slug, qualidade='alta'):
    """Gera respostas plausíveis no formato das seções acima."""
    base = 3 if qualidade == 'alta' else 2

    def nota():
        return max(1, min(4, base + random.randint(-1, 1)))

    areas = AREAS_POR_CURSO.get(slug, [])
    cols_area = [
        'Atuação da empresa: Obra', 'Atuação da empresa: Projeto',
        'Sua atuação: Obra', 'Sua atuação: Projeto',
    ]
    sec_areas = {}
    for it in random.sample(areas, k=min(4, len(areas))):
        sec_areas[it] = random.sample(cols_area, k=random.randint(1, 3))

    disciplinas = DISCIPLINAS_POR_CURSO.get(slug, [])
    sec_apl = {
        it: random.choice(['Suficiente', 'Suficiente', 'Insuficiente', 'Não utilizado'])
        for it in disciplinas
    }

    softs = SOFTWARES_POR_CURSO.get(slug, [])
    sec_sw = {
        it: {'Pela empresa': nota(), 'Por você': nota(), 'Se sentiu apto': nota()}
        for it in random.sample(softs, k=min(6, len(softs)))
    }

    sec_comp = {it: nota() for it in ITENS_COMPORTAMENTAIS}
    sec_exp = {it: nota() for it in ITENS_EXPERIENCIA}

    return {
        'preenchido_em': date.today().isoformat(),
        'tipo_relatorio': 'parcial',
        'secoes': {
            'area_atuacao': sec_areas,
            'area_atuacao_texto': 'Atuei em projetos diversificados, com foco em entrega e qualidade.',
            'aplicacao_conhecimento': sec_apl,
            'aplicacao_conhecimento_texto': 'O conhecimento acadêmico foi essencial para a execução das atividades.',
            'softwares': sec_sw,
            'softwares_texto': 'Aprofundei o uso das ferramentas principais da área.',
            'comportamental': sec_comp,
            'experiencia': sec_exp,
            'experiencia_efetivacao': random.choice(['Sim', 'Não']),
            'experiencia_texto_positivo': (
                'Equipe acolhedora e supervisor presente.' if qualidade == 'alta'
                else 'Ambiente colaborativo.'
            ),
            'experiencia_texto_negativo': (
                'Carga eventualmente intensa.' if qualidade == 'alta'
                else 'Atividades pouco aderentes à formação em alguns momentos.'
            ),
        }
    }


# ── EXECUÇÃO ────────────────────────────────────────────────────────────

print('🧹 Limpando dados existentes…')
LogDocumento.objects.all().delete()
DocumentoProcesso.objects.all().delete()
ProcessoEstagio.objects.all().delete()
ModeloFormulario.objects.all().delete()
Aluno.objects.all().delete()
SupervisorEmpresa.objects.all().delete()
# Coordenadores precisam ser desvinculados dos cursos antes (FK PROTECT no Curso? Não, SET_NULL)
Curso.objects.update(coordenador=None)
Coordenador.objects.all().delete()
EmpresaConcedente.objects.all().delete()
Curso.objects.all().delete()
Usuario.objects.filter(is_superuser=False).delete()

print('👑 Garantindo superuser admin/admin…')
admin, _ = Usuario.objects.get_or_create(username='admin')
admin.is_superuser = True
admin.is_staff = True
admin.email = 'admin@ibmec.edu.br'
admin.tipo = 'coordenador'
admin.nome = 'Administrador IBMEC'
admin.email_institucional = 'admin@ibmec.edu.br'
admin.set_password('admin')
admin.save()

print('🏛  Criando usuários de visão global (Secretaria, CASA, Reitor, Pró-Reitor)…')
VISAO_GLOBAL_USERS = [
    ('ana.secretaria',     'Ana Paula Secretaria', 'secretaria'),
    ('marcos.casa',        'Marcos CASA',          'casa'),
    ('roberto.reitor',     'Roberto Reitor',       'reitor'),
    ('claudia.proreitor',  'Cláudia Pró-Reitora',  'pro_reitor'),
]
for username, nome, tipo in VISAO_GLOBAL_USERS:
    Usuario.objects.create_user(
        username=username, password=PASSWORD, tipo=tipo,
        nome=nome, email_institucional=f'{username}@ibmec.edu.br',
    )

print('🎓 Criando cursos…')
cursos = []
for nome, _ in CURSOS:
    cursos.append(Curso.objects.create(
        nome=nome,
        carga_horaria_minima_total=300,
        carga_horaria_maxima_diaria=6,
    ))

print('👔 Criando coordenadores e vinculando aos cursos…')
coordenadores = []
for curso_idx, username, nome, departamento in COORDENADORES:
    u = Usuario.objects.create_user(
        username=username, password=PASSWORD, tipo='coordenador',
        nome=nome, email_institucional=f'{username}@ibmec.edu.br',
    )
    c = Coordenador.objects.create(usuario=u, departamento=departamento)
    cursos[curso_idx].coordenador = c
    cursos[curso_idx].save(update_fields=['coordenador'])
    coordenadores.append(c)

print('👨‍🎓 Criando alunos…')
alunos = []
for idx, (curso_idx, username, nome) in enumerate(ALUNOS):
    u = Usuario.objects.create_user(
        username=username, password=PASSWORD, tipo='aluno',
        nome=nome, email_institucional=f'{username}@aluno.ibmec.edu.br',
    )
    a = Aluno.objects.create(
        usuario=u,
        cpf=fake_cpf(idx), rg=fake_rg(idx),
        coeficiente_rendimento=Decimal(str(round(random.uniform(5.0, 9.5), 2))),
        curso=cursos[curso_idx],
        periodo_atual=random.randint(3, 10),
        matriculado_estagio=True,
    )
    alunos.append(a)

print('🏢 Criando empresas…')
empresas = []
for d in EMPRESAS:
    e = EmpresaConcedente.objects.create(aprovada_ibmec=True, **d)
    empresas.append(e)

print('🧑‍💼 Criando supervisores de empresa…')
supervisores = []
for emp_idx, username, nome, cargo in SUPERVISORES:
    u = Usuario.objects.create_user(
        username=username, password=PASSWORD, tipo='supervisor_empresa',
        nome=nome, email_institucional=f'{username}@empresa.com.br',
    )
    s = SupervisorEmpresa.objects.create(usuario=u, empresa=empresas[emp_idx], cargo=cargo)
    supervisores.append(s)

print('📝 Criando modelos de formulário (um por curso)…')
modelos = []
for ci, curso in enumerate(cursos):
    nome, slug = CURSOS[ci]
    m = ModeloFormulario.objects.create(
        curso=curso,
        criado_por=coordenadores[ci],
        titulo=f'Avaliação de Estágio — {nome}',
        secoes=gerar_modelo_secoes(slug),
        ativo=True,
    )
    modelos.append(m)

print('📋 Criando processos de estágio…')
# (aluno_idx, empresa_idx, status, qualidade_avaliacao_ou_None)
PROCESSOS_SPEC = [
    # 3 ativos (com avaliação)
    (4,  0, 'ATIVO',     'alta'),   # Pedro Reis (CDIA)    → Tech Solutions
    (12, 0, 'ATIVO',     'alta'),   # Thiago Pacheco (ENGC) → Tech Solutions
    (16, 0, 'ATIVO',     'media'),  # Felipe Brito (ENGS)  → Tech Solutions
    # 2 pendentes
    (5,  2, 'PENDENTE',  None),     # Isabella Nunes (CDIA) → Banco Capital
    (8,  3, 'PENDENTE',  None),     # Mateus Domingues (PUB) → Agência Criativa
    # 2 aprovados
    (0,  0, 'APROVADO',  None),     # Gabriel Silva (ADM)  → Tech Solutions
    (2,  1, 'APROVADO',  None),     # Fernanda Castro (ARQ) → Construtora
    # 1 encerrado (com avaliação)
    (10, 4, 'ENCERRADO', 'alta'),   # Vinícius Ramos (DIR) → Machado & Associados
    # 1 cancelado
    (14, 1, 'CANCELADO', None),     # André Macedo (ENGP)  → Construtora
    # 1 rejeitado
    (6,  2, 'REJEITADO', None),     # Bruno Cavalcanti (ECO) → Banco Capital
]

processos = []
for aluno_idx, emp_idx, status, qualidade in PROCESSOS_SPEC:
    aluno = alunos[aluno_idx]
    empresa = empresas[emp_idx]
    supervisor = supervisores[emp_idx]
    curso_idx = ALUNOS[aluno_idx][0]
    coord = cursos[curso_idx].coordenador
    modelo = modelos[curso_idx]
    slug = CURSOS[curso_idx][1]

    meses_offset = random.choice([-12, -8, -6, -3, 0, 3])
    inicio = date(2025, 1, 15) + timedelta(days=meses_offset * 30 + random.randint(0, 60))
    fim = inicio + timedelta(days=180)
    horas = random.choice([20, 30])
    valor_bolsa = Decimal(str(random.choice([1200, 1500, 1800, 2000, 2500, 3000])))
    valor_aux = Decimal('200') if random.random() > 0.5 else Decimal('0')

    respostas = gerar_respostas(slug, qualidade) if qualidade else None

    p = ProcessoEstagio.objects.create(
        aluno=aluno,
        empresa=empresa,
        supervisor=supervisor,
        coordenador=coord,
        status=status,
        horas_semanais=horas,
        data_inicio_prevista=inicio,
        data_fim_prevista=fim,
        plano_atividades=(
            f'Atuação em projetos da área de {empresa.areas_atuacao.split(chr(0x00B7))[0].strip()} '
            f'sob supervisão da equipe. Atividades incluem análise, execução e relatórios periódicos '
            f'alinhados ao plano pedagógico do curso de {CURSOS[curso_idx][0]}.'
        ),
        valor_bolsa=valor_bolsa,
        valor_auxilio_transporte=valor_aux,
        modelo_formulario=modelo,
        respostas_formulario=respostas,
        data_inicio_real=inicio if status in ('ATIVO', 'ENCERRADO') else None,
        data_fim_real=fim if status == 'ENCERRADO' else None,
        justificativa_rejeicao=(
            'Documentação incompleta — falta TCE assinado pelo responsável legal.'
            if status == 'REJEITADO' else ''
        ),
    )
    processos.append(p)

print()
print('✅ Banco populado com sucesso!')
print(f'  Cursos:              {Curso.objects.count()}')
print(f'  Coordenadores:       {Coordenador.objects.count()}')
print(f'  Alunos:              {Aluno.objects.count()}')
print(f'  Empresas:            {EmpresaConcedente.objects.count()}')
print(f'  Supervisores:        {SupervisorEmpresa.objects.count()}')
print(f'  Modelos formulário:  {ModeloFormulario.objects.count()}')
print(f'  Processos:           {ProcessoEstagio.objects.count()}')
por_status = {}
for p in ProcessoEstagio.objects.all():
    por_status[p.status] = por_status.get(p.status, 0) + 1
print(f'  Por status:          {por_status}')
print()
print('🔑 Credenciais:')
print('  admin / admin                          (superuser)')
print(f'  <username> / {PASSWORD}                (demais usuários)')
print('  Ex: pedro.reis, fernanda.castro, joao.oliveira, marcos.santiago, …')
