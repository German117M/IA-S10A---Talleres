"use strict";

(function () {

    function escapar(valor) {

        return String(
            valor ?? ""
        )
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }


    function iniciar() {

        const formulario =
            document.getElementById(
                "formPrioridad"
            );


        const contenedor =
            document.getElementById(
                "resultadoPrioridad"
            );


        if (
            !formulario
            ||
            !contenedor
        ) {

            return;
        }


        formulario.addEventListener(
            "submit",

            async evento => {

                /*
                 * Capturamos el formulario antes
                 * del controlador antiguo de app.js.
                 */

                evento.preventDefault();
                evento.stopPropagation();
                evento.stopImmediatePropagation();


                const entrada = {

                    edad:
                        Number(
                            document.getElementById(
                                "prioridadEdad"
                            )?.value
                        ),

                    documentos_pendientes:
                        Number(
                            document.getElementById(
                                "prioridadDocumentos"
                            )?.value
                        ),

                    resultados_pendientes:
                        Number(
                            document.getElementById(
                                "prioridadResultados"
                            )?.value
                        ),

                    imagenes_pendientes:
                        Number(
                            document.getElementById(
                                "prioridadImagenes"
                            )?.value
                        )
                };


                contenedor.classList.remove(
                    "hidden"
                );


                contenedor.innerHTML = `
                    <div class="consenso-cargando">
                        Analizando el caso mediante
                        varios métodos...
                    </div>
                `;


                try {

                    const respuesta =
                        await fetch(
                            "/api/prioridad/consenso",
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body:
                                    JSON.stringify(
                                        entrada
                                    )
                            }
                        );


                    const datos =
                        await respuesta.json();


                    if (
                        !respuesta.ok
                        ||
                        !datos.success
                    ) {

                        throw new Error(
                            datos.error
                            ||
                            "No fue posible analizar el caso."
                        );
                    }


                    const r =
                        datos.resultado;


                    const revision =
                        r.revision_recomendada
                            ? "Recomendada"
                            : "No necesaria";


                    const claseRevision =
                        r.revision_recomendada
                            ? "revision-si"
                            : "revision-no";


                    const claseAcuerdo =
                        r.nivel_acuerdo === "Alto"
                            ? "acuerdo-alto"
                            : "acuerdo-medio";


                    const detalles =
                        Object.entries(
                            r.detalle || {}
                        )
                        .map(
                            ([nombre, detalle]) => `
                                <div class="metodo-verificacion">

                                    <div>
                                        <strong>
                                            ${escapar(nombre)}
                                        </strong>

                                        <small>
                                            ${escapar(
                                                detalle.metodo
                                            )}
                                        </small>
                                    </div>

                                    <span>
                                        ${escapar(
                                            detalle.resultado
                                        )}
                                    </span>

                                </div>
                            `
                        )
                        .join("");


                    contenedor.innerHTML = `

                        <div class="resultado-consenso">

                            <div class="resultado-principal">

                                <span class="resultado-etiqueta">
                                    Resultado sugerido
                                </span>

                                <strong class="resultado-valor">
                                    ${escapar(r.resultado)}
                                </strong>

                                <p>
                                    Clasificación obtenida después
                                    de contrastar el caso mediante
                                    tres métodos de análisis.
                                </p>

                            </div>


                            <div class="consenso-resumen-grid">

                                <div class="consenso-resumen">

                                    <span>
                                        Nivel de acuerdo
                                    </span>

                                    <strong
                                        class="${claseAcuerdo}"
                                    >
                                        ${escapar(
                                            r.nivel_acuerdo
                                        )}
                                    </strong>

                                    <small>
                                        ${escapar(
                                            r.texto_coincidencia
                                        )}
                                    </small>

                                </div>


                                <div class="consenso-resumen">

                                    <span>
                                        Revisión adicional
                                    </span>

                                    <strong
                                        class="${claseRevision}"
                                    >
                                        ${revision}
                                    </strong>

                                    <small>
                                        ${
                                            r.revision_recomendada
                                                ? "Existe una diferencia entre los análisis."
                                                : "Los análisis coinciden."
                                        }
                                    </small>

                                </div>

                            </div>


                            <div class="consenso-explicacion">

                                <h4>
                                    ¿Qué significa?
                                </h4>

                                <p>
                                    ${escapar(
                                        r.explicacion
                                    )}
                                </p>

                            </div>


                            <details class="consenso-detalles">

                                <summary>
                                    Ver cómo se obtuvo el resultado
                                </summary>

                                <p class="detalle-ayuda">
                                    HIS_IA realizó el mismo análisis
                                    utilizando tres enfoques distintos
                                    y comparó sus respuestas.
                                </p>

                                ${detalles}

                            </details>

                        </div>
                    `;


                } catch (error) {

                    console.error(
                        "Prioridad Semana 11:",
                        error
                    );


                    contenedor.innerHTML = `
                        <div class="consenso-error">

                            <strong>
                                No fue posible completar
                                el análisis.
                            </strong>

                            <p>
                                ${escapar(
                                    error.message
                                )}
                            </p>

                        </div>
                    `;
                }

            },

            /*
             * Capture = true.
             * Así este controlador actúa antes
             * del listener antiguo de app.js.
             */
            true
        );
    }


    if (
        document.readyState === "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            iniciar,
            {
                once: true
            }
        );

    } else {

        iniciar();
    }

})();
