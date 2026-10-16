from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Prenda, Pedido
from .serializers import PrendaSerializer, PedidoConDetallesSerializer


# Ejercicio 5 y 8: Recurso simple con Búsqueda y Ordenamiento
class PrendaViewSet(viewsets.ModelViewSet):
    queryset = Prenda.objects.all()
    serializer_class = PrendaSerializer
    
    # Ejercicio 8: SearchFilter y OrderingFilter configurados
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'marca', 'categoria', 'tipo']
    ordering_fields = ['precio', 'stock', 'nombre']
    ordering = ['id']


# Ejercicio 7 y 8: Recurso con relaciones, filtro por parámetro ?estado= y @action propia
class PedidoReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PedidoConDetallesSerializer

    def get_queryset(self):
        # Optimización con prefetch_related para evitar N+1
        qs = Pedido.objects.prefetch_related('detalles__prenda').all()
        
        # Ejercicio 8: Filtro manual por parámetro de consulta (?estado=)
        estado = self.request.query_params.get('estado')
        if estado:
            qs = qs.filter(estado__iexact=estado)
        return qs

    # Ejercicio 8: Acción personalizada @action que reutiliza el QuerySet personalizado (.pagados())
    @action(detail=False, methods=['get'])
    def pagados(self, request):
        """
        Endpoint: /api/pedidos/pagados/
        Reutiliza el método .pagados() del PedidoQuerySet de la Semana 7.
        """
        pedidos_pagados = self.get_queryset().pagados()
        serializer = self.get_serializer(pedidos_pagados, many=True)
        return Response(serializer.data)
