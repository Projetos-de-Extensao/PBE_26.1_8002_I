"""
Testes de RBAC — SolicitacaoEstagio

Cenários cobertos:
  1.  Aluno vê apenas as próprias solicitações na listagem
  2.  Aluno não pode recuperar solicitação de outro aluno (404)
  3.  Aluno não pode chamar alterar-status (403)
  4.  Aluno não pode forçar aluno/status na criação
  5.  Aluno pode criar solicitação (aluno e status definidos pelo servidor)
  6.  Coordenador aprova solicitação do seu próprio curso (200)
  7.  Rejeição exige justificativa não-vazia (400)
  7b. Rejeição com justificativa válida persiste os dados (200)
  8.  Coordenador não pode ver solicitação de outro curso (404)
  9.  Coordenador lista apenas solicitações do seu curso
  10. Coordenador não pode criar solicitação (403)
"""
import datetime
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import (
    Usuario, Aluno, Coordenador, Curso, Empresa, SolicitacaoEstagio,
)


# ── fixture helpers ───────────────────────────────────────────────────────────

def _make_usuario(username, tipo, nome=''):
    return Usuario.objects.create_user(
        username=username, password='senha_teste_123', tipo=tipo, nome=nome or username,
    )


def _token(user):
    t, _ = Token.objects.get_or_create(user=user)
    return t


def _empresa():
    return Empresa.objects.create(
        cnpj='12.345.678/0001-90',
        razao_social='Empresa Teste',
        areas_atuacao='TI',
        localizacao='Rio de Janeiro',
        email_contato='contato@empresa.com',
        aprovada_ibmec=True,
    )


def _solicitacao(aluno, empresa):
    return SolicitacaoEstagio.objects.create(
        aluno=aluno,
        empresa=empresa,
        horas_semanais=20,
        data_inicio_prevista=datetime.date(2026, 6, 1),
        data_fim_prevista=datetime.date(2026, 12, 1),
    )


# ── classe de teste ───────────────────────────────────────────────────────────

class SolicitacaoRBACTest(APITestCase):
    """Testa o RBAC do endpoint /api/solicitacoes-estagio/."""

    LIST_URL = '/api/solicitacoes-estagio/'

    def detail_url(self, pk):
        return f'/api/solicitacoes-estagio/{pk}/'

    def status_url(self, pk):
        return f'/api/solicitacoes-estagio/{pk}/alterar-status/'

    # ── setUp ─────────────────────────────────────────────────────────────────

    def setUp(self):
        self.empresa = _empresa()

        # Coordenador A e seu curso
        self.user_coord_a = _make_usuario('coord_a', 'coordenador', 'Coord A')
        self.coord_a = Coordenador.objects.create(usuario=self.user_coord_a)
        self.token_coord_a = _token(self.user_coord_a)
        self.curso_a = Curso.objects.create(nome='Engenharia', coordenador=self.coord_a)

        # Coordenador B e seu curso (outro curso)
        self.user_coord_b = _make_usuario('coord_b', 'coordenador', 'Coord B')
        self.coord_b = Coordenador.objects.create(usuario=self.user_coord_b)
        self.token_coord_b = _token(self.user_coord_b)
        self.curso_b = Curso.objects.create(nome='Direito', coordenador=self.coord_b)

        # Aluno 1 — pertence ao Curso A
        self.user_aluno1 = _make_usuario('aluno1', 'aluno', 'Aluno 1')
        self.aluno1 = Aluno.objects.create(
            usuario=self.user_aluno1, cpf='111.111.111-11', curso=self.curso_a,
        )
        self.token_aluno1 = _token(self.user_aluno1)

        # Aluno 2 — também pertence ao Curso A (solicitação diferente)
        self.user_aluno2 = _make_usuario('aluno2', 'aluno', 'Aluno 2')
        self.aluno2 = Aluno.objects.create(
            usuario=self.user_aluno2, cpf='222.222.222-22', curso=self.curso_a,
        )
        self.token_aluno2 = _token(self.user_aluno2)

        # Aluno 3 — pertence ao Curso B (coordenador diferente)
        self.user_aluno3 = _make_usuario('aluno3', 'aluno', 'Aluno 3')
        self.aluno3 = Aluno.objects.create(
            usuario=self.user_aluno3, cpf='333.333.333-33', curso=self.curso_b,
        )
        self.token_aluno3 = _token(self.user_aluno3)

        # Solicitações pré-criadas para os testes de leitura/status
        self.sol1 = _solicitacao(self.aluno1, self.empresa)  # Curso A
        self.sol2 = _solicitacao(self.aluno2, self.empresa)  # Curso A
        self.sol3 = _solicitacao(self.aluno3, self.empresa)  # Curso B

    def _auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    # ── testes: aluno ─────────────────────────────────────────────────────────

    def test_01_aluno_lista_apenas_proprias_solicitacoes(self):
        """Listagem retorna somente as solicitações do aluno autenticado."""
        self._auth(self.token_aluno1)
        r = self.client.get(self.LIST_URL)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        ids = [s['id'] for s in r.data]
        self.assertIn(self.sol1.pk, ids)
        self.assertNotIn(self.sol2.pk, ids)
        self.assertNotIn(self.sol3.pk, ids)

    def test_02_aluno_nao_ve_solicitacao_de_outro_aluno(self):
        """Aluno 1 não obtém detalhe da solicitação do Aluno 2 (404)."""
        self._auth(self.token_aluno1)
        r = self.client.get(self.detail_url(self.sol2.pk))
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_03_aluno_nao_pode_alterar_status(self):
        """Aluno não consegue chamar alterar-status mesmo na própria solicitação (403)."""
        self._auth(self.token_aluno1)
        r = self.client.post(
            self.status_url(self.sol1.pk),
            {'status': 'APROVADO'},
        )
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_04_aluno_nao_pode_forcar_campos_protegidos_na_criacao(self):
        """Campos 'aluno' e 'status' enviados pelo cliente são ignorados."""
        self._auth(self.token_aluno1)
        # Tenta criar como se fosse aluno2 e com status já aprovado
        r = self.client.post(self.LIST_URL, {
            'empresa': self.empresa.pk,
            'horas_semanais': 20,
            'data_inicio_prevista': '2026-07-01',
            'data_fim_prevista': '2026-12-31',
            'aluno': self.aluno2.pk,   # deve ser ignorado
            'status': 'APROVADO',      # deve ser ignorado
        })
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        nova = SolicitacaoEstagio.objects.get(pk=r.data['id'])
        self.assertEqual(nova.aluno, self.aluno1)
        self.assertEqual(nova.status, SolicitacaoEstagio.Status.PENDENTE)

    def test_05_aluno_pode_criar_solicitacao_propria(self):
        """Aluno cria nova solicitação com aluno e status definidos pelo servidor."""
        self._auth(self.token_aluno1)
        r = self.client.post(self.LIST_URL, {
            'empresa': self.empresa.pk,
            'horas_semanais': 30,
            'data_inicio_prevista': '2026-08-01',
            'data_fim_prevista': '2026-12-31',
        })
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        nova = SolicitacaoEstagio.objects.get(pk=r.data['id'])
        self.assertEqual(nova.aluno, self.aluno1)
        self.assertEqual(nova.status, SolicitacaoEstagio.Status.PENDENTE)

    # ── testes: coordenador ───────────────────────────────────────────────────

    def test_06_coordenador_aprova_solicitacao_do_seu_curso(self):
        """Coordenador A aprova solicitação de aluno do Curso A (200)."""
        self._auth(self.token_coord_a)
        r = self.client.post(
            self.status_url(self.sol1.pk),
            {'status': 'APROVADO'},
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.sol1.refresh_from_db()
        self.assertEqual(self.sol1.status, SolicitacaoEstagio.Status.APROVADO)

    def test_07_rejeicao_sem_justificativa_retorna_400(self):
        """Rejeitar uma solicitação sem justificativa retorna 400."""
        self._auth(self.token_coord_a)
        r = self.client.post(
            self.status_url(self.sol1.pk),
            {'status': 'REJEITADO'},  # justificativa ausente
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('justificativa_rejeicao', r.data)

    def test_07b_rejeicao_com_justificativa_retorna_200(self):
        """Rejeitar com justificativa válida retorna 200 e persiste os dados."""
        self._auth(self.token_coord_a)
        r = self.client.post(
            self.status_url(self.sol1.pk),
            {'status': 'REJEITADO', 'justificativa_rejeicao': 'Documentação incompleta.'},
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.sol1.refresh_from_db()
        self.assertEqual(self.sol1.status, SolicitacaoEstagio.Status.REJEITADO)
        self.assertEqual(self.sol1.justificativa_rejeicao, 'Documentação incompleta.')

    def test_08_coordenador_nao_ve_solicitacao_de_outro_curso(self):
        """Coordenador A não consegue recuperar solicitação do Curso B (404)."""
        self._auth(self.token_coord_a)
        r = self.client.get(self.detail_url(self.sol3.pk))
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_09_coordenador_lista_apenas_solicitacoes_do_seu_curso(self):
        """Coordenador A lista sol1 e sol2 (Curso A), mas não sol3 (Curso B)."""
        self._auth(self.token_coord_a)
        r = self.client.get(self.LIST_URL)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        ids = [s['id'] for s in r.data]
        self.assertIn(self.sol1.pk, ids)
        self.assertIn(self.sol2.pk, ids)
        self.assertNotIn(self.sol3.pk, ids)

    def test_10_coordenador_nao_pode_criar_solicitacao(self):
        """Coordenador não pode criar uma nova solicitação de estágio (403)."""
        self._auth(self.token_coord_a)
        r = self.client.post(self.LIST_URL, {
            'empresa': self.empresa.pk,
            'horas_semanais': 20,
            'data_inicio_prevista': '2026-06-01',
            'data_fim_prevista': '2026-12-01',
        })
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
