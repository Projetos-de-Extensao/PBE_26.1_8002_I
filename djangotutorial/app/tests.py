"""
Testes de ProcessoEstagio — issue #46

Cenários cobertos:
  Criação de processo (RN01, RN03, RN05, RN09, validação de datas)
  Isolamento de queryset por papel (aluno, supervisor, coordenador, admin)
  Alterar status (transições, justificativa RN11, permissões por papel)
  State machine (unit tests do módulo state_machine)
"""
from datetime import date

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from app.models import (
    Aluno,
    Coordenador,
    Curso,
    EmpresaConcedente,
    ProcessoEstagio,
    SupervisorEmpresa,
    Usuario,
)
from app.state_machine import (
    APROVADO,
    ATIVO,
    CANCELADO,
    CORRECAO_SOLICITADA,
    ENCERRADO,
    ESTADOS_TERMINAIS,
    ESTADOS_VIVOS,
    PENDENTE,
    RASCUNHO,
    REJEITADO,
    eh_terminal,
    pode_transicionar,
    transicoes_validas,
)


LIST_URL = '/api/processos-estagio/'


def _detail_url(pk):
    return f'/api/processos-estagio/{pk}/'


def _status_url(pk):
    return f'/api/processos-estagio/{pk}/alterar_status/'


def _documentos_url(pk):
    return f'/api/processos-estagio/{pk}/documentos/'


class ProcessoEstagioBaseTest(APITestCase):
    """Setup compartilhado: 1 admin, 2 coordenadores, 2 cursos,
    3 alunos (2 matriculados, 1 não), 2 empresas, 1 supervisor."""

    def setUp(self):
        # ── Coordenadores (criados antes dos cursos para satisfazer FK) ─────
        self.user_coord_eng = Usuario.objects.create_user(
            username='coord_eng',
            password='senha123',
            tipo='coordenador',
            nome='Coord Eng',
        )
        self.coord_eng = Coordenador.objects.create(
            usuario=self.user_coord_eng, departamento='Engenharia',
        )

        self.user_coord_adm = Usuario.objects.create_user(
            username='coord_adm',
            password='senha123',
            tipo='coordenador',
            nome='Coord Adm',
        )
        self.coord_adm = Coordenador.objects.create(
            usuario=self.user_coord_adm, departamento='Administração',
        )

        # ── Cursos ──────────────────────────────────────────────────────────
        self.curso_eng = Curso.objects.create(
            nome='Engenharia',
            coordenador=self.coord_eng,
            carga_horaria_minima_total=400,
            carga_horaria_maxima_diaria=6,
        )
        self.curso_adm = Curso.objects.create(
            nome='Administração',
            coordenador=self.coord_adm,
            carga_horaria_minima_total=300,
            carga_horaria_maxima_diaria=6,
        )

        # ── Empresas ────────────────────────────────────────────────────────
        self.empresa_aprovada = EmpresaConcedente.objects.create(
            cnpj='11.111.111/0001-11',
            razao_social='Tech Aprovada',
            areas_atuacao='TI',
            localizacao='RJ',
            email_contato='rh@aprovada.com',
            aprovada_ibmec=True,
        )
        self.empresa_nao_aprovada = EmpresaConcedente.objects.create(
            cnpj='22.222.222/0001-22',
            razao_social='Não Aprovada',
            areas_atuacao='X',
            localizacao='RJ',
            email_contato='rh@x.com',
            aprovada_ibmec=False,
        )

        # ── Alunos ──────────────────────────────────────────────────────────
        self.user_aluno1 = Usuario.objects.create_user(
            username='aluno1',
            password='senha123',
            tipo='aluno',
            nome='Aluno 1',
        )
        self.aluno_matriculado = Aluno.objects.create(
            usuario=self.user_aluno1,
            cpf='111.111.111-11',
            curso=self.curso_eng,
            matriculado_estagio=True,
        )

        self.user_aluno2 = Usuario.objects.create_user(
            username='aluno2',
            password='senha123',
            tipo='aluno',
            nome='Aluno 2',
        )
        self.aluno_nao_matriculado = Aluno.objects.create(
            usuario=self.user_aluno2,
            cpf='222.222.222-22',
            curso=self.curso_eng,
            matriculado_estagio=False,
        )

        self.user_aluno3 = Usuario.objects.create_user(
            username='aluno3',
            password='senha123',
            tipo='aluno',
            nome='Aluno 3',
        )
        self.aluno_curso_adm = Aluno.objects.create(
            usuario=self.user_aluno3,
            cpf='333.333.333-33',
            curso=self.curso_adm,
            matriculado_estagio=True,
        )

        # ── Supervisor ──────────────────────────────────────────────────────
        self.user_sup = Usuario.objects.create_user(
            username='sup1',
            password='senha123',
            tipo='supervisor_empresa',
            nome='Sup 1',
        )
        self.supervisor = SupervisorEmpresa.objects.create(
            usuario=self.user_sup,
            empresa=self.empresa_aprovada,
            cargo='Gerente',
        )

        # ── Admin ───────────────────────────────────────────────────────────
        self.user_admin = Usuario.objects.create_superuser(
            username='admin',
            password='senha123',
            nome='Admin',
            email='admin@ibmec.edu.br',
        )

    def _payload_valido(self):
        return {
            'empresa': self.empresa_aprovada.pk,
            'horas_semanais': 20,
            'data_inicio_prevista': '2026-07-01',
            'data_fim_prevista': '2026-12-31',
            'plano_atividades': 'Desenvolvimento de APIs.',
        }

    def _criar_processo_pendente(self, aluno=None, empresa=None):
        aluno = aluno or self.aluno_matriculado
        empresa = empresa or self.empresa_aprovada
        return ProcessoEstagio.objects.create(
            aluno=aluno,
            empresa=empresa,
            coordenador=aluno.curso.coordenador if aluno.curso else None,
            status=ProcessoEstagio.Status.PENDENTE,
            horas_semanais=20,
            data_inicio_prevista=date(2026, 7, 1),
            data_fim_prevista=date(2026, 12, 31),
            plano_atividades='Desenvolvimento de APIs.',
        )


# ── Criação de processo ─────────────────────────────────────────────────────

class CriacaoProcessoTest(ProcessoEstagioBaseTest):
    """Cenários de criação via POST /api/processos-estagio/."""

    def test_aluno_cria_processo_valido_201_status_pendente(self):
        """Aluno matriculado cria processo válido → 201, status PENDENTE,
        coordenador setado automaticamente ao do seu curso."""
        self.client.force_authenticate(user=self.user_aluno1)
        resp = self.client.post(LIST_URL, self._payload_valido(), format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        processo = ProcessoEstagio.objects.get(pk=resp.data['id'])
        self.assertEqual(processo.status, ProcessoEstagio.Status.PENDENTE)
        self.assertEqual(processo.aluno, self.aluno_matriculado)
        self.assertEqual(processo.coordenador, self.coord_eng)

    def test_aluno_nao_matriculado_400_rn01(self):
        """RN01: aluno com matriculado_estagio=False não pode criar processo."""
        self.client.force_authenticate(user=self.user_aluno2)
        resp = self.client.post(LIST_URL, self._payload_valido(), format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        body = str(resp.data).lower()
        self.assertTrue('rn01' in body or 'matricul' in body)

    def test_empresa_nao_aprovada_400_rn09(self):
        """RN09: empresa.aprovada_ibmec=False → 400."""
        self.client.force_authenticate(user=self.user_aluno1)
        payload = self._payload_valido()
        payload['empresa'] = self.empresa_nao_aprovada.pk
        resp = self.client.post(LIST_URL, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        body = str(resp.data).lower()
        self.assertTrue('rn09' in body or 'aprovada' in body)

    def test_horas_excedem_limite_curso_400_rn03(self):
        """RN03: horas_semanais acima do limite (6×5=30 para curso_eng) → 400."""
        self.client.force_authenticate(user=self.user_aluno1)
        payload = self._payload_valido()
        payload['horas_semanais'] = 40
        resp = self.client.post(LIST_URL, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        body = str(resp.data).lower()
        self.assertIn('rn03', body)

    def test_horas_acima_limite_legal_30h_400(self):
        """Horas acima do limite legal (30h) → 400."""
        self.client.force_authenticate(user=self.user_aluno1)
        payload = self._payload_valido()
        payload['horas_semanais'] = 35
        resp = self.client.post(LIST_URL, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        body = str(resp.data).lower()
        self.assertTrue('legal' in body or '30h' in body or '30' in body)

    def test_data_fim_antes_inicio_400(self):
        """data_fim_prevista <= data_inicio_prevista → 400."""
        self.client.force_authenticate(user=self.user_aluno1)
        payload = self._payload_valido()
        payload['data_inicio_prevista'] = '2026-07-01'
        payload['data_fim_prevista'] = '2026-06-01'
        resp = self.client.post(LIST_URL, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_aluno_com_processo_vivo_nao_cria_outro_400_rn05(self):
        """RN05: aluno com processo vivo não pode criar segundo."""
        # Cria 1º processo direto via ORM
        self._criar_processo_pendente(aluno=self.aluno_matriculado)
        # Tenta criar 2º via API
        self.client.force_authenticate(user=self.user_aluno1)
        resp = self.client.post(LIST_URL, self._payload_valido(), format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        body = str(resp.data).lower()
        self.assertTrue('rn05' in body or 'andamento' in body)

    def test_nao_autenticado_401_403(self):
        """Sem autenticação → 401 ou 403."""
        resp = self.client.post(LIST_URL, self._payload_valido(), format='json')
        self.assertIn(
            resp.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )


# ── Isolamento de queryset ──────────────────────────────────────────────────

class IsolamentoQuerysetTest(ProcessoEstagioBaseTest):
    """GET /api/processos-estagio/ filtra resultados conforme papel."""

    def test_aluno_lista_apenas_proprios(self):
        """Aluno vê só os próprios processos."""
        proc_meu = self._criar_processo_pendente(aluno=self.aluno_matriculado)
        self._criar_processo_pendente(aluno=self.aluno_curso_adm)

        self.client.force_authenticate(user=self.user_aluno1)
        resp = self.client.get(LIST_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.data if isinstance(resp.data, list) else resp.data.get('results', resp.data)
        ids = [p['id'] for p in data]
        self.assertEqual(len(ids), 1)
        self.assertIn(proc_meu.pk, ids)

    def test_supervisor_lista_apenas_empresa_dele(self):
        """Supervisor vê só processos da sua empresa."""
        proc_aprovada = self._criar_processo_pendente(
            aluno=self.aluno_matriculado, empresa=self.empresa_aprovada,
        )
        self._criar_processo_pendente(
            aluno=self.aluno_curso_adm, empresa=self.empresa_nao_aprovada,
        )

        self.client.force_authenticate(user=self.user_sup)
        resp = self.client.get(LIST_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.data if isinstance(resp.data, list) else resp.data.get('results', resp.data)
        ids = [p['id'] for p in data]
        self.assertEqual(len(ids), 1)
        self.assertIn(proc_aprovada.pk, ids)

    def test_coordenador_lista_apenas_cursos_dele(self):
        """Coordenador vê só processos de alunos do(s) seu(s) curso(s)."""
        proc_eng = self._criar_processo_pendente(aluno=self.aluno_matriculado)
        self._criar_processo_pendente(aluno=self.aluno_curso_adm)

        self.client.force_authenticate(user=self.user_coord_eng)
        resp = self.client.get(LIST_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.data if isinstance(resp.data, list) else resp.data.get('results', resp.data)
        ids = [p['id'] for p in data]
        self.assertEqual(len(ids), 1)
        self.assertIn(proc_eng.pk, ids)

    def test_admin_lista_todos(self):
        """Admin (superuser) vê todos os processos."""
        p1 = self._criar_processo_pendente(aluno=self.aluno_matriculado)
        p2 = self._criar_processo_pendente(aluno=self.aluno_curso_adm)
        p3 = ProcessoEstagio.objects.create(
            aluno=self.aluno_matriculado,
            empresa=self.empresa_nao_aprovada,
            coordenador=self.coord_eng,
            status=ProcessoEstagio.Status.RASCUNHO,
            horas_semanais=10,
            data_inicio_prevista=date(2026, 8, 1),
            data_fim_prevista=date(2026, 11, 30),
            plano_atividades='Outro plano.',
        )

        self.client.force_authenticate(user=self.user_admin)
        resp = self.client.get(LIST_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.data if isinstance(resp.data, list) else resp.data.get('results', resp.data)
        ids = {p['id'] for p in data}
        self.assertEqual(ids, {p1.pk, p2.pk, p3.pk})


# ── Alterar status ──────────────────────────────────────────────────────────

class AlterarStatusTest(ProcessoEstagioBaseTest):
    """POST /api/processos-estagio/{id}/alterar_status/."""

    def test_coord_aprova_pendente_200(self):
        """Coordenador do curso do aluno aprova processo PENDENTE → 200."""
        proc = self._criar_processo_pendente(aluno=self.aluno_matriculado)
        self.client.force_authenticate(user=self.user_coord_eng)
        resp = self.client.post(
            _status_url(proc.pk),
            {'status': 'APROVADO'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        proc.refresh_from_db()
        self.assertEqual(proc.status, ProcessoEstagio.Status.APROVADO)

    def test_coord_de_outro_curso_403(self):
        """Coordenador de outro curso não pode alterar status → 403."""
        proc = self._criar_processo_pendente(aluno=self.aluno_matriculado)
        self.client.force_authenticate(user=self.user_coord_adm)
        resp = self.client.post(
            _status_url(proc.pk),
            {'status': 'APROVADO'},
            format='json',
        )
        self.assertIn(
            resp.status_code,
            (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND),
        )

    def test_aluno_nao_pode_aprovar_proprio_400_ou_403(self):
        """Aluno não pode aprovar o próprio processo → 403."""
        proc = self._criar_processo_pendente(aluno=self.aluno_matriculado)
        self.client.force_authenticate(user=self.user_aluno1)
        resp = self.client.post(
            _status_url(proc.pk),
            {'status': 'APROVADO'},
            format='json',
        )
        self.assertIn(
            resp.status_code,
            (status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN),
        )

    def test_coord_rejeita_sem_justificativa_400_rn11(self):
        """RN11: rejeitar sem justificativa_rejeicao → 400."""
        proc = self._criar_processo_pendente(aluno=self.aluno_matriculado)
        self.client.force_authenticate(user=self.user_coord_eng)
        resp = self.client.post(
            _status_url(proc.pk),
            {'status': 'REJEITADO'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        body = str(resp.data).lower()
        self.assertTrue('rn11' in body or 'justificativa' in body)

    def test_coord_rejeita_com_justificativa_200(self):
        """Rejeitar com justificativa válida → 200, status REJEITADO."""
        proc = self._criar_processo_pendente(aluno=self.aluno_matriculado)
        self.client.force_authenticate(user=self.user_coord_eng)
        resp = self.client.post(
            _status_url(proc.pk),
            {'status': 'REJEITADO', 'justificativa_rejeicao': 'motivo válido'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        proc.refresh_from_db()
        self.assertEqual(proc.status, ProcessoEstagio.Status.REJEITADO)

    def test_transicao_invalida_400_lista_validas(self):
        """Transição inválida (REJEITADO → ATIVO) → 400, lista transicoes_validas vazia."""
        proc = ProcessoEstagio.objects.create(
            aluno=self.aluno_matriculado,
            empresa=self.empresa_aprovada,
            coordenador=self.coord_eng,
            status=ProcessoEstagio.Status.REJEITADO,
            horas_semanais=20,
            data_inicio_prevista=date(2026, 7, 1),
            data_fim_prevista=date(2026, 12, 31),
            plano_atividades='Plano X.',
            justificativa_rejeicao='inicial',
        )
        self.client.force_authenticate(user=self.user_coord_eng)
        resp = self.client.post(
            _status_url(proc.pk),
            {'status': 'ATIVO'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('transicoes_validas', resp.data)
        self.assertEqual(list(resp.data['transicoes_validas']), [])

    def test_aluno_cancela_proprio_200(self):
        """Aluno pode cancelar o próprio processo PENDENTE → 200."""
        proc = self._criar_processo_pendente(aluno=self.aluno_matriculado)
        self.client.force_authenticate(user=self.user_aluno1)
        resp = self.client.post(
            _status_url(proc.pk),
            {'status': 'CANCELADO'},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        proc.refresh_from_db()
        self.assertEqual(proc.status, ProcessoEstagio.Status.CANCELADO)

    def test_aluno_nao_pode_alterar_processo_de_outro_403(self):
        """Aluno não pode alterar status de processo de outro aluno → 403."""
        proc = self._criar_processo_pendente(aluno=self.aluno_curso_adm)
        self.client.force_authenticate(user=self.user_aluno1)
        resp = self.client.post(
            _status_url(proc.pk),
            {'status': 'CANCELADO'},
            format='json',
        )
        self.assertIn(
            resp.status_code,
            (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND),
        )


# ── State machine (unit tests do módulo) ────────────────────────────────────

class StateMachineUnitTest(TestCase):
    """Unit tests do módulo app.state_machine (sem ORM)."""

    def test_pode_transicionar_valida(self):
        """PENDENTE → APROVADO é transição válida."""
        self.assertTrue(pode_transicionar(PENDENTE, APROVADO))

    def test_pode_transicionar_invalida(self):
        """REJEITADO → ATIVO não é transição válida."""
        self.assertFalse(pode_transicionar(REJEITADO, ATIVO))

    def test_estados_terminais_sem_saida(self):
        """REJEITADO, ENCERRADO, CANCELADO não têm transições válidas."""
        self.assertEqual(set(transicoes_validas(REJEITADO)), set())
        self.assertEqual(set(transicoes_validas(ENCERRADO)), set())
        self.assertEqual(set(transicoes_validas(CANCELADO)), set())

    def test_eh_terminal(self):
        """eh_terminal distingue estados terminais de não-terminais."""
        self.assertTrue(eh_terminal(REJEITADO))
        self.assertTrue(eh_terminal(ENCERRADO))
        self.assertTrue(eh_terminal(CANCELADO))
        self.assertFalse(eh_terminal(PENDENTE))
        self.assertFalse(eh_terminal(APROVADO))
