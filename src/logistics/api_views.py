from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Material, Proveedor, OrdenDespacho
from .serializers import (
    MaterialSerializer,
    ProveedorSerializer,
    OrdenDespachoConDetallesSerializer,
)


# Ejercicio 11: ModelViewSet para el recurso simple Material
class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'unidad_medida', 'categoria__nombre']
    ordering_fields = ['precio_unitario', 'stock', 'nombre']
    ordering = ['id']

    # Ejercicio 13: Acción personalizada que reutiliza el método .con_stock() de MaterialQuerySet (Semana 7)
    @action(detail=False, methods=['get'])
    def con_stock(self, request):
        """Endpoint: /api/materiales/con_stock/"""
        materiales_stock = self.get_queryset().con_stock()
        serializer = self.get_serializer(materiales_stock, many=True)
        return Response(serializer.data)


# Ejercicio 11: Segundo ModelViewSet para Proveedor
class ProveedorViewSet(viewsets.ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['razon_social', 'ruc', 'correo']
    ordering_fields = ['razon_social', 'ruc']
    ordering = ['razon_social']


# Ejercicio 12: ReadOnlyModelViewSet para OrdenDespacho con relaciones anidadas y optimización
class OrdenDespachoReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrdenDespachoConDetallesSerializer

    def get_queryset(self):
        # Optimización con select_related y prefetch_related para evitar N+1
        qs = OrdenDespacho.objects.select_related('sucursal_destino', 'transportista').prefetch_related('detalles__material').all()
        
        # Filtro por parámetro ?estado=
        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado__iexact=estado)
        return qs

    # Acción personalizada @action que reutiliza el método .entregadas() del QuerySet
    @action(detail=False, methods=['get'])
    def entregadas(self, request):
        entregadas_qs = self.get_queryset().entregadas()
        serializer = self.get_serializer(entregadas_qs, many=True)
        return Response(serializer.data)
