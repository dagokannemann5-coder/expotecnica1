# Cambios de la aplicación (sin cargar_preguntas.py)

Este paquete contiene únicamente archivos de la aplicación. No incluye ni reemplaza `cargar_preguntas.py`.

Incluye:
- `app.py`: selección de categoría al iniciar.
- `repositorio/repositorio_quiz.py`: preguntas aleatorias sin repetir enunciados durante una partida, con filtro por categoría.
- `templates/inicio.html`: selector de preguntas aleatorias o de una categoría.
- `templates/base.html`: crédito inferior actualizado.
- `static/css/style.css`: estilos del selector y amarillo de marca.
- `static/img/`: logo EPET y foto de la escuela para conservar los recursos usados en la interfaz.

## Cómo aplicarlo

1. Sube `quiz_argentina_app_sin_cargador.zip` a la raíz del repositorio `expotecnica1` en GitHub y confirma con **Commit changes**.
2. En el Codespace ejecuta:

```bash
cd /workspaces/expotecnica1
git pull origin main
unzip -o quiz_argentina_app_sin_cargador.zip -d .
```

3. Reinicia Flask con `Ctrl+C` y luego:

```bash
python app.py
```

4. Recarga la web con `Ctrl+Shift+R`.

No hace falta volver a ejecutar `cargar_preguntas.py` para aplicar estos cambios de la aplicación. La selección por categoría consultará las preguntas que ya estén en MongoDB; el cargador de preguntas es un paso aparte.
