from rest_framework import serializers
from .models import (
    Usuario, Curso, Empresa, Aluno, Coordenador, SolicitacaoEstagio,
    TermoCompromisso, ApoliceSeguro, RelatorioEstagio, AssinaturaDigital,
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
    class Meta:
        model = SolicitacaoEstagio
        fields = '__all__'


class TermoCompromissoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermoCompromisso
        fields = '__all__'


class ApoliceSeguroSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApoliceSeguro
        fields = '__all__'


class RelatorioEstagioSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelatorioEstagio
        fields = '__all__'


class AssinaturaDigitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssinaturaDigital
        fields = '__all__'
