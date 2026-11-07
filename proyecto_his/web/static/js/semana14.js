document.addEventListener("DOMContentLoaded", () => {

    const formConsulta =
        document.getElementById("formSemana14Consulta");

    const resultadoConsulta =
        document.getElementById("resultadoSemana14Consulta");

    const formOracion =
        document.getElementById("formSemana14Oracion");

    const resultadoOracion =
        document.getElementById("resultadoSemana14Oracion");

    const btnRed =
        document.getElementById("btnSemana14Red");

    const resultadoRed =
        document.getElementById("resultadoSemana14Red");


    // ======================================================
    // CONTROL DINÁMICO DE CAMPOS
    // ======================================================

    const tipoConsulta =
        document.getElementById("semana14Tipo");

    const campoOrigen =
        document.getElementById("semana14Origen");

    const campoRelacion =
        document.getElementById("semana14Relacion");

    const campoDestino =
        document.getElementById("semana14Destino");


    function obtenerGrupo(elemento) {

        if (!elemento) {
            return null;
        }

        return elemento.closest(
            ".form-group"
        );
    }


    function actualizarCamposSemana14() {

        if (!tipoConsulta) {
            return;
        }


        const tipo =
            tipoConsulta.value;

        const grupoOrigen =
            obtenerGrupo(
                campoOrigen
            );

        const grupoRelacion =
            obtenerGrupo(
                campoRelacion
            );

        const grupoDestino =
            obtenerGrupo(
                campoDestino
            );


        if (grupoOrigen) {
            grupoOrigen.style.display = "";
        }

        if (grupoRelacion) {
            grupoRelacion.style.display = "";
        }

        if (grupoDestino) {
            grupoDestino.style.display = "";
        }


        if (tipo === "relacion") {

            if (grupoDestino) {
                grupoDestino.style.display = "none";
            }


        } else if (tipo === "es_un") {

            if (grupoDestino) {
                grupoDestino.style.display = "none";
            }


        } else if (tipo === "herencia") {

            if (grupoDestino) {
                grupoDestino.style.display = "none";
            }


        } else if (tipo === "camino") {

            if (grupoRelacion) {
                grupoRelacion.style.display = "none";
            }
        }
    }


    if (tipoConsulta) {

        tipoConsulta.addEventListener(
            "change",
            actualizarCamposSemana14
        );

        actualizarCamposSemana14();
    }



    // ======================================================
    // CONSULTA SEMÁNTICA
    // ======================================================

    if (formConsulta) {

        formConsulta.addEventListener(
            "submit",
            async (evento) => {

                evento.preventDefault();

                const tipo =
                    document.getElementById(
                        "semana14Tipo"
                    ).value;

                const origen =
                    document.getElementById(
                        "semana14Origen"
                    ).value.trim();

                const relacion =
                    document.getElementById(
                        "semana14Relacion"
                    ).value.trim();

                const destino =
                    document.getElementById(
                        "semana14Destino"
                    ).value.trim();


                let datos = {
                    tipo: tipo
                };


                if (tipo === "relacion") {

                    datos.sujeto = origen;
                    datos.relacion = relacion;

                } else if (tipo === "es_un") {

                    datos.origen = origen;
                    datos.categoria = relacion;

                } else if (tipo === "herencia") {

                    datos.concepto = origen;
                    datos.relacion = relacion;

                } else if (tipo === "camino") {

                    datos.origen = origen;
                    datos.destino = destino;
                }


                resultadoConsulta.classList.remove(
                    "hidden"
                );

                resultadoConsulta.innerHTML =
                    "<p>Consultando red...</p>";


                try {

                    const respuesta = await fetch(
                        "/api/semana14/consultar",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify(datos)
                        }
                    );


                    const data = await respuesta.json();


                    if (!respuesta.ok || !data.success) {

                        throw new Error(
                            data.error
                            ||
                            "No fue posible realizar la consulta."
                        );
                    }


                    let contenido = "";


                    if (tipo === "camino") {

                        const pasos =
                            data.resultado || [];


                        if (pasos.length === 0) {

                            contenido =
                                "<p>No se encontró un camino.</p>";

                        } else {

                            contenido = `
                                <h3>Camino encontrado</h3>
                                <ul>
                                    ${pasos.map(
                                        paso => `
                                            <li>
                                                <strong>
                                                    ${paso.desde}
                                                </strong>
                                                →
                                                ${paso.relacion}
                                                →
                                                <strong>
                                                    ${paso.hasta}
                                                </strong>
                                            </li>
                                        `
                                    ).join("")}
                                </ul>
                            `;
                        }

                    } else {

                        const valor =
                            data.resultado;


                        contenido = `
                            <h3>Resultado</h3>

                            <p>
                                ${
                                    Array.isArray(valor)
                                    ? valor.join(", ")
                                    : String(valor)
                                }
                            </p>
                        `;
                    }


                    resultadoConsulta.innerHTML =
                        contenido;


                } catch (error) {

                    resultadoConsulta.innerHTML = `
                        <p>
                            <strong>Error:</strong>
                            ${error.message}
                        </p>
                    `;
                }

            }
        );
    }


    // ======================================================
    // ORACIÓN A TRIPLE
    // ======================================================

    if (formOracion) {

        formOracion.addEventListener(
            "submit",
            async (evento) => {

                evento.preventDefault();


                const oracion =
                    document.getElementById(
                        "semana14Oracion"
                    ).value.trim();


                resultadoOracion.classList.remove(
                    "hidden"
                );

                resultadoOracion.innerHTML =
                    "<p>Interpretando oración...</p>";


                try {

                    const respuesta = await fetch(
                        "/api/semana14/oracion",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({
                                oracion: oracion
                            })
                        }
                    );


                    const data = await respuesta.json();


                    if (!respuesta.ok || !data.success) {

                        throw new Error(
                            data.error
                            ||
                            "No fue posible interpretar la oración."
                        );
                    }


                    const r = data.resultado;


                    resultadoOracion.innerHTML = `

                        <h3>
                            Triple semántico
                        </h3>


                        <p>
                            <strong>Sujeto:</strong>
                            ${r.sujeto}
                        </p>


                        <p>
                            <strong>Relación:</strong>
                            ${r.relacion}
                        </p>


                        <p>
                            <strong>Objeto:</strong>
                            ${r.objeto}
                        </p>


                        <p>
                            <strong>Triple:</strong>
                        </p>


                        <code>
                            (${r.triple.join(", ")})
                        </code>
                    `;


                } catch (error) {

                    resultadoOracion.innerHTML = `
                        <p>
                            <strong>Error:</strong>
                            ${error.message}
                        </p>
                    `;
                }

            }
        );
    }


    // ======================================================
    // MOSTRAR RED COMPLETA
    // ======================================================

    if (btnRed) {

        btnRed.addEventListener(
            "click",
            async () => {

                resultadoRed.classList.remove(
                    "hidden"
                );

                resultadoRed.innerHTML =
                    "<p>Cargando red...</p>";


                try {

                    const respuesta = await fetch(
                        "/api/semana14/red"
                    );


                    const data = await respuesta.json();


                    if (!respuesta.ok || !data.success) {

                        throw new Error(
                            data.error
                            ||
                            "No fue posible cargar la red."
                        );
                    }


                    const r = data.resultado;


                    const triples = (
                        r.triples
                        ||
                        []
                    )
                    .map(
                        triple => `
                            <li>
                                <code>
                                    (${triple.join(", ")})
                                </code>
                            </li>
                        `
                    )
                    .join("");


                    resultadoRed.innerHTML = `

                        <h3>
                            Red semántica HIS_IA
                        </h3>

                        <p>
                            <strong>
                                Total de triples:
                            </strong>
                            ${r.total_triples}
                        </p>

                        <ul>
                            ${triples}
                        </ul>
                    `;


                } catch (error) {

                    resultadoRed.innerHTML = `
                        <p>
                            <strong>Error:</strong>
                            ${error.message}
                        </p>
                    `;
                }

            }
        );
    }

});
