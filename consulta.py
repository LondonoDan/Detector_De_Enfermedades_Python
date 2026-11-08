"""Validación del perfil del paciente y cálculo del resultado orientativo."""

from arbol import DIAGNOSTICOS, NOMBRE_MOTIVO

SEXOS = {"femenino", "masculino", "no_dice"}
DURACIONES = {"hoy", "1-3", "4-7", "mas_semana"}
FUMA = {"no", "a_veces", "si"}
EJERCICIO = {"nunca", "poco", "mucho"}
SUENO = {"poco", "normal", "mucho"}

CLAVES_BOOLEANAS = ("brusco", "alergias", "medicamentos", "previas")

TRIAJE = {
    0: {
        "clave": "autocuidado",
        "titulo": "Puedes manejarlo en casa",
        "texto": (
            "Descansa, hidrátate y vigila cómo evolucionas. Si en 3 días no mejoras "
            "o aparece alguna señal de alarma, consulta a tu médico de familia."
        ),
    },
    1: {
        "clave": "medico_familia",
        "titulo": "Consulta a tu médico de familia",
        "texto": (
            "Pide cita en las próximas 24 a 48 horas para que te examinen. "
            "Si aparece alguna señal de alarma, ve a urgencias sin esperar."
        ),
    },
    2: {
        "clave": "urgencias",
        "titulo": "Ve a urgencias",
        "texto": (
            "Acude hoy a urgencias o llama a emergencias (en Colombia, 123). "
            "No esperes a que pase solo."
        ),
    },
}


def validar_perfil(datos):
    """Devuelve (perfil_limpio, None) o (None, mensaje_de_error)."""
    if not isinstance(datos, dict):
        return None, "El perfil debe ser un objeto JSON."

    nombre = datos.get("nombre")
    if not isinstance(nombre, str) or not 1 <= len(nombre.strip()) <= 30:
        return None, "El nombre debe tener entre 1 y 30 caracteres."

    edad = datos.get("edad")
    if isinstance(edad, bool) or not isinstance(edad, int) or not 1 <= edad <= 110:
        return None, "La edad debe ser un número entre 1 y 110."

    if datos.get("sexo") not in SEXOS:
        return None, "Sexo no válido."

    motivos = datos.get("motivos")
    if (
        not isinstance(motivos, list)
        or not motivos
        or len(set(motivos)) != len(motivos)
        or any(m not in NOMBRE_MOTIVO for m in motivos)
    ):
        return None, "Elige al menos un motivo de consulta válido."

    if datos.get("duracion") not in DURACIONES:
        return None, "Duración no válida."

    intensidad = datos.get("intensidad")
    if isinstance(intensidad, bool) or not isinstance(intensidad, int) or not 1 <= intensidad <= 10:
        return None, "La intensidad debe ser un número entre 1 y 10."

    for clave in CLAVES_BOOLEANAS:
        if not isinstance(datos.get(clave), bool):
            return None, f"El campo '{clave}' debe ser verdadero o falso."

    if datos.get("fuma") not in FUMA:
        return None, "Valor no válido en 'fuma'."
    if datos.get("ejercicio") not in EJERCICIO:
        return None, "Valor no válido en 'ejercicio'."
    if datos.get("sueno") not in SUENO:
        return None, "Valor no válido en 'sueno'."

    perfil = {k: datos[k] for k in (
        "edad", "sexo", "motivos", "duracion", "intensidad",
        "brusco", "alergias", "medicamentos", "previas",
        "fuma", "ejercicio", "sueno",
    )}
    perfil["nombre"] = nombre.strip()
    return perfil, None


def _subir(nivel, minimo):
    return max(nivel, minimo)


def calcular_resultado(perfil, clave):
    """Ajusta el diagnóstico del árbol con lo que dijo la persona."""
    motivos = perfil["motivos"]
    intensidad = perfil["intensidad"]
    duracion = perfil["duracion"]
    edad = perfil["edad"]
    edad_riesgo = edad < 5 or edad >= 65

    razones = []
    principal = NOMBRE_MOTIVO[motivos[0]].lower()
    razones.append(
        f"Tu motivo principal es {principal} y tus respuestas a las preguntas apuntan a un cuadro compatible."
    )
    if len(motivos) > 1:
        otros = ", ".join(NOMBRE_MOTIVO[m].lower() for m in motivos[1:])
        razones.append(f"También mencionaste: {otros}.")

    if clave in ("viral", "resfriado") and "fiebre" in motivos and len(motivos) >= 2 and intensidad >= 6:
        clave = "influenza"
        razones.append(
            "La fiebre junto con otros síntomas y una intensidad alta se parece más a una gripe."
        )

    diagnostico = DIAGNOSTICOS[clave]
    nivel = diagnostico["nivel"]
    base = nivel

    if nivel == 0 and duracion == "mas_semana":
        nivel = _subir(nivel, 1)
        razones.append("Lleva más de una semana, y conviene que un médico lo revise.")
    if nivel == 0 and "fiebre" in motivos and duracion in ("4-7", "mas_semana"):
        nivel = _subir(nivel, 1)
        razones.append("La fiebre lleva varios días.")
    if nivel == 0 and intensidad >= 8:
        nivel = _subir(nivel, 1)
        razones.append("La intensidad que describes es alta.")
    if nivel == 1 and intensidad >= 9:
        nivel = _subir(nivel, 2)
        razones.append("La intensidad es muy alta y por eso conviene que te vean hoy.")
    if perfil["previas"] and nivel == 0 and intensidad >= 6:
        nivel = _subir(nivel, 1)
        razones.append("Tienes enfermedades previas, y con esta intensidad es mejor consultar.")
    elif perfil["previas"] and nivel == 1 and base >= 1 and intensidad >= 7:
        nivel = _subir(nivel, 2)
        razones.append("Tus enfermedades previas junto con una intensidad alta suben la alerta.")
    if edad_riesgo and nivel == 0 and intensidad >= 5:
        nivel = _subir(nivel, 1)
        razones.append(f"Por tu edad ({edad} años) conviene ser más precavido.")
    elif edad_riesgo and nivel == 1 and base >= 1 and intensidad >= 8:
        nivel = _subir(nivel, 2)
        razones.append(f"Por tu edad ({edad} años) y la intensidad, es mejor que te vean hoy.")
    if nivel == 0 and perfil["brusco"] and intensidad >= 7:
        nivel = _subir(nivel, 1)
        razones.append("Empezó de golpe y con intensidad alta.")
    if nivel == 0 and "tos" in motivos and perfil["fuma"] == "si" and duracion in ("4-7", "mas_semana"):
        nivel = _subir(nivel, 1)
        razones.append("Fumas y la tos lleva varios días.")

    nivel = min(nivel, 2)
    if len(razones) == 1 + (1 if len(motivos) > 1 else 0):
        razones.append("Con tu edad, intensidad y antecedentes no se agregó ninguna alerta extra.")

    cuidados = list(diagnostico["cuidados"])
    if perfil["medicamentos"]:
        cuidados.append("Como tomas medicamentos, consulta con tu médico o farmacéutico antes de tomar otros.")
    if perfil["alergias"]:
        cuidados.append("Recuerda informar tus alergias a medicamentos antes de recibir cualquier tratamiento.")

    return {
        "enfermedad": {
            "clave": clave,
            "nombre": diagnostico["nombre"],
            "descripcion": diagnostico["descripcion"],
        },
        "otras": diagnostico["otras"],
        "triaje": {"nivel": nivel, **TRIAJE[nivel]},
        "razones": razones,
        "cuidados": cuidados,
        "alarma": diagnostico["alarma"],
    }
