# Modelo de datos

Proyecto Final Integrador - Programación II + Bases de Datos II

## Qué guardamos

Nuestra app es un quiz de cultura general argentina. Usamos MongoDB (en Atlas) y la base se llama `quiz_argentina`. Tiene 3 colecciones: `categorias`, `preguntas` y `puntuaciones`.

El diagrama ER está en `docs/diagrama_ER.svg`.

## Colecciones

### categorias

Son los temas del quiz: historia, geografía, deportes, música y comidas y costumbres.

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

Ejemplo:

```json
{
  "jugador": "Jugador de prueba",
  "puntos": 800,
  "aciertos": 8,
  "total_preguntas": 10
}
```

Más adelante, desde el código Python, vamos a agregar también la fecha de cada partida.

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

MongoDB crea solo un índice sobre `_id` en cada colección. Nosotros creamos dos más desde Atlas:

- En `preguntas`: índice sobre `categoria_id` (ascendente), para buscar rápido las preguntas de una categoría.
- En `puntuaciones`: índice sobre `puntos` (descendente), para sacar el ranking con los puntajes más altos primero.

## Datos de prueba

Cargamos 5 categorías, 10 preguntas (2 por categoría) y 1 puntuación de ejemplo. Todo se cargó a mano desde Atlas, con la opción Insert Document.

## Conexión

La contraseña y la cadena de conexión de Atlas no se suben a GitHub. Las compartimos entre nosotros por privado y en el código las vamos a leer desde un archivo `.env`.
