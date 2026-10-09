from datetime import datetime


class Puntuacion:
    """Resultado de una partida del quiz."""

    def __init__(self, jugador, puntos, aciertos, total_preguntas, fecha=None):
        self.jugador = jugador
        self.puntos = puntos
        self.aciertos = aciertos
        self.total_preguntas = total_preguntas
        # Si no se indica la fecha, se usa la de ahora
        self.__fecha = fecha if fecha else datetime.now()

    # ---------- jugador ----------
    @property
    def jugador(self):
        return self.__jugador

    @jugador.setter
    def jugador(self, valor):
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El nombre del jugador no puede estar vacío.")
        self.__jugador = valor.strip()

    # ---------- puntos ----------
    @property
    def puntos(self):
        return self.__puntos

    @puntos.setter
    def puntos(self, valor):
        if not isinstance(valor, int) or not 0 <= valor <= 1000:
            raise ValueError("Los puntos deben ser un número entre 0 y 1000.")
        self.__puntos = valor

    # ---------- aciertos ----------
    @property
    def aciertos(self):
        return self.__aciertos

    @aciertos.setter
    def aciertos(self, valor):
        if not isinstance(valor, int) or valor < 0:
            raise ValueError("Los aciertos deben ser un número entero mayor o igual a 0.")
        self.__aciertos = valor

    # ---------- total_preguntas ----------
    @property
    def total_preguntas(self):
        return self.__total_preguntas

    @total_preguntas.setter
    def total_preguntas(self, valor):
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("El total de preguntas debe ser un número entero mayor a 0.")
        self.__total_preguntas = valor

    @property
    def fecha(self):
        return self.__fecha

    def a_diccionario(self):
        """Arma el documento para guardarlo en MongoDB."""
        return {
            "jugador": self.__jugador,
            "puntos": self.__puntos,
            "aciertos": self.__aciertos,
            "total_preguntas": self.__total_preguntas,
            "fecha": self.__fecha,
        }

    @classmethod
    def desde_diccionario(cls, datos):
        """Crea una Puntuacion a partir de un documento de MongoDB."""
        return cls(
            datos["jugador"],
            datos["puntos"],
            datos["aciertos"],
            datos["total_preguntas"],
            datos.get("fecha"),
        )
