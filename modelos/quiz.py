from modelos.puntuacion import Puntuacion


class Quiz:
    """Una partida: lleva el control de la pregunta actual y de los aciertos."""

    PUNTOS_POR_ACIERTO = 100

    def __init__(self, preguntas):
        if not preguntas:
            raise ValueError("El quiz necesita al menos una pregunta.")
        self.__preguntas = list(preguntas)
        self.__indice = 0      # pregunta en la que estamos
        self.__aciertos = 0

    @property
    def aciertos(self):
        return self.__aciertos

    @property
    def total_preguntas(self):
        return len(self.__preguntas)

    def terminado(self):
        """True si ya se respondieron todas las preguntas."""
        return self.__indice >= len(self.__preguntas)

    def pregunta_actual(self):
        """Devuelve la pregunta que toca responder."""
        if self.terminado():
            raise ValueError("El quiz ya terminó.")
        return self.__preguntas[self.__indice]

    def responder(self, indice_elegido):
        """Corrige la respuesta, suma el acierto si corresponde y pasa a la siguiente."""
        pregunta = self.pregunta_actual()
        es_correcta = pregunta.es_correcta(indice_elegido)
        if es_correcta:
            self.__aciertos += 1
        self.__indice += 1
        return es_correcta

    def calcular_puntos(self):
        """100 puntos por cada respuesta correcta."""
        return self.__aciertos * self.PUNTOS_POR_ACIERTO

    def crear_puntuacion(self, jugador):
        """Cuando termina la partida, arma la Puntuacion para guardarla."""
        if not self.terminado():
            raise ValueError("Todavía no terminó el quiz.")
        return Puntuacion(jugador, self.calcular_puntos(), self.__aciertos, self.total_preguntas)
