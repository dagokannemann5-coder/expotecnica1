import os
from pathlib import Path

from bson import ObjectId
from bson.errors import InvalidId
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from modelos.pregunta import Pregunta
from modelos.puntuacion import Puntuacion

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


class RepositorioQuiz:
    """Se encarga de leer y guardar datos en MongoDB (Atlas)."""

    def __init__(self):
        uri = os.getenv("MONGO_URI")
        if not uri:
            raise RuntimeError("Falta MONGO_URI en el archivo .env")
        # Si no puede conectar en 5 segundos, avisa en vez de quedarse colgado
        self.__cliente = MongoClient(uri, serverSelectionTimeoutMS=5000)
        self.__db = self.__cliente["quiz_argentina"]

    # ---------- categorias ----------
    def obtener_categorias(self):
        try:
            return list(self.__db.categorias.find())
        except PyMongoError as e:
            raise RuntimeError(f"No se pudieron leer las categorías: {e}")

    # ---------- preguntas (CRUD) ----------
    def crear_pregunta(self, pregunta):
        """Guarda una pregunta nueva y devuelve su id."""
        try:
            resultado = self.__db.preguntas.insert_one(pregunta.a_diccionario())
            return str(resultado.inserted_id)
        except PyMongoError as e:
            raise RuntimeError(f"No se pudo guardar la pregunta: {e}")

    def listar_preguntas(self, categoria_id=None):
        """Devuelve todas las preguntas (o solo las de una categoría)."""
        filtro = {"categoria_id": categoria_id} if categoria_id else {}
        try:
            return [Pregunta.desde_diccionario(d) for d in self.__db.preguntas.find(filtro)]
        except PyMongoError as e:
            raise RuntimeError(f"No se pudieron leer las preguntas: {e}")

    def obtener_pregunta(self, id_pregunta):
        try:
            doc = self.__db.preguntas.find_one({"_id": ObjectId(id_pregunta)})
        except (InvalidId, PyMongoError):
            return None
        return Pregunta.desde_diccionario(doc) if doc else None

    def actualizar_pregunta(self, id_pregunta, pregunta):
        """Devuelve True si se modificó una pregunta existente."""
        try:
            resultado = self.__db.preguntas.update_one(
                {"_id": ObjectId(id_pregunta)}, {"$set": pregunta.a_diccionario()}
            )
            return resultado.matched_count == 1
        except (InvalidId, PyMongoError) as e:
            raise RuntimeError(f"No se pudo actualizar la pregunta: {e}")

    def eliminar_pregunta(self, id_pregunta):
        """Devuelve True si se borró la pregunta."""
        try:
            resultado = self.__db.preguntas.delete_one({"_id": ObjectId(id_pregunta)})
            return resultado.deleted_count == 1
        except (InvalidId, PyMongoError) as e:
            raise RuntimeError(f"No se pudo eliminar la pregunta: {e}")

    def obtener_preguntas_para_partida(self, cantidad=10, categoria_id=None):
        """Elige al azar preguntas sin repetir enunciados, opcionalmente por categoría."""
        pipeline = []
        if categoria_id:
            pipeline.append({"$match": {"categoria_id": categoria_id}})

        # Agrupa preguntas repetidas por texto normalizado y conserva un documento
        # por enunciado antes de seleccionar la muestra aleatoria.
        pipeline.extend([
            {
                "$group": {
                    "_id": {"$toLower": {"$trim": {"input": "$texto"}}},
                    "documento": {"$first": "$$ROOT"},
                }
            },
            {"$replaceRoot": {"newRoot": "$documento"}},
            {"$sample": {"size": cantidad}},
        ])

        try:
            docs = self.__db.preguntas.aggregate(pipeline)
            return [Pregunta.desde_diccionario(d) for d in docs]
        except PyMongoError as e:
            raise RuntimeError(f"No se pudieron obtener preguntas: {e}")

    # ---------- puntuaciones ----------
    def guardar_puntuacion(self, puntuacion):
        try:
            self.__db.puntuaciones.insert_one(puntuacion.a_diccionario())
        except PyMongoError as e:
            raise RuntimeError(f"No se pudo guardar la puntuación: {e}")

    def obtener_ranking(self, cantidad=10):
        """Devuelve las mejores puntuaciones (de mayor a menor)."""
        try:
            docs = self.__db.puntuaciones.find().sort("puntos", -1).limit(cantidad)
            return [Puntuacion.desde_diccionario(d) for d in docs]
        except PyMongoError as e:
            raise RuntimeError(f"No se pudo leer el ranking: {e}")

    def limpiar_ranking(self):
        """Elimina todas las puntuaciones sin afectar otras colecciones."""
        try:
            return self.__db.puntuaciones.delete_many({})
        except PyMongoError as e:
            raise RuntimeError(f"No se pudo limpiar el ranking: {e}")
