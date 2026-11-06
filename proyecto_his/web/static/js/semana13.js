document.addEventListener("DOMContentLoaded", () => {

    const formulario = document.getElementById(
        "formSemana13"
    );

    const resultado = document.getElementById(
        "resultadoSemana13"
    );


    if (!formulario || !resultado) {
        return;
    }


    formulario.addEventListener(
        "submit",
        async (evento) => {

            evento.preventDefault();


            resultado.classList.remove(
                "hidden"
            );


            resultado.innerHTML = `
                <p>
                    Analizando caso...
                </p>
            `;


            const datos = {

                edad: Number(
                    document.getElementById(
                        "semana13Edad"
                    ).value
                ),

                temperatura: Number(
                    document.getElementById(
                        "semana13Temperatura"
                    ).value
                ),

                latidos: Number(
                    document.getElementById(
                        "semana13Latidos"
                    ).value
                ),

                presion: Number(
                    document.getElementById(
                        "semana13Presion"
                    ).value
                ),

                documentos_pendientes: Number(
                    document.getElementById(
                        "semana13Documentos"
                    ).value
                ),

                resultados_pendientes: Number(
                    document.getElementById(
                        "semana13Resultados"
                    ).value
                ),

                imagenes_pendientes: Number(
                    document.getElementById(
                        "semana13Imagenes"
                    ).value
                ),

                motivo_consulta:
                    document.getElementById(
                        "semana13Motivo"
                    ).value
            };


            try {

                const respuesta = await fetch(
                    "/api/semana13/analizar",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify(
                            datos
                        )
                    }
                );


                const data = await respuesta.json();


                if (
                    !respuesta.ok
                    ||
                    !data.success
                ) {

                    throw new Error(
                        data.error
                        ||
                        "No fue posible analizar el caso."
                    );
                }


                const r = data.resultado;


                const hallazgos = (
                    r.hallazgos
                    ||
                    []
                )
                .map(
                    item => `<li>${item}</li>`
                )
                .join("");


                const acciones = (
                    r.acciones_recomendadas
                    ||
                    []
                )
                .map(
                    item => `<li>${item}</li>`
                )
                .join("");


                const reglas = (
                    r.reglas_activadas
                    ||
                    []
                )
                .map(
                    regla => `
                        <li>
                            <strong>
                                ${regla.regla}
                            </strong>
                            →
                            ${regla.conclusion}
                            <br>
                            <small>
                                ${regla.descripcion}
                            </small>
                        </li>
                    `
                )
                .join("");


                const detalle11 = (
                    r.detalle_semana11
                    ||
                    {}
                );


                let modelos = "";


                Object.entries(
                    detalle11
                )
                .forEach(
                    ([nombre, detalle]) => {

                        modelos += `
                            <li>
                                <strong>
                                    ${nombre}
                                </strong>:
                                ${detalle.resultado}
                                (${detalle.metodo})
                            </li>
                        `;
                    }
                );


                resultado.innerHTML = `

                    <h3>
                        Resultado del análisis
                    </h3>


                    <p>
                        <strong>
                            Prioridad:
                        </strong>
                        ${r.prioridad}
                    </p>


                    <p>
                        <strong>
                            Nivel de acuerdo:
                        </strong>
                        ${r.nivel_acuerdo}
                    </p>


                    <p>
                        <strong>
                            Coincidencia:
                        </strong>
                        ${r.coincidencia}
                    </p>


                    <hr>


                    <h3>
                        Estado del caso
                    </h3>

                    <p>
                        ${r.estado_caso}
                    </p>


                    <h3>
                        Hallazgos
                    </h3>

                    <ul>
                        ${hallazgos}
                    </ul>


                    <h3>
                        Interpretación
                    </h3>

                    <p>
                        ${r.interpretacion}
                    </p>


                    <h3>
                        Acciones recomendadas
                    </h3>

                    <ul>
                        ${acciones}
                    </ul>


                    <details>

                        <summary>
                            Ver explicación técnica
                        </summary>


                        <h4>
                            Reglas activadas
                        </h4>

                        <ul>
                            ${reglas}
                        </ul>


                        <h4>
                            Verificación Semana 11
                        </h4>

                        <ul>
                            ${modelos}
                        </ul>

                    </details>
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
