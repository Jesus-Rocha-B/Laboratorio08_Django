# Laboratorio 08 — Construcción de una API REST Empresarial con Django REST Framework (DRF)

**Curso:** Desarrollo de Aplicaciones Empresariales  
**Institución:** Tecsup  
**Sección:** 4 - C24 - Sección CD  
**Docente:** Yunior Bestard Aroche  

**Integrantes:**
1. Jesús Enrique Rocha Bobadilla
2. Erick Arturo Gamarra Mundaca

**Proyecto:** UrbanTrend — Plataforma Textil Streetwear y Sistema Logístico Avanzado con Django ORM, SQLite y Django REST Framework  
**Repositorio GitHub:** [https://github.com/Jesus-Rocha-B/Laboratorio08_Django.git](https://github.com/Jesus-Rocha-B/Laboratorio08_Django.git)

---

## 🎯 1. Objetivo del Laboratorio 08

El Laboratorio 08 implementa una arquitectura desacoplada exponiendo los recursos de la aplicación empresarial como servicios web a través de **Django REST Framework (DRF)**.

Se cubrieron dos grandes dominios:
1. **PARTE 1 — Dominio Comercial (`store`):** Exposición de catálogo de prendas, pedidos y detalles anidados, implementando validaciones de negocio, vistas genéricas, ViewSets, routers, filtros y acciones personalizadas.
2. **PARTE 2 — Dominio de Investigación Propia (`logistics`):** Exposición de insumos textiles, proveedores y órdenes de despacho con relaciones anidadas, optimización de consultas SQL (resolución del problema $N+1$), búsqueda, ordenamiento y acciones propias reutilizando QuerySets de la Semana 7.

---

## 🏗️ 2. Arquitectura de la API REST

### 2.1 Estructura Modular de Endpoints (`/api/`)

Todos los recursos se encuentran unificados bajo un enrutador central `DefaultRouter` en `config/api_urls.py`, accesible a través del API Root:

```text
/api/
├── /prendas/      -> PrendaViewSet (CRUD completo, SearchFilter, OrderingFilter)
├── /pedidos/      -> PedidoReadOnlyViewSet (Solo lectura, prefetch_related, @action /pagados/)
├── /materiales/   -> MaterialViewSet (CRUD completo, validación precio > 0, @action /con_stock/)
├── /proveedores/  -> ProveedorViewSet (CRUD completo, validación RUC 11 dígitos)
└── /despachos/    -> OrdenDespachoReadOnlyViewSet (Solo lectura, select_related + prefetch_related, @action /entregadas/)
```

---

## 📦 3. Recursos, Serializers y ViewSets Implementados

### 3.1 Dominio Comercial (`store`)

| Recurso | Tipo | Serializer | ViewSet / Vistas | Reglas de Negocio / Optimizaciones |
| :--- | :--- | :--- | :--- | :--- |
| **Prenda** | Recurso Simple | `PrendaSerializer` | `PrendaViewSet` (ModelViewSet) | Validación `validate_precio` (`precio > 0.00`). |
| **Pedido** | Recurso con Relaciones | `PedidoConDetallesSerializer`<br>`DetallePedidoSerializer` | `PedidoReadOnlyViewSet` (ReadOnlyModelViewSet) | Serialización anidada de detalles y prendas. `get_queryset()` optimizado con `prefetch_related('detalles__prenda')`. |

### 3.2 Dominio Logístico de Investigación (`logistics`)

| Recurso | Tipo | Serializer | ViewSet / Vistas | Reglas de Negocio / Optimizaciones |
| :--- | :--- | :--- | :--- | :--- |
| **Material** | Recurso Simple | `MaterialSerializer` | `MaterialViewSet` (ModelViewSet) | Validación `validate_precio_unitario` (`precio_unitario > 0.00`) y `validate_stock`. |
| **Proveedor** | Recurso Simple | `ProveedorSerializer` | `ProveedorViewSet` (ModelViewSet) | Validación `validate_ruc` (11 dígitos numéricos obligatorios). |
| **OrdenDespacho**| Recurso con Relaciones | `OrdenDespachoConDetallesSerializer`<br>`DetalleDespachoSerializer` | `OrdenDespachoReadOnlyViewSet` (ReadOnlyModelViewSet) | Serialización anidada con `select_related('sucursal_destino', 'transportista')` y `prefetch_related('detalles__material')`. |

---

## 🔍 4. Búsqueda, Ordenamiento, Filtros y Acciones Propias

Se implementaron filtros globales y por parámetro, así como acciones `@action` que reutilizan métodos encapsulados en los QuerySets personalizados de la Semana 7:

| Endpoint | Parámetro / Acción | Tipo | Función / Comportamiento |
| :--- | :--- | :--- | :--- |
| `/api/prendas/?search=Oversize` | `?search=` | `SearchFilter` | Búsqueda por texto en campos `nombre`, `marca`, `categoria`, `tipo`. |
| `/api/prendas/?search=Rebel&ordering=-precio` | `&` combinado | Búsqueda + Orden | Filtra por marca "Rebel" y ordena de mayor a menor precio. |
| `/api/pedidos/?estado=Pagado` | `?estado=` | Filtro por parámetro | Filtra pedidos según su estado mediante `get_queryset()`. |
| `/api/pedidos/pagados/` | `@action(detail=False)` | Acción personalizada | Reutiliza `PedidoQuerySet.pagados()`. |
| `/api/materiales/?search=Hilo&ordering=-precio_unitario` | `&` combinado | Búsqueda + Orden | Filtra insumos coincidentes con "Hilo" y ordena descendentemente por costo. |
| `/api/materiales/con_stock/` | `@action(detail=False)` | Acción personalizada | Reutiliza `MaterialQuerySet.con_stock()`. |
| `/api/despachos/?estado=Entregado` | `?estado=` | Filtro por parámetro | Filtra órdenes de despacho en estado "Entregado". |
| `/api/despachos/entregadas/` | `@action(detail=False)` | Acción personalizada | Reutiliza `OrdenDespachoQuerySet.entregadas()`. |

---

## ⚡ 5. Medición Empírica del Rendimiento SQL (Problema $N+1$)

Se realizaron pruebas empíricas mediante el shell de Django con `django.db.connection.queries` para comprobar el impacto de la optimización con `select_related` y `prefetch_related`:

### 5.1 Caso 1: `Pedido` y sus detalles anidados (`store`)
* **Sin optimización (`Pedido.objects.all()`):** **17 consultas SQL**.
* **Con optimización (`prefetch_related('detalles__prenda')`):** **3 consultas SQL**.
* **Impacto:** Reducción del **82.3%** en el número de queries a la base de datos.

### 5.2 Caso 2: `OrdenDespacho` con relaciones 1:1, 1:N y N:M (`logistics`)
* **Sin optimización (`OrdenDespacho.objects.all()`):** **25 consultas SQL**.
* **Con optimización (`select_related(...) + prefetch_related(...)`):** **3 consultas SQL**.
* **Impacto:** Reducción del **88.0%** en consultas SQL hacia SQLite.

---

## 🌐 6. Códigos de Estado HTTP Verificados

Se verificaron con clientes de prueba (Thunder Client / Postman) los códigos de estado REST estándar:

| Código HTTP | Petición de Prueba | Endpoint | Comportamiento |
| :--- | :--- | :--- | :--- |
| **`200 OK`** | `GET` | `/api/prendas/1/` | Lectura de recurso individual exitosa. |
| **`201 Created`** | `POST` | `/api/prendas/` | Creación y persistencia de nuevo registro válido. |
| **`400 Bad Request`**| `POST` | `/api/prendas/` | Captura de error de validación (precio <= 0). |
| **`404 Not Found`** | `GET` | `/api/prendas/9999/` | Solicitud de identificador inexistente. |
| **`204 No Content`**| `DELETE` | `/api/prendas/<id>/` | Eliminación exitosa sin contenido en el cuerpo. |

---

## 💻 7. Instalación y Ejecución Local

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/Jesus-Rocha-B/Laboratorio08_Django.git
   cd Laboratorio08_Django
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar migraciones y sembrado de datos:**
   ```bash
   python src/manage.py migrate
   python src/seed_prendas.py
   python src/seed_logistics.py
   ```

4. **Iniciar el servidor de desarrollo:**
   ```bash
   python src/manage.py runserver
   ```

5. **Navegar a la API interactiva de DRF:**
   * API Root: `http://127.0.0.1:8000/api/`
   * Catálogo de Prendas: `http://127.0.0.1:8000/api/prendas/`
   * Pedidos Anidados: `http://127.0.0.1:8000/api/pedidos/`
   * Insumos Textiles: `http://127.0.0.1:8000/api/materiales/`
   * Despachos Anidados: `http://127.0.0.1:8000/api/despachos/`
