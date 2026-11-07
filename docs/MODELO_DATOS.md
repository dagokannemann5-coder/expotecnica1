# Modelo de datos

Proyecto Final Integrador - Programación II + Bases de Datos II

## Qué guardamos

Nuestra app es un quiz de cultura general argentina. Usamos MongoDB (en Atlas) y la base se llama `quiz_argentina`. Tiene 3 colecciones: `categorias`, `preguntas` y `puntuaciones`.

El [diagrama ER](../diagrama_ER.pdf) está en la raíz del proyecto.

La meta del banco es **60 preguntas en total**, distribuidas en **12 por cada una de las 5 categorías**. Cada partida selecciona **10 preguntas**; este es el número que ve el jugador por partida, no el total que debe guardarse en la base. El total y la distribución que hay actualmente en Atlas quedan **pendientes de verificar directamente en la base**; la configuración del cargador indica la meta, no el estado actual de los datos.

## Colecciones

### categorias

Son los temas del quiz: historia, geografía, deportes, música y comidas y costumbres.

`categorias` es una colección aparte porque cada categoría tiene datos propios (`nombre` y `descripcion`) y puede estar asociada a muchas preguntas. Cada pregunta guarda solo el identificador de su categoría; así no repetimos el nombre y la descripción en cada documento. Además, la aplicación puede mostrar las categorías y filtrar preguntas por tema.

Campos:
- `_id`: un nombre corto, por ejemplo "historia"
- `nombre`: cómo se muestra en pantalla
- `descripcion`: una frase sobre el tema

Ejemplo:

```json
{
  "_id": "historia",
  "nombre": "Historia",
  "descripcion": "Hechos y personajes de la historia argentina"
}
```

### preguntas

Acá están todas las preguntas del juego.

Campos:
- `_id`: lo genera MongoDB solo
- `texto`: la pregunta
- `opciones`: lista con las 4 opciones
- `respuesta_correcta`: el número de la opción correcta (de 0 a 3, empezando a contar desde 0)
- `categoria_id`: la categoría a la que pertenece
- `dificultad`: facil, media o dificil

Ejemplo:

```json
{
  "texto": "¿Cuál es la montaña más alta de América?",
  "opciones": ["Aconcagua", "Fitz Roy", "Tronador", "Lanín"],
  "respuesta_correcta": 0,
  "categoria_id": "geografia",
  "dificultad": "facil"
}
```

### puntuaciones

Cada vez que alguien termina una partida se guarda un documento acá. Con esto armamos el ranking.

Campos:
- `_id`: lo genera MongoDB solo
- `jugador`: el nombre de quien jugó
- `puntos`: el puntaje de la partida
- `aciertos`: cuántas respuestas acertó
- `total_preguntas`: cuántas preguntas tuvo la partida
- `fecha`: fecha y hora en que se guardó el resultado (tipo BSON Date)

Al terminar la partida, la aplicación calcula `puntos` con `round(1000 * aciertos / total_preguntas)`. La regla está en la aplicación; no hay una clase `Quiz` con un cálculo paralelo.

Ejemplo:

```json
{
  "jugador": "Jugador de prueba",
  "puntos": 800,
  "aciertos": 8,
  "total_preguntas": 10,
  "fecha": {"$date": "2025-11-01T12:00:00Z"}
}
```

La fecha ya se guarda: `Puntuacion` establece la fecha y hora actuales al crear el resultado y `a_diccionario()` incluye ese valor en el documento insertado en MongoDB. PyMongo lo serializa como BSON Date. El ejemplo usa Extended JSON para representarlo en este documento.

## Relaciones

- Una categoría tiene muchas preguntas (relación 1 a N). Cada pregunta guarda en `categoria_id` el `_id` de su categoría, así no repetimos el nombre en cada pregunta.
- Las opciones van dentro de la misma pregunta porque siempre se usan juntas, y no hacía falta otra colección.
- `puntuaciones` no se relaciona con las otras colecciones. Guarda el nombre del jugador como texto porque la app no tiene usuarios ni login.

## Validaciones

Estas reglas las controlamos en las clases de Python:

- el texto de la pregunta no puede estar vacío
- tiene que haber exactamente 4 opciones
- `respuesta_correcta` es un número de 0 a 3
- la dificultad solo puede ser facil, media o dificil
- el nombre del jugador no puede estar vacío
- los puntos van de 0 a 1000

## Índices

MongoDB crea automáticamente un índice sobre `_id` en cada colección. Para crear los dos índices adicionales previstos para la aplicación, abrí MongoDB Shell (`mongosh`) con acceso a la base y ejecutá:

```javascript
use quiz_argentina
db.preguntas.createIndex({ categoria_id: 1 })
db.puntuaciones.createIndex({ puntos: -1 })
```

El primero acelera la búsqueda de preguntas por categoría; el segundo ayuda a ordenar las puntuaciones de mayor a menor, como hace la consulta del ranking. Para comprobar qué índices existen en la base, ejecutá:

```javascript
db.preguntas.getIndexes()
db.puntuaciones.getIndexes()
```

MongoDB asigna normalmente los nombres `categoria_id_1` y `puntos_-1`; cada colección conserva también su índice automático `_id_`. **La existencia actual de los índices en Atlas está pendiente de verificar** con `getIndexes()`.

## Datos de prueba

El objetivo es contar con 5 categorías y 60 preguntas (12 por categoría); la aplicación selecciona 10 preguntas por partida. No afirmamos aquí el total actual de documentos ni la cantidad de puntuaciones de ejemplo porque esos datos deben comprobarse directamente en Atlas.

El cargador `cargar_preguntas.py` tiene configuradas una meta de 60 preguntas y una meta de 12 por categoría. Antes de insertar, consulta los documentos existentes: si encuentra 60 o más, informa el total y no agrega ni elimina preguntas. Si hay menos, recorre preguntas candidatas para completar las metas, omite textos duplicados y no borra documentos. La lista del cargador no representa ni reemplaza el contenido que ya está en Atlas.

## Conexión

La contraseña y la cadena de conexión de Atlas no se suben a GitHub. Las compartimos entre nosotros por privado y en el código las vamos a leer desde un archivo `.env`.
