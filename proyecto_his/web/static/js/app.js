const titulos = {
    inicio: "Panel principal",
    analisis: "Análisis de información",
    prioridad: "Evaluación de prioridad",
    revision: "Organización de revisión",
    asistente: "Asistente HIS_IA"
};


function mostrarSeccion(id, boton = null) {

    document
        .querySelectorAll(".section")
        .forEach(seccion => {
            seccion.classList.remove("active");
        });


    document
        .getElementById(id)
        .classList.add("active");


    document.getElementById(
        "tituloPagina"
    ).textContent = titulos[id];


    document
        .querySelectorAll(".nav-item")
        .forEach(item => {
            item.classList.remove("active");
        });


    if (boton) {
        boton.classList.add("active");
    }
}


function abrirDesdeCard(id) {

    const botones =
        document.querySelectorAll(".nav-item");

    const mapa = {
        analisis: 1,
        prioridad: 2,
        revision: 3,
        asistente: 4
    };

    mostrarSeccion(
        id,
        botones[mapa[id]]
    );
}


function mostrarLoader() {
    document
        .getElementById("loader")
        .classList.remove("hidden");
}


function ocultarLoader() {
    document
        .getElementById("loader")
        .classList.add("hidden");
}


async function analizarInformacion() {

    const texto =
        document.getElementById(
            "textoAnalisis"
        ).value;

    const contenedor =
        document.getElementById(
            "resultadoAnalisis"
        );

    mostrarLoader();

    try {

        const respuesta = await fetch(
            "/api/analizar",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    texto
                })
            }
        );


        const datos =
            await respuesta.json();


        if (!datos.ok) {
            throw new Error(
                datos.mensaje
            );
        }


        contenedor.innerHTML = `
            <h4>Resultado del análisis</h4>

            <p>
                <strong>Categoría principal:</strong>
                ${datos.categoria}
            </p>

            <p>
                <strong>Información detectada:</strong>
                ${
                    datos.detectadas.length
                    ? datos.detectadas.join(", ")
                    : "Sin coincidencias"
                }
            </p>
        `;


        contenedor.classList.remove(
            "hidden"
        );

    }

    catch (error) {

        contenedor.innerHTML =
            `<p>${error.message}</p>`;

        contenedor.classList.remove(
            "hidden"
        );

    }

    finally {
        ocultarLoader();
    }
}


async function evaluarPrioridad() {

    const datosFormulario = {

        edad:
            document.getElementById(
                "edad"
            ).value,

        documentos:
            document.getElementById(
                "documentos"
            ).value,

        resultados:
            document.getElementById(
                "resultados"
            ).value,

        imagenes:
            document.getElementById(
                "imagenes"
            ).value
    };


    const contenedor =
        document.getElementById(
            "resultadoPrioridad"
        );


    mostrarLoader();


    try {

        const respuesta = await fetch(
            "/api/prioridad",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify(
                        datosFormulario
                    )
            }
        );


        const datos =
            await respuesta.json();


        if (!datos.ok) {
            throw new Error(
                datos.mensaje
            );
        }


        contenedor.innerHTML = `
            <h4>Prioridad estimada</h4>

            <p class="priority-value">
                ${datos.prioridad}
            </p>
        `;


        contenedor.classList.remove(
            "hidden"
        );

    }

    catch (error) {

        contenedor.innerHTML =
            `<p>${error.message}</p>`;

        contenedor.classList.remove(
            "hidden"
        );

    }

    finally {
        ocultarLoader();
    }
}


async function organizarRevision() {

    const elementos = [

        ...document.querySelectorAll(
            'input[name="elemento"]:checked'
        )

    ].map(
        elemento => elemento.value
    );


    const contenedor =
        document.getElementById(
            "resultadoRevision"
        );


    mostrarLoader();


    try {

        const respuesta = await fetch(
            "/api/revision",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    elementos
                })
            }
        );


        const datos =
            await respuesta.json();


        if (!datos.ok) {
            throw new Error(
                datos.mensaje
            );
        }


        const pasos =
            datos.secuencia
                .map(
                    (elemento, indice) =>
                    `
                    <li>
                        <span>
                            ${indice + 1}
                        </span>
                        ${elemento}
                    </li>
                    `
                )
                .join("");


        contenedor.innerHTML = `
            <h4>
                Secuencia sugerida
            </h4>

            <ol class="sequence">
                ${pasos}
            </ol>

            <p>
                <strong>
                    Costo total estimado:
                </strong>

                ${datos.costo}
            </p>
        `;


        contenedor.classList.remove(
            "hidden"
        );

    }

    catch (error) {

        contenedor.innerHTML =
            `<p>${error.message}</p>`;

        contenedor.classList.remove(
            "hidden"
        );

    }

    finally {
        ocultarLoader();
    }
}


async function consultarAsistente() {

    const input =
        document.getElementById(
            "consulta"
        );

    const consulta =
        input.value.trim();


    if (!consulta) {
        return;
    }


    const chat =
        document.getElementById(
            "chat"
        );


    chat.innerHTML += `
        <div class="message user">
            <p>${escaparHTML(consulta)}</p>
        </div>
    `;


    input.value = "";

    chat.scrollTop =
        chat.scrollHeight;


    mostrarLoader();


    try {

        const respuesta = await fetch(
            "/api/asistente",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    consulta
                })
            }
        );


        const datos =
            await respuesta.json();


        if (!datos.ok) {
            throw new Error(
                datos.mensaje
            );
        }


        const reglas =
            datos.reglas.length
            ? datos.reglas.join(", ")
            : "Sin regla específica";


        chat.innerHTML += `
            <div class="message ai">

                <strong>HIS_IA</strong>

                <p>
                    ${escaparHTML(datos.evidencia)}
                </p>

                <br>

                <p>
                    <b>Categoría:</b>
                    ${escaparHTML(datos.clase)}
                </p>

                <p>
                    <b>Acción:</b>
                    ${escaparHTML(reglas)}
                </p>

                <p>
                    <b>Similitud:</b>
                    ${datos.similitud}
                </p>

            </div>
        `;


        chat.scrollTop =
            chat.scrollHeight;

    }

    catch (error) {

        chat.innerHTML += `
            <div class="message ai">
                <strong>HIS_IA</strong>
                <p>${escaparHTML(error.message)}</p>
            </div>
        `;

    }

    finally {
        ocultarLoader();
    }
}


function enviarConEnter(event) {

    if (event.key === "Enter") {
        consultarAsistente();
    }
}


function escaparHTML(texto) {

    const elemento =
        document.createElement("div");

    elemento.textContent = texto;

    return elemento.innerHTML;
}