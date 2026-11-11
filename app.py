import hmac
import logging
import os
import re
import secrets
import time
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash

from modelos.pregunta import Pregunta
from modelos.puntuacion import Puntuacion
from repositorio.repositorio_quiz import RepositorioQuiz

load_dotenv(Path(__file__).resolve().parent / ".env")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("Configura FLASK_SECRET_KEY como variable de entorno antes de iniciar la app.")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("COOKIE_SECURE", "0") == "1",
    MAX_CONTENT_LENGTH=16 * 1024,  # Hardening: ninguna petición de este sitio necesita más de 16 KB
)

# Los detalles técnicos de los errores se guardan en un archivo, nunca se muestran al usuario
logging.basicConfig(
    filename="errores.log",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(message)s",
)

# Hardening: nombre del jugador (letras, números, espacio, punto, guion y guion bajo; 3 a 20 caracteres)
NOMBRE_VALIDO = re.compile(r"[A-Za-z0-9ÁÉÍÓÚÜáéíóúüÑñ ._-]{3,20}")

# Hardening: límite de intentos fallidos de login de administrador (en memoria)
MAX_INTENTOS_ADMIN = 5
VENTANA_INTENTOS_SEG = 300
intentos_admin = {}

repo = RepositorioQuiz()


def exigir_csrf():
    esperado = session.get("csrf_token", "")
    recibido = request.form.get("_csrf", "")
    if not esperado or not hmac.compare_digest(esperado, recibido):
        abort(400, description="Formulario vencido o inválido. Recargá la página e intentá de nuevo.")


@app.context_processor
def incluir_csrf():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return {"csrf_token": session["csrf_token"]}


def obtener_categorias():
    return repo.obtener_categorias()


def exigir_admin():
    if not session.get("es_admin"):
        return redirect(url_for("ingresar_admin"))
    return None


def login_bloqueado(ip):
    ahora = time.time()
    recientes = [t for t in intentos_admin.get(ip, []) if ahora - t < VENTANA_INTENTOS_SEG]
    intentos_admin[ip] = recientes
    return len(recientes) >= MAX_INTENTOS_ADMIN


def registrar_intento_fallido(ip):
    intentos_admin.setdefault(ip, []).append(time.time())


def pregunta_desde_formulario():
    categorias_validas = {str(c["_id"]) for c in obtener_categorias()}
    categoria_id = request.form.get("categoria_id", "").strip()
    if categoria_id not in categorias_validas:
        raise ValueError("Elegí una de las categorías existentes.")

    try:
        respuesta = int(request.form.get("respuesta_correcta", ""))
    except ValueError as exc:
        raise ValueError("Seleccioná cuál de las cuatro opciones es la correcta.") from exc

    return Pregunta(
        texto=request.form.get("texto", ""),
        opciones=[request.form.get(f"opcion_{i}", "") for i in range(4)],
        respuesta_correcta=respuesta,
        categoria_id=categoria_id,
        dificultad=request.form.get("dificultad", "facil"),
    )


@app.get("/")
def inicio():
    return render_template("inicio.html", categorias=obtener_categorias())


@app.post("/iniciar")
def iniciar_partida():
    exigir_csrf()
    nombre = request.form.get("jugador", "").strip()
    if not nombre:
        flash("Escribí tu nombre para comenzar.", "error")
        return redirect(url_for("inicio"))
    if not NOMBRE_VALIDO.fullmatch(nombre):
        flash("El nombre debe tener entre 3 y 20 caracteres: letras, números, espacios, punto, guion o guion bajo.", "error")
        return redirect(url_for("inicio"))

    categoria_id = request.form.get("categoria_id", "").strip() or None
    categorias_validas = {str(c["_id"]) for c in obtener_categorias()}
    if categoria_id is not None and categoria_id not in categorias_validas:
        flash("La categoría elegida no es válida.", "error")
        return redirect(url_for("inicio"))

    preguntas = repo.obtener_preguntas_para_partida(10, categoria_id=categoria_id)
    if not preguntas:
        flash("No hay preguntas disponibles para esa selección. Elegí otra categoría o avisa al administrador.", "error")
        return redirect(url_for("inicio"))

    session["jugador"] = nombre[:60]
    session["pregunta_ids"] = [p.id for p in preguntas]
    session["indice"] = 0
    session["aciertos"] = 0
    session["puntos"] = 0
    session["partida_guardada"] = False
    session.pop("respuesta_elegida", None)
    return redirect(url_for("pregunta_actual"))


@app.get("/pregunta")
def pregunta_actual():
    ids = session.get("pregunta_ids")
    indice = session.get("indice")
    if not ids or indice is None:
        flash("Iniciá una partida para responder preguntas.", "error")
        return redirect(url_for("inicio"))
    if indice >= len(ids):
        return redirect(url_for("resultado"))

    pregunta = repo.obtener_pregunta(ids[indice])
    if pregunta is None:
        flash("Una pregunta de la partida ya no está disponible. Iniciá otra partida.", "error")
        session.pop("pregunta_ids", None)
        session.pop("respuesta_elegida", None)
        return redirect(url_for("inicio"))

    categorias = {str(c["_id"]): c["nombre"] for c in obtener_categorias()}
    return render_template(
        "pregunta.html",
        pregunta=pregunta,
        categoria=categorias.get(pregunta.categoria_id, pregunta.categoria_id),
        numero=indice + 1,
        total=len(ids),
        respuesta_elegida=session.get("respuesta_elegida"),
    )


@app.post("/responder")
def responder():
    exigir_csrf()
    ids = session.get("pregunta_ids")
    indice = session.get("indice")
    if not ids or indice is None or indice >= len(ids):
        return redirect(url_for("inicio"))
    if "respuesta_elegida" in session:
        return redirect(url_for("pregunta_actual"))

    try:
        elegida = int(request.form.get("opcion", ""))
    except ValueError:
        flash("Seleccioná una opción antes de continuar.", "error")
        return redirect(url_for("pregunta_actual"))

    pregunta = repo.obtener_pregunta(ids[indice])
    if pregunta is None or not 0 <= elegida < len(pregunta.opciones):
        flash("La opción enviada no es válida.", "error")
        return redirect(url_for("pregunta_actual"))

    if pregunta.es_correcta(elegida):
        session["aciertos"] = session.get("aciertos", 0) + 1
    session["respuesta_elegida"] = elegida
    return redirect(url_for("pregunta_actual"))


@app.post("/siguiente")
def siguiente_pregunta():
    exigir_csrf()
    ids = session.get("pregunta_ids")
    indice = session.get("indice")
    if not ids or indice is None or indice >= len(ids):
        return redirect(url_for("pregunta_actual"))
    if "respuesta_elegida" not in session:
        return redirect(url_for("pregunta_actual"))

    session.pop("respuesta_elegida")
    session["indice"] = indice + 1
    if session["indice"] >= len(ids):
        aciertos = session.get("aciertos", 0)
        total = len(ids)
        puntos = round(1000 * aciertos / total) if total else 0
        session["puntos"] = puntos
        if not session.get("partida_guardada"):
            repo.guardar_puntuacion(Puntuacion(session.get("jugador", "Jugador"), puntos, aciertos, total))
            session["partida_guardada"] = True
        return redirect(url_for("resultado"))
    return redirect(url_for("pregunta_actual"))


@app.get("/resultado")
def resultado():
    if not session.get("partida_guardada"):
        flash("No hay un resultado de partida para mostrar.", "error")
        return redirect(url_for("inicio"))
    return render_template(
        "resultado.html",
        jugador=session.get("jugador", "Jugador"),
        puntos=session.get("puntos", 0),
        aciertos=session.get("aciertos", 0),
        total=len(session.get("pregunta_ids", [])),
    )


@app.get("/ranking")
def ranking():
    return render_template("ranking.html", puntuaciones=repo.obtener_ranking(20))


@app.post("/administrar/limpiar-ranking")
def limpiar_ranking():
    redireccion = exigir_admin()
    if redireccion:
        return redireccion
    exigir_csrf()
    try:
        repo.limpiar_ranking()
    except RuntimeError as exc:
        flash(str(exc), "error")
        return redirect(url_for("administrar"))
    flash("Se limpiaron todos los puntajes del ranking.", "success")
    return redirect(url_for("ranking"))


@app.route("/administrar/ingresar", methods=["GET", "POST"])
def ingresar_admin():
    if session.get("es_admin"):
        return redirect(url_for("administrar"))
    if request.method == "POST":
        exigir_csrf()
        ip = request.remote_addr or "desconocida"
        if login_bloqueado(ip):
            flash("Demasiados intentos fallidos. Esperá unos minutos e intentá de nuevo.", "error")
            return render_template("ingresar_admin.html"), 429
        # Hardening: la clave NO se guarda en texto plano, solo su hash (werkzeug.security)
        hash_configurado = os.getenv("ADMIN_PASSWORD_HASH", "")
        clave_ingresada = request.form.get("password", "")
        if hash_configurado and check_password_hash(hash_configurado, clave_ingresada):
            intentos_admin.pop(ip, None)
            session["es_admin"] = True
            return redirect(url_for("administrar"))
        registrar_intento_fallido(ip)
        flash("Contraseña incorrecta o acceso de administrador no configurado.", "error")
    return render_template("ingresar_admin.html")


@app.post("/administrar/salir")
def salir_admin():
    exigir_csrf()
    session.pop("es_admin", None)
    flash("Cerraste la sesión de administración.", "info")
    return redirect(url_for("inicio"))


@app.get("/administrar")
def administrar():
    redireccion = exigir_admin()
    if redireccion:
        return redireccion
    preguntas = repo.listar_preguntas()
    categorias = obtener_categorias()
    nombres = {str(c["_id"]): c["nombre"] for c in categorias}
    return render_template("administrar.html", preguntas=preguntas, categorias=categorias, nombres=nombres)


@app.route("/administrar/nueva", methods=["GET", "POST"])
def nueva_pregunta():
    redireccion = exigir_admin()
    if redireccion:
        return redireccion
    categorias = obtener_categorias()
    if request.method == "POST":
        exigir_csrf()
        try:
            repo.crear_pregunta(pregunta_desde_formulario())
            flash("Pregunta creada.", "success")
            return redirect(url_for("administrar"))
        except (ValueError, RuntimeError) as exc:
            flash(str(exc), "error")
    return render_template("editar_pregunta.html", pregunta=None, categorias=categorias, titulo="Nueva pregunta")


@app.route("/administrar/editar/<id_pregunta>", methods=["GET", "POST"])
def editar_pregunta(id_pregunta):
    redireccion = exigir_admin()
    if redireccion:
        return redireccion
    pregunta = repo.obtener_pregunta(id_pregunta)
    if pregunta is None:
        abort(404)
    categorias = obtener_categorias()
    if request.method == "POST":
        exigir_csrf()
        try:
            repo.actualizar_pregunta(id_pregunta, pregunta_desde_formulario())
            flash("Pregunta actualizada.", "success")
            return redirect(url_for("administrar"))
        except (ValueError, RuntimeError) as exc:
            flash(str(exc), "error")
    return render_template("editar_pregunta.html", pregunta=pregunta, categorias=categorias, titulo="Editar pregunta")


@app.post("/administrar/eliminar/<id_pregunta>")
def eliminar_pregunta(id_pregunta):
    redireccion = exigir_admin()
    if redireccion:
        return redireccion
    exigir_csrf()
    try:
        if repo.eliminar_pregunta(id_pregunta):
            flash("Pregunta eliminada.", "success")
        else:
            flash("La pregunta ya no existe.", "info")
    except RuntimeError as exc:
        flash(str(exc), "error")
    return redirect(url_for("administrar"))


# ---------- Manejo seguro de excepciones ----------
def pagina_error(codigo, mensaje):
    return render_template("error.html", codigo=codigo, mensaje=mensaje), codigo


@app.errorhandler(HTTPException)
def error_http(e):
    mensajes = {
        404: "La página que buscás no existe.",
        405: "Esa acción no está permitida.",
        413: "La petición enviada es demasiado grande.",
    }
    if e.code == 400:
        mensaje = e.description  # mensajes propios de la app (ej. formulario vencido)
    else:
        mensaje = mensajes.get(e.code, "No pudimos procesar la solicitud.")
    return pagina_error(e.code, mensaje)


@app.errorhandler(Exception)
def error_inesperado(e):
    # El detalle (stack trace, datos de MongoDB) va solo al log del servidor
    app.logger.exception("Error inesperado en %s", request.path)
    return pagina_error(500, "Ocurrió un error interno. Intentá de nuevo más tarde.")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG") == "1")
