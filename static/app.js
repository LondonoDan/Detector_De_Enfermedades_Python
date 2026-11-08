(function () {
  "use strict";

  const app = document.getElementById("app");

  const ETAPAS = [
    { titulo: "Datos básicos", icono: "usuario" },
    { titulo: "Motivo de consulta", icono: "estetoscopio" },
    { titulo: "Detalles del síntoma", icono: "reloj" },
    { titulo: "Antecedentes", icono: "notas" },
    { titulo: "Hábitos", icono: "corazon" },
    { titulo: "Preguntas de síntomas", icono: "ayuda" },
  ];

  const SI_NO = [["no", "No"], ["si", "Sí"]];
  const OPC = {
    sexo: [["femenino", "Femenino"], ["masculino", "Masculino"], ["no_dice", "Prefiero no decir"]],
    dur: [["hoy", "Hoy"], ["1-3", "1–3 días"], ["4-7", "4–7 días"], ["mas_semana", "+1 semana"]],
    brusco: SI_NO,
    alerg: SI_NO,
    meds: SI_NO,
    prev: SI_NO,
    fuma: [["no", "No"], ["a_veces", "A veces"], ["si", "Sí"]],
    ejer: [["nunca", "Nunca"], ["poco", "1–2 veces"], ["mucho", "3 o más"]],
    sueno: [["poco", "Menos de 6 h"], ["normal", "6–8 h"], ["mucho", "Más de 8 h"]],
  };

  const ICONOS = {
    corazon: '<polyline points="3 12 7 12 9.5 6 14 18 16.5 12 21 12"/>',
    atras: '<path d="M19 12H5"/><path d="M11 6l-6 6 6 6"/>',
    adelante: '<path d="M5 12h14"/><path d="M13 6l6 6-6 6"/>',
    si: '<polyline points="5 12.5 10 17.5 19 7.5"/>',
    no: '<path d="M6 6l12 12"/><path d="M18 6L6 18"/>',
    ayuda:
      '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.7.4-1 1-1 1.7"/><path d="M12 17h.01"/>',
    alerta: '<path d="M12 4L2.5 20h19z"/><path d="M12 10v4"/><path d="M12 17h.01"/>',
    ok: '<circle cx="12" cy="12" r="9"/><polyline points="8 12.5 11 15.5 16 9"/>',
    reiniciar:
      '<path d="M4 12a8 8 0 0 1 14-5l2 2"/><path d="M20 4v5h-5"/><path d="M20 12a8 8 0 0 1-14 5l-2-2"/><path d="M4 20v-5h5"/>',
    usuario: '<circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 4-6 8-6s8 2 8 6"/>',
    estetoscopio:
      '<path d="M6 4H5a2 2 0 0 0-2 2v3.5a5.5 5.5 0 0 0 11 0V6a2 2 0 0 0-2-2h-1"/><path d="M8 15a6 6 0 0 0 12 0v-3"/><path d="M11 3v2"/><path d="M6 3v2"/><circle cx="20" cy="10" r="2"/>',
    reloj: '<circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 15 14"/>',
    notas:
      '<path d="M14 3v4a1 1 0 0 0 1 1h4"/><path d="M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"/><path d="M9 13h6"/><path d="M9 17h4"/>',
    casa: '<path d="M3 11l9-8 9 8"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>',
    urgencias: '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M12 8v8"/><path d="M8 12h8"/>',
  };

  const NIVELES = ["leve", "alerta", "peligro"];

  let catalogo = null;

  function nuevoEstado() {
    return {
      st: 0,
      nombre: "",
      edad: "",
      sexo: "",
      motivos: [],
      dur: "1-3",
      int: 5,
      brusco: "no",
      alerg: "no",
      meds: "no",
      prev: "no",
      fuma: "no",
      ejer: "poco",
      sueno: "normal",
      nodo: null,
      nodos: [],
      resp: [],
      res: null,
      err: {},
      error: null,
      ocupado: false,
    };
  }

  let S = nuevoEstado();

  function icono(nombre) {
    return '<svg class="ico" viewBox="0 0 24 24" aria-hidden="true">' + ICONOS[nombre] + "</svg>";
  }

  function esc(texto) {
    return String(texto).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function etiqueta(clave, valor) {
    const par = OPC[clave].find(function (p) {
      return p[0] === valor;
    });
    return par ? par[1] : valor;
  }

  function nombreMotivo(id) {
    const m = catalogo && catalogo.find(function (x) {
      return x.id === id;
    });
    return m ? m.nombre : id;
  }

  async function pedir(url, cuerpo) {
    const opciones =
      cuerpo === undefined
        ? {}
        : {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(cuerpo),
          };
    const respuesta = await fetch(url, opciones);
    if (!respuesta.ok) throw new Error("HTTP " + respuesta.status);
    return respuesta.json();
  }

  /* ---------- Piezas de interfaz ---------- */

  function aviso() {
    return (
      '<p class="aviso">' + icono("alerta") + "Proyecto académico. No reemplaza a un médico.</p>"
    );
  }

  function segmentado(clave) {
    let h = '<div class="seg" role="group">';
    OPC[clave].forEach(function (par) {
      const on = S[clave] === par[0];
      h +=
        '<button type="button" data-k="' + clave + '" data-v="' + par[0] + '" aria-pressed="' + on + '"' +
        (on ? ' class="activo"' : "") + ">" + par[1] + "</button>";
    });
    return h + "</div>";
  }

  function cabecera() {
    const e = ETAPAS[S.st];
    let h = '<div class="cabecera">';
    h += S.st > 0
      ? '<button type="button" class="btn-icono" data-act="atras" aria-label="Volver">' + icono("atras") + "</button>"
      : '<span class="espacio"></span>';
    h +=
      '<div class="cabecera-texto"><p class="etapa-n">Etapa ' + (S.st + 1) + " de 6</p>" +
      '<p class="etapa-t">' + e.titulo + "</p></div>" +
      '<div class="icono-etapa">' + icono(e.icono) + "</div></div>";
    h += '<div class="segmentos">';
    for (let i = 0; i < 6; i++) h += '<div class="' + (i <= S.st ? "on" : "") + '"></div>';
    return h + "</div>";
  }

  function sub(texto) {
    return '<p class="sub">' + texto + "</p>";
  }

  /* ---------- Etapas ---------- */

  function etapa0() {
    return (
      sub("Para empezar, cuéntanos quién eres.") +
      '<label class="lb" for="nombre">Nombre</label>' +
      '<input id="nombre" type="text" maxlength="30" placeholder="Tu nombre" autocomplete="off" value="' + esc(S.nombre) + '">' +
      '<p class="error-campo" id="er-nombre">' + esc(S.err.nombre || "") + "</p>" +
      '<label class="lb" for="edad">Edad</label>' +
      '<input id="edad" type="number" min="1" max="110" inputmode="numeric" placeholder="Años" value="' + esc(S.edad) + '">' +
      '<p class="error-campo" id="er-edad">' + esc(S.err.edad || "") + "</p>" +
      '<span class="lb">Sexo</span>' +
      segmentado("sexo") +
      '<p class="error-campo" id="er-sexo">' + esc(S.err.sexo || "") + "</p>"
    );
  }

  function etapa1() {
    let h = sub("Hola, " + esc(S.nombre.trim()) + ". ¿Qué te trae por aquí? Puedes elegir varios.");
    h += '<div class="motivos" role="group">';
    catalogo.forEach(function (m) {
      const on = S.motivos.indexOf(m.id) > -1;
      h +=
        '<button type="button" data-m="' + m.id + '" aria-pressed="' + on + '"' + (on ? ' class="activo"' : "") + ">" +
        (on ? icono("si") : "") + esc(m.nombre) + "</button>";
    });
    return h + '</div><p class="error-campo" id="er-motivos">' + esc(S.err.motivos || "") + "</p>";
  }

  function etapa2() {
    return (
      sub("Cuéntanos más sobre lo que sientes.") +
      '<span class="lb">¿Desde cuándo lo sientes?</span>' + segmentado("dur") +
      '<span class="lb" style="margin-top:20px">¿Qué tan fuerte es? <strong id="intv">' + S.int + "</strong> de 10</span>" +
      '<input id="int" type="range" min="1" max="10" step="1" value="' + S.int + '">' +
      '<div class="escala-rango"><span>Leve</span><span>Muy fuerte</span></div>' +
      '<span class="lb" style="margin-top:20px">¿Empezó de golpe?</span>' + segmentado("brusco")
    );
  }

  function etapa3() {
    return (
      sub("Esto ayuda a que la orientación sea más segura.") +
      '<span class="lb">¿Tienes alergias a medicamentos?</span>' + segmentado("alerg") +
      '<span class="lb" style="margin-top:18px">¿Tomas algún medicamento actualmente?</span>' + segmentado("meds") +
      '<span class="lb" style="margin-top:18px">¿Tienes enfermedades como asma, diabetes o hipertensión?</span>' + segmentado("prev")
    );
  }

  function etapa4() {
    return (
      sub("Tu estilo de vida también cuenta.") +
      '<span class="lb">¿Fumas?</span>' + segmentado("fuma") +
      '<span class="lb" style="margin-top:18px">¿Haces ejercicio?</span>' + segmentado("ejer") +
      '<span class="lb" style="margin-top:18px">¿Cuánto duermes por noche?</span>' + segmentado("sueno")
    );
  }

  function etapa5() {
    return (
      sub("Unas preguntas según lo que elegiste: " + esc(nombreMotivo(S.motivos[0]).toLowerCase()) + ".") +
      '<p class="pregunta-n">Pregunta ' + (S.resp.length + 1) + "</p>" +
      '<p class="pregunta">' + esc(S.nodo.pregunta) + "</p>" +
      '<div class="opciones">' +
      '<button type="button" class="btn opcion" data-act="si">' + icono("si") + "Sí</button>" +
      '<button type="button" class="btn opcion" data-act="no">' + icono("no") + "No</button>" +
      "</div>"
    );
  }

  function pantallaFormulario() {
    const cuerpo = [etapa0, etapa1, etapa2, etapa3, etapa4, etapa5][S.st]();
    let h = '<div class="pantalla">' + cabecera() + cuerpo;
    if (S.st < 5) {
      h +=
        '<button type="button" class="btn btn-primario siguiente" data-act="siguiente">' +
        (S.st === 4 ? "Empezar preguntas" : "Continuar") + icono("adelante") + "</button>";
    }
    return h + aviso() + "</div>";
  }

  function fila(a, b) {
    return '<div class="fila"><span>' + a + "</span><span>" + b + "</span></div>";
  }

  function pantallaResultado() {
    const r = S.res;
    const nivel = r.triaje.nivel;
    const clase = NIVELES[nivel];

    const escala = [
      { icono: "casa", texto: "Cuidarte en casa" },
      { icono: "estetoscopio", texto: "Médico de familia" },
      { icono: "urgencias", texto: "Urgencias" },
    ];

    let h = '<div class="pantalla">';
    h +=
      '<p class="encabezado-resultado">Resultado orientativo para <strong>' + esc(S.nombre.trim()) + "</strong></p>";
    h +=
      '<div class="resultado ' + clase + '">' + icono(nivel === 0 ? "ok" : "alerta") +
      '<p class="etiqueta-res">Posible diagnóstico</p>' +
      '<p class="nombre">' + esc(r.enfermedad.nombre) + "</p>" +
      '<p class="detalle">' + esc(r.enfermedad.descripcion) + "</p></div>";
    h += '<p class="otras">También podría ser: ' + r.otras.map(esc).join(" · ") + "</p>";

    h += '<p class="titulo-seccion">¿Qué hacer ahora?</p><div class="escala">';
    escala.forEach(function (item, i) {
      h +=
        '<div class="escala-item' + (i === nivel ? " activo " + clase : "") + '"' +
        (i === nivel ? ' aria-current="true"' : "") + ">" + icono(item.icono) + item.texto + "</div>";
    });
    h += "</div>";
    h +=
      '<div class="recomendacion"><p class="titulo">' + esc(r.triaje.titulo) + "</p><p>" + esc(r.triaje.texto) + "</p></div>";

    h += '<div class="alarmas"><p>Ve a urgencias de inmediato si aparece:</p><ul>';
    r.alarma.forEach(function (a) {
      h += "<li>" + icono("alerta") + "<span>" + esc(a) + "</span></li>";
    });
    h += "</ul></div>";

    h += "<details><summary>Por qué llegamos a esto</summary><div class=\"contenido\"><ul>";
    r.razones.forEach(function (x) {
      h += "<li>" + esc(x) + "</li>";
    });
    h += "</ul></div></details>";

    h += "<details><summary>Cuidados mientras tanto</summary><div class=\"contenido\"><ul>";
    r.cuidados.forEach(function (x) {
      h += "<li>" + esc(x) + "</li>";
    });
    h += "</ul></div></details>";

    const motivos = S.motivos.map(function (m) {
      return nombreMotivo(m).toLowerCase();
    }).join(", ");
    h += "<details><summary>Resumen de tu consulta</summary><div class=\"contenido\">";
    h += fila("Paciente", esc(S.nombre.trim()) + ", " + esc(S.edad) + " años, " + etiqueta("sexo", S.sexo).toLowerCase());
    h += fila("Motivo", esc(motivos));
    h += fila("Evolución", etiqueta("dur", S.dur).toLowerCase() + ", intensidad " + S.int + "/10" + (S.brusco === "si" ? ", inicio brusco" : ""));
    h += fila("Alergias", etiqueta("alerg", S.alerg).toLowerCase());
    h += fila("Medicamentos", etiqueta("meds", S.meds).toLowerCase());
    h += fila("Enfermedades previas", etiqueta("prev", S.prev).toLowerCase());
    h += fila("Fuma", etiqueta("fuma", S.fuma).toLowerCase());
    h += fila("Ejercicio", etiqueta("ejer", S.ejer).toLowerCase());
    h += fila("Sueño", etiqueta("sueno", S.sueno).toLowerCase());
    h += "</div></details>";

    h +=
      '<div class="acciones">' +
      '<button type="button" class="btn" data-act="atras">Atrás</button>' +
      '<button type="button" class="btn btn-primario" data-act="nueva">' + icono("reiniciar") + "Nueva consulta</button></div>";
    return h + aviso() + "</div>";
  }

  function pantallaError() {
    return (
      '<div class="pantalla pantalla-error">' +
      '<div class="icono-grande">' + icono("alerta") + "</div>" +
      '<p class="etapa-t">Sin conexión</p>' +
      '<p class="mensaje-error">No se pudo conectar con el servidor. Revisa que Flask esté corriendo.</p>' +
      '<button type="button" class="btn btn-primario" data-act="reintentar">' + icono("reiniciar") + "Reintentar</button>" +
      '<button type="button" class="btn" data-act="nueva">Empezar de nuevo</button>' +
      aviso() +
      "</div>"
    );
  }

  function render() {
    if (S.error) app.innerHTML = pantallaError();
    else if (S.st === 6) app.innerHTML = pantallaResultado();
    else app.innerHTML = pantallaFormulario();
    const campo = document.getElementById("nombre");
    if (campo && !campo.value) campo.focus();
  }

  /* ---------- Comunicación con el servidor ---------- */

  function mostrarError(reintento) {
    S.error = { reintento: reintento };
    render();
  }

  async function cargarCatalogo() {
    if (catalogo) return;
    const datos = await pedir("/api/motivos");
    catalogo = datos.motivos;
  }

  function armarPerfil() {
    return {
      nombre: S.nombre.trim(),
      edad: parseInt(S.edad, 10),
      sexo: S.sexo,
      motivos: S.motivos,
      duracion: S.dur,
      intensidad: S.int,
      brusco: S.brusco === "si",
      alergias: S.alerg === "si",
      medicamentos: S.meds === "si",
      previas: S.prev === "si",
      fuma: S.fuma,
      ejercicio: S.ejer,
      sueno: S.sueno,
    };
  }

  async function obtenerResultado() {
    try {
      S.res = await pedir("/api/consulta", { perfil: armarPerfil(), respuestas: S.resp });
    } catch (e) {
      return mostrarError(obtenerResultado);
    }
    S.st = 6;
    render();
  }

  async function cargarPregunta() {
    let datos;
    try {
      datos = await pedir("/api/pregunta", { motivo: S.motivos[0], respuestas: S.resp });
    } catch (e) {
      return mostrarError(cargarPregunta);
    }
    if (datos.tipo === "fin") return obtenerResultado();
    S.nodo = datos;
    S.st = 5;
    render();
  }

  /* ---------- Acciones ---------- */

  async function siguiente() {
    if (S.ocupado) return;

    if (S.st === 0) {
      const errores = {};
      const edad = parseInt(S.edad, 10);
      if (!S.nombre.trim()) errores.nombre = "Escribe tu nombre";
      if (!(edad >= 1 && edad <= 110)) errores.edad = "Escribe una edad entre 1 y 110";
      if (!S.sexo) errores.sexo = "Elige una opción";
      if (Object.keys(errores).length) {
        S.err = errores;
        render();
        return;
      }
      S.ocupado = true;
      try {
        await cargarCatalogo();
      } catch (e) {
        S.ocupado = false;
        return mostrarError(siguiente);
      }
      S.ocupado = false;
    }

    if (S.st === 1 && !S.motivos.length) {
      S.err = { motivos: "Elige al menos un motivo" };
      render();
      return;
    }

    S.err = {};

    if (S.st === 4) {
      S.resp = [];
      S.nodos = [];
      S.ocupado = true;
      try {
        await cargarPregunta();
      } finally {
        S.ocupado = false;
      }
      return;
    }

    S.st++;
    render();
  }

  async function responder(valor) {
    if (S.ocupado || !S.nodo) return;
    S.ocupado = true;
    S.nodos.push(S.nodo);
    S.resp.push(valor);
    try {
      await cargarPregunta();
    } finally {
      S.ocupado = false;
    }
  }

  function atras() {
    if (S.st === 6 || (S.st === 5 && S.resp.length > 0)) {
      S.resp.pop();
      S.nodo = S.nodos.pop();
      S.st = 5;
    } else if (S.st > 0) {
      S.st--;
    }
    S.err = {};
    render();
  }

  function nueva() {
    S = nuevoEstado();
    render();
  }

  function reintentar() {
    const accion = S.error && S.error.reintento;
    S.error = null;
    if (accion) accion();
    else render();
  }

  /* ---------- Eventos ---------- */

  app.addEventListener("click", function (e) {
    const b = e.target.closest("button");
    if (!b || !app.contains(b)) return;

    const k = b.getAttribute("data-k");
    const m = b.getAttribute("data-m");
    const a = b.getAttribute("data-act");

    if (k) {
      S[k] = b.getAttribute("data-v");
      S.err = {};
      render();
    } else if (m) {
      const i = S.motivos.indexOf(m);
      if (i > -1) S.motivos.splice(i, 1);
      else S.motivos.push(m);
      S.err = {};
      render();
    } else if (a === "siguiente") siguiente();
    else if (a === "atras") atras();
    else if (a === "si") responder("si");
    else if (a === "no") responder("no");
    else if (a === "nueva") nueva();
    else if (a === "reintentar") reintentar();
  });

  app.addEventListener("input", function (e) {
    const id = e.target.id;
    if (id === "nombre") S.nombre = e.target.value;
    else if (id === "edad") S.edad = e.target.value;
    else if (id === "int") {
      S.int = parseInt(e.target.value, 10);
      document.getElementById("intv").textContent = S.int;
    }
    const er = document.getElementById("er-" + id);
    if (er) er.textContent = "";
  });

  app.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && e.target.tagName === "INPUT" && S.st === 0) siguiente();
  });

  render();
})();
