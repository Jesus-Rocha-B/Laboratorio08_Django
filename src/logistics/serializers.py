from rest_framework import serializers
from .models import Proveedor, CategoriaInsumo, Material, Sucursal, Transportista, OrdenDespacho, DetalleDespacho


# 1. Serializer para Proveedor
class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = '__all__'

    def validate_ruc(self, value):
        if len(value) != 11 or not value.isdigit():
            raise serializers.ValidationError("El RUC debe contener exactamente 11 dígitos numéricos.")
        return value


# 2. Serializer para CategoriaInsumo
class CategoriaInsumoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaInsumo
        fields = '__all__'


# 3. Serializer para Material (Insumo Textil) con validación de regla de negocio
class MaterialSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')

    class Meta:
        model = Material
        fields = ['id', 'categoria', 'categoria_nombre', 'nombre', 'unidad_medida', 'precio_unitario', 'stock']

    # Regla de negocio: El precio unitario debe ser estrictamente mayor a 0
    def validate_precio_unitario(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio unitario del insumo debe ser mayor que cero (S/ 0.00).")
        return value

    # Validación adicional de stock
    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock en almacén no puede ser negativo.")
        return value


# 4. Serializer para Detalle de Despacho (relación anidada)
class DetalleDespachoSerializer(serializers.ModelSerializer):
    material_nombre = serializers.ReadOnlyField(source='material.nombre')
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = DetalleDespacho
        fields = ['id', 'material', 'material_nombre', 'cantidad_despachada', 'costo_unitario_historico', 'lote_produccion', 'subtotal']


# 5. Serializer para Orden de Despacho con detalles anidados
class OrdenDespachoConDetallesSerializer(serializers.ModelSerializer):
    detalles = DetalleDespachoSerializer(many=True, read_only=True)
    sucursal_nombre = serializers.ReadOnlyField(source='sucursal_destino.nombre')
    transportista_empresa = serializers.ReadOnlyField(source='transportista.empresa')
    costo_total = serializers.ReadOnlyField()

    class Meta:
        model = OrdenDespacho
        fields = [
            'id',
            'codigo',
            'sucursal_destino',
            'sucursal_nombre',
            'transportista',
            'transportista_empresa',
            'fecha_emision',
            'estado',
            'observaciones',
            'costo_total',
            'detalles'
        ]
