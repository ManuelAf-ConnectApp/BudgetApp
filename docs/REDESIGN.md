# Rediseño de experiencia — BudgetApp

## Objetivo

Convertir la aplicación en un espacio de trabajo claro para crear, revisar y
enviar presupuestos. La prioridad es reducir la carga visual, dar visibilidad
permanente al importe y a las acciones de mayor valor, y conservar el ritmo de
trabajo de una aplicación de escritorio.

Este documento es una propuesta de diseño. No cambia comportamiento ni código.

## Problemas que resuelve

- El editor y el historial compiten por el ancho disponible sin una jerarquía
  clara.
- Guardar, exportar y cambiar el estado del presupuesto quedan repartidos
  entre menús y botones.
- El total se ve al final del editor, después de una lista secundaria que no
  aporta decisión inmediata.
- La información de cliente ocupa mucho alto aunque se use menos que las
  líneas de presupuesto.

## Principios

1. **El presupuesto es el foco.** Las líneas y el total dominan la pantalla.
2. **Acciones cercanas a su resultado.** Guardar, exportar y el estado viven
   en la cabecera del presupuesto; añadir una línea vive junto a la tabla.
3. **Información progresiva.** Historial, configuración y opciones poco
   frecuentes se muestran solo cuando se necesitan.
4. **Datos financieros inequívocos.** Importes alineados a la derecha, moneda
   explícita, estado visible y acciones destructivas separadas.
5. **Escritorio sin fricción.** Se mantienen atajos, edición directa de la
   tabla y densidad suficiente para trabajar rápido.

## Arquitectura propuesta

### Pantalla de bienvenida

Una tarjeta centrada de 520–600 px con logo, idioma y dos acciones:

- **Continuar en local** como acción primaria.
- **Conectar a servidor** como acción secundaria, con una breve explicación
  de que se solicitarán los datos de conexión.

El selector de idioma se sitúa arriba a la derecha de la tarjeta. La pantalla
no debe parecer una pantalla de configuración: el mensaje principal es
“¿Dónde quieres trabajar?”.

### Espacio de trabajo de presupuestos

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Logo · Presupuestos   [Buscar]           Borrador ▾  Exportar  Guardar  │
├───────────────┬─────────────────────────────────────────┬──────────────┤
│ HISTORIAL      │ Presupuesto #00042 · 28 oct 2026         │ RESUMEN      │
│ + Nuevo        │ Cliente                                  │ Subtotal     │
│ Buscar…        │ [Empresa] [NIF]                          │ Descuento    │
│                │ [Nombre] [Apellidos]                     │ IVA          │
│ Hoy            │                                         │ ───────────  │
│ · Acme · 980 € │ Líneas              + Añadir línea       │ TOTAL        │
│ Ayer           │ ┌─────────────────────────────────────┐ │ 1.185,80 €  │
│ · Nova · 430 € │ │ Descripción · Cant. · Precio · Total│ │              │
│                │ └─────────────────────────────────────┘ │ Guardar      │
│                │ Notas del presupuesto                    │ Exportar PDF │
└───────────────┴─────────────────────────────────────────┴──────────────┘
```

La pantalla usa tres áreas redimensionables:

| Área | Función | Comportamiento |
| --- | --- | --- |
| Historial izquierdo | Crear, buscar y abrir presupuestos | Se puede ocultar y recuperar desde la cabecera. |
| Editor central | Cliente, tabla de líneas y notas | Es el área flexible y recibe el foco inicial. |
| Resumen derecho | Desglose, total y acciones finales | Permanece visible al desplazarse; puede contraerse en ventanas estrechas. |

### Cabecera de presupuesto

- Migas o título: `Presupuestos / #00042`.
- Fecha editable y selector de estado (`Borrador`, `Enviado`, `Aceptado`) con
  color acompañado siempre de texto.
- Acción primaria: **Guardar**. Si no hay cambios, queda inactiva.
- Acción secundaria: **Exportar PDF**. Las acciones menos frecuentes
  (duplicar, imprimir, eliminar) se agrupan bajo `Más`.
- Indicador discreto “Cambios sin guardar” junto al título, no en un diálogo.

### Cliente y líneas

- El bloque Cliente se presenta como una tarjeta compacta de dos columnas:
  empresa/NIF y nombre/apellidos; la fecha queda en la cabecera.
- La tabla elimina elementos decorativos y reserva el contraste para la fila
  seleccionada y los campos con error. Las columnas monetarias se alinean a la
  derecha; `Total` es solo lectura.
- La barra de tabla contiene `+ Añadir línea`, duplicar y eliminar. Eliminar
  requiere confirmación solo cuando borra contenido ya guardado.
- Las notas se sitúan tras la tabla y se pliegan cuando están vacías.

### Historial

- Agrupado por recencia (`Hoy`, `Esta semana`, `Anteriores`) con búsqueda por
  identificador, cliente o empresa.
- Cada fila muestra cliente, fecha, estado y total; nunca depende solo del
  color para mostrar el estado.
- Un presupuesto abierto conserva un resaltado sutil y una etiqueta de estado.

## Lenguaje visual

La base actual de azules suaves y grises fríos funciona, pero se aplicará de
forma consistente mediante tokens de diseño:

| Token | Uso | Valor inicial |
| --- | --- | --- |
| Fondo de aplicación | Superficie exterior | `#F8FAFC` |
| Superficie | Tarjetas y paneles | `#FFFFFF` |
| Texto principal | Títulos y cifras | `#0F172A` |
| Texto secundario | Etiquetas y ayuda | `#475569` |
| Primario | Guardar y foco | `#2563EB` |
| Éxito | Aceptado | `#15803D` |
| Aviso | Enviado | `#B45309` |
| Borde | Separación suave | `#E2E8F0` |

- Tipografía: la tipografía de sistema, con 14 px de base; títulos de sección
  de 16–18 px; total de 24–28 px.
- Espaciado: escala de 4, 8, 12, 16, 24 y 32 px.
- Radio: 8 px para campos y 12 px para tarjetas.
- Accesibilidad: contraste AA, foco visible, objetivos de 36 px mínimos y
  atajos existentes preservados.

## Estados y retroalimentación

- Guardado correcto: aviso no bloqueante con enlace a “Ver en historial”.
- Error de guardado o conexión: mensaje visible junto a la acción afectada,
  conservando los datos introducidos.
- Sin presupuestos: explicación breve y botón **Crear primer presupuesto**.
- Sin resultados de búsqueda: se muestra el término buscado y opción de
  limpiar filtros.
- Confirmación de acciones destructivas: menciona el identificador del
  presupuesto o el número de líneas afectadas.

## Orden recomendado de implementación futura

1. Reorganizar la composición visual en panel de historial, editor y resumen,
   sin cambiar casos de uso ni modelos.
2. Introducir cabecera de presupuesto y jerarquía de acciones.
3. Simplificar formulario de cliente y herramientas de líneas.
4. Aplicar tokens y estados accesibles de forma transversal.
5. Mejorar búsqueda, vacío y feedback; validar con usuarios antes de cambios
   estructurales adicionales.

## Criterios de aceptación de diseño

- El total y la acción Guardar son visibles sin desplazamiento en una ventana
  de 1280 × 800 px.
- Se puede crear, editar, guardar y exportar un presupuesto sin abrir el menú
  principal.
- El historial puede ocultarse sin perder el presupuesto que se está editando.
- Todos los estados y errores se entienden sin depender exclusivamente del
  color.
- La interfaz conserva funcionamiento en español e inglés y uso por teclado.
