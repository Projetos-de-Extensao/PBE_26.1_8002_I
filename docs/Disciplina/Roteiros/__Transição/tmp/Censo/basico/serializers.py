from rest_framework import serializers
from .models import *

class DomicilioSerializer(serializers.ModelSerializer):
    especie = serializers.CharField(source='get_especie_display')
    tipo = serializers.CharField(source='get_tipo_display')
    
    class Meta:
        model = Domicilio
        fields = '__all__'

class MoradorSerializer(serializers.ModelSerializer):
    sexo = serializers.CharField(source='get_sexo_display')
    raca_cor = serializers.CharField(source='get_raca_cor_display')
    
    class Meta:
        model = Morador
        fields = '__all__'

class ResponsavelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Responsavel
        fields = ['renda_mensal', 'faixa_rendimento']

class FalecidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Falecido
        fields = '__all__'