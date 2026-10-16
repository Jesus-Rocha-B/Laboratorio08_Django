from django.urls import path, include
from rest_framework.routers import DefaultRouter

from store.api_views import PrendaViewSet, PedidoReadOnlyViewSet
from logistics.api_views import MaterialViewSet, ProveedorViewSet, OrdenDespachoReadOnlyViewSet

# Router centralizado para todos los recursos de la API REST
router = DefaultRouter()

# Recursos de la App Principal (store)
router.register(r'prendas', PrendaViewSet, basename='prenda')
router.register(r'pedidos', PedidoReadOnlyViewSet, basename='pedido')

# Recursos de la Investigación Propia (logistics)
router.register(r'materiales', MaterialViewSet, basename='material')
router.register(r'proveedores', ProveedorViewSet, basename='proveedor')
router.register(r'despachos', OrdenDespachoReadOnlyViewSet, basename='despacho')

urlpatterns = [
    path('', include(router.urls)),
]
