class Pregunta:
    """Representa una pregunta del quiz de cultura general argentina."""

    DIFICULTADES = ("facil", "media", "dificil")

    def __init__(self, texto, opciones, respuesta_correcta, categoria_id, dificultad="facil", id=None):
        # Se usan los setters para que las validaciones se ejecuten al crear el objeto
        self.texto = texto
        self.opciones = opciones
        self.respuesta_correcta = respuesta_correcta
        self.categoria_id = categoria_id
        self.dificultad = dificultad
        self.__id = id

    @property
    def id(self):
        return self.__id

    # ---------- texto ----------
    @property
    def texto(self):
        return self.__texto

    @texto.setter
    def texto(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El texto de la pregunta no puede estar vacío.")
        self.__texto = valor.strip()

    # ---------- opciones ----------
    @property
    def opciones(self):
        return list(self.__opciones)  # copia, para proteger el atributo privado

    @opciones.setter
    def opciones(self, valor):
        if not isinstance(valor, (list, tuple)) or len(valor) != 4:
            raise ValueError("La pregunta debe tener exactamente 4 opciones.")
        if any(not isinstance(o, str) or not o.strip() for o in valor):
            raise ValueError("Las opciones no pueden estar vacías.")
        self.__opciones = [o.strip() for o in valor]

    # ---------- respuesta_correcta ----------
    @property
    def respuesta_correcta(self):
        return self.__respuesta_correcta

    @respuesta_correcta.setter
    def respuesta_correcta(self, valor):
        if not isinstance(valor, int) or not 0 <= valor <= 3:
            raise ValueError("La respuesta correcta debe ser un número entre 0 y 3.")
        self.__respuesta_correcta = valor

    # ---------- categoria_id ----------
    @property
    def categoria_id(self):
        return self.__categoria_id

    @categoria_id.setter
    def categoria_id(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("La categoría es obligatoria.")
        self.__categoria_id = valor.strip()

    # ---------- dificultad ----------
    @property
    def dificultad(self):
        return self.__dificultad

    @dificultad.setter
    def dificultad(self, valor):
        if valor not in self.DIFICULTADES:
            raise ValueError("La dificultad debe ser: facil, media o dificil.")
        self.__dificultad = valor

    # ---------- métodos ----------
    def es_correcta(self, indice_elegido):
        """Devuelve True si la opción elegida es la correcta."""
        return indice_elegido == self.__respuesta_correcta

    def a_diccionario(self):
        """Convierte la pregunta a un diccionario para guardarla en MongoDB."""
        return {
            "texto": self.__texto,
            "opciones": self.__opciones,
            "respuesta_correcta": self.__respuesta_correcta,
            "categoria_id": self.__categoria_id,
            "dificultad": self.__dificultad,
        }

    @classmethod
    def desde_diccionario(cls, datos):
        """Crea una Pregunta a partir de un documento de MongoDB."""
        return cls(
            datos["texto"],
            datos["opciones"],
            datos["respuesta_correcta"],
            datos["categoria_id"],
            datos.get("dificultad", "facil"),
            str(datos["_id"]) if "_id" in datos else None,
        )