"""Views de dashboard para coordenadores e admins."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status as drf_status
from rest_framework.permissions import IsAuthenticated

from .models import (
    ProcessoEstagio, EmpresaConcedente, DocumentoProcesso, ModeloFormulario,
)
from .permissions import get_coordenador, is_admin
from .dashboard_utils import (
    calcular_semestre,
    agregar_escala_1_4,
    agregar_escala_1_4_multi,
    agregar_escala_3,
    agregar_checkbox_duplo,
    calcular_avaliacao_media,
)


def _base_queryset(user):
    """Retorna queryset de processos filtrado por papel do usuário."""
    coord = get_coordenador(user)
    if is_admin(user):
        return ProcessoEstagio.objects.select_related(
            'aluno__usuario', 'aluno__curso', 'empresa', 'coordenador',
        ).all()
    if coord is not None:
        cursos = coord.cursos_coordenados.all()
        return ProcessoEstagio.objects.select_related(
            'aluno__usuario', 'aluno__curso', 'empresa', 'coordenador',
        ).filter(aluno__curso__in=cursos)
    return ProcessoEstagio.objects.none()


def _aplicar_filtros(qs, params):
    empresa = params.get('empresa')
    if empresa:
        qs = qs.filter(empresa_id=empresa)
    semestre = params.get('semestre')
    if semestre:
        qs = [p for p in qs if calcular_semestre(p.data_inicio_prevista) == semestre]
        return qs
    status_filtro = params.get('status')
    if status_filtro:
        qs = qs.filter(status=status_filtro.upper())
    curso = params.get('curso')
    if curso:
        qs = qs.filter(aluno__curso_id=curso)
    com_respostas = params.get('com_respostas')
    if com_respostas is not None:
        flag = com_respostas.lower() in ('true', '1')
        if flag:
            qs = qs.exclude(respostas_formulario=None)
        else:
            qs = qs.filter(respostas_formulario=None)
    return qs


def _score_medio_documentos(processo):
    docs = DocumentoProcesso.objects.filter(processo=processo)
    scores = [d.score_conformidade for d in docs if d.score_conformidade is not None]
    if not scores:
        return None
    return round(sum(scores) / len(scores), 2)


def _processo_dict(p):
    return {
        'id': p.pk,
        'aluno_nome': p.aluno.usuario.nome if p.aluno and p.aluno.usuario else '',
        'aluno_matricula': p.aluno.usuario.username if p.aluno and p.aluno.usuario else '',
        'curso_nome': p.aluno.curso.nome if p.aluno and p.aluno.curso else '',
        'empresa_nome': p.empresa.razao_social if p.empresa else '',
        'empresa_id': p.empresa_id,
        'semestre': calcular_semestre(p.data_inicio_prevista),
        'horas_semanais': p.horas_semanais,
        'horas_totais_estimadas': _estimar_horas_totais(p),
        'remuneracao': float(p.valor_bolsa) if p.valor_bolsa is not None else None,
        'status': p.status,
        'tem_respostas': p.respostas_formulario is not None,
        'score_medio_documentos': _score_medio_documentos(p),
    }


def _estimar_horas_totais(p):
    if p.data_inicio_prevista and p.data_fim_prevista:
        delta = (p.data_fim_prevista - p.data_inicio_prevista).days
        semanas = delta / 7
        return round(semanas * p.horas_semanais)
    return None


class DashboardProcessosView(APIView):
    """GET /api/dashboard/processos/ — lista processos com dados agregados."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        coord = get_coordenador(user)
        if not is_admin(user) and coord is None:
            return Response(
                {'erro': 'Acesso restrito a coordenadores e administradores.'},
                status=drf_status.HTTP_403_FORBIDDEN,
            )
        qs = _base_queryset(user)
        qs = _aplicar_filtros(qs, request.query_params)
        processos = list(qs)
        data = [_processo_dict(p) for p in processos]
        return Response(data, status=drf_status.HTTP_200_OK)


class DashboardEstatisticasView(APIView):
    """GET /api/dashboard/estatisticas/ — estatísticas agregadas dos processos."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        coord = get_coordenador(user)
        if not is_admin(user) and coord is None:
            return Response(
                {'erro': 'Acesso restrito a coordenadores e administradores.'},
                status=drf_status.HTTP_403_FORBIDDEN,
            )
        qs = _base_queryset(user)
        qs = _aplicar_filtros(qs, request.query_params)
        processos = list(qs)

        total = len(processos)
        com_respostas = sum(1 for p in processos if p.respostas_formulario is not None)

        remuneracoes = [float(p.valor_bolsa) for p in processos if p.valor_bolsa is not None]
        media_remuneracao = round(sum(remuneracoes) / len(remuneracoes), 2) if remuneracoes else None

        horas = [p.horas_semanais for p in processos if p.horas_semanais is not None]
        media_horas_semanais = round(sum(horas) / len(horas), 2) if horas else None

        todos_scores = []
        for p in processos:
            docs = DocumentoProcesso.objects.filter(processo=p)
            for d in docs:
                if d.score_conformidade is not None:
                    todos_scores.append(d.score_conformidade)
        media_score_documentos = round(sum(todos_scores) / len(todos_scores), 2) if todos_scores else None

        por_status = {}
        for p in processos:
            por_status[p.status] = por_status.get(p.status, 0) + 1

        por_semestre = {}
        for p in processos:
            sem = calcular_semestre(p.data_inicio_prevista)
            if sem:
                por_semestre[sem] = por_semestre.get(sem, 0) + 1

        por_empresa = {}
        for p in processos:
            nome = p.empresa.razao_social if p.empresa else 'N/A'
            por_empresa[nome] = por_empresa.get(nome, 0) + 1

        secoes_agregadas = {}
        if coord is not None:
            cursos = coord.cursos_coordenados.all()
            modelo = ModeloFormulario.objects.filter(curso__in=cursos, ativo=True).order_by('-criado_em').first()
            if modelo:
                processos_com_resp = [p for p in processos if p.respostas_formulario is not None]
                for secao in modelo.secoes:
                    tipo = secao.get('tipo')
                    sid = secao.get('id')
                    titulo = secao.get('titulo', sid)
                    if tipo == 'escala_1_4':
                        secoes_agregadas[sid] = {
                            'titulo': titulo,
                            'tipo': tipo,
                            'dados': agregar_escala_1_4(processos_com_resp, sid),
                        }
                    elif tipo == 'escala_1_4_multi':
                        colunas = secao.get('colunas', [])
                        secoes_agregadas[sid] = {
                            'titulo': titulo,
                            'tipo': tipo,
                            'dados': agregar_escala_1_4_multi(processos_com_resp, sid, colunas),
                        }
                    elif tipo == 'escala_3':
                        opcoes = secao.get('opcoes', [])
                        secoes_agregadas[sid] = {
                            'titulo': titulo,
                            'tipo': tipo,
                            'dados': agregar_escala_3(processos_com_resp, sid, opcoes),
                        }
                    elif tipo == 'checkbox_duplo':
                        colunas = secao.get('colunas', [])
                        secoes_agregadas[sid] = {
                            'titulo': titulo,
                            'tipo': tipo,
                            'dados': agregar_checkbox_duplo(processos_com_resp, sid, colunas),
                        }

        return Response({
            'total_processos': total,
            'com_respostas': com_respostas,
            'media_remuneracao': media_remuneracao,
            'media_horas_semanais': media_horas_semanais,
            'media_score_documentos': media_score_documentos,
            'por_status': por_status,
            'por_semestre': por_semestre,
            'por_empresa': por_empresa,
            'secoes_agregadas': secoes_agregadas,
        }, status=drf_status.HTTP_200_OK)


class DashboardEmpresasView(APIView):
    """GET /api/dashboard/empresas/ — estatísticas por empresa concedente."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        coord = get_coordenador(user)
        if not is_admin(user) and coord is None:
            return Response(
                {'erro': 'Acesso restrito a coordenadores e administradores.'},
                status=drf_status.HTTP_403_FORBIDDEN,
            )
        qs = _base_queryset(user)
        processos = list(qs)

        empresas = {}
        for p in processos:
            if p.empresa_id not in empresas:
                empresas[p.empresa_id] = {
                    'empresa_id': p.empresa_id,
                    'nome': p.empresa.razao_social if p.empresa else '',
                    'cnpj': p.empresa.cnpj if p.empresa else '',
                    '_processos': [],
                }
            empresas[p.empresa_id]['_processos'].append(p)

        resultado = []
        for emp_id, dados in empresas.items():
            procs = dados['_processos']
            remuneracoes = [float(p.valor_bolsa) for p in procs if p.valor_bolsa is not None]
            horas = [p.horas_semanais for p in procs]
            avaliacao_media = calcular_avaliacao_media(procs)
            estagiarios = [
                {
                    'aluno_nome': p.aluno.usuario.nome if p.aluno and p.aluno.usuario else '',
                    'curso_nome': p.aluno.curso.nome if p.aluno and p.aluno.curso else '',
                    'status': p.status,
                    'semestre': calcular_semestre(p.data_inicio_prevista),
                }
                for p in procs
            ]
            resultado.append({
                'empresa_id': emp_id,
                'nome': dados['nome'],
                'cnpj': dados['cnpj'],
                'total_estagios': len(procs),
                'media_remuneracao': round(sum(remuneracoes) / len(remuneracoes), 2) if remuneracoes else None,
                'media_horas_semanais': round(sum(horas) / len(horas), 2) if horas else None,
                'avaliacao_media': avaliacao_media,
                'estagiarios': estagiarios,
            })

        return Response(resultado, status=drf_status.HTTP_200_OK)
