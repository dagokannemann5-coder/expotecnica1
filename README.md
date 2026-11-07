# Quiz de Cultura General Argentina

Proyecto Final Integrador de Programación II, Bases de Datos II, Seguridad Informática y Redes II. ExpoTécnica 2026.

## Integrantes

- Kannemann Dago
- Romero Matías

## Descripción

Aplicación web de preguntas y respuestas sobre cultura general argentina. La **meta del banco** es tener 60 preguntas: 12 por cada una de las 5 categorías. Cada partida muestra **10 preguntas** elegidas al azar; esa cantidad no es el total del banco. El puntaje se calcula en proporción a los aciertos, hasta un máximo de 1000 puntos.

La cantidad que hay actualmente en MongoDB Atlas debe comprobarse directamente en la base antes de afirmar que se alcanzó la meta. El cargador está configurado con metas de 60 preguntas y 12 por categoría, pero sus preguntas candidatas no prueban cuántas hay en Atlas.

## Funciones implementadas

- Partidas de 10 preguntas, con opción de elegir una categoría.
- Validación de las respuestas en el servidor. Después de responder, se muestra “¡Correcto!” o, si fue incorrecta, cuál era la respuesta correcta; las opciones se resaltan y se puede continuar con “Siguiente”.
- Cálculo y guardado de puntaje al finalizar la partida, y consulta del ranking.
- Interfaz adaptable a computadoras y celulares, con tema claro/oscuro cuya preferencia se conserva entre pantallas.
- Íconos SVG lineales para las categorías y medallas visuales para los tres primeros puestos del ranking.
- Panel de administración protegido por contraseña, con alta, edición y eliminación de preguntas.
- Botón **“Limpiar ranking”** disponible en el panel de administración. Pide confirmación, requiere una solicitud POST protegida con CSRF y elimina únicamente los documentos de puntajes.

## Tecnologías

- Backend: Python, Flask y programación orientada a objetos.
- Base de datos: MongoDB Atlas, con PyMongo.
- Interfaz: HTML, CSS y JavaScript.

## Documentación

- [Modelo de datos, colecciones e índices](docs/MODELO_DATOS.md)
- [Diagrama ER](diagrama_ER.pdf), ubicado en la raíz del proyecto.

## Instalar y ejecutar

Seguí estos pasos en la computadora donde quieras correr la aplicación. Necesitás Python y acceso a la base MongoDB Atlas del proyecto.

1. **Descargá o cloná el proyecto** y abrí una terminal en la carpeta raíz, donde están `app.py` y `requirements.txt`. En VS Code podés abrir esa carpeta y elegir **Terminal > Nueva terminal**.

   En PowerShell, si ya estás en otra ubicación:

   ```powershell
   cd C:\ruta\de\expotecnica
   ```

2. **Configurá MongoDB Atlas.** La cuenta de Atlas debe tener un usuario de base de datos habilitado y acceso de red desde tu ubicación. Pedile la URI al equipo por un canal privado. No incluyas credenciales en mensajes públicos ni subas el archivo `.env` a GitHub.

3. **Creá `.env` en la raíz del proyecto** (al mismo nivel que `app.py`) con tus propios valores:

   ```dotenv
   MONGO_URI=URI_privada_de_MongoDB_Atlas
   FLASK_SECRET_KEY=clave_larga_aleatoria_y_privada
   ADMIN_PASSWORD=clave_privada_para_el_panel
   ```

   Para generar una clave aleatoria de Flask, ejecutá:

   ```powershell
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

   Guardá el resultado localmente como `FLASK_SECRET_KEY`. No compartas ni publiques los valores de `.env`.

4. **Creá y activá un entorno virtual** (recomendado). En Windows PowerShell:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   En macOS o Linux:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   Si Windows no reconoce `python`, instalá Python marcando la opción para agregarlo al PATH y abrí una terminal nueva. Si ya existe el entorno `.venv`, podés ejecutar la aplicación con `.\.venv\Scripts\python.exe` sin activar el entorno.

5. **Instalá las dependencias** desde la raíz del proyecto:

   ```powershell
   python -m pip install -r requirements.txt
   ```

6. **Iniciá Flask:**

   ```powershell
   python app.py
   ```

   Si usás el entorno virtual sin activarlo:

   ```powershell
   .\.venv\Scripts\python.exe app.py
   ```

7. **Abrí la aplicación** en `http://127.0.0.1:5000`. Para entrar al panel de administración, usá la contraseña configurada en `ADMIN_PASSWORD`.

La terminal debe quedar abierta mientras se usa la aplicación. Para detenerla, presioná `Ctrl+C`. Desde VS Code también se puede reenviar el puerto `5000`; para que otras personas accedan por ese enlace, configurá su visibilidad de acuerdo con las opciones de VS Code.

### Carga opcional de preguntas

`cargar_preguntas.py` es un paso independiente de iniciar Flask. Está configurado con las metas de 60 preguntas en total y 12 por categoría; primero consulta los documentos existentes, omite textos duplicados y no elimina preguntas. Si la base ya tiene 60, informa ese total y termina. Si se ejecuta con menos de 60, puede insertar preguntas candidatas en las categorías que aún no llegaron a la meta. Por eso, ejecutalo solo si corresponde completar el banco y tenés acceso autorizado a Atlas. La cantidad actual de documentos en la base sigue pendiente de verificación.

## Estado del proyecto

- [x] Propuesta y setup de GitHub / Trello
- [x] Modelo de datos y colecciones de la aplicación
- [x] Clases POO y CRUD de preguntas
- [x] Interfaz web, partidas, respuesta correcta posterior a una respuesta incorrecta y ranking
- [x] Administración con confirmación para limpiar solo los puntajes del ranking
- [x] Documentación de instalación, modelo de datos e índices
- [ ] Verificar en Atlas el total actual de preguntas y su distribución por categoría
- [ ] Verificar en Atlas que estén creados los dos índices documentados
- [ ] Pruebas automatizadas incorporadas al proyecto
