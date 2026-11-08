"""Árboles de decisión (uno por motivo de consulta) y catálogo de diagnósticos.

Cada árbol es un diccionario de nodos. Hay dos tipos de nodo:
  - pregunta: {"pregunta": "...", "si": id_nodo, "no": id_nodo}
  - hoja:     {"diagnostico": clave_del_diagnostico}
"""

MOTIVOS = [
    {"id": "fiebre", "nombre": "Fiebre"},
    {"id": "tos", "nombre": "Tos"},
    {"id": "estomago", "nombre": "Dolor de estómago"},
    {"id": "cabeza", "nombre": "Dolor de cabeza"},
    {"id": "garganta", "nombre": "Dolor de garganta"},
    {"id": "cansancio", "nombre": "Cansancio"},
]

NOMBRE_MOTIVO = {m["id"]: m["nombre"] for m in MOTIVOS}


def _p(pregunta, si, no):
    return {"pregunta": pregunta, "si": si, "no": no}


def _h(diagnostico):
    return {"diagnostico": diagnostico}


INICIO = {
    "fiebre": "f1",
    "tos": "t1",
    "estomago": "e1",
    "cabeza": "c1",
    "garganta": "g1",
    "cansancio": "n1",
}

ARBOLES = {
    "fiebre": {
        "f1": _p("¿Tienes tos o dolor de garganta?", "f2", "f4"),
        "f2": _p("¿Sientes dificultad para respirar o dolor en el pecho al respirar?", "h_neumonia", "f3"),
        "f3": _p("¿Tienes dolores musculares fuertes o escalofríos?", "h_influenza", "h_viral"),
        "f4": _p(
            "¿Tienes dolor detrás de los ojos, dolor fuerte de articulaciones o manchas en la piel?",
            "h_dengue",
            "f5",
        ),
        "f5": _p("¿Sientes ardor al orinar o dolor en la zona baja de la espalda?", "h_urinaria", "h_viral"),
        "h_neumonia": _h("neumonia"),
        "h_influenza": _h("influenza"),
        "h_viral": _h("viral"),
        "h_dengue": _h("dengue"),
        "h_urinaria": _h("urinaria"),
    },
    "tos": {
        "t1": _p("¿Sientes dificultad para respirar o silbidos en el pecho?", "t2", "t3"),
        "t2": _p("¿Tienes fiebre alta o dolor en el pecho al respirar?", "h_neumonia", "h_asma"),
        "t3": _p("¿La tos tiene flema o lleva más de dos semanas?", "h_bronquitis", "t4"),
        "t4": _p("¿Tienes estornudos, picazón en la nariz o los ojos, o congestión?", "h_alergia", "h_resfriado"),
        "h_neumonia": _h("neumonia"),
        "h_asma": _h("asma"),
        "h_bronquitis": _h("bronquitis"),
        "h_alergia": _h("alergia"),
        "h_resfriado": _h("resfriado"),
    },
    "estomago": {
        "e1": _p("¿Tienes vómito o diarrea?", "e2", "e3"),
        "e2": _p("¿Hay sangre en el vómito o en las heces, o no logras tomar líquidos?", "h_gastro_grave", "h_gastro"),
        "e3": _p(
            "¿El dolor es muy fuerte, se concentra abajo a la derecha o el abdomen está duro?",
            "h_abdomen",
            "e4",
        ),
        "e4": _p("¿Sientes ardor o dolor en la parte alta del abdomen, sobre todo con las comidas?", "h_gastritis", "h_indigestion"),
        "h_gastro_grave": _h("gastro_grave"),
        "h_gastro": _h("gastroenteritis"),
        "h_abdomen": _h("abdomen_agudo"),
        "h_gastritis": _h("gastritis"),
        "h_indigestion": _h("indigestion"),
    },
    "cabeza": {
        "c1": _p("¿Tienes rigidez en el cuello, confusión o fiebre junto con el dolor?", "h_meningitis", "c2"),
        "c2": _p("¿El dolor es de un solo lado, pulsátil, con náuseas o molestia a la luz?", "h_migrana", "c3"),
        "c3": _p("¿Sientes presión en la cara, congestión nasal o secreción?", "h_sinusitis", "h_tensional"),
        "h_meningitis": _h("meningitis"),
        "h_migrana": _h("migrana"),
        "h_sinusitis": _h("sinusitis"),
        "h_tensional": _h("cefalea_tensional"),
    },
    "garganta": {
        "g1": _p("¿Tienes fiebre, ganglios inflamados o puntos blancos en la garganta?", "h_faringo", "g2"),
        "g2": _p("¿Tienes tos, mocos o estornudos?", "h_resfriado", "g3"),
        "g3": _p("¿Te cuesta tragar la saliva o abrir la boca?", "h_profunda", "h_irritacion"),
        "h_faringo": _h("faringo"),
        "h_resfriado": _h("resfriado"),
        "h_profunda": _h("infeccion_profunda"),
        "h_irritacion": _h("irritacion"),
    },
    "cansancio": {
        "n1": _p("¿Has perdido peso sin querer o tienes sudoración nocturna?", "n2", "n3"),
        "n2": _p("¿Tienes mucha sed u orinas con mucha frecuencia?", "h_diabetes", "h_estudio"),
        "n3": _p("¿Te sientes con poco ánimo, triste o con mucha ansiedad?", "h_animo", "n4"),
        "n4": _p("¿Tienes palidez, mareos o menstruación muy abundante?", "h_anemia", "h_sueno"),
        "h_diabetes": _h("diabetes"),
        "h_estudio": _h("estudio"),
        "h_animo": _h("animo"),
        "h_anemia": _h("anemia"),
        "h_sueno": _h("sueno_estres"),
    },
}

# nivel base: 0 = manejo en casa, 1 = médico de familia, 2 = urgencias
DIAGNOSTICOS = {
    "neumonia": {
        "nombre": "Posible infección respiratoria baja (neumonía)",
        "descripcion": "Infección de los pulmones que suele dar fiebre, tos y dificultad para respirar.",
        "nivel": 2,
        "otras": ["Bronquitis aguda", "Crisis de asma"],
        "cuidados": [
            "Mantente en reposo y toma líquidos mientras recibes atención.",
            "No te automediques antibióticos.",
        ],
        "alarma": [
            "Labios o uñas azulados o morados",
            "Respiración muy rápida o confusión",
            "Dolor de pecho que empeora",
        ],
    },
    "influenza": {
        "nombre": "Posible influenza (gripe)",
        "descripcion": "Infección viral con fiebre, malestar general, dolores musculares y tos.",
        "nivel": 0,
        "otras": ["Resfriado común", "COVID-19 u otra infección viral"],
        "cuidados": [
            "Reposo e hidratación abundante.",
            "Controla la temperatura cada pocas horas.",
            "Evita contagiar a otros: lávate las manos y usa mascarilla.",
        ],
        "alarma": [
            "Dificultad para respirar",
            "Fiebre que no baja después de 3 días",
            "Confusión o somnolencia excesiva",
        ],
    },
    "viral": {
        "nombre": "Posible infección viral leve",
        "descripcion": "Cuadro frecuente que suele pasar solo en pocos días con reposo.",
        "nivel": 0,
        "otras": ["Resfriado común", "Inicio de una gripe"],
        "cuidados": ["Descansa e hidrátate.", "Vigila la fiebre y cómo evolucionas."],
        "alarma": ["Fiebre alta persistente", "Dificultad para respirar", "Decaimiento marcado"],
    },
    "dengue": {
        "nombre": "Posible dengue u otra infección tropical",
        "descripcion": "Infección transmitida por mosquitos con fiebre, dolor detrás de los ojos y dolor de articulaciones.",
        "nivel": 1,
        "otras": ["Chikungunya o zika", "Infección viral"],
        "cuidados": [
            "Reposo e hidratación abundante.",
            "Evita aspirina e ibuprofeno salvo que un médico lo indique.",
            "Protégete de los mosquitos.",
        ],
        "alarma": [
            "Dolor abdominal fuerte",
            "Vómitos repetidos",
            "Sangrado de encías o de la nariz",
            "Mucho sueño o irritabilidad",
        ],
    },
    "urinaria": {
        "nombre": "Posible infección urinaria",
        "descripcion": "Infección de la vejiga o los riñones: ardor al orinar, ganas frecuentes y a veces fiebre.",
        "nivel": 1,
        "otras": ["Infección de riñón", "Infección viral"],
        "cuidados": ["Toma abundante agua.", "No te automediques antibióticos."],
        "alarma": [
            "Fiebre alta con escalofríos",
            "Dolor intenso en la espalda",
            "Sangre en la orina o vómitos",
        ],
    },
    "asma": {
        "nombre": "Posible crisis de asma o bronquitis",
        "descripcion": "Inflamación de los bronquios con silbidos en el pecho y sensación de falta de aire.",
        "nivel": 1,
        "otras": ["Bronquitis aguda", "Alergia respiratoria"],
        "cuidados": [
            "Si tienes inhalador, úsalo según te indicó tu médico.",
            "Evita humo, polvo y esfuerzos.",
        ],
        "alarma": [
            "No puedes hablar con frases completas",
            "El inhalador no te alivia",
            "Labios azulados",
        ],
    },
    "bronquitis": {
        "nombre": "Posible bronquitis aguda",
        "descripcion": "Inflamación de los bronquios, con tos y flema que puede durar varias semanas.",
        "nivel": 0,
        "otras": ["Resfriado prolongado", "Alergia respiratoria"],
        "cuidados": [
            "Hidratación y reposo.",
            "Evita el humo del cigarrillo.",
            "Una bebida tibia con miel puede aliviar la tos en adultos.",
        ],
        "alarma": ["Dificultad para respirar", "Fiebre alta", "Tos con sangre"],
    },
    "alergia": {
        "nombre": "Posible alergia respiratoria (rinitis)",
        "descripcion": "Reacción al polvo, polen o animales: estornudos, picazón y congestión.",
        "nivel": 0,
        "otras": ["Resfriado común", "Sinusitis"],
        "cuidados": [
            "Evita el desencadenante (polvo, polen, mascotas).",
            "Lava las fosas nasales con suero salino.",
        ],
        "alarma": [
            "Hinchazón de la cara o los labios",
            "Dificultad para respirar",
            "Ronchas extendidas por el cuerpo",
        ],
    },
    "resfriado": {
        "nombre": "Posible resfriado común",
        "descripcion": "Infección viral leve de nariz y garganta que suele pasar sola en una semana.",
        "nivel": 0,
        "otras": ["Alergia respiratoria", "Inicio de una gripe"],
        "cuidados": [
            "Descansa y toma líquidos tibios.",
            "Lávate las manos para no contagiar a otros.",
        ],
        "alarma": [
            "Fiebre alta",
            "Dificultad para respirar",
            "Síntomas que empeoran después del quinto día",
        ],
    },
    "gastro_grave": {
        "nombre": "Posible gastroenteritis con deshidratación o sangrado",
        "descripcion": "Infección intestinal con pérdida importante de líquidos o presencia de sangre.",
        "nivel": 2,
        "otras": ["Intoxicación alimentaria", "Infección intestinal bacteriana"],
        "cuidados": [
            "Toma sorbos pequeños de suero oral mientras llegas.",
            "Ve acompañado.",
        ],
        "alarma": [
            "Sangre en las heces o en el vómito",
            "No puedes tomar líquidos",
            "Mareo, boca seca o muy poca orina",
        ],
    },
    "gastroenteritis": {
        "nombre": "Posible gastroenteritis",
        "descripcion": "Infección intestinal frecuente, con vómito, diarrea y dolor de barriga.",
        "nivel": 0,
        "otras": ["Intoxicación alimentaria", "Infección viral"],
        "cuidados": [
            "Suero oral y líquidos en sorbos pequeños.",
            "Comidas suaves cuando las toleres.",
            "Lávate las manos con frecuencia.",
        ],
        "alarma": [
            "Sangre en las heces",
            "No puedes tomar líquidos",
            "Poca orina, boca seca o mareo",
        ],
    },
    "abdomen_agudo": {
        "nombre": "Posible abdomen agudo (como apendicitis)",
        "descripcion": "Dolor abdominal intenso que puede necesitar revisión urgente, incluso cirugía.",
        "nivel": 2,
        "otras": ["Gastroenteritis", "Cólico renal o intestinal"],
        "cuidados": [
            "No comas ni tomes analgésicos fuertes sin indicación médica.",
            "Ve acompañado.",
        ],
        "alarma": [
            "Dolor que empeora o se extiende",
            "Fiebre o vómitos persistentes",
            "Abdomen duro",
        ],
    },
    "gastritis": {
        "nombre": "Posible gastritis",
        "descripcion": "Irritación del estómago con ardor y malestar, sobre todo con las comidas.",
        "nivel": 0,
        "otras": ["Reflujo", "Indigestión"],
        "cuidados": [
            "Evita comidas pesadas, picantes, café y alcohol.",
            "Come porciones pequeñas.",
        ],
        "alarma": [
            "Vómito con sangre o heces negras",
            "Dolor muy fuerte",
            "Pérdida de peso sin explicación",
        ],
    },
    "indigestion": {
        "nombre": "Posible indigestión o estreñimiento",
        "descripcion": "Molestia digestiva leve relacionada con las comidas, el estrés o poca fibra.",
        "nivel": 0,
        "otras": ["Gastritis", "Colon irritable"],
        "cuidados": ["Más fibra, agua y movimiento.", "Evita las comidas copiosas."],
        "alarma": ["Dolor que aumenta", "Vómito persistente", "Sangre en las heces"],
    },
    "meningitis": {
        "nombre": "Posible infección grave del sistema nervioso",
        "descripcion": "Rigidez de cuello con fiebre o confusión puede indicar una infección que requiere atención inmediata.",
        "nivel": 2,
        "otras": ["Migraña intensa", "Infección viral con fiebre"],
        "cuidados": ["No esperes: busca atención ya.", "Ve acompañado."],
        "alarma": [
            "Manchas moradas en la piel",
            "Convulsiones",
            "Pérdida de conciencia",
        ],
    },
    "migrana": {
        "nombre": "Posible migraña",
        "descripcion": "Dolor de cabeza pulsátil, de un lado, con náuseas y molestia a la luz o al ruido.",
        "nivel": 0,
        "otras": ["Cefalea tensional", "Sinusitis"],
        "cuidados": [
            "Descansa en un lugar oscuro y silencioso.",
            "Hidrátate y no te saltes comidas.",
            "Anota qué la desencadena.",
        ],
        "alarma": [
            "El peor dolor de cabeza de tu vida",
            "Debilidad, visión doble o dificultad para hablar",
            "Dolor después de un golpe en la cabeza",
        ],
    },
    "sinusitis": {
        "nombre": "Posible sinusitis",
        "descripcion": "Inflamación de los senos de la cara: presión, congestión y secreción nasal.",
        "nivel": 0,
        "otras": ["Resfriado común", "Alergia respiratoria"],
        "cuidados": [
            "Lavados nasales con suero salino.",
            "Vapor tibio y buena hidratación.",
        ],
        "alarma": [
            "Hinchazón alrededor del ojo",
            "Fiebre alta",
            "Dolor que empeora después de 10 días",
        ],
    },
    "cefalea_tensional": {
        "nombre": "Posible cefalea tensional",
        "descripcion": "Dolor como una banda de presión, común con estrés, mala postura o poco sueño.",
        "nivel": 0,
        "otras": ["Migraña", "Cansancio acumulado"],
        "cuidados": [
            "Descanso y pausas de pantalla.",
            "Hidratación y buen sueño.",
            "Estiramientos de cuello y hombros.",
        ],
        "alarma": [
            "Dolor súbito e intensísimo",
            "Debilidad o confusión",
            "Dolor que cambia o empeora cada semana",
        ],
    },
    "faringo": {
        "nombre": "Posible faringoamigdalitis (garganta infectada)",
        "descripcion": "Infección de la garganta y las amígdalas, a veces bacteriana, con fiebre y dolor al tragar.",
        "nivel": 1,
        "otras": ["Infección viral de garganta", "Mononucleosis"],
        "cuidados": [
            "Líquidos tibios y reposo de la voz.",
            "Gárgaras de agua tibia con sal.",
            "No tomes antibióticos sin indicación médica.",
        ],
        "alarma": [
            "No puedes tragar la saliva",
            "Dificultad para respirar",
            "Babeo o voz apagada",
        ],
    },
    "infeccion_profunda": {
        "nombre": "Posible infección profunda de garganta",
        "descripcion": "No poder tragar la saliva o abrir la boca puede indicar una complicación que necesita revisión pronta.",
        "nivel": 2,
        "otras": ["Absceso de amígdala", "Amigdalitis severa"],
        "cuidados": ["No fuerces la boca a abrirse.", "Ve acompañado."],
        "alarma": ["Dificultad para respirar", "Babeo", "Hinchazón del cuello"],
    },
    "irritacion": {
        "nombre": "Posible irritación de garganta",
        "descripcion": "Molestia por aire seco, esfuerzo de la voz, reflujo o humo.",
        "nivel": 0,
        "otras": ["Reflujo", "Inicio de un resfriado"],
        "cuidados": ["Hidratación frecuente y líquidos tibios.", "Evita el humo y los gritos."],
        "alarma": [
            "Fiebre",
            "Dificultad para tragar",
            "Molestia que dura más de dos semanas",
        ],
    },
    "diabetes": {
        "nombre": "Posible alteración del azúcar (diabetes)",
        "descripcion": "Sed intensa, orinar mucho, cansancio y pérdida de peso pueden indicar azúcar alta en la sangre.",
        "nivel": 1,
        "otras": ["Anemia", "Problema de tiroides"],
        "cuidados": [
            "Pide exámenes de sangre (glucosa).",
            "Evita las bebidas azucaradas mientras tanto.",
        ],
        "alarma": [
            "Vómitos o aliento con olor a fruta",
            "Confusión o mucho sueño",
            "Respiración rápida",
        ],
    },
    "estudio": {
        "nombre": "Cansancio con pérdida de peso: requiere estudio médico",
        "descripcion": "Perder peso sin querer junto con cansancio necesita exámenes para encontrar la causa.",
        "nivel": 1,
        "otras": ["Problema de tiroides", "Infección crónica"],
        "cuidados": [
            "Pide cita y lleva anotados tus síntomas y tu peso.",
            "No cambies tu dieta de forma drástica.",
        ],
        "alarma": ["Fiebre persistente", "Sangrado", "Dificultad para respirar"],
    },
    "animo": {
        "nombre": "Posible cansancio por estrés o bajo estado de ánimo",
        "descripcion": "El agotamiento junto con tristeza o ansiedad es común y se puede tratar.",
        "nivel": 1,
        "otras": ["Falta de sueño", "Anemia"],
        "cuidados": [
            "Habla con alguien de confianza.",
            "Mantén una rutina de sueño y algo de actividad física.",
            "Tu médico de familia puede orientarte.",
        ],
        "alarma": [
            "Pensamientos de hacerte daño: busca ayuda de inmediato",
            "No poder cuidar de ti mismo",
            "Síntomas que empeoran rápido",
        ],
    },
    "anemia": {
        "nombre": "Posible anemia",
        "descripcion": "Pocos glóbulos rojos: causa cansancio, palidez y mareos.",
        "nivel": 1,
        "otras": ["Falta de sueño", "Déficit de hierro o de vitaminas"],
        "cuidados": [
            "Pide un hemograma.",
            "Come alimentos con hierro (carnes, legumbres, verduras verdes).",
        ],
        "alarma": [
            "Desmayos",
            "Dolor de pecho o palpitaciones fuertes",
            "Sangrado abundante",
        ],
    },
    "sueno_estres": {
        "nombre": "Posible cansancio por sueño insuficiente o sobrecarga",
        "descripcion": "Dormir poco o la sobrecarga diaria bastan para causar agotamiento.",
        "nivel": 0,
        "otras": ["Estrés", "Hábitos poco saludables"],
        "cuidados": [
            "Duerme 7 a 8 horas con un horario regular.",
            "Mueve el cuerpo y limita la cafeína.",
        ],
        "alarma": [
            "Cansancio que dura más de dos semanas",
            "Pérdida de peso sin explicación",
            "Mareos o desmayos",
        ],
    },
}


def es_hoja(nodo):
    return "diagnostico" in nodo


def recorrer(motivo, respuestas):
    """Repite las respuestas desde la raíz y devuelve (id_nodo, nodo, paso).

    Lanza ValueError si el motivo no existe, si una respuesta no es "si" o "no",
    o si hay más respuestas de las necesarias.
    """
    if motivo not in ARBOLES:
        raise ValueError("Motivo desconocido.")
    arbol = ARBOLES[motivo]
    id_nodo = INICIO[motivo]
    for respuesta in respuestas:
        if respuesta not in ("si", "no"):
            raise ValueError("Las respuestas deben ser 'si' o 'no'.")
        nodo = arbol[id_nodo]
        if es_hoja(nodo):
            raise ValueError("Hay más respuestas de las necesarias.")
        id_nodo = nodo[respuesta]
    return id_nodo, arbol[id_nodo], len(respuestas) + 1


def profundidad_maxima(motivo):
    arbol = ARBOLES[motivo]

    def altura(id_nodo):
        nodo = arbol[id_nodo]
        if es_hoja(nodo):
            return 0
        return 1 + max(altura(nodo["si"]), altura(nodo["no"]))

    return altura(INICIO[motivo])
