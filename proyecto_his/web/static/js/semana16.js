document.addEventListener("DOMContentLoaded", () => {

    const form =
        document.getElementById("formSemana16");

    const pregunta =
        document.getElementById("semana16Pregunta");

    const resultado =
        document.getElementById("resultadoSemana16");


    if (!form || !pregunta || !resultado) {
        return;
    }


    form.addEventListener(
        "submit",
        async (evento) => {

            evento.preventDefault();

            resultado.classList.remove(
                "hidden"
            );

            resultado.innerHTML =
                "<p>Buscando referencia validada...</p>";


            try {

                const respuesta = await fetch(
                    "/api/semana16/consultar",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            pregunta:
                                pregunta.value.trim()
                        })
                    }
                );


                const data =
                    await respuesta.json();


                if (!respuesta.ok || !data.success) {

                    throw new Error(
                        data.error
                        || "No fue posible realizar la consulta."
                    );
                }


                const r = data.resultado;


                // ==========================================
                // SIN DATOS
                // ==========================================

                if (r.estado === "SIN_DATOS") {

                    resultado.innerHTML = `
                        <h3>
                            Sin datos
                        </h3>

                        <p>
                            ${r.mensaje}
                        </p>
                    `;

                    return;
                }


                // ==========================================
                // SIN REFERENCIA
                // ==========================================

                if (r.estado === "SIN_REFERENCIA") {

                    resultado.innerHTML = `
                        <h3>
                            Sin referencia validada
                        </h3>

                        <p>
                            ${r.mensaje}
                        </p>

                        <p>
                            <strong>
                                Términos analizados:
                            </strong>
                            ${
                                (
                                    r.palabras_consulta
                                    || []
                                ).join(", ")
                            }
                        </p>
                    `;

                    return;
                }


                // ==========================================
                // REFERENCIA ENCONTRADA
                // ==========================================

                const ref =
                    r.referencia;


                resultado.innerHTML = `

                    <h3>
                        Referencia encontrada
                    </h3>

                    <p>
                        <strong>Estado:</strong>
                        ${r.estado}
                    </p>

                    <p>
                        <strong>Respuesta:</strong>
                    </p>

                    <p>
                        ${r.mensaje}
                    </p>

                    <hr>

                    <p>
                        <strong>ID:</strong>
                        ${ref.id}
                    </p>

                    <p>
                        <strong>Título:</strong>
                        ${ref.titulo}
                    </p>

                    <p>
                        <strong>Dominio:</strong>
                        ${ref.dominio}
                    </p>

                    <p>
                        <strong>Aplicación:</strong>
                        ${ref.aplicacion || "No aplica"}
                    </p>

                    <p>
                        <strong>Responsable:</strong>
                        ${ref.responsable}
                    </p>

                    <p>
                        <strong>Herramienta:</strong>
                        ${ref.herramienta || "No aplica"}
                    </p>

                    <p>
                        <strong>Fuente:</strong>
                        ${ref.fuente}
                    </p>

                    <p>
                        <strong>Fecha de revisión:</strong>
                        ${ref.fecha_revision}
                    </p>

                    <p>
                        <strong>Estado del conocimiento:</strong>
                        ${ref.estado}
                    </p>

                    <hr>

                    <p>
                        <strong>Coincidencias:</strong>
                        ${ref.coincidencias}
                    </p>

                    <p>
                        <strong>
                            Términos coincidentes:
                        </strong>
                        ${
                            (
                                ref.terminos_coincidentes
                                || []
                            ).join(", ")
                        }
                    </p>

                    <p>
                        <strong>
                            Palabras analizadas:
                        </strong>
                        ${
                            (
                                r.palabras_consulta
                                || []
                            ).join(", ")
                        }
                    </p>
                `;


            } catch (error) {

                resultado.innerHTML = `
                    <p>
                        <strong>Error:</strong>
                        ${error.message}
                    </p>
                `;
            }

        }
    );

});
