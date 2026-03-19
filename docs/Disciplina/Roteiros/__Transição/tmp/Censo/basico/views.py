from rest_framework import viewsets
from .models import *
from .serializers import *

class DomicilioViewSet(viewsets.ModelViewSet):
    queryset = Domicilio.objects.prefetch_related('moradores')
    serializer_class = DomicilioSerializer

class MoradorViewSet(viewsets.ModelViewSet):
    queryset = Morador.objects.select_related('domicilio')
    serializer_class = MoradorSerializer

class ResponsavelViewSet(viewsets.ModelViewSet):
    queryset = Responsavel.objects.select_related('morador')
    serializer_class = ResponsavelSerializer

class FalecidoViewSet(viewsets.ModelViewSet):
    queryset = Falecido.objects.all()
    serializer_class = FalecidoSerializer