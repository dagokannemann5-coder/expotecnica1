# Interfaz web del Quiz Argentina

Este paquete añade cinco pantallas a tu proyecto existente: inicio, pregunta, resultado, ranking y administración. Usa Flask para conectar los formularios con las clases `RepositorioQuiz`, `Pregunta` y `Puntuacion` que ya están en la raíz del proyecto. Las categorías son de solo lectura; el panel administra preguntas con el CRUD existente.

## 1. Copiar los archivos al Codespace

Descargá y descomprimí `quiz_argentina_web.zip`. Copiá `app.py` y `requirements.txt` a la carpeta raíz `expotecnica1`, y copiá las carpetas `templates` y `static` también a esa raíz. No reemplaces tus módulos `modelos/` ni `repositorio/`.

La estructura debe quedar así:

```text
expotecnica1/
├── app.py
├── requirements.txt
├── modelos/
├── repositorio/
├── static/css/style.css
└── templates/
    ├── base.html
    ├── inicio.html
    ├── pregunta.html
    ├── resultado.html
    ├── ranking.html
    ├── ingresar_admin.html
    ├── administrar.html
    └── editar_pregunta.html
```

## 2. Configurar variables privadas

La aplicación necesita `MONGO_URI` y dos valores nuevos. No los publiques en el repositorio. En Codespaces podés configurarlos como secretos de Codespaces y autorizar el repositorio `expotecnica1`:

- `MONGO_URI`: la URI de Atlas que ya configuraste.
- `FLASK_SECRET_KEY`: una clave aleatoria larga que firme las sesiones. Podés generar una localmente con `python -c "import secrets; print(secrets.token_hex(32))"`.
- `ADMIN_PASSWORD`: contraseña que usarán para entrar en Administrar.

Después de agregar o modificar secretos, detené y reiniciá el Codespace para que estén disponibles en su entorno. Si trabajás con un `.env` local ignorado por Git, agregá allí estas tres variables. Nunca compartas ese archivo.

## 3. Instalar dependencias y ejecutar

Desde la raíz del proyecto:

```bash
python -m pip install -r requirements.txt
python app.py
```

Abrí el puerto 5000 desde la pestaña **Ports** del Codespace. Para administrar preguntas, elegí **Administrar** e ingresá `ADMIN_PASSWORD`.

## Comportamiento

- Una partida elige hasta 10 preguntas aleatorias de MongoDB; cada respuesta se verifica en el servidor.
- El resultado se guarda una sola vez en el ranking al responder la última pregunta. El puntaje es proporcional a los aciertos, con máximo 1000.
- La administración permite crear, listar, editar y eliminar preguntas; categoría debe ser una de las existentes, y cada pregunta exige cuatro opciones y una dificultad válida.
- Se incluyen protección de formularios CSRF y sesión de administrador. Para un despliegue público, usá HTTPS, activá `COOKIE_SECURE=1` y agregá medidas adicionales de seguridad y protección contra intentos reiterados de contraseña.

## Nota sobre estilos

La tipografía intenta cargar DM Sans, Manrope y DM Mono desde Google Fonts. Si no hay conexión externa, el navegador usará las fuentes de respaldo disponibles.
