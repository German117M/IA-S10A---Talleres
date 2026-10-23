"use strict";

(function () {

    function escapar(valor) {
        return String(valor ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }


    function interpretarCaso(caso) {

        if (caso.coincidencia === "1 de 3") {
            return (
                "Los dos métodos de verificación obtuvieron " +
                "un resultado diferente al análisis principal."
            );
        }

        return (
            "Uno de los métodos de verificación obtuvo " +
            "un resultado diferente."
        );
    }


    function crearCaso(caso) {

        const principalCorrecto =
            caso.resultado_sugerido ===
            caso.resultado_esperado;


        return `
            <article class="s11-caso">

                <div class="s11-caso-cabecera">

                    <div>
                        <span class="s11-etiqueta">
                            Caso de validación
                        </span>

                        <h3>
                            Caso ${escapar(caso.caso)}
                        </h3>
                    </div>

                    <span class="s11-revision-badge">
                        Revisión recomendada
                    </span>

                </div>


                <div class="s11-datos-caso">

                    <div>
                        <span>Edad</span>
                        <strong>
                            ${escapar(caso.edad)}
                        </strong>
                    </div>

                    <div>
                        <span>Documentos pendientes</span>
                        <strong>
                            ${escapar(
                                caso.documentos_pendientes
                            )}
                        </strong>
                    </div>

                    <div>
                        <span>Resultados pendientes</span>
                        <strong>
                            ${escapar(
                                caso.resultados_pendientes
                            )}
                        </strong>
                    </div>

                    <div>
                        <span>Imágenes pendientes</span>
                        <strong>
                            ${escapar(
                                caso.imagenes_pendientes
                            )}
                        </strong>
                    </div>

                </div>


                <div class="s11-decision">

                    <div>
                        <span>
                            Decisión del sistema
                        </span>

                        <strong>
                            ${escapar(
                                caso.resultado_sugerido
                            )}
                        </strong>
                    </div>

                    <div>
                        <span>
                            Resultado conocido
                        </span>

                        <strong>
                            ${escapar(
                                caso.resultado_esperado
                            )}
                        </strong>
                    </div>

                    <div>
                        <span>
                            ¿Fue correcta?
                        </span>

                        <strong class="${
                            principalCorrecto
                                ? "s11-correcto"
                                : "s11-incorrecto"
                        }">
                            ${
                                principalCorrecto
                                    ? "Sí"
                                    : "No"
                            }
                        </strong>
                    </div>

                </div>


                <div class="s11-explicacion-caso">

                    <strong>
                        ¿Por qué se marcó para revisión?
                    </strong>

                    <p>
                        ${escapar(
                            interpretarCaso(caso)
                        )}
                    </p>

                </div>


                <details class="s11-tecnico">

                    <summary>
                        Ver detalle técnico
                    </summary>

                    <div class="s11-metodos">

                        <div>
                            <span>
                                Análisis principal
                            </span>

                            <small>
                                Random Forest
                            </small>

                            <strong>
                                ${escapar(
                                    caso.analisis_principal
                                )}
                            </strong>
                        </div>


                        <div>
                            <span>
                                Verificación estadística
                            </span>

                            <small>
                                Logistic Regression
                            </small>

                            <strong>
                                ${escapar(
                                    caso.verificacion_estadistica
                                )}
                            </strong>
                        </div>


                        <div>
                            <span>
                                Verificación neuronal
                            </span>

                            <small>
                                MLP
                            </small>

                            <strong>
                                ${escapar(
                                    caso.verificacion_neuronal
                                )}
                            </strong>
                        </div>

                    </div>

                </details>

            </article>
        `;
    }


    async function ejecutarAuditoria() {

        const resumen =
            document.getElementById(
                "semana11Resumen"
            );

        const casos =
            document.getElementById(
                "semana11Casos"
            );

        const boton =
            document.getElementById(
                "btnAuditarSemana11"
            );


        if (!resumen || !casos) {
            return;
        }


        if (boton) {
            boton.disabled = true;
            boton.textContent =
                "Analizando decisiones...";
        }


        resumen.innerHTML = `
            <div class="s11-cargando">
                Revisando los casos de validación...
            </div>
        `;

        casos.innerHTML = "";


        try {

            const respuesta =
                await fetch(
                    "/api/semana11/auditoria",
                    {
                        cache: "no-store"
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
                    "No fue posible realizar la revisión."
                );
            }


            const r =
                datos.resultado;


            resumen.innerHTML = `

                <div class="s11-metricas">

                    <div class="s11-metrica">

                        <span>
                            Casos verificados
                        </span>

                        <strong>
                            ${escapar(
                                r.casos_evaluados
                            )}
                        </strong>

                        <small>
                            Casos reservados para validación
                        </small>

                    </div>


                    <div class="s11-metrica">

                        <span>
                            Decisiones estables
                        </span>

                        <strong>
                            ${escapar(
                                r.acuerdo_completo
                            )}
                        </strong>

                        <small>
                            ${escapar(
                                r.porcentaje_acuerdo
                            )}% sin discrepancias
                        </small>

                    </div>


                    <div class="s11-metrica s11-alerta">

                        <span>
                            Para revisar
                        </span>

                        <strong>
                            ${escapar(
                                r.revision_recomendada
                            )}
                        </strong>

                        <small>
                            ${escapar(
                                r.porcentaje_revision
                            )}% presentó diferencias
                        </small>

                    </div>


                    <div class="s11-metrica">

                        <span>
                            Decisiones correctas
                        </span>

                        <strong>
                            ${escapar(
                                r.precision_modelo_principal
                            )}%
                        </strong>

                        <small>
                            Resultado del análisis principal
                        </small>

                    </div>

                </div>


                <div class="s11-lectura">

                    <div>
                        <span class="s11-etiqueta">
                            Lectura sencilla
                        </span>

                        <h3>
                            El sistema mantiene una
                            precisión del
                            ${escapar(
                                r.precision_modelo_principal
                            )}%
                        </h3>

                        <p>
                            De ${escapar(r.casos_evaluados)}
                            casos evaluados,
                            ${escapar(r.acuerdo_completo)}
                            obtuvieron resultados consistentes
                            entre los distintos métodos.
                            ${escapar(r.revision_recomendada)}
                            casos presentaron diferencias y
                            fueron identificados automáticamente
                            para revisión.
                        </p>
                    </div>

                </div>
            `;


            if (
                !r.casos_revision
                ||
                r.casos_revision.length === 0
            ) {

                casos.innerHTML = `
                    <div class="s11-sin-casos">
                        No se encontraron casos que
                        requieran revisión.
                    </div>
                `;

                return;
            }


            casos.innerHTML = `

                <div class="s11-seccion-titulo">

                    <span class="s11-etiqueta">
                        Atención requerida
                    </span>

                    <h3>
                        Casos con resultados diferentes
                    </h3>

                    <p>
                        Estos casos no se descartan ni se
                        cambian automáticamente. HIS_IA los
                        identifica para que puedan revisarse
                        con mayor atención.
                    </p>

                </div>

                ${r.casos_revision
                    .map(crearCaso)
                    .join("")}
            `;


        } catch (error) {

            resumen.innerHTML = `
                <div class="s11-error">

                    <strong>
                        No fue posible realizar
                        el control de calidad.
                    </strong>

                    <p>
                        ${escapar(error.message)}
                    </p>

                </div>
            `;

        } finally {

            if (boton) {

                boton.disabled = false;

                boton.textContent =
                    "Volver a revisar";
            }
        }
    }


    function iniciar() {

        const seccion =
            document.getElementById(
                "semana11"
            );


        if (!seccion) {
            return;
        }


        /*
         * Conservamos la sección y navegación existentes,
         * pero Semana 11 deja de mostrarse como un
         * benchmark técnico.
         */

        seccion.innerHTML = `

            <div class="section-header">

                <div>

                    <span class="s11-etiqueta">
                        Semana 11
                    </span>

                    <h2>
                        Control de calidad de decisiones
                    </h2>

                    <p>
                        HIS_IA contrasta sus decisiones con
                        otros métodos para detectar casos que
                        merecen una revisión adicional.
                    </p>

                </div>


                <button
                    type="button"
                    id="btnAuditarSemana11"
                    class="primary-button"
                >
                    Revisar decisiones
                </button>

            </div>


            <div
                id="semana11Resumen"
                class="s11-resumen"
            >
            </div>


            <div
                id="semana11Casos"
                class="s11-casos"
            >
            </div>


            <details class="s11-como-funciona">

                <summary>
                    ¿Cómo funciona este control?
                </summary>

                <div>

                    <p>
                        HIS_IA utiliza un método principal
                        para generar la clasificación de
                        prioridad.
                    </p>

                    <p>
                        Después compara esa decisión con
                        dos enfoques adicionales. Cuando
                        los resultados no coinciden, el
                        caso se marca para revisión.
                    </p>

                    <p>
                        Los métodos de verificación no
                        reemplazan automáticamente la
                        decisión principal.
                    </p>

                </div>

            </details>
        `;


        document
            .getElementById(
                "btnAuditarSemana11"
            )
            ?.addEventListener(
                "click",
                ejecutarAuditoria
            );


        ejecutarAuditoria();
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
