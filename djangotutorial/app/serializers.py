from rest_framework import serializers
from .models import (
    Usuario, Curso, Empresa, Aluno, Coordenador, SolicitacaoEstagio,
)


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'


class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = '__all__'


class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = '__all__'


class AlunoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aluno
        fields = '__all__'


class CoordenadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordenador
        fields = '__all__'


class SolicitacaoEstagioSerializer(serializers.ModelSerializer):
    """Serializer completo — usado somente por admin."""
    class Meta:
        model = SolicitacaoEstagio
        fields = '__all__'


class CriarSolicitacaoSerializer(serializers.ModelSerializer):
    """
    Serializer para criação de solicitação pelo aluno.
    'aluno', 'status' e 'coordenador' são somente-leitura:
    o servidor os define, o cliente não pode enviá-los.
    """
    class Meta:
        model = SolicitacaoEstagio
        fields = [
            'id', 'empresa', 'horas_semanais',
            'data_inicio_prevista', 'data_fim_prevista',
            'aluno', 'status', 'coordenador',
        ]
        read_only_fields = ['aluno', 'status', 'coordenador']


class AlterarStatusSerializer(serializers.ModelSerializer):
    """
    Serializer para mudança de status pelo coordenador.
    Somente 'status' e 'justificativa_rejeicao' são editáveis.
    Rejeição exige justificativa não-vazia.
    """
    class Meta:
        model = SolicitacaoEstagio
        fields = [
            'id', 'aluno', 'empresa', 'horas_semanais',
            'data_inicio_prevista', 'data_fim_prevista',
            'coordenador', 'status', 'justificativa_rejeicao',
        ]
        read_only_fields = [
            'aluno', 'empresa', 'horas_semanais',
            'data_inicio_prevista', 'data_fim_prevista', 'coordenador',
        ]

    def validate_status(self, value):
        status_permitidos = {
            SolicitacaoEstagio.Status.APROVADO,
            SolicitacaoEstagio.Status.REJEITADO,
            SolicitacaoEstagio.Status.RETIFICACAO_SOLICITADA,
            SolicitacaoEstagio.Status.ATIVO,
            SolicitacaoEstagio.Status.ENCERRADO,
        }
        if value not in status_permitidos:
            raise serializers.ValidationError(
                f"Status inválido. Opções permitidas: {', '.join(status_permitidos)}"
            )
        return value

    def validate(self, data):
        if data.get('status') == SolicitacaoEstagio.Status.REJEITADO:
            justificativa = data.get(
                'justificativa_rejeicao',
                self.instance.justificativa_rejeicao if self.instance else '',
            )
            if not justificativa or not justificativa.strip():
                raise serializers.ValidationError(
                    {'justificativa_rejeicao': 'Obrigatório ao rejeitar uma solicitação.'}
                )
        return data





