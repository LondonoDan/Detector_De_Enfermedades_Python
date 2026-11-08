from flask import Flask, jsonify, render_template, request

from arbol import MOTIVOS, es_hoja, profundidad_maxima, recorrer
from consulta import calcular_resultado, validar_perfil

app = Flask(__name__)


def _cuerpo_json():
    datos = request.get_json(silent=True)
    return datos if isinstance(datos, dict) else None


def _error(mensaje, codigo=400):
    return jsonify({"error": mensaje}), codigo


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/motivos", methods=["GET"])
def motivos():
    return jsonify({"motivos": MOTIVOS})


@app.route("/api/pregunta", methods=["POST"])
def pregunta():
    datos = _cuerpo_json()
    if datos is None:
        return _error("El cuerpo debe ser JSON.")

    motivo = datos.get("motivo")
    respuestas = datos.get("respuestas", [])
    if not isinstance(respuestas, list):
        return _error("'respuestas' debe ser una lista.")

    try:
        id_nodo, nodo, paso = recorrer(motivo, respuestas)
    except ValueError as e:
        return _error(str(e))

    if es_hoja(nodo):
        return jsonify({"tipo": "fin"})

    return jsonify(
        {
            "tipo": "pregunta",
            "id": id_nodo,
            "pregunta": nodo["pregunta"],
            "paso": paso,
            "profundidad": profundidad_maxima(motivo),
        }
    )


@app.route("/api/consulta", methods=["POST"])
def consulta():
    datos = _cuerpo_json()
    if datos is None:
        return _error("El cuerpo debe ser JSON.")

    perfil, error = validar_perfil(datos.get("perfil"))
    if error:
        return _error(error)

    respuestas = datos.get("respuestas")
    if not isinstance(respuestas, list):
        return _error("'respuestas' debe ser una lista.")

    try:
        _, nodo, _ = recorrer(perfil["motivos"][0], respuestas)
    except ValueError as e:
        return _error(str(e))

    if not es_hoja(nodo):
        return _error("Faltan respuestas para completar la consulta.")

    return jsonify(calcular_resultado(perfil, nodo["diagnostico"]))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
