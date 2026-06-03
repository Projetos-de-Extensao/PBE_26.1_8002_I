"""
Testes de Auth e Permissões — feat/auth-e-permissoes

Cenários cobertos:
  1.  Registro de aluno com sucesso
  2.  Registro de coordenador com sucesso
  3.  Registro de empresa com sucesso
  4.  Login válido retorna token + tipo + nome + id
  5.  Login inválido retorna 401
  6.  Username duplicado retorna erro 400
  7.  Senha com menos de 8 caracteres retorna erro 400
  8.  Tipo inválido retorna erro 400
  9.  Campos obrigatórios faltando retorna erro 400
  10. Curso inexistente no registro de aluno retorna erro 400
  11. Logout invalida o token (próxima requisição retorna 401)
  12. IsAluno bloqueia coordenador
  13. IsCoordenador bloqueia aluno
  14. IsEmpresa bloqueia aluno
  15. IsAdminOrReadOnly permite leitura mas bloqueia escrita para não-admin
"""
import datetime
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Usuario, Aluno, Coordenador, Curso, Empresa, SolicitacaoEstagio
from .permissions import IsAluno, IsCoordenador, IsEmpresa, IsAdminOrReadOnly


REGISTER_URL = '/api/auth/register/'
LOGIN_URL    = '/api/auth/login/'
LOGOUT_URL   = '/api/auth/logout/'


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_usuario(username, tipo, nome='', password='senha123'):
    return Usuario.objects.create_user(
        username=username, password=password,
        tipo=tipo, nome=nome or username,
    )


def _token(user):
    t, _ = Token.objects.get_or_create(user=user)
    return t


# ── testes de registro / login / logout ──────────────────────────────────────

class AuthRegistroTest(APITestCase):

    def setUp(self):
        self.curso = Curso.objects.create(nome='Engenharia')

    def test_01_registro_aluno_com_sucesso(self):
        """Registro de aluno retorna 201 com token."""
        r = self.client.post(REGISTER_URL, {
            'tipo': 'aluno',
            'username': 'aluno1',
            'password': 'senha123',
            'nome': 'Aluno Teste',
            'cpf': '111.111.111-11',
            'curso_id': self.curso.pk,
        })
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', r.data)
        self.assertEqual(r.data['tipo'], 'aluno')
        self.assertTrue(Aluno.objects.filter(usuario__username='aluno1').exists())

    def test_02_registro_coordenador_com_sucesso(self):
        """Registro de coordenador retorna 201 com token."""
        r = self.client.post(REGISTER_URL, {
            'tipo': 'coordenador',
            'username': 'coord1',
            'password': 'senha123',
            'nome': 'Coord Teste',
            'departamento': 'Engenharia',
        })
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', r.data)
        self.assertTrue(Coordenador.objects.filter(usuario__username='coord1').exists())

    def test_03_registro_empresa_com_sucesso(self):
        """Registro de empresa retorna 201 com token."""
        r = self.client.post(REGISTER_URL, {
            'tipo': 'empresa',
            'username': 'empresa1',
            'password': 'senha123',
            'nome': 'Empresa Teste',
            'cnpj': '11.111.111/0001-11',
            'razao_social': 'Empresa SA',
            'areas_atuacao': 'TI',
            'localizacao': 'Rio de Janeiro',
            'email_contato': 'contato@empresa.com',
        })
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', r.data)
        self.assertTrue(Empresa.objects.filter(cnpj='11.111.111/0001-11').exists())

    def test_06_username_duplicado_retorna_400(self):
        """Tentar registrar username já existente retorna 400."""
        _make_usuario('duplicado', 'aluno')
        r = self.client.post(REGISTER_URL, {
            'tipo': 'aluno',
            'username': 'duplicado',
            'password': 'senha123',
            'nome': 'Outro',
            'cpf': '999.999.999-99',
            'curso_id': self.curso.pk,
        })
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_07_senha_curta_retorna_400(self):
        """Senha com menos de 8 caracteres retorna 400."""
        r = self.client.post(REGISTER_URL, {
            'tipo': 'aluno',
            'username': 'novo_aluno',
            'password': '123',
            'nome': 'Teste',
            'cpf': '222.222.222-22',
            'curso_id': self.curso.pk,
        })
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('erro', r.data)

    def test_08_tipo_invalido_retorna_400(self):
        """Tipo de usuário inválido retorna 400."""
        r = self.client.post(REGISTER_URL, {
            'tipo': 'professor',
            'username': 'prof1',
            'password': 'senha123',
            'nome': 'Prof',
        })
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_09_campos_obrigatorios_faltando_retorna_400(self):
        """Requisição sem username ou password retorna 400."""
        r = self.client.post(REGISTER_URL, {
            'tipo': 'aluno',
            'nome': 'Sem Credenciais',
        })
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_10_curso_inexistente_retorna_400(self):
        """Curso inexistente no registro de aluno retorna 400."""
        r = self.client.post(REGISTER_URL, {
            'tipo': 'aluno',
            'username': 'aluno_sem_curso',
            'password': 'senha123',
            'nome': 'Aluno',
            'cpf': '333.333.333-33',
            'curso_id': 9999,
        })
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)


class AuthLoginLogoutTest(APITestCase):

    def setUp(self):
        self.user = _make_usuario('user_login', 'aluno', 'User Login')

    def test_04_login_valido_retorna_token_e_dados(self):
        """Login válido retorna token, tipo, nome e id."""
        r = self.client.post(LOGIN_URL, {
            'username': 'user_login',
            'password': 'senha123',
        })
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn('token', r.data)
        self.assertIn('tipo', r.data)
        self.assertIn('nome', r.data)
        self.assertIn('id', r.data)
        self.assertEqual(r.data['tipo'], 'aluno')
        self.assertEqual(r.data['nome'], 'User Login')
        self.assertEqual(r.data['id'], self.user.pk)

    def test_05_login_invalido_retorna_401(self):
        """Credenciais erradas retornam 401."""
        r = self.client.post(LOGIN_URL, {
            'username': 'user_login',
            'password': 'errada',
        })
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_11_logout_invalida_token(self):
        """Após logout, o token não funciona mais."""
        token = _token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        # Logout
        r = self.client.post(LOGOUT_URL)
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        # Tenta usar o token depois do logout
        r2 = self.client.post(LOGOUT_URL)
        self.assertEqual(r2.status_code, status.HTTP_401_UNAUTHORIZED)


# ── testes das classes de permissão ──────────────────────────────────────────

class PermissoesTest(APITestCase):
    """Testa as 5 classes de permissão customizadas."""

    def setUp(self):
        self.curso = Curso.objects.create(nome='Engenharia')

        self.user_aluno = _make_usuario('aluno_perm', 'aluno')
        self.aluno = Aluno.objects.create(
            usuario=self.user_aluno, cpf='444.444.444-44', curso=self.curso
        )

        self.user_coord = _make_usuario('coord_perm', 'coordenador')
        self.coord = Coordenador.objects.create(usuario=self.user_coord)

        self.user_empresa = _make_usuario('empresa_perm', 'empresa')

        self.empresa = Empresa.objects.create(
            cnpj='55.555.555/0001-55',
            razao_social='Empresa Perm',
            areas_atuacao='TI',
            localizacao='RJ',
            email_contato='perm@empresa.com',
        )

    def _auth(self, user):
        token = _token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_12_is_aluno_bloqueia_coordenador(self):
        """IsCoordenador não pode acessar endpoint exclusivo de aluno."""
        # Testa via permissão direta
        perm = IsAluno()

        class FakeRequest:
            user = self.user_coord
        self.assertFalse(perm.has_permission(FakeRequest(), None))

    def test_13_is_coordenador_bloqueia_aluno(self):
        """IsAluno não pode acessar endpoint exclusivo de coordenador."""
        perm = IsCoordenador()

        class FakeRequest:
            user = self.user_aluno
        self.assertFalse(perm.has_permission(FakeRequest(), None))

    def test_14_is_empresa_bloqueia_aluno(self):
        """IsEmpresa bloqueia usuário do tipo aluno."""
        perm = IsEmpresa()

        class FakeRequest:
            user = self.user_aluno
        self.assertFalse(perm.has_permission(FakeRequest(), None))

    def test_14b_is_empresa_permite_empresa(self):
        """IsEmpresa permite usuário do tipo empresa."""
        perm = IsEmpresa()

        class FakeRequest:
            user = self.user_empresa
        self.assertTrue(perm.has_permission(FakeRequest(), None))

    def test_15_is_admin_or_read_only_permite_leitura(self):
        """IsAdminOrReadOnly permite GET para qualquer usuário autenticado."""
        perm = IsAdminOrReadOnly()

        class FakeRequest:
            user = self.user_aluno
            method = 'GET'
        self.assertTrue(perm.has_permission(FakeRequest(), None))

    def test_15b_is_admin_or_read_only_bloqueia_escrita_para_nao_admin(self):
        """IsAdminOrReadOnly bloqueia POST para usuário não-admin."""
        perm = IsAdminOrReadOnly()

        class FakeRequest:
            user = self.user_aluno
            method = 'POST'
        self.assertFalse(perm.has_permission(FakeRequest(), None))
