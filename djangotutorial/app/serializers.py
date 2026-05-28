from rest_framework import serializers
from .models import (
    Usuario, Curso, EmpresaConcedente, Aluno, Coordenador,
    SupervisorEmpresa, ProcessoEstagio, DocumentoProcesso,
)
from .state_machine import ESTADOS_VIVOS


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'tipo', 'nome', 'email_institucional', 'is_active']


class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = '__all__'


class EmpresaConcedenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmpresaConcedente
        fields = '__all__'


class AlunoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aluno
        fields = '__all__'


class CoordenadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordenador
        fields = '__all__'


class SupervisorEmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupervisorEmpresa
        fields = '__all__'


class DocumentoProcessoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentoProcesso
        fields = '__all__'
        read_only_fields = ['enviado_por', 'data_upload', 'versao']


class ProcessoEstagioSerializer(serializers.ModelSerializer):
    """Leitura full."""
    class Meta:
        model = ProcessoEstagio
        fields = '__all__'


class CriarProcessoSerializer(serializers.ModelSerializer):
    """Criação por aluno. aluno/status/coordenador são preenchidos pelo servidor."""
    class Meta:
        model = ProcessoEstagio
        fields = [
            'id', 'empresa', 'horas_semanais',
            'data_inicio_prevista', 'data_fim_prevista', 'plano_atividades',
            'aluno', 'status', 'coordenador',
        ]
        read_only_fields = ['aluno', 'status', 'coordenador']

    def validate(self, data):
        # Data: fim > início
        if data['data_fim_prevista'] <= data['data_inicio_prevista']:
            raise serializers.ValidationError({
                'data_fim_prevista': 'Deve ser posterior à data de início.'
            })

        request = self.context.get('request')
        if request is None or not getattr(request.user, 'is_authenticated', False):
            raise serializers.ValidationError('Usuário não autenticado.')

        try:
            aluno = request.user.aluno
        except Exception:
            raise serializers.ValidationError('Apenas alunos podem criar processos de estágio.')

        # RN01: matriculado em estágio
        if not aluno.matriculado_estagio:
            raise serializers.ValidationError({
                'aluno': 'RN01: aluno deve estar com matrícula ativa em estágio supervisionado.'
            })

        # RN09: empresa aprovada pelo IBMEC
        empresa = data['empresa']
        if not empresa.aprovada_ibmec:
            raise serializers.ValidationError({
                'empresa': 'RN09: empresa não está aprovada pelo IBMEC.'
            })

        # RN03: jornada compatível com o curso
        horas = data['horas_semanais']
        if aluno.curso is not None and aluno.curso.carga_horaria_maxima_diaria:
            limite_curso = aluno.curso.carga_horaria_maxima_diaria * 5
            if horas > limite_curso:
                raise serializers.ValidationError({
                    'horas_semanais': f'RN03: excede o limite do curso ({limite_curso}h/semana).'
                })
        # Ceiling legal (Lei 11.788/08)
        if horas > 30:
            raise serializers.ValidationError({
                'horas_semanais': 'Limite legal de 30h semanais (Lei 11.788/08).'
            })

        # RN05: 1 processo vivo por aluno
        if ProcessoEstagio.objects.filter(aluno=aluno, status__in=ESTADOS_VIVOS).exists():
            raise serializers.ValidationError(
                'RN05: aluno já possui um processo de estágio em andamento. '
                'Cancele ou aguarde o encerramento antes de abrir outro.'
            )

        return data


class AlterarStatusSerializer(serializers.ModelSerializer):
    """Mudança de status. Apenas status e justificativa_rejeicao editáveis."""
    class Meta:
        model = ProcessoEstagio
        fields = ['status', 'justificativa_rejeicao']

    def validate(self, data):
        if data.get('status') == ProcessoEstagio.Status.REJEITADO:
            justif = data.get(
                'justificativa_rejeicao',
                self.instance.justificativa_rejeicao if self.instance else '',
            )
            if not justif or not justif.strip():
                raise serializers.ValidationError({
                    'justificativa_rejeicao': 'RN11: justificativa obrigatória ao rejeitar uma solicitação.'
                })
        return data
