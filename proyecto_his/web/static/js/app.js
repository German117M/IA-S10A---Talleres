// ==========================================================
// HIS_IA v1.3
// FRONTEND
// ==========================================================


// ==========================================================
// NAVEGACIÓN
// ==========================================================

function mostrarSeccion(id, boton = null) {

    document
        .querySelectorAll(".section")
        .forEach(seccion => {
            seccion.classList.remove(
                "active"
            );
        });


    const destino =
        document.getElementById(id);


    if (destino) {
        destino.classList.add(
            "active"
        );
    }


    document
        .querySelectorAll(".menu-item")
        .forEach(item => {
            item.classList.remove(
                "active"
            );
        });


    if (boton) {

        boton.classList.add(
            "active"
        );

    } else {

        const botonCorrespondiente =
            document.querySelector(
                `.menu-item[data-section="${id}"]`
            );


        if (botonCorrespondiente) {
            botonCorrespondiente.classList.add(
                "active"
            );
        }
    }


    window.scrollTo({
        top: 0,
        behavior: "smooth"
    });
}



function abrirDesdeCard(id) {
    mostrarSeccion(id);
}



// ==========================================================
// PROTECCIÓN HTML
// ==========================================================

function escaparHTML(valor) {

    return String(
        valor ?? ""
    )
        .replaceAll(
            "&",
            "&amp;"
        )
        .replaceAll(
            "<",
            "&lt;"
        )
        .replaceAll(
            ">",
            "&gt;"
        )
        .replaceAll(
            '"',
            "&quot;"
        )
        .replaceAll(
            "'",
            "&#039;"
        );
}



// ==========================================================
// PETICIONES API
// ==========================================================

async function enviarAPI(
    url,
    datos
) {

    const respuesta =
        await fetch(
            url,
            {
                method:
                    "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify(
                        datos
                    )
            }
        );


    let resultado;


    try {

        resultado =
            await respuesta.json();

    }

    catch {

        throw new Error(
            "El servidor devolvió una respuesta no válida."
        );
    }


    if (!respuesta.ok) {

        throw new Error(
            resultado.error
            || "Ocurrió un error al procesar la solicitud."
        );
    }


    return resultado;
}



function mostrarError(
    contenedor,
    error
) {

    contenedor.classList.remove(
        "hidden"
    );


    contenedor.innerHTML = `

        <div class="error-message">

            <strong>
                Error:
            </strong>

            ${escaparHTML(
                error.message
            )}

        </div>
    `;
}



// ==========================================================
// SEMANA 3
// ==========================================================

async function analizarInformacion() {

    const texto =
        document
            .getElementById(
                "textoAnalisis"
            )
            .value
            .trim();


    const contenedor =
        document.getElementById(
            "resultadoAnalisis"
        );


    if (!texto) {

        mostrarError(
            contenedor,
            new Error(
                "Debe ingresar información para analizar."
            )
        );

        return;
    }


    try {

        const resultado =
            await enviarAPI(
                "/api/analizar",
                {
                    texto:
                        texto
                }
            );


        const categorias =
            Array.isArray(
                resultado.categorias
            )
            && resultado.categorias.length

                ? resultado.categorias
                    .map(
                        escaparHTML
                    )
                    .join(
                        ", "
                    )

                : "No se identificaron categorías";


        contenedor.classList.remove(
            "hidden"
        );


        contenedor.innerHTML = `

            <div class="result-header">

                <span>
                    Resultado
                </span>

                <h3>
                    Análisis de información
                </h3>

            </div>


            <div class="result-row">

                <span>
                    Categoría principal
                </span>

                <strong>
                    ${escaparHTML(
                        resultado.principal
                    )}
                </strong>

            </div>


            <div class="result-row">

                <span>
                    Categorías detectadas
                </span>

                <strong>
                    ${categorias}
                </strong>

            </div>
        `;

    }

    catch (error) {

        mostrarError(
            contenedor,
            error
        );
    }
}



// ==========================================================
// SEMANA 2
// ==========================================================

async function evaluarPrioridad() {

    const contenedor =
        document.getElementById(
            "resultadoPrioridad"
        );


    const datos = {

        edad:
            Number(
                document
                    .getElementById(
                        "edad"
                    )
                    .value
            ),

        documentos_pendientes:
            Number(
                document
                    .getElementById(
                        "documentos"
                    )
                    .value
            ),

        resultados_pendientes:
            Number(
                document
                    .getElementById(
                        "resultados"
                    )
                    .value
            ),

        imagenes_pendientes:
            Number(
                document
                    .getElementById(
                        "imagenes"
                    )
                    .value
            )
    };


    if (
        Object
            .values(
                datos
            )
            .some(
                valor =>
                    Number.isNaN(
                        valor
                    )
                    || valor < 0
            )
    ) {

        mostrarError(
            contenedor,
            new Error(
                "Ingrese valores numéricos válidos."
            )
        );

        return;
    }


    try {

        const resultado =
            await enviarAPI(
                "/api/prioridad",
                datos
            );


        contenedor.classList.remove(
            "hidden"
        );


        contenedor.innerHTML = `

            <div class="result-header">

                <span>
                    Machine Learning
                </span>

                <h3>
                    Resultado de prioridad
                </h3>

            </div>


            <div class="priority-result">

                ${escaparHTML(
                    resultado.prioridad
                )}

            </div>
        `;

    }

    catch (error) {

        mostrarError(
            contenedor,
            error
        );
    }
}



// ==========================================================
// SEMANA 4
// A*
// ==========================================================

async function organizarRevision() {

    const seleccionados = [

        ...document.querySelectorAll(
            'input[name="revision"]:checked'
        )

    ].map(
        elemento =>
            elemento.value
    );


    const contenedor =
        document.getElementById(
            "resultadoRevision"
        );


    if (!seleccionados.length) {

        mostrarError(
            contenedor,
            new Error(
                "Seleccione al menos un elemento."
            )
        );

        return;
    }


    try {

        const resultado =
            await enviarAPI(
                "/api/revision",
                {
                    elementos:
                        seleccionados
                }
            );


        const ordenHTML =
            resultado.orden
                .map(
                    elemento => `
                        <li>
                            ${escaparHTML(
                                elemento
                            )}
                        </li>
                    `
                )
                .join("");


        contenedor.classList.remove(
            "hidden"
        );


        contenedor.innerHTML = `

            <div class="result-header">

                <span>
                    Algoritmo A*
                </span>

                <h3>
                    Orden de revisión
                </h3>

            </div>


            <ol class="result-list">
                ${ordenHTML}
            </ol>


            <div class="result-row">

                <span>
                    Costo total estimado
                </span>

                <strong>
                    ${escaparHTML(
                        resultado.costo_total
                    )}
                </strong>

            </div>
        `;

    }

    catch (error) {

        mostrarError(
            contenedor,
            error
        );
    }
}



// ==========================================================
// SEMANA 4
// MINIMAX
// ==========================================================

function obtenerPaciente(
    numero
) {

    return {

        motivo_consulta:
            document
                .getElementById(
                    `p${numero}Motivo`
                )
                .value
                .trim(),

        dolor_intenso:
            document
                .getElementById(
                    `p${numero}Dolor`
                )
                .checked,

        dificultad_respiratoria:
            document
                .getElementById(
                    `p${numero}Respiracion`
                )
                .checked,

        sangrado_activo:
            document
                .getElementById(
                    `p${numero}Sangrado`
                )
                .checked,

        perdida_movilidad:
            document
                .getElementById(
                    `p${numero}Movilidad`
                )
                .checked,

        alteracion_conciencia:
            document
                .getElementById(
                    `p${numero}Conciencia`
                )
                .checked,

        trauma:
            document
                .getElementById(
                    `p${numero}Trauma`
                )
                .checked,

        requiere_soporte:
            document
                .getElementById(
                    `p${numero}Soporte`
                )
                .checked
    };
}



async function priorizarPacientes() {

    const paciente1 =
        obtenerPaciente(
            1
        );


    const paciente2 =
        obtenerPaciente(
            2
        );


    const contenedor =
        document.getElementById(
            "resultadoMinimax"
        );


    if (
        !paciente1.motivo_consulta
        || !paciente2.motivo_consulta
    ) {

        mostrarError(
            contenedor,
            new Error(
                "Ingrese el motivo de consulta de ambos pacientes."
            )
        );

        return;
    }


    try {

        const resultado =
            await enviarAPI(
                "/api/priorizar-pacientes",
                {
                    paciente1:
                        paciente1,

                    paciente2:
                        paciente2
                }
            );


        contenedor.classList.remove(
            "hidden"
        );


        contenedor.innerHTML = `

            <div class="result-header">

                <span>
                    Minimax
                </span>

                <h3>
                    Comparación de prioridad
                </h3>

            </div>


            <div class="priority-result large">

                ${escaparHTML(
                    resultado
                        .paciente_prioritario
                )}

            </div>


            <div class="comparison-grid">


                <div class="comparison-card">

                    <span class="comparison-label">
                        Paciente 1
                    </span>

                    <h4>
                        ${escaparHTML(
                            resultado
                                .paciente1
                                .motivo_consulta
                        )}
                    </h4>


                    <div class="metric">

                        <span>
                            Gravedad
                        </span>

                        <strong>
                            ${escaparHTML(
                                resultado
                                    .paciente1
                                    .gravedad
                            )}
                        </strong>

                    </div>


                    <div class="metric">

                        <span>
                            Impacto
                        </span>

                        <strong>
                            ${escaparHTML(
                                resultado
                                    .paciente1
                                    .impacto
                            )}
                        </strong>

                    </div>


                    <div class="metric highlight">

                        <span>
                            Valor Minimax
                        </span>

                        <strong>
                            ${escaparHTML(
                                resultado
                                    .paciente1
                                    .valor_minimax
                            )}
                        </strong>

                    </div>

                </div>


                <div class="comparison-card">

                    <span class="comparison-label">
                        Paciente 2
                    </span>

                    <h4>
                        ${escaparHTML(
                            resultado
                                .paciente2
                                .motivo_consulta
                        )}
                    </h4>


                    <div class="metric">

                        <span>
                            Gravedad
                        </span>

                        <strong>
                            ${escaparHTML(
                                resultado
                                    .paciente2
                                    .gravedad
                            )}
                        </strong>

                    </div>


                    <div class="metric">

                        <span>
                            Impacto
                        </span>

                        <strong>
                            ${escaparHTML(
                                resultado
                                    .paciente2
                                    .impacto
                            )}
                        </strong>

                    </div>


                    <div class="metric highlight">

                        <span>
                            Valor Minimax
                        </span>

                        <strong>
                            ${escaparHTML(
                                resultado
                                    .paciente2
                                    .valor_minimax
                            )}
                        </strong>

                    </div>

                </div>

            </div>
        `;

    }

    catch (error) {

        mostrarError(
            contenedor,
            error
        );
    }
}



// ==========================================================
// SEMANA 7
// ==========================================================

async function analizarReconocimiento() {

    const contenedor =
        document.getElementById(
            "resultadoReconocimiento"
        );


    const motivo =
        document
            .getElementById(
                "recMotivo"
            )
            .value
            .trim();


    const campoTemperatura =
        document.getElementById(
            "recTemperatura"
        );


    const campoLatidos =
        document.getElementById(
            "recLatidos"
        );


    const campoPresion =
        document.getElementById(
            "recPresion"
        );


    if (!motivo) {

        mostrarError(
            contenedor,
            new Error(
                "Ingrese el motivo de consulta."
            )
        );

        return;
    }


    if (
        campoTemperatura.value.trim()
        === ""
    ) {

        mostrarError(
            contenedor,
            new Error(
                "Ingrese la temperatura."
            )
        );

        return;
    }


    if (
        campoLatidos.value.trim()
        === ""
    ) {

        mostrarError(
            contenedor,
            new Error(
                "Ingrese los latidos."
            )
        );

        return;
    }


    if (
        campoPresion.value.trim()
        === ""
    ) {

        mostrarError(
            contenedor,
            new Error(
                "Ingrese la presión."
            )
        );

        return;
    }


    const temperatura =
        Number(
            campoTemperatura.value
        );


    const latidos =
        Number(
            campoLatidos.value
        );


    const presion =
        Number(
            campoPresion.value
        );


    const caso = {

        motivo_consulta:
            motivo,

        temperatura:
            temperatura,

        latidos:
            latidos,

        presion:
            presion
    };


    try {

        const resultado =
            await enviarAPI(
                "/api/reconocimiento",
                {
                    caso:
                        caso
                }
            );


        const numerica =
            resultado
                .representacion_numerica;


        const simbolica =
            resultado
                .representacion_simbolica;


        const automata =
            resultado
                .automata;


        const integrado =
            resultado
                .resultado_integrado;


        const referencias =
            numerica
                .referencias;


        const detallesHTML =
            integrado
                .detalles
                .map(
                    detalle => `
                        <li>
                            ${escaparHTML(
                                detalle
                            )}
                        </li>
                    `
                )
                .join("");


        contenedor.classList.remove(
            "hidden"
        );


        contenedor.innerHTML = `

            <div class="result-header">

                <span>
                    Semana 7
                </span>

                <h3>
                    Resultado del reconocimiento
                </h3>

            </div>


            <div class="case-summary">

                <span>
                    Motivo de consulta
                </span>

                <strong>
                    ${escaparHTML(
                        resultado
                            .motivo_consulta
                    )}
                </strong>

            </div>


            <div class="recognition-grid">


                <!-- NUMÉRICA -->

                <div class="recognition-card">

                    <span class="recognition-number">
                        01
                    </span>

                    <h4>
                        Representación numérica
                    </h4>

                    <p class="recognition-description">

                        Los signos se representan
                        mediante un vector numérico.

                    </p>


                    <div class="metric highlight">

                        <span>
                            Vector
                        </span>

                        <strong>
                            [
                            ${numerica.vector.join(", ")}
                            ]
                        </strong>

                    </div>


                    <div class="metric">

                        <span>
                            Temperatura
                        </span>

                        <strong>
                            ${numerica.temperatura} °C
                        </strong>

                    </div>


                    <div class="metric">

                        <span>
                            Latidos
                        </span>

                        <strong>
                            ${numerica.latidos} lpm
                        </strong>

                    </div>


                    <div class="metric">

                        <span>
                            Presión
                        </span>

                        <strong>
                            ${numerica.presion} mmHg
                        </strong>

                    </div>


                    <p class="recognition-description">
                        Rangos de referencia
                    </p>


                    <div class="metric">

                        <span>
                            Temperatura normal
                        </span>

                        <strong>
                            ${referencias.temperatura.min}
                            -
                            ${referencias.temperatura.max}
                            ${referencias.temperatura.unidad}
                        </strong>

                    </div>


                    <div class="metric">

                        <span>
                            Frecuencia cardíaca normal
                        </span>

                        <strong>
                            ${referencias.latidos.min}
                            -
                            ${referencias.latidos.max}
                            ${referencias.latidos.unidad}
                        </strong>

                    </div>


                    <div class="metric">

                        <span>
                            Presión normal
                        </span>

                        <strong>
                            ${referencias.presion.min}
                            -
                            ${referencias.presion.max}
                            ${referencias.presion.unidad}
                        </strong>

                    </div>

                </div>


                <!-- SIMBÓLICA -->

                <div class="recognition-card">

                    <span class="recognition-number">
                        02
                    </span>

                    <h4>
                        Representación simbólica
                    </h4>


                    <div class="metric">

                        <span>
                            Temperatura
                        </span>

                        <strong>
                            ${escaparHTML(
                                simbolica
                                    .hechos
                                    .temperatura
                            )}
                        </strong>

                    </div>


                    <div class="metric">

                        <span>
                            Frecuencia cardíaca
                        </span>

                        <strong>
                            ${escaparHTML(
                                simbolica
                                    .hechos
                                    .latidos
                            )}
                        </strong>

                    </div>


                    <div class="metric">

                        <span>
                            Presión arterial
                        </span>

                        <strong>
                            ${escaparHTML(
                                simbolica
                                    .hechos
                                    .presion
                            )}
                        </strong>

                    </div>

                </div>


                <!-- AUTÓMATA -->

                <div class="recognition-card">

                    <span class="recognition-number">
                        03
                    </span>

                    <h4>
                        Autómata
                    </h4>


                    <div class="metric">

                        <span>
                            Secuencia
                        </span>

                        <strong>
                            ${escaparHTML(
                                automata.secuencia
                            )}
                        </strong>

                    </div>


                    <div class="metric">

                        <span>
                            Estado final
                        </span>

                        <strong>
                            ${escaparHTML(
                                automata.estado_final
                            )}
                        </strong>

                    </div>


                    <div class="metric">

                        <span>
                            Consulta procesada
                        </span>

                        <strong>
                            ${
                                automata.aceptada
                                    ? "Sí"
                                    : "No"
                            }
                        </strong>

                    </div>


                    <div class="automata-route">

                        <span>
                            Recorrido
                        </span>

                        <p>
                            ${
                                automata
                                    .recorrido
                                    .map(
                                        escaparHTML
                                    )
                                    .join(
                                        " → "
                                    )
                            }
                        </p>

                    </div>

                </div>


                <!-- RESULTADO INTEGRADO -->

                <div class="recognition-card">

                    <span class="recognition-number">
                        04
                    </span>

                    <h4>
                        Resultado integrado
                    </h4>


                    <p class="recognition-description">

                        HIS_IA integra las tres variables
                        y genera una conclusión a partir
                        de las reglas definidas.

                    </p>


                    <div class="metric">

                        <span>
                            Variables evaluadas
                        </span>

                        <strong>
                            ${integrado.variables_evaluadas}
                        </strong>

                    </div>


                    <div class="metric">

                        <span>
                            En categoría esperada
                        </span>

                        <strong>
                            ${
                                integrado
                                    .variables_en_categoria_esperada
                            }
                        </strong>

                    </div>


                    <div class="metric highlight">

                        <span>
                            Con hallazgos
                        </span>

                        <strong>
                            ${
                                integrado
                                    .variables_con_hallazgos
                            }
                        </strong>

                    </div>


                    <p class="recognition-description">
                        Detalle
                    </p>


                    <ul class="result-list">

                        ${detallesHTML}

                    </ul>


                    <div class="automata-route">

                        <span>
                            Conclusión
                        </span>

                        <p>
                            ${escaparHTML(
                                integrado
                                    .conclusion
                            )}
                        </p>

                    </div>

                </div>

            </div>
        `;

    }

    catch (error) {

        mostrarError(
            contenedor,
            error
        );
    }
}



// ==========================================================
// SEMANA 5
// ASISTENTE
// ==========================================================

function agregarMensaje(
    contenido,
    tipo,
    html = false
) {

    const chat =
        document.getElementById(
            "chat"
        );


    const mensaje =
        document.createElement(
            "div"
        );


    mensaje.className =
        `message ${tipo}`;


    if (html) {

        mensaje.innerHTML =
            contenido;

    } else {

        mensaje.textContent =
            contenido;
    }


    chat.appendChild(
        mensaje
    );


    chat.scrollTop =
        chat.scrollHeight;
}



async function consultarAsistente() {

    const entrada =
        document.getElementById(
            "consultaAsistente"
        );


    const consulta =
        entrada.value.trim();


    if (!consulta) {

        return;
    }


    agregarMensaje(
        consulta,
        "user"
    );


    entrada.value =
        "";


    try {

        const resultado =
            await enviarAPI(
                "/api/asistente",
                {
                    consulta:
                        consulta
                }
            );


        const reglas =
            Array.isArray(
                resultado.reglas
            )
            && resultado.reglas.length

                ? resultado.reglas
                    .map(
                        escaparHTML
                    )
                    .join(
                        ", "
                    )

                : "Sin regla específica";


        const similitud =
            Number(
                resultado.similitud
            );


        agregarMensaje(
            `

                <div class="assistant-result">

                    <p>

                        <strong>
                            Categoría:
                        </strong>

                        ${escaparHTML(
                            resultado.clase
                        )}

                    </p>


                    <p>

                        <strong>
                            Acción:
                        </strong>

                        ${reglas}

                    </p>


                    <p>

                        <strong>
                            Información relacionada:
                        </strong>

                        ${escaparHTML(
                            resultado.evidencia
                        )}

                    </p>


                    <p>

                        <strong>
                            Similitud:
                        </strong>

                        ${
                            Number.isNaN(
                                similitud
                            )

                                ? "N/D"

                                : similitud
                                    .toFixed(
                                        3
                                    )
                        }

                    </p>

                </div>
            `,
            "assistant",
            true
        );

    }

    catch (error) {

        agregarMensaje(
            error.message,
            "assistant"
        );
    }
}



function enviarConEnter(
    evento
) {

    if (
        evento.key === "Enter"
    ) {

        evento.preventDefault();

        consultarAsistente();
    }
}