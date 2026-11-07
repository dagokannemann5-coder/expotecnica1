import hmac
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for

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
)

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
        clave_configurada = os.getenv("ADMIN_PASSWORD", "")
        clave_ingresada = request.form.get("password", "")
        if clave_configurada and hmac.compare_digest(clave_ingresada, clave_configurada):
            session["es_admin"] = True
            return redirect(url_for("administrar"))
        flash("Contraseña incorrecta o ADMIN_PASSWORD no configurada.", "error")
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG") == "1")
