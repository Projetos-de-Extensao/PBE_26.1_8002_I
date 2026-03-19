from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'domicilios', views.DomicilioViewSet)
router.register(r'moradores', views.MoradorViewSet)
router.register(r'responsaveis', views.ResponsavelViewSet)
router.register(r'falecidos', views.FalecidoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]