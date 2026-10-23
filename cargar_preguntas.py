from modelos.pregunta import Pregunta
from repositorio.repositorio_quiz import RepositorioQuiz

# Formato: texto, opciones, índice de la respuesta correcta, categoría, dificultad
preguntas = [
    # Historia
    ("¿Quién lideró el cruce de los Andes?", ["Manuel Belgrano", "José de San Martín", "Martín Miguel de Güemes", "Guillermo Brown"], 1, "historia", "facil"),
    ("¿En qué año se sancionó la Constitución Nacional Argentina?", ["1816", "1853", "1880", "1916"], 1, "historia", "media"),
    ("¿En qué ciudad se encuentra la Casa Histórica donde se declaró la Independencia?", ["Salta", "Córdoba", "San Miguel de Tucumán", "Buenos Aires"], 2, "historia", "facil"),
    ("¿En qué año se formó la Primera Junta de gobierno?", ["1806", "1810", "1816", "1820"], 1, "historia", "facil"),

    # Geografía
    ("¿Qué río forma parte del límite entre Argentina y Uruguay?", ["Río Paraná", "Río Uruguay", "Río Colorado", "Río Negro"], 1, "geografia", "facil"),
    ("¿En qué provincia se encuentra el Parque Nacional Iguazú?", ["Corrientes", "Misiones", "Chaco", "Formosa"], 1, "geografia", "facil"),
    ("¿Cuál es la capital de la provincia de Tierra del Fuego, Antártida e Islas del Atlántico Sur?", ["Río Grande", "Ushuaia", "Tolhuin", "Rawson"], 1, "geografia", "media"),
    ("¿En qué provincia argentina está la ciudad de Mar del Plata?", ["Buenos Aires", "Santa Fe", "Entre Ríos", "Río Negro"], 0, "geografia", "facil"),

    # Deportes
    ("¿Qué tenista argentino ganó el Abierto de Estados Unidos en 2009?", ["Guillermo Vilas", "Juan Martín del Potro", "David Nalbandian", "Diego Schwartzman"], 1, "deportes", "media"),
    ("¿Qué club de fútbol argentino juega de local en La Bombonera?", ["River Plate", "Boca Juniors", "Racing Club", "San Lorenzo"], 1, "deportes", "facil"),
    ("¿En qué equipo de la NBA jugó gran parte de su carrera Emanuel Ginóbili?", ["Chicago Bulls", "Los Angeles Lakers", "San Antonio Spurs", "Boston Celtics"], 2, "deportes", "media"),
    ("¿Qué deporte se juega tradicionalmente a caballo y tiene gran popularidad en Argentina?", ["Béisbol", "Polo", "Críquet", "Rugby"], 1, "deportes", "facil"),

    # Música
    ("¿Qué banda argentina lideró Gustavo Cerati?", ["Los Fabulosos Cadillacs", "Soda Stereo", "Virus", "Los Enanitos Verdes"], 1, "musica", "facil"),
    ("¿Qué instrumento es característico del tango?", ["Bandoneón", "Saxofón", "Ukelele", "Clarinete"], 0, "musica", "facil"),
    ("¿Qué músico argentino es reconocido por renovar el tango y componer 'Adiós Nonino'?", ["Astor Piazzolla", "Atahualpa Yupanqui", "Charly García", "Fito Páez"], 0, "musica", "media"),
    ("¿Qué músico argentino integró el dúo Sui Generis junto con Nito Mestre?", ["Andrés Calamaro", "Charly García", "León Gieco", "Luis Alberto Spinetta"], 1, "musica", "media"),

    # Comidas y costumbres
    ("¿Cuál es la infusión tradicional que se prepara con yerba mate?", ["Té negro", "Mate", "Café", "Horchata"], 1, "costumbres", "facil"),
    ("¿Qué ingrediente es característico del locro tradicional?", ["Maíz", "Arroz", "Pescado", "Pepino"], 0, "costumbres", "facil"),
    ("¿Cómo se llama la estructura sobre la que habitualmente se cocina el asado?", ["Parrilla", "Wok", "Tetera", "Plancha de vapor"], 0, "costumbres", "facil"),
    ("¿Qué dulce suele usarse como relleno de muchos alfajores argentinos?", ["Dulce de leche", "Mermelada de naranja", "Crema pastelera", "Miel"], 0, "costumbres", "facil"),
]

repo = RepositorioQuiz()
existentes = repo.listar_preguntas()
textos_existentes = {p.texto.strip().casefold() for p in existentes}

# No cargar más de 30 en total.
cupos = max(0, 30 - len(existentes))
agregadas = 0

for texto, opciones, respuesta, categoria, dificultad in preguntas:
    if agregadas >= cupos:
        break

    if texto.strip().casefold() in textos_existentes:
        print("Ya existía; se omite:", texto)
        continue

    nueva = Pregunta(
        texto=texto,
        opciones=opciones,
        respuesta_correcta=respuesta,
        categoria_id=categoria,
        dificultad=dificultad,
    )
    repo.crear_pregunta(nueva)
    textos_existentes.add(texto.strip().casefold())
    agregadas += 1
    print("Agregada:", texto)

total = len(repo.listar_preguntas())
print(f"\nSe agregaron {agregadas} preguntas. Total actual: {total}")
