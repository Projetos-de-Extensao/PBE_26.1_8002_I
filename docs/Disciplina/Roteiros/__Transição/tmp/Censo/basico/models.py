from django.db import models
from enum import Enum

class TipoDomicilio(models.TextChoices):
    PERMANENTE = '1', 'Domicílio Particular Permanente'
    IMPROVISADO = '5', 'Domicílio Particular Improvisado'
    COLETIVO = '6', 'Domicílio Coletivo com Morador'

class TipoConstrucao(models.TextChoices):
    CASA = '011', 'Casa'
    APARTAMENTO = '013', 'Apartamento'
    # ... (adicionar todos os outros tipos do questionário 1.12)

class Sexo(models.TextChoices):
    MASCULINO = '1', 'Masculino'
    FEMININO = '2', 'Feminino'

class RacaCor(models.TextChoices):
    BRANCA = '1', 'Branca'
    PRETA = '2', 'Preta'
    AMARELA = '3', 'Amarela'
    PARDA = '4', 'Parda'
    INDIGENA = '5', 'Indígena'

class Domicilio(models.Model):
    uf = models.CharField(max_length=2)
    municipio = models.CharField(max_length=100)
    especie = models.CharField(max_length=1, choices=TipoDomicilio.choices)
    tipo = models.CharField(max_length=3, choices=TipoConstrucao.choices)
    
    # Seção 3 - Características do Domicílio
    abastecimento_agua = models.CharField(max_length=1)  # 3.01
    banheiros = models.PositiveIntegerField()  # 3.04
    destino_esgoto = models.CharField(max_length=1)  # 3.07 ou 3.08
    coleta_lixo = models.CharField(max_length=1)  # 3.09

class Morador(models.Model):
    domicilio = models.ForeignKey(Domicilio, on_delete=models.CASCADE, related_name='moradores')
    nome = models.CharField(max_length=100)  # 2.03.1
    sobrenome = models.CharField(max_length=100)  # 2.03.2
    sexo = models.CharField(max_length=1, choices=Sexo.choices)  # 2.04
    data_nascimento = models.DateField(null=True, blank=True)  # 2.05
    idade = models.PositiveIntegerField()  # 2.05.5 ou 2.05.6
    parentesco = models.CharField(max_length=2)  # 2.06 (01-20)
    
    # Seção 4 - Identificação Étnico-Racial
    raca_cor = models.CharField(max_length=1, choices=RacaCor.choices)  # 4.01
    considera_indigena = models.BooleanField(null=True)  # 4.02
    etnia_indigena = models.CharField(max_length=100, blank=True)  # 4.03
    fala_lingua_indigena = models.BooleanField(null=True)  # 4.04
    
    # Seção 6 - Educação (para >=5 anos)
    alfabetizado = models.BooleanField(null=True)  # 6.01

class Responsavel(models.Model):
    morador = models.OneToOneField(Morador, on_delete=models.CASCADE)
    renda_mensal = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # 7.01.1
    faixa_rendimento = models.CharField(max_length=1)  # 7.01.2

class Falecido(models.Model):
    domicilio = models.ForeignKey(Domicilio, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)  # 8.02.1
    data_falecimento = models.DateField()  # 8.03
    idade_falecimento = models.PositiveIntegerField()  # 8.05.1 ou 8.05.2