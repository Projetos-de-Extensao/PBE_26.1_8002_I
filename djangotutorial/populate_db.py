"""
Script de população do banco de dados para desenvolvimento.
Execute a partir de djangotutorial/:
    python populate_db.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

import datetime
from django.core.files.base import ContentFile
from app.models import (
    Curso, Empresa,
    Aluno, Coordenador,
    SolicitacaoEstagio,
    TermoCompromisso, ApoliceSeguro, RelatorioEstagio,
    AssinaturaDigital,
)


def criar_cursos():
    eng, _ = Curso.objects.get_or_create(
        nome='Engenharia de Computação',
        defaults={'carga_horaria_minima_total': 400, 'carga_horaria_maxima_diaria': 6},
    )
    adm, _ = Curso.objects.get_or_create(
        nome='Administração',
        defaults={'carga_horaria_minima_total': 300, 'carga_horaria_maxima_diaria': 6},
    )
    dir_, _ = Curso.objects.get_or_create(
        nome='Direito',
        defaults={'carga_horaria_minima_total': 350, 'carga_horaria_maxima_diaria': 5},
    )
    return eng, adm, dir_


def criar_empresas():
    e1, _ = Empresa.objects.get_or_create(
        cnpj='12.345.678/0001-90',
        defaults={
            'razao_social': 'Tech Solutions LTDA',
            'areas_atuacao': 'Tecnologia da Informação, Desenvolvimento de Software',
            'localizacao': 'Rio de Janeiro, RJ',
            'email_contato': 'rh@techsolutions.com.br',
            'aprovada_ibmec': True,
        },
    )
    e2, _ = Empresa.objects.get_or_create(
        cnpj='98.765.432/0001-10',
        defaults={
            'razao_social': 'Consultoria RJ S/A',
            'areas_atuacao': 'Consultoria Empresarial, Gestão Financeira',
            'localizacao': 'Rio de Janeiro, RJ',
            'email_contato': 'estagios@consultoriarju.com.br',
            'aprovada_ibmec': True,
        },
    )
    e3, _ = Empresa.objects.get_or_create(
        cnpj='11.222.333/0001-44',
        defaults={
            'razao_social': 'Escritório Advocacia Moreira',
            'areas_atuacao': 'Direito Trabalhista, Direito Civil',
            'localizacao': 'Rio de Janeiro, RJ',
            'email_contato': 'estagio@adv-moreira.com.br',
            'aprovada_ibmec': False,
        },
    )
    return e1, e2, e3


def criar_coordenadores():
    c1 = Coordenador.objects.filter(username='coord.santos').first()
    if not c1:
        c1 = Coordenador.objects.create_user(
            username='coord.santos', password='senha123',
            nome='Dr. Carlos Santos',
            email_institucional='carlos.santos@ibmec.edu.br',
            departamento='Computação',
        )

    c2 = Coordenador.objects.filter(username='coord.lima').first()
    if not c2:
        c2 = Coordenador.objects.create_user(
            username='coord.lima', password='senha123',
            nome='Dra. Ana Lima',
            email_institucional='ana.lima@ibmec.edu.br',
            departamento='Administração',
        )
    return c1, c2


def criar_alunos(eng, adm, dir_):
    a1 = Aluno.objects.filter(username='joao.silva').first()
    if not a1:
        a1 = Aluno.objects.create_user(
            username='joao.silva', password='senha123',
            nome='João Silva',
            email_institucional='joao.silva@ibmec.edu.br',
            matricula='2021001', cpf='111.222.333-44', rg='10.111.222-3',
            coeficiente_rendimento=7.5, curso=eng,
        )

    a2 = Aluno.objects.filter(username='maria.souza').first()
    if not a2:
        a2 = Aluno.objects.create_user(
            username='maria.souza', password='senha123',
            nome='Maria Souza',
            email_institucional='maria.souza@ibmec.edu.br',
            matricula='2021002', cpf='555.666.777-88', rg='20.222.333-4',
            coeficiente_rendimento=8.2, curso=adm,
        )

    a3 = Aluno.objects.filter(username='pedro.costa').first()
    if not a3:
        a3 = Aluno.objects.create_user(
            username='pedro.costa', password='senha123',
            nome='Pedro Costa',
            email_institucional='pedro.costa@ibmec.edu.br',
            matricula='2021003', cpf='999.888.777-66', rg='30.333.444-5',
            coeficiente_rendimento=6.8, curso=dir_,
        )
    return a1, a2, a3


def criar_solicitacoes(a1, a2, a3, e1, e2, e3, c1, c2):
    sol1, _ = SolicitacaoEstagio.objects.get_or_create(
        aluno=a1, empresa=e1,
        defaults={
            'coordenador': c1, 'status': 'ATIVO',
            'horas_semanais': 30,
            'data_inicio_prevista': datetime.date(2026, 2, 1),
            'data_fim_prevista': datetime.date(2026, 7, 31),
        },
    )
    sol2, _ = SolicitacaoEstagio.objects.get_or_create(
        aluno=a2, empresa=e2,
        defaults={
            'status': 'PENDENTE', 'horas_semanais': 20,
            'data_inicio_prevista': datetime.date(2026, 3, 1),
            'data_fim_prevista': datetime.date(2026, 8, 31),
        },
    )
    sol3, _ = SolicitacaoEstagio.objects.get_or_create(
        aluno=a3, empresa=e3,
        defaults={
            'coordenador': c2, 'status': 'REJEITADO',
            'horas_semanais': 25,
            'data_inicio_prevista': datetime.date(2026, 4, 1),
            'data_fim_prevista': datetime.date(2026, 9, 30),
            'justificativa_rejeicao': 'Empresa não aprovada pelo IBMEC.',
        },
    )
    return sol1, sol2, sol3


def criar_documentos(sol1):
    placeholder = ContentFile(b'%PDF-1.4 placeholder para desenvolvimento')

    if not TermoCompromisso.objects.filter(solicitacao=sol1).exists():
        tc = TermoCompromisso(
            solicitacao=sol1, status='APROVADO', versao=1,
            plano_atividades='Desenvolvimento de APIs REST com Django e manutenção de sistemas legados.',
        )
        tc.arquivo.save('termo_sol1.pdf', placeholder, save=True)
    else:
        tc = TermoCompromisso.objects.filter(solicitacao=sol1).first()

    if not ApoliceSeguro.objects.filter(solicitacao=sol1).exists():
        ap = ApoliceSeguro(
            solicitacao=sol1, status='APROVADO', versao=1,
            data_vencimento=datetime.date(2026, 12, 31),
        )
        ap.arquivo.save('apolice_sol1.pdf', placeholder, save=True)
    else:
        ap = ApoliceSeguro.objects.filter(solicitacao=sol1).first()

    if not RelatorioEstagio.objects.filter(solicitacao=sol1).exists():
        rel = RelatorioEstagio(
            solicitacao=sol1, status='PENDENTE', versao=1,
            periodo_referencia='Fevereiro/2026',
        )
        rel.arquivo.save('relatorio_sol1.pdf', placeholder, save=True)
    else:
        rel = RelatorioEstagio.objects.filter(solicitacao=sol1).first()

    return tc, ap, rel


def criar_assinaturas(tc, ap, rel):
    if tc and not AssinaturaDigital.objects.filter(termo_compromisso=tc).exists():
        AssinaturaDigital.objects.create(
            signatario_nome='João Silva', signatario_perfil='ALUNO',
            ip_address='192.168.1.1', termo_compromisso=tc,
        )
    if ap and not AssinaturaDigital.objects.filter(apolice_seguro=ap).exists():
        AssinaturaDigital.objects.create(
            signatario_nome='Dr. Carlos Santos', signatario_perfil='COORDENADOR',
            ip_address='192.168.1.2', apolice_seguro=ap,
        )
    if rel and not AssinaturaDigital.objects.filter(relatorio_estagio=rel).exists():
        AssinaturaDigital.objects.create(
            signatario_nome='Tech Solutions LTDA', signatario_perfil='EMPRESA',
            ip_address='192.168.1.3', relatorio_estagio=rel,
        )


if __name__ == '__main__':
    print('Populando banco de dados...')
    eng, adm, dir_ = criar_cursos()
    print(f'  Cursos: {Curso.objects.count()}')

    e1, e2, e3 = criar_empresas()
    print(f'  Empresas: {Empresa.objects.count()}')

    c1, c2 = criar_coordenadores()
    print(f'  Coordenadores: {Coordenador.objects.count()}')

    a1, a2, a3 = criar_alunos(eng, adm, dir_)
    print(f'  Alunos: {Aluno.objects.count()}')

    sol1, sol2, sol3 = criar_solicitacoes(a1, a2, a3, e1, e2, e3, c1, c2)
    print(f'  Solicitações de Estágio: {SolicitacaoEstagio.objects.count()}')

    tc, ap, rel = criar_documentos(sol1)
    print(f'  Termos de Compromisso: {TermoCompromisso.objects.count()}')
    print(f'  Apólices de Seguro: {ApoliceSeguro.objects.count()}')
    print(f'  Relatórios de Estágio: {RelatorioEstagio.objects.count()}')

    criar_assinaturas(tc, ap, rel)
    print(f'  Assinaturas Digitais: {AssinaturaDigital.objects.count()}')

    print('\nBanco populado com sucesso!')
    print('\nUsuários de teste criados (todos com senha: senha123):')
    print('  coord.santos — coordenador')
    print('  coord.lima   — coordenador')
    print('  joao.silva   — aluno')
    print('  maria.souza  — aluno')
    print('  pedro.costa  — aluno')
