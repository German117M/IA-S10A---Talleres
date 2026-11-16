document.addEventListener("DOMContentLoaded", () => {

    const dominioBuscar =
        document.getElementById("semana15DominioBuscar");

    const dominioRegistro =
        document.getElementById("semana15Dominio");

    const aplicacion =
        document.getElementById("semana15Aplicacion");

    const experto =
        document.getElementById("semana15Experto");

    const herramienta =
        document.getElementById("semana15Herramienta");

    const formBuscar =
        document.getElementById("formSemana15Buscar");

    const resultadoBuscar =
        document.getElementById("resultadoSemana15Buscar");

    const formRegistrar =
        document.getElementById("formSemana15Registrar");

    const resultadoRegistrar =
        document.getElementById("resultadoSemana15Registrar");

    const btnArticulos =
        document.getElementById("btnSemana15Articulos");

    const resultadoArticulos =
        document.getElementById("resultadoSemana15Articulos");


    // ======================================================
    // CATÁLOGOS
    // ======================================================

    async function cargarCatalogos() {

        try {

            const respuesta = await fetch(
                "/api/semana15/catalogos"
            );

            const data = await respuesta.json();


            if (!respuesta.ok || !data.success) {

                throw new Error(
                    data.error
                    || "No fue posible cargar los catálogos."
                );
            }


            for (const item of data.dominios) {

                const opcion1 =
                    document.createElement("option");

                opcion1.value = item.nombre;
                opcion1.textContent = item.nombre;

                dominioBuscar.appendChild(
                    opcion1
                );


                const opcion2 =
                    document.createElement("option");

                opcion2.value = item.id;
                opcion2.textContent = item.nombre;

                dominioRegistro.appendChild(
                    opcion2
                );
            }


            for (const item of data.aplicaciones) {

                const opcion =
                    document.createElement("option");

                opcion.value = item.id;

                opcion.textContent =
                    `${item.nombre} (${item.dominio})`;

                aplicacion.appendChild(
                    opcion
                );
            }


            for (const item of data.expertos) {

                const opcion =
                    document.createElement("option");

                opcion.value = item.id;

                opcion.textContent =
                    `${item.nombre} - ${item.cargo}`;

                experto.appendChild(
                    opcion
                );
            }


            for (const item of data.herramientas) {

                const opcion =
                    document.createElement("option");

                opcion.value = item.id;

                opcion.textContent =
                    `${item.nombre} - ${item.finalidad}`;

                herramienta.appendChild(
                    opcion
                );
            }


        } catch (error) {

            console.error(
                "Semana 15:",
                error
            );
        }
    }


    // ======================================================
    // BUSCAR ARTÍCULOS VALIDADOS
    // ======================================================

    if (formBuscar) {

        formBuscar.addEventListener(
            "submit",
            async (evento) => {

                evento.preventDefault();

                const dominio =
                    dominioBuscar.value;


                resultadoBuscar.classList.remove(
                    "hidden"
                );

                resultadoBuscar.innerHTML =
                    "<p>Buscando conocimiento...</p>";


                try {

                    const respuesta = await fetch(
                        `/api/semana15/articulos?dominio=${encodeURIComponent(dominio)}`
                    );

                    const data =
                        await respuesta.json();


                    if (!respuesta.ok || !data.success) {

                        throw new Error(
                            data.error
                            || "No fue posible buscar artículos."
                        );
                    }


                    const articulos =
                        data.articulos || [];


                    if (articulos.length === 0) {

                        resultadoBuscar.innerHTML = `
                            <p>
                                No existen artículos VALIDADO
                                para este dominio.
                            </p>
                        `;

                        return;
                    }


                    resultadoBuscar.innerHTML =
                        articulos.map(
                            articulo => `
                                <div class="panel">

                                    <h3>
                                        ${articulo.titulo}
                                    </h3>

                                    <p>
                                        ${articulo.contenido}
                                    </p>

                                    <p>
                                        <strong>Dominio:</strong>
                                        ${articulo.dominio}
                                    </p>

                                    <p>
                                        <strong>Aplicación:</strong>
                                        ${articulo.aplicacion || "No aplica"}
                                    </p>

                                    <p>
                                        <strong>Responsable:</strong>
                                        ${articulo.responsable}
                                    </p>

                                    <p>
                                        <strong>Herramienta:</strong>
                                        ${articulo.herramienta || "No aplica"}
                                    </p>

                                    <p>
                                        <strong>Fuente:</strong>
                                        ${articulo.fuente}
                                    </p>

                                    <p>
                                        <strong>Fecha revisión:</strong>
                                        ${articulo.fecha_revision}
                                    </p>

                                    <p>
                                        <strong>Estado:</strong>
                                        ${articulo.estado}
                                    </p>

                                </div>
                            `
                        ).join("");

                } catch (error) {

                    resultadoBuscar.innerHTML = `
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
    // REGISTRAR ARTÍCULO
    // ======================================================

    if (formRegistrar) {

        formRegistrar.addEventListener(
            "submit",
            async (evento) => {

                evento.preventDefault();


                const datos = {

                    titulo:
                        document.getElementById(
                            "semana15Titulo"
                        ).value.trim(),

                    contenido:
                        document.getElementById(
                            "semana15Contenido"
                        ).value.trim(),

                    dominio_id:
                        dominioRegistro.value,

                    aplicacion_id:
                        aplicacion.value || null,

                    experto_id:
                        experto.value,

                    herramienta_id:
                        herramienta.value || null,

                    fuente:
                        document.getElementById(
                            "semana15Fuente"
                        ).value.trim()
                };


                resultadoRegistrar.classList.remove(
                    "hidden"
                );

                resultadoRegistrar.innerHTML =
                    "<p>Registrando artículo...</p>";


                try {

                    const respuesta = await fetch(
                        "/api/semana15/articulos",
                        {
                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify(datos)
                        }
                    );


                    const data =
                        await respuesta.json();


                    if (!respuesta.ok || !data.success) {

                        throw new Error(
                            data.error
                            || "No fue posible registrar el artículo."
                        );
                    }


                    resultadoRegistrar.innerHTML = `
                        <h3>
                            Artículo registrado
                        </h3>

                        <p>
                            <strong>ID:</strong>
                            ${data.articulo_id}
                        </p>

                        <p>
                            <strong>Estado inicial:</strong>
                            ${data.estado}
                        </p>

                        <p>
                            El artículo debe ser validado
                            antes de aparecer en las búsquedas.
                        </p>
                    `;


                    formRegistrar.reset();


                } catch (error) {

                    resultadoRegistrar.innerHTML = `
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
    // LISTAR TODOS LOS ARTÍCULOS
    // ======================================================

    async function cargarArticulos() {

        resultadoArticulos.classList.remove(
            "hidden"
        );

        resultadoArticulos.innerHTML =
            "<p>Cargando artículos...</p>";


        try {

            const respuesta = await fetch(
                "/api/semana15/articulos"
            );

            const data =
                await respuesta.json();


            if (!respuesta.ok || !data.success) {

                throw new Error(
                    data.error
                    || "No fue posible cargar los artículos."
                );
            }


            const articulos =
                data.articulos || [];


            resultadoArticulos.innerHTML =
                articulos.map(
                    articulo => {

                        const boton = (
                            articulo.estado === "BORRADOR"
                        )
                            ? `
                                <button
                                    type="button"
                                    class="btn-primary btn-validar-semana15"
                                    data-id="${articulo.id}"
                                >
                                    Validar artículo
                                </button>
                            `
                            : `
                                <p>
                                    ✓ Artículo validado
                                </p>
                            `;


                        return `
                            <div class="panel">

                                <h3>
                                    ${articulo.titulo}
                                </h3>

                                <p>
                                    <strong>ID:</strong>
                                    ${articulo.id}
                                </p>

                                <p>
                                    <strong>Dominio:</strong>
                                    ${articulo.dominio}
                                </p>

                                <p>
                                    <strong>Responsable:</strong>
                                    ${articulo.responsable}
                                </p>

                                <p>
                                    <strong>Estado:</strong>
                                    ${articulo.estado}
                                </p>

                                <p>
                                    <strong>Fecha:</strong>
                                    ${articulo.fecha_revision}
                                </p>

                                ${boton}

                            </div>
                        `;
                    }
                ).join("");


            document.querySelectorAll(
                ".btn-validar-semana15"
            ).forEach(
                boton => {

                    boton.addEventListener(
                        "click",
                        async () => {

                            const id =
                                boton.dataset.id;

                            await validarArticulo(
                                id
                            );
                        }
                    );
                }
            );


        } catch (error) {

            resultadoArticulos.innerHTML = `
                <p>
                    <strong>Error:</strong>
                    ${error.message}
                </p>
            `;
        }
    }


    // ======================================================
    // VALIDAR ARTÍCULO
    // ======================================================

    async function validarArticulo(id) {

        try {

            const respuesta = await fetch(
                `/api/semana15/articulos/${id}/validar`,
                {
                    method: "POST"
                }
            );


            const data =
                await respuesta.json();


            if (!respuesta.ok || !data.success) {

                throw new Error(
                    data.error
                    || "No fue posible validar el artículo."
                );
            }


            await cargarArticulos();


        } catch (error) {

            alert(
                `Error: ${error.message}`
            );
        }
    }


    if (btnArticulos) {

        btnArticulos.addEventListener(
            "click",
            cargarArticulos
        );
    }


    // ======================================================
    // INICIO
    // ======================================================

    if (
        dominioBuscar
        &&
        dominioRegistro
        &&
        aplicacion
        &&
        experto
        &&
        herramienta
    ) {

        cargarCatalogos();
    }

});
