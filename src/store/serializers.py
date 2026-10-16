from rest_framework import serializers
from .models import Prenda, Pedido, DetallePedido


class PrendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prenda
        fields = '__all__'

    # Regla de negocio: El precio debe ser estrictamente mayor que cero
    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio de la prenda debe ser mayor que cero (S/ 0.00).")
        return value


# Ejercicio 7: Serializer para la entidad relacionada anidada
class DetallePedidoSerializer(serializers.ModelSerializer):
    prenda_nombre = serializers.ReadOnlyField(source='prenda.nombre')
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = DetallePedido
        fields = ['id', 'prenda', 'prenda_nombre', 'cantidad', 'precio_unitario', 'subtotal']


# Ejercicio 7: Serializer para el recurso con relaciones (Pedido con sus detalles anidados)
class PedidoConDetallesSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoSerializer(many=True, read_only=True)
    total_calculado = serializers.ReadOnlyField(source='total')

    class Meta:
        model = Pedido
        fields = [
            'id',
            'codigo',
            'cliente_nombre',
            'cliente_email',
            'fecha_creacion',
            'estado',
            'total_calculado',
            'detalles'
        ]
