"""
Script de seed para desenvolvimento e testes.

Executar a partir de djangotutorial/:
    python3 manage.py shell < populate_db.py

Idempotente: usa get_or_create em tudo, pode rodar várias vezes sem duplicar.

Cria:
  - 2 coordenadores (departamentos diferentes)
  - 3 cursos distribuídos entre eles
  - 4 alunos nos cursos (CPFs fictícios, CRs variados, alguns matriculados)
  - 3 empresas (2 aprovadas, 1 não aprovada)
  - 2 processos de estágio (status PENDENTE e APROVADO)
"""
import datetime
from decimal import Decimal

from app.models import (
    Usuario, Coordenador, Curso, Aluno, Empresa, SolicitacaoEstagio,
)

SENHA_PADRAO = 'senha123'


def get_or_create_usuario(username, tipo, nome, email):
    """Cria (ou recupera) um Usuario, garantindo a senha padrão se for novo."""
    user, criado = Usuario.objects.get_or_create(
        username=username,
        defaults={'tipo': tipo, 'nome': nome, 'email_institucional': email},
    )
    if criado:
        user.set_password(SENHA_PADRAO)
        user.save()
    return user


# ── Coordenadores ─────────────────────────────────────────────────────────────

user_c1 = get_or_create_usuario(
    'coord.santos', 'coordenador', 'Dr. Carlos Santos', 'carlos.santos@ibmec.edu.br',
)
coord1, _ = Coordenador.objects.get_or_create(
    usuario=user_c1, defaults={'departamento': 'Computação'},
)

user_c2 = get_or_create_usuario(
    'coord.lima', 'coordenador', 'Dra. Ana Lima', 'ana.lima@ibmec.edu.br',
)
coord2, _ = Coordenador.objects.get_or_create(
    usuario=user_c2, defaults={'departamento': 'Administração'},
)


# ── Cursos ────────────────────────────────────────────────────────────────────

curso_eng, _ = Curso.objects.get_or_create(
    nome='Engenharia de Computação',
    defaults={'coordenador': coord1, 'carga_horaria_maxima_diaria': 6},
)
curso_si, _ = Curso.objects.get_or_create(
    nome='Sistemas de Informação',
    defaults={'coordenador': coord1, 'carga_horaria_maxima_diaria': 6},
)
curso_adm, _ = Curso.objects.get_or_create(
    nome='Administração',
    defaults={'coordenador': coord2, 'carga_horaria_maxima_diaria': 5},
)


# ── Alunos ──────────────────────────────────────────────────────────────────
# CR em escala 0.00–0.99 por limitação do modelo (max_digits=2, decimal_places=2)

user_a1 = get_or_create_usuario(
    'joao.silva', 'aluno', 'João Silva', 'joao.silva@alunos.ibmec.edu.br',
)
aluno1, _ = Aluno.objects.get_or_create(
    usuario=user_a1,
    defaults={
        'cpf': '111.222.333-44', 'rg': '10.111.222-3',
        'coeficiente_rendimento': Decimal('0.85'),
        'curso': curso_eng, 'matriculado_estagio': True,
    },
)

user_a2 = get_or_create_usuario(
    'maria.souza', 'aluno', 'Maria Souza', 'maria.souza@alunos.ibmec.edu.br',
)
aluno2, _ = Aluno.objects.get_or_create(
    usuario=user_a2,
    defaults={
        'cpf': '555.666.777-88', 'rg': '20.222.333-4',
        'coeficiente_rendimento': Decimal('0.92'),
        'curso': curso_si, 'matriculado_estagio': False,
    },
)

user_a3 = get_or_create_usuario(
    'pedro.costa', 'aluno', 'Pedro Costa', 'pedro.costa@alunos.ibmec.edu.br',
)
aluno3, _ = Aluno.objects.get_or_create(
    usuario=user_a3,
    defaults={
        'cpf': '999.888.777-66', 'rg': '30.333.444-5',
        'coeficiente_rendimento': Decimal('0.68'),
        'curso': curso_adm, 'matriculado_estagio': True,
    },
)

user_a4 = get_or_create_usuario(
    'ana.oliveira', 'aluno', 'Ana Oliveira', 'ana.oliveira@alunos.ibmec.edu.br',
)
aluno4, _ = Aluno.objects.get_or_create(
    usuario=user_a4,
    defaults={
        'cpf': '444.333.222-11', 'rg': '40.444.555-6',
        'coeficiente_rendimento': Decimal('0.77'),
        'curso': curso_adm, 'matriculado_estagio': False,
    },
)


# ── Empresas ──────────────────────────────────────────────────────────────────

empresa1, _ = Empresa.objects.get_or_create(
    cnpj='12.345.678/0001-90',
    defaults={
        'razao_social': 'Tech Solutions LTDA',
        'areas_atuacao': 'Tecnologia da Informação, Desenvolvimento de Software',
        'localizacao': 'Rio de Janeiro, RJ',
        'email_contato': 'rh@techsolutions.com.br',
        'aprovada_ibmec': True,
    },
)
empresa2, _ = Empresa.objects.get_or_create(
    cnpj='98.765.432/0001-10',
    defaults={
        'razao_social': 'Consultoria RJ S/A',
        'areas_atuacao': 'Consultoria Empresarial, Gestão Financeira',
        'localizacao': 'Rio de Janeiro, RJ',
        'email_contato': 'estagios@consultoriarj.com.br',
        'aprovada_ibmec': True,
    },
)
empresa3, _ = Empresa.objects.get_or_create(
    cnpj='11.222.333/0001-44',
    defaults={
        'razao_social': 'Startup XYZ ME',
        'areas_atuacao': 'Marketing Digital',
        'localizacao': 'Niterói, RJ',
        'email_contato': 'contato@startupxyz.com.br',
        'aprovada_ibmec': False,
    },
)


# ── Processos de estágio (status diferentes) ───────────────────────────────────

processo_pendente, _ = SolicitacaoEstagio.objects.get_or_create(
    aluno=aluno1, empresa=empresa1,
    defaults={
        'coordenador': coord1,
        'status': SolicitacaoEstagio.Status.PENDENTE,
        'horas_semanais': 20,
        'data_inicio_prevista': datetime.date(2026, 3, 1),
        'data_fim_prevista': datetime.date(2026, 8, 31),
    },
)

processo_aprovado, _ = SolicitacaoEstagio.objects.get_or_create(
    aluno=aluno3, empresa=empresa2,
    defaults={
        'coordenador': coord2,
        'status': SolicitacaoEstagio.Status.APROVADO,
        'horas_semanais': 30,
        'data_inicio_prevista': datetime.date(2026, 2, 1),
        'data_fim_prevista': datetime.date(2026, 7, 31),
    },
)


# ── Resumo ──────────────────────────────────────────────────────────────────

print('Banco populado com sucesso!')
print(f'  Coordenadores: {Coordenador.objects.count()}')
print(f'  Cursos:        {Curso.objects.count()}')
print(f'  Alunos:        {Aluno.objects.count()}')
print(f'  Empresas:      {Empresa.objects.count()}')
print(f'  Processos:     {SolicitacaoEstagio.objects.count()}')
print()
print('Usuarios de teste (senha: senha123):')
print('  coord.santos  -> coordenador (Computacao): Eng. Computacao, Sistemas de Informacao')
print('  coord.lima    -> coordenador (Administracao): Administracao')
print('  joao.silva    -> aluno (Eng. Computacao, matriculado) [processo PENDENTE]')
print('  maria.souza   -> aluno (Sistemas de Informacao)')
print('  pedro.costa   -> aluno (Administracao, matriculado) [processo APROVADO]')
print('  ana.oliveira  -> aluno (Administracao)')
