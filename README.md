# Detector de síntomas (Flask)

Proyecto académico de Redes de Datos. Aplicación web cliente-servidor que simula una consulta médica general: el navegador (cliente) recoge los datos de la persona y hace las preguntas; el servidor Flask contiene los árboles de decisión y devuelve, en JSON por HTTP, una posible enfermedad y la recomendación de ir a urgencias o consultar al médico de familia.

> Esto NO reemplaza a un médico. Es un proyecto académico.

## Cómo ejecutarlo

```bash
python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abre http://localhost:5000 en el navegador. Desde otro dispositivo de la misma red usa `http://IP_DEL_PC:5000`.

## Estructura

```
detector_enfermedades/
├── app.py              # Servidor Flask y endpoints de la API
├── arbol.py            # 6 árboles de decisión (uno por motivo) y catálogo de diagnósticos
├── consulta.py         # Validación del perfil y cálculo del resultado
├── requirements.txt
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── app.js          # Interfaz por etapas (fetch a la API)
```

## Cómo funciona la consulta

Igual que en una consulta real, se sigue una historia clínica:

1. **Datos básicos:** nombre, edad y sexo.
2. **Motivo de consulta:** fiebre, tos, dolor de estómago, dolor de cabeza, dolor de garganta o cansancio (se pueden elegir varios).
3. **Detalles del síntoma:** desde cuándo, intensidad de 1 a 10 y si empezó de golpe.
4. **Antecedentes:** alergias, medicamentos y enfermedades previas.
5. **Hábitos:** si fuma, ejercicio y horas de sueño.
6. **Preguntas de síntomas:** árbol de decisiones del primer motivo elegido (sí / no).
7. **Resultado:** posible enfermedad, otras posibilidades, escala *cuidarte en casa / médico de familia / urgencias*, señales de alarma, razones, cuidados y resumen.

### Cómo se decide la recomendación

El árbol da un diagnóstico con un nivel base (0 casa, 1 médico de familia, 2 urgencias). Después `consulta.py` lo ajusta con lo que dijo la persona: duración, intensidad, inicio brusco, edad (menores de 5 y mayores de 64), enfermedades previas, tabaquismo y combinación de síntomas (por ejemplo, fiebre más otros síntomas con intensidad alta se parece más a una gripe).

## API

| Método | Ruta | Descripción |
| ------ | ---- | ----------- |
| GET | `/api/motivos` | Lista de motivos de consulta |
| POST | `/api/pregunta` | Recibe `{"motivo": "fiebre", "respuestas": ["si"]}` y devuelve la siguiente pregunta, o `{"tipo": "fin"}` |
| POST | `/api/consulta` | Recibe `{"perfil": {...}, "respuestas": [...]}` y devuelve el resultado |

El servidor no guarda sesión (API sin estado): el cliente envía en cada petición todas las respuestas, y el servidor las repite desde la raíz del árbol para validarlas.

Ejemplo de `perfil`:

```json
{
  "nombre": "Ana", "edad": 30, "sexo": "femenino",
  "motivos": ["fiebre", "tos"], "duracion": "4-7", "intensidad": 7,
  "brusco": false, "alergias": false, "medicamentos": false, "previas": true,
  "fuma": "no", "ejercicio": "poco", "sueno": "normal"
}
```

Prueba con curl:

```bash
curl http://localhost:5000/api/motivos
curl -X POST http://localhost:5000/api/pregunta \
  -H "Content-Type: application/json" \
  -d '{"motivo": "fiebre", "respuestas": []}'
```

Códigos de respuesta: `200` correcto, `400` petición inválida (JSON mal formado, campo fuera de rango, respuestas que no corresponden al árbol).

## Cómo agregar enfermedades

En `arbol.py`:

1. Agrega el diagnóstico en `DIAGNOSTICOS` (nombre, descripción, `nivel` 0, 1 o 2, otras posibilidades, cuidados y señales de alarma).
2. Conéctalo a una hoja de un árbol: `"h_nuevo": _h("clave_del_diagnostico")`.
3. Apunta a esa hoja desde una pregunta: `_p("¿...?", "h_nuevo", "otro_nodo")`.

Para un motivo nuevo, agrégalo en `MOTIVOS`, `INICIO` y `ARBOLES`.

## Conceptos de redes que demuestra

- Modelo cliente-servidor
- Protocolo HTTP: métodos GET y POST, códigos de estado
- Intercambio de datos en JSON
- API REST sin estado
- Validación de datos en el servidor (el cliente no es de confianza)
