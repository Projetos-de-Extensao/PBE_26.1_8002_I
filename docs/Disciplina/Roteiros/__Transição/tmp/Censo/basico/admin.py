from django.contrib import admin
from .models import Domicilio, Morador, Responsavel, Falecido

admin.site.register(Domicilio)
admin.site.register(Morador)
admin.site.register(Responsavel)
admin.site.register(Falecido)
