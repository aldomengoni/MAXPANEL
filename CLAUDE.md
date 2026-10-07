# CLAUDE.md — Guía de Desarrollo Odoo 19.0

> Documento de contexto para Claude AI al trabajar en proyectos Odoo 18.
> Claude debe leer este archivo al inicio de cada sesión de desarrollo.

---

## 1. ROL Y CONTEXTO

Eres un experto desarrollador Odoo 19.0 con dominio completo de:
- ORM de Odoo (modelos, campos, métodos, decoradores)
- Estructura de módulos y sistema de herencia
- Motor de vistas (XML, QWeb, Assets)
- Reportes QWeb (PDF), Excel (xlsx), Pivotes y Asistentes (Wizards)
- Seguridad, grupos, reglas de acceso y record rules
- API RPC, controladores HTTP y JSON-RPC
- Pagina web (website) controller
- Integración via xml para facturación electrónica
- Análisis de xml para envío de facturas y firma digital
- Revisar el módulo signxml para facturación y ver otras opciones de librerias en python
- Versión de python a utilizar 3.12
- Importante analizar el módulo "certificate" de odoo para las claves
- Migración de Odoo Versión 18 a Odoo Versión 19 analizando siempre los modulos base para no causar conflictos

Antes de generar cualquier código, **analiza el módulo base correspondiente** para respetar la estructura existente y realizar herencias correctas.

---

## 2. CAMBIOS DE COMPATIBILIDAD ODOO 19 (obligatorio revisar en cada módulo)

Detectados al migrar/depurar módulos existentes (ej. `monnet_comercial`) para que instalen en Odoo 19. Verificar siempre estos puntos antes de dar por terminado un módulo:

1. **Versión del manifest**: `__manifest__.py` debe declarar `"version": "19.0.x.y.z"`. Si el prefijo de versión no coincide con la serie del servidor, Odoo marca el módulo como `installable=False` sin más detalle en el log.

2. **`_sql_constraints` eliminado**: ya no se soporta como lista de tuplas. Reemplazar por atributos de clase `models.Constraint`:
   ```python
   # Antes (Odoo ≤17)
   _sql_constraints = [("name_uniq", "unique(name)", "mensaje")]

   # Ahora (Odoo 19)
   _name_uniq = models.Constraint("unique(name)", "mensaje")
   ```
   El nombre del atributo Python (con `_` inicial) es el nombre técnico del constraint.

3. **`name_get()` ya no se invoca**: el ORM lo eliminó por completo (no lanza error, simplemente el override deja de tener efecto). Migrar a `_compute_display_name`:
   ```python
   @api.depends("campo_a", "campo_b")
   def _compute_display_name(self):
       for rec in self:
           rec.display_name = f"..."
   ```

4. **`res.groups` perdió el campo `category_id`**: ahora la categoría se asigna vía un nuevo modelo intermedio `res.groups.privilege` (campo `privilege_id` en `res.groups`). Patrón correcto en XML de seguridad:
   ```xml
   <record id="privilege_xxx" model="res.groups.privilege">
       <field name="name">Nombre</field>
       <field name="category_id" ref="module_category_xxx"/>
   </record>
   <record id="group_xxx" model="res.groups">
       <field name="name">Nombre grupo</field>
       <field name="privilege_id" ref="privilege_xxx"/>
   </record>
   ```
   Escribir `category_id` directamente sobre un `res.groups` produce `ParseError` al cargar el XML.

5. **`<group>` de "Agrupar por" en vistas `search` ya no acepta `string` ni `expand`**: el esquema RNG (`base/rng/search_view.rng` + `common.rng`) solo permite un `<group>` sin atributos, conteniendo `<filter>`. Usar:
   ```xml
   <group>
       <filter name="group_x" string="Campo" context="{'group_by': 'campo'}"/>
   </group>
   ```
   (nada de `expand="0" string="Agrupar por"`, eso ya generaba `ParseError: Invalid attribute expand for element group`).

6. **Verificación rápida de vistas antes de instalar**: para validar `list`/`search`/`graph`/`pivot`/`calendar` contra el esquema real sin necesitar el servidor levantado, se puede usar `lxml.etree.RelaxNG` cargando `odoo/addons/base/rng/<tipo>_view.rng` del código fuente de Odoo 19 y validar el `arch` de cada vista. Las vistas `form`/`kanban` no tienen RNG estricto (validación más laxa vía `view_validation.py`).

7. **Campos `compute=` sin `store=True` no son filtrables**: si un `filter`/`domain` de una vista `search` usa un campo así, la validación de la vista falla al instalar con `No se puede buscar el campo "x" en la ruta "x"`. Esto aplica sobre todo a `Selection`/`Boolean` calculados en base a fechas relativas (`today`) que no conviene guardar en BD (quedarían desactualizados sin un cron). Solución: agregar un método `search=` que traduzca el filtro a un dominio sobre los campos reales, usando la nueva API `odoo.fields.Domain`:
   ```python
   from odoo.fields import Domain

   estado = fields.Selection(..., compute="_compute_estado", search="_search_estado")

   def _search_estado(self, operator, value):
       if operator != "in":
           return NotImplemented
       hoy = fields.Date.context_today(self)
       domain = Domain.FALSE
       if "activa" in value:
           domain |= Domain("fecha_inicio", "<=", hoy) & Domain("fecha_fin", ">=", hoy)
       return domain
   ```
   Nota: el framework normaliza `('estado', '=', 'x')` a operador `'in'` con lista antes de llamar al método `search`, igual que hace el propio core (ver `account_lock_exception.py`).

---