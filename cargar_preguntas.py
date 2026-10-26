from modelos.pregunta import Pregunta
from repositorio.repositorio_quiz import RepositorioQuiz

META_PREGUNTAS = 60

# Las primeras 30 son las preguntas nuevas enviadas por el equipo.
# Las preguntas de respaldo solo se usarán si hacen falta para llegar a 60
# (por ejemplo, si alguna de las 30 ya estaba cargada en la base).
preguntas = [
    # Deportes
    ("¿En qué año ganó Argentina su primer Mundial de fútbol?", ["1978", "1986", "1990", "1930"], 0, "deportes", "facil"),
    ("¿Cómo se conoce popularmente a la Selección Argentina de rugby?", ["Los Leones", "Los Pumas", "Los Cóndores", "Los Tigres"], 1, "deportes", "facil"),
    ("¿Qué piloto argentino fue campeón mundial de Fórmula 1 en cinco ocasiones?", ["Carlos Reutemann", "Gastón Mazzacane", "Juan Manuel Fangio", "José Froilán González"], 2, "deportes", "media"),
    ("¿Qué club argentino ganó la Copa Libertadores de 1986?", ["Independiente", "River Plate", "Boca Juniors", "Racing Club"], 1, "deportes", "media"),
    ("¿Qué boxeador argentino ganó la medalla de oro en los Juegos Olímpicos de Helsinki 1952?", ["Pascual Pérez", "Carlos Monzón", "Víctor Galíndez", "Noel Chialvo"], 0, "deportes", "dificil"),
    ("¿Qué atleta argentino ganó la medalla de oro en maratón en los Juegos Olímpicos de Londres 1948?", ["Delfo Cabrera", "Juan Carlos Zabala", "Osvaldo Suárez", "Reinaldo Gorno"], 0, "deportes", "dificil"),

    # Geografía
    ("¿Cuál es la capital de la provincia de Córdoba?", ["Villa Carlos Paz", "Río Cuarto", "Córdoba", "Alta Gracia"], 2, "geografia", "facil"),
    ("¿Qué provincia argentina es conocida por sus viñedos y la producción de vino?", ["Mendoza", "Chaco", "Corrientes", "Formosa"], 0, "geografia", "facil"),
    ("¿Qué provincia argentina tiene la mayor superficie territorial?", ["Santa Fe", "Buenos Aires", "Chubut", "Tierra del Fuego"], 1, "geografia", "media"),
    ("¿Qué cordillera recorre el límite occidental de Argentina?", ["Cordillera Cantábrica", "Cordillera de los Andes", "Cordillera Central", "Cordillera Oriental"], 1, "geografia", "media"),
    ("¿Cómo se llama el cerro más alto de Argentina y de América?", ["Cerro Tronador", "Monte Fitz Roy", "Aconcagua", "Cerro Catedral"], 2, "geografia", "dificil"),
    ("¿En qué provincia argentina se encuentra gran parte del sector argentino del campo de hielo patagónico sur?", ["Misiones", "Santa Cruz", "San Juan", "La Pampa"], 1, "geografia", "dificil"),

    # Historia
    ("¿Quién fue el primer presidente constitucional de Argentina?", ["Bartolomé Mitre", "Justo José de Urquiza", "Domingo F. Sarmiento", "Julio A. Roca"], 1, "historia", "facil"),
    ("¿Cómo se llamaba el último virreinato al que perteneció el territorio argentino antes de la Revolución de Mayo?", ["Virreinato de Nueva España", "Virreinato del Perú", "Virreinato del Río de la Plata", "Virreinato de Nueva Granada"], 2, "historia", "facil"),
    ("¿En qué año se produjo la batalla de Caseros?", ["1810", "1820", "1852", "1861"], 2, "historia", "media"),
    ("¿Durante qué presidencia se sancionó la Ley 1420 de educación común, gratuita y obligatoria?", ["Nicolás Avellaneda", "Julio A. Roca", "Hipólito Yrigoyen", "Juan Domingo Perón"], 1, "historia", "media"),
    ("¿En qué año se produjo la Semana Trágica en Buenos Aires?", ["1905", "1919", "1930", "1945"], 1, "historia", "dificil"),
    ("¿Qué tratado de 1881 estableció límites entre Argentina y Chile?", ["Tratado de Tordesillas", "Tratado de Pilar", "Tratado de Límites de 1881", "Pacto Federal"], 2, "historia", "dificil"),

    # Comidas y costumbres
    ("¿Qué comida argentina se prepara tradicionalmente con masa y distintos rellenos?", ["Empanadas", "Sushi", "Tacos", "Falafel"], 0, "costumbres", "facil"),
    ("¿Qué se suele hacer en Argentina durante una reunión de amigos acompañada de mate?", ["Compartir la ronda de mate", "Servirlo siempre en vasos grandes", "Tomarlo exclusivamente frío", "Prepararlo con café"], 0, "costumbres", "facil"),
    ("¿Qué corte de carne es muy común en el asado argentino?", ["Vacío", "Bacalao", "Pechuga de pavo", "Conejo"], 0, "costumbres", "media"),
    ("¿Qué se celebra tradicionalmente en Argentina el 25 de mayo?", ["El Día de la Bandera", "La Revolución de Mayo", "El Día de la Independencia", "El Día de la Tradición"], 1, "costumbres", "media"),
    ("¿Qué nombre recibe una preparación tradicional argentina de carne cocida lentamente en una olla, a veces acompañada de verduras y frutas?", ["Carbonada", "Gazpacho", "Paella valenciana", "Ratatouille"], 0, "costumbres", "dificil"),
    ("¿Qué celebración tradicional argentina se relaciona especialmente con las destrezas gauchas y las tradiciones rurales?", ["Fiesta Nacional de la Vendimia", "Fiesta Nacional del Chamamé", "Fiesta de la Tradición", "Carnaval de Gualeguaychú"], 2, "costumbres", "dificil"),

    # Música
    ("¿Qué género musical y baile nació en la región del Río de la Plata?", ["Samba", "Tango", "Cumbia colombiana", "Bossa nova"], 1, "musica", "facil"),
    ("¿Qué cantante argentina es conocida como 'La Sole'?", ["Mercedes Sosa", "Soledad Pastorutti", "Valeria Lynch", "Patricia Sosa"], 1, "musica", "facil"),
    ("¿Qué banda argentina publicó el álbum 'Canción Animal'?", ["Los Redondos", "Soda Stereo", "Los Piojos", "Enanitos Verdes"], 1, "musica", "media"),
    ("¿Qué músico argentino es conocido por interpretar y difundir la canción 'El arriero'?", ["Atahualpa Yupanqui", "Fito Páez", "Andrés Calamaro", "Pedro Aznar"], 0, "musica", "media"),
    ("¿Qué compositor argentino creó la obra sinfónica 'Estancia'?", ["Alberto Ginastera", "Astor Piazzolla", "Carlos Guastavino", "Juan Carlos Paz"], 0, "musica", "dificil"),
    ("¿Qué músico argentino compuso la canción 'Muchacha (Ojos de papel)'?", ["Charly García", "León Gieco", "Luis Alberto Spinetta", "Litto Nebbia"], 2, "musica", "dificil"),

    # Preguntas de respaldo. Se insertan solo si hacen falta para alcanzar 60.
    ("¿Qué océano baña la costa argentina?", ["Océano Atlántico", "Océano Pacífico", "Océano Índico", "Océano Ártico"], 0, "geografia", "facil"),
    ("¿Qué provincia argentina tiene como capital a San Miguel de Tucumán?", ["Salta", "Santiago del Estero", "Tucumán", "Jujuy"], 2, "geografia", "facil"),
    ("¿En qué provincia se encuentra el Parque Nacional Talampaya?", ["La Rioja", "Neuquén", "Entre Ríos", "San Luis"], 0, "geografia", "media"),
    ("¿Qué instrumento suele acompañar al tango y tiene fuelle?", ["Bandoneón", "Charango", "Siku", "Arpa"], 0, "musica", "facil"),
    ("¿Qué cantante argentina interpretó la canción 'Alfonsina y el mar'?", ["Mercedes Sosa", "Soledad Pastorutti", "Gilda", "Fabiana Cantilo"], 0, "musica", "media"),
    ("¿Qué escritor argentino escribió 'Martín Fierro'?", ["José Hernández", "Leopoldo Lugones", "Jorge Luis Borges", "Roberto Arlt"], 0, "historia", "media"),
    ("¿Qué prócer argentino es conocido como el creador de la bandera nacional?", ["Manuel Belgrano", "José de San Martín", "Mariano Moreno", "Juan José Castelli"], 0, "historia", "facil"),
    ("¿Qué deporte practica tradicionalmente un equipo de cuatro jinetes con tacos largos?", ["Polo", "Hockey", "Rugby", "Béisbol"], 0, "deportes", "facil"),
    ("¿Qué torneo de tenis se disputa cada año en Buenos Aires?", ["Argentina Open", "Copa Davis de Wimbledon", "Masters de Córdoba", "Roland Garros"], 0, "deportes", "media"),
    ("¿Qué postre argentino suele llevar una cubierta de merengue y dulce de leche?", ["Rogel", "Tiramisú", "Baklava", "Crème brûlée"], 0, "costumbres", "media"),
]

repo = RepositorioQuiz()
existentes = repo.listar_preguntas()
textos_existentes = {p.texto.strip().casefold() for p in existentes}
categorias_validas = {str(c["_id"]) for c in repo.obtener_categorias()}

if len(existentes) >= META_PREGUNTAS:
    print(f"La base ya tiene {len(existentes)} preguntas; la meta es {META_PREGUNTAS}. No se agregaron preguntas.")
    raise SystemExit(0)

agregadas = 0
omitidas = 0

for texto, opciones, respuesta, categoria, dificultad in preguntas:
    total_actual = len(existentes) + agregadas
    if total_actual >= META_PREGUNTAS:
        break

    texto_normalizado = texto.strip().casefold()
    if texto_normalizado in textos_existentes:
        omitidas += 1
        print("Ya existía; se omite:", texto)
        continue

    if categoria not in categorias_validas:
        raise RuntimeError(f"La categoría '{categoria}' no existe en MongoDB. No se cargó esta pregunta.")

    nueva = Pregunta(
        texto=texto,
        opciones=opciones,
        respuesta_correcta=respuesta,
        categoria_id=categoria,
        dificultad=dificultad,
    )
    repo.crear_pregunta(nueva)
    textos_existentes.add(texto_normalizado)
    agregadas += 1
    print("Agregada:", texto)


total_final = len(repo.listar_preguntas())
print(f"\nAgregadas: {agregadas}")
print(f"Omitidas por duplicado: {omitidas}")
print(f"Total actual: {total_final} de {META_PREGUNTAS}")
if total_final < META_PREGUNTAS:
    print("Faltan preguntas nuevas: agrega más entradas a la lista antes de volver a ejecutar.")
