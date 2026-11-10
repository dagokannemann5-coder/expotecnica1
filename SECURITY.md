# SECURITY.md — Modelado de Amenazas

**Proyecto:** Quiz de Cultura General Argentina — Expotécnica 2026
**Grupo 7:** Romero – Kanemann
**Stack:** Python / Flask + MongoDB Atlas (`quiz_argentina`)
**Materia:** Seguridad Informática — E.P.E.T. N°1 UNESCO

---

## 1. Arquitectura analizada

| Componente | Descripción |
|---|---|
| `app.py` | Rutas Flask: `/`, `/iniciar`, `/pregunta`, `/responder`, `/siguiente`, `/resultado`, `/ranking` y el panel `/administrar/*` |
| `repositorio/repositorio_quiz.py` | Único punto de acceso a MongoDB (patrón repositorio) |
| `modelos/pregunta.py`, `modelos/puntuacion.py` | Clases POO con validación en los setters |
| `templates/` + `static/` | Vistas Jinja2 renderizadas en el servidor; no hay JavaScript propio que calcule puntajes |
| Colecciones | `categorias`, `preguntas`, `puntuaciones` |

**Datos sensibles:** respuestas correctas (`respuesta_correcta`), integridad del ranking, cadena de conexión `MONGO_URI`, clave de administrador y `FLASK_SECRET_KEY`.

**Actores de amenaza:** jugador malicioso (anónimo, sin login), usuario que intenta acceder al panel de administración, y cualquier persona que pueda ver el repositorio público.

---

## 2. Vulnerabilidades hipotéticas y vectores de ataque

### Riesgo 1 — Manipulación de puntajes con Postman / consola

- **Vector de ataque:** El atacante envía peticiones HTTP manipuladas (Postman, `curl`, scripts) a `/responder` y `/siguiente`, o automatiza partidas completas para obtener siempre 1000 puntos y ocupar el ranking.
- **Impacto:** Alteración de la integridad del ranking de mejores puntuaciones.
- **Mitigación (Hardening):** El puntaje **se calcula únicamente en el servidor** (`puntos = round(1000 * aciertos / total)` en `/siguiente`). Ninguna ruta acepta un puntaje enviado por el cliente. Todos los formularios exigen token CSRF.
- **Riesgo residual / a reforzar:** Un bot puede jugar muchas partidas y aprender las respuestas. Se propone limitar la frecuencia de partidas por cliente (rate limiting) y registrar el tiempo mínimo de una partida.

### Riesgo 2 — Alteración o repetición del estado de la partida en el cliente

- **Vector de ataque:** El estado de la partida (`pregunta_ids`, `indice`, `aciertos`, `partida_guardada`) se guarda en la **cookie de sesión de Flask**. La cookie está *firmada* (no se puede modificar sin `FLASK_SECRET_KEY`), pero **no está cifrada** y puede ser leída y **reutilizada** (replay): el jugador guarda la cookie antes de responder, ve el resultado y vuelve a restaurarla para elegir la opción correcta. Esto es posible porque `pregunta.html` muestra la respuesta correcta apenas se responde ("Incorrecto. La respuesta correcta era: ...").
- **Impacto:** Ventaja injusta en el juego y posibilidad de guardar varias veces una misma partida.
- **Mitigación (Hardening):** Las variables críticas ya están en la sesión de Flask y no en `localStorage` ni en JavaScript. Cookies con `HttpOnly` y `SameSite=Lax`; `Secure` configurable. Se propone guardar el estado de la partida del lado del servidor (colección `partidas` en MongoDB) y dejar en la cookie solo un identificador aleatorio.
- **Riesgo residual:** Mientras el estado siga en la cookie, el replay es posible.

### Riesgo 3 — Entradas inválidas y exposición de errores internos

- **Vector de ataque:** Enviar campos vacíos, valores no numéricos, `opcion` fuera de rango, IDs de pregunta mal formados (`/administrar/editar/<id>`), cuerpos muy grandes, o provocar una falla de conexión con Atlas.
- **Impacto:** Errores 500 y posible filtración de detalles internos (host de la base, mensajes de `PyMongoError`) que ayudan a planificar otros ataques.
- **Mitigación (Hardening):**
  - Conversión estricta con `int()` dentro de `try/except` y control de rango (`0 <= elegida < len(opciones)`).
  - La categoría se valida contra una lista blanca de categorías existentes.
  - `ObjectId` se construye dentro de `try/except (InvalidId, PyMongoError)`.
  - Las clases `Pregunta` y `Puntuacion` validan tipo y rango en los setters.
  - `debug` desactivado por defecto (solo se activa con `FLASK_DEBUG=1`).
  - Timeout de conexión de 5 s (`serverSelectionTimeoutMS`).
- **A reforzar:** Manejadores globales de error (400/404/500 y `Exception`) con plantillas propias, no incluir `{e}` del driver en los mensajes mostrados, y definir `MAX_CONTENT_LENGTH`.

### Riesgo 4 — Credenciales expuestas y acceso no autorizado al panel de administración

- **Vector de ataque (a):** El archivo `.env` (con `MONGO_URI`) está subido al repositorio de GitHub (`dagokannemann5-coder/expotecnica1`). Aunque `.gitignore` ya lista `.env`, Git sigue versionando los archivos que se agregaron *antes* de ignorarlos, y el historial conserva las versiones anteriores de la contraseña.
- **Vector de ataque (b):** El panel `/administrar` se protege con una clave comparada contra `ADMIN_PASSWORD` en texto plano y sin límite de intentos (fuerza bruta).
- **Impacto:** Lectura, modificación o borrado de toda la base de datos; borrado del ranking y de las preguntas.
- **Mitigación (Hardening):**
  - Quitar `.env` del repositorio (`git rm --cached .env`), agregarlo a `.gitignore`, rotar la contraseña de Atlas y la `FLASK_SECRET_KEY`, y publicar un `.env.example` con valores ficticios.
  - Guardar la clave de administrador como **hash** (`werkzeug.security.generate_password_hash` / `check_password_hash`) en lugar de texto plano.
  - Limitar intentos de login y restringir el acceso por IP en Atlas.
- **Ya implementado:** comparación en tiempo constante con `hmac.compare_digest` y exigencia de sesión de administrador (`exigir_admin`) en todas las rutas `/administrar/*`.

### Riesgo 5 — Cross-Site Scripting (XSS) por el nombre del jugador

- **Vector de ataque:** El campo `jugador` acepta cualquier texto (solo se recorta a 60 caracteres). Un atacante puede ingresar `<script>...</script>`, que queda guardado en `puntuaciones` y se muestra en `/ranking`, `/resultado` y `/pregunta`.
- **Impacto:** Si el texto se imprimiera sin escapar, se ejecutaría código en el navegador de quienes ven el ranking (robo de datos, redirecciones, defacement).
- **Mitigación (Hardening) ya presente:** Las plantillas usan `{{ variable }}` y Jinja2 escapa automáticamente el HTML; en la revisión de `templates/` **no se encontró ningún uso de `|safe` ni de `Markup`**, por lo que el `<script>` se muestra como texto y no se ejecuta.
- **A reforzar (defensa en profundidad):** Validar el nombre también al guardarlo (letras, números y espacios, entre 3 y 20 caracteres) en `Puntuacion` y en `/iniciar`, para no almacenar HTML en la base de datos y proteger a cualquier otro sistema que lea esa colección.

---

## 3. Riesgos analizados y descartados

| Riesgo | Por qué no aplica |
|---|---|
| Inyección de operadores NoSQL (`$ne`, `$gt`) | Todos los datos llegan por formularios HTML (`request.form` siempre devuelve strings, nunca objetos). La categoría se valida con lista blanca y los IDs se convierten a `ObjectId`. Si en el futuro se aceptara JSON, habría que castear cada campo a `str`. |
| Manipulación de variables en `localStorage` | La aplicación no usa JavaScript propio ni `localStorage`: la lógica del juego está en el servidor. |

---

## 4. Auditoría técnica (Parte 4)

*Se completa en la entrega final con la tabla: Activo Afectado · Vulnerabilidad Detectada · Nivel de Riesgo · Medida de Hardening Aplicada.*

## 5. Políticas de seguridad para la exposición (Parte 4)

*Se completa en la entrega final (3 reglas para producción).*
