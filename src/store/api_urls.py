from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import PrendaViewSet, PedidoReadOnlyViewSet

# Ejercicio 5 y 7: Registro de los ViewSets con DefaultRouter
router = DefaultRouter()
router.register(r'prendas', PrendaViewSet, basename='prenda')
router.register(r'pedidos', PedidoReadOnlyViewSet, basename='pedido')

urlpatterns = [
    path('', include(router.urls)),
]
