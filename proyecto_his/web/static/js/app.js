"use strict";





// ==========================================================

// HIS_IA

// FRONTEND PRINCIPAL

// ==========================================================





// ==========================================================

// UTILIDADES GENERALES

// ==========================================================



function obtenerElemento(id) {

    return document.getElementById(id);

}





function mostrarElemento(elemento) {



    if (!elemento) {

        return;

    }



    elemento.classList.remove("hidden");

}





function ocultarElemento(elemento) {



    if (!elemento) {

        return;

    }



    elemento.classList.add("hidden");

}





function escaparHTML(valor) {



    if (

        valor === null ||

        valor === undefined

    ) {

        return "";

    }



    return String(valor)

        .replaceAll("&", "&amp;")

        .replaceAll("<", "&lt;")

        .replaceAll(">", "&gt;")

        .replaceAll('"', "&quot;")

        .replaceAll("'", "&#039;");

}





function valorSeguro(

    valor,

    defecto = "--"

) {



    if (

        valor === null ||

        valor === undefined ||

        valor === ""

    ) {

        return defecto;

    }



    return valor;

}





function porcentaje(valor) {



    if (

        valor === null ||

        valor === undefined ||

        Number.isNaN(Number(valor))

    ) {

        return "--";

    }



    return `${(Number(valor) * 100).toFixed(2)}%`;

}





function formatearTamano(bytes) {



    if (!bytes) {

        return "0 KB";

    }



    const kb = bytes / 1024;



    if (kb < 1024) {

        return `${kb.toFixed(1)} KB`;

    }



    const mb = kb / 1024;



    return `${mb.toFixed(2)} MB`;

}





// ==========================================================

// NORMALIZAR TEXTO

// ==========================================================



function normalizarTexto(texto) {



    return String(

        texto || ""

    )

        .normalize("NFD")

        .replace(/[\u0300-\u036f]/g, "")

        .trim()

        .toLowerCase();

}





// ==========================================================

// TOAST

// ==========================================================



function mostrarToast(

    mensaje,

    tipo = "info"

) {



    const contenedor = obtenerElemento(

        "toastContainer"

    );



    if (!contenedor) {

        return;

    }



    const toast = document.createElement(

        "div"

    );



    toast.className = `toast toast-${tipo}`;



    toast.innerHTML = `

        <span>

            ${escaparHTML(mensaje)}

        </span>

    `;



    contenedor.appendChild(

        toast

    );



    requestAnimationFrame(() => {

        toast.classList.add("show");

    });



    setTimeout(() => {



        toast.classList.remove(

            "show"

        );



        setTimeout(() => {

            toast.remove();

        }, 300);



    }, 4000);

}





// ==========================================================

// PETICIONES JSON

// ==========================================================



async function apiJSON(

    url,

    opciones = {}

) {



    const respuesta = await fetch(

        url,

        opciones

    );



    let datos;



    try {



        datos = await respuesta.json();



    } catch {



        throw new Error(

            "El servidor devolvió una respuesta no válida."

        );

    }





    if (!respuesta.ok) {



        const mensaje =

            datos.error ||

            datos.detalle ||

            "Ocurrió un error en el servidor.";



        throw new Error(

            mensaje

        );

    }





    if (

        datos &&

        datos.ok === false

    ) {



        throw new Error(

            datos.error ||

            "La operación no pudo completarse."

        );

    }





    return datos;

}





// ==========================================================

// NAVEGACIÓN

// ==========================================================



const titulosSeccion = {



    inicio:

        "Panel principal",



    clasificacion:

        "Clasificación",



    prioridad:

        "Evaluación de prioridad",



    astar:

        "Algoritmo A*",



    minimax:

        "Priorización Minimax",



    semana7:

        "Representaciones",



    semana8:

        "Reconocimiento y representación",


    semana9:

        "Procesamiento visual",



    asistente:

        "Asistente HIS_IA"

};





function cambiarSeccion(

    nombreSeccion

) {



    document

        .querySelectorAll(

            ".content-section"

        )

        .forEach(seccion => {



            seccion.classList.remove(

                "active"

            );

        });





    const destino = obtenerElemento(

        nombreSeccion

    );





    if (destino) {



        destino.classList.add(

            "active"

        );

    }





    document

        .querySelectorAll(

            ".nav-item"

        )

        .forEach(item => {



            item.classList.toggle(

                "active",

                item.dataset.section === nombreSeccion

            );

        });





    const titulo = obtenerElemento(

        "tituloSeccion"

    );





    if (titulo) {



        titulo.textContent =

            titulosSeccion[

                nombreSeccion

            ] ||

            "HIS_IA";

    }





    if (

        nombreSeccion === "semana8"

    ) {



        cargarResumenSemana8();

    }





    window.scrollTo({

        top: 0,

        behavior: "smooth"

    });

}





// ==========================================================

// NAVEGACIÓN LATERAL

// ==========================================================



document

    .querySelectorAll(

        ".nav-item"

    )

    .forEach(item => {



        item.addEventListener(

            "click",

            () => {



                cambiarSeccion(

                    item.dataset.section

                );

            }

        );

    });





// ==========================================================

// BOTONES INTERNOS DE NAVEGACIÓN

// ==========================================================



document

    .querySelectorAll(

        "[data-go-section]"

    )

    .forEach(boton => {



        boton.addEventListener(

            "click",

            () => {



                cambiarSeccion(

                    boton.dataset.goSection

                );

            }

        );

    });





// ==========================================================

// CLASIFICACIÓN

// ==========================================================



const formClasificacion =

    obtenerElemento(

        "formClasificacion"

    );





if (formClasificacion) {



    formClasificacion.addEventListener(

        "submit",

        async evento => {



            evento.preventDefault();





            const texto =

                obtenerElemento(

                    "textoClasificacion"

                )?.value.trim();





            const contenedor =

                obtenerElemento(

                    "resultadoClasificacion"

                );





            if (!texto) {



                mostrarToast(

                    "Debe ingresar información para analizar.",

                    "error"

                );



                return;

            }





            try {



                const datos = await apiJSON(

                    "/api/clasificar",

                    {

                        method:

                            "POST",



                        headers: {

                            "Content-Type":

                                "application/json"

                        },



                        body: JSON.stringify({

                            texto:

                                texto

                        })

                    }

                );





                mostrarElemento(

                    contenedor

                );





                if (contenedor) {



                    contenedor.innerHTML = `

                        <h3>

                            Resultado

                        </h3>



                        <pre>${escaparHTML(

                            JSON.stringify(

                                datos.resultado,

                                null,

                                2

                            )

                        )}</pre>

                    `;

                }





            } catch (error) {



                mostrarToast(

                    error.message,

                    "error"

                );

            }

        }

    );

}





// ==========================================================

// PRIORIDAD

// ==========================================================

const formPrioridad =
    obtenerElemento(
        "formPrioridad"
    );


if (formPrioridad) {

    formPrioridad.addEventListener(
        "submit",
        async evento => {

            evento.preventDefault();

            const datosEntrada = {

                edad:
                    Number(
                        obtenerElemento(
                            "prioridadEdad"
                        )?.value
                    ),

                documentos_pendientes:
                    Number(
                        obtenerElemento(
                            "prioridadDocumentos"
                        )?.value
                    ),

                resultados_pendientes:
                    Number(
                        obtenerElemento(
                            "prioridadResultados"
                        )?.value
                    ),

                imagenes_pendientes:
                    Number(
                        obtenerElemento(
                            "prioridadImagenes"
                        )?.value
                    )

            };


            try {

                const datos = await apiJSON(
                    "/api/prioridad",
                    {
                        method:
                            "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                datosEntrada
                            )
                    }
                );


                const contenedor =
                    obtenerElemento(
                        "resultadoPrioridad"
                    );


                mostrarElemento(
                    contenedor
                );


                const resultado =
                    datos.resultado || {};


                if (contenedor) {

                    contenedor.innerHTML = `
                        <h3>
                            Evaluación de prioridad
                        </h3>

                        <div class="result-summary-grid">
                            <div>
                                <span>
                                    Resultado
                                </span>

                                <strong>
                                    ${escaparHTML(
                                        valorSeguro(
                                            resultado.prioridad
                                        )
                                    )}
                                </strong>
                            </div>

                            <div>
                                <span>
                                    Precisión del modelo
                                </span>

                                <strong>
                                    ${
                                        resultado.precision_modelo !==
                                        null &&
                                        resultado.precision_modelo !==
                                        undefined
                                            ? porcentaje(
                                                resultado.precision_modelo
                                            )
                                            : "--"
                                    }
                                </strong>
                            </div>
                        </div>

                        <pre>${escaparHTML(
                            JSON.stringify(
                                resultado,
                                null,
                                2
                            )
                        )}</pre>
                    `;

                }


            } catch (error) {

                mostrarToast(
                    error.message,
                    "error"
                );

            }
        }
    );

}


// ==========================================================

// A*

// ==========================================================

const formAstar =
    obtenerElemento(
        "formAstar"
    );


if (formAstar) {

    formAstar.addEventListener(
        "submit",
        async evento => {

            evento.preventDefault();


            const elementos =
                Array.from(
                    document.querySelectorAll(
                        'input[name="astarElemento"]:checked'
                    )
                )
                .map(input =>
                    input.value
                );


            if (!elementos.length) {

                mostrarToast(
                    "Seleccione al menos un elemento para organizar.",
                    "error"
                );

                return;
            }


            try {

                const datos = await apiJSON(
                    "/api/astar",
                    {
                        method:
                            "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify({
                                elementos
                            })
                    }
                );


                const contenedor =
                    obtenerElemento(
                        "resultadoAstar"
                    );


                mostrarElemento(
                    contenedor
                );


                const resultado =
                    datos.resultado || {};


                if (contenedor) {

                    const orden =
                        Array.isArray(
                            resultado.orden
                        )
                            ? resultado.orden
                            : [];


                    contenedor.innerHTML = `
                        <h3>
                            Orden sugerido
                        </h3>

                        <div class="ordered-result">
                            ${
                                orden.length
                                    ? orden
                                        .map(
                                            (elemento, indice) => `
                                                <div>
                                                    <span>
                                                        ${indice + 1}
                                                    </span>

                                                    <strong>
                                                        ${escaparHTML(
                                                            elemento
                                                        )}
                                                    </strong>
                                                </div>
                                            `
                                        )
                                        .join("")
                                    : `
                                        <p>
                                            No se generó un orden.
                                        </p>
                                    `
                            }
                        </div>

                        <p class="result-note">
                            Costo total:
                            <strong>
                                ${escaparHTML(
                                    valorSeguro(
                                        resultado.costo_total,
                                        0
                                    )
                                )}
                            </strong>
                        </p>
                    `;

                }


            } catch (error) {

                mostrarToast(
                    error.message,
                    "error"
                );

            }
        }
    );

}


// ==========================================================

// MINIMAX

// ==========================================================

const formMinimax =
    obtenerElemento(
        "formMinimax"
    );


function construirPacienteMinimax(
    numero
) {

    const criterios = [
        "dolor_intenso",
        "dificultad_respiratoria",
        "sangrado_activo",
        "perdida_movilidad",
        "alteracion_conciencia",
        "trauma",
        "requiere_soporte"
    ];


    const paciente = {

        motivo_consulta:
            obtenerElemento(
                `minimaxP${numero}_motivo`
            )?.value.trim() ||
            `Caso académico ${numero}`

    };


    criterios.forEach(
        criterio => {

            paciente[
                criterio
            ] = Boolean(
                obtenerElemento(
                    `minimaxP${numero}_${criterio}`
                )?.checked
            );

        }
    );


    return paciente;
}


if (formMinimax) {

    formMinimax.addEventListener(
        "submit",
        async evento => {

            evento.preventDefault();


            const paciente1 =
                construirPacienteMinimax(
                    1
                );


            const paciente2 =
                construirPacienteMinimax(
                    2
                );


            try {

                const datos = await apiJSON(
                    "/api/minimax",
                    {
                        method:
                            "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify({
                                paciente1,
                                paciente2
                            })
                    }
                );


                const contenedor =
                    obtenerElemento(
                        "resultadoMinimax"
                    );


                mostrarElemento(
                    contenedor
                );


                const resultado =
                    datos.resultado || {};


                if (contenedor) {

                    contenedor.innerHTML = `
                        <h3>
                            Resultado Minimax
                        </h3>

                        <div class="result-summary-grid">
                            <div>
                                <span>
                                    Caso priorizado
                                </span>

                                <strong>
                                    ${escaparHTML(
                                        valorSeguro(
                                            resultado.paciente_prioritario
                                        )
                                    )}
                                </strong>
                            </div>

                            <div>
                                <span>
                                    Valor Minimax
                                </span>

                                <strong>
                                    ${escaparHTML(
                                        valorSeguro(
                                            resultado.valor_minimax
                                        )
                                    )}
                                </strong>
                            </div>
                        </div>

                        <pre>${escaparHTML(
                            JSON.stringify(
                                resultado,
                                null,
                                2
                            )
                        )}</pre>
                    `;

                }


            } catch (error) {

                mostrarToast(
                    error.message,
                    "error"
                );

            }
        }
    );

}


// ==========================================================

// SEMANA 7

// ==========================================================



const formSemana7 =

    obtenerElemento(

        "formSemana7"

    );





if (formSemana7) {



    formSemana7.addEventListener(

        "submit",

        async evento => {



            evento.preventDefault();





            const temperatura =

                Number(

                    obtenerElemento(

                        "semana7Temperatura"

                    )?.value

                );





            const latidos =

                Number(

                    obtenerElemento(

                        "semana7Latidos"

                    )?.value

                );





            const presion =

                Number(

                    obtenerElemento(

                        "semana7Presion"

                    )?.value

                );





            try {



                const datos = await apiJSON(

                    "/api/semana7",

                    {

                        method:

                            "POST",



                        headers: {

                            "Content-Type":

                                "application/json"

                        },



                        body:

                            JSON.stringify({

                                temperatura,

                                latidos,

                                presion

                            })

                    }

                );





                const resultado =

                    datos.resultado || {};





                const contenedor =

                    obtenerElemento(

                        "resultadoSemana7"

                    );





                mostrarElemento(

                    contenedor

                );





                const numerica =

                    resultado.numerica ||

                    resultado.representacion_numerica ||

                    {};





                const simbolica =

                    resultado.simbolica ||

                    resultado.representacion_simbolica ||

                    {};





                const automata =

                    resultado.automata ||

                    {};





                const integrado =

                    resultado.integrado ||

                    resultado.resultado_integrado ||

                    resultado.conclusion ||

                    {};





                const elementoNumerica =

                    obtenerElemento(

                        "semana7Numerica"

                    );





                if (elementoNumerica) {



                    elementoNumerica.innerHTML = `

                        <pre>${escaparHTML(

                            JSON.stringify(

                                numerica,

                                null,

                                2

                            )

                        )}</pre>

                    `;

                }





                const elementoSimbolica =

                    obtenerElemento(

                        "semana7Simbolica"

                    );





                if (elementoSimbolica) {



                    elementoSimbolica.innerHTML = `

                        <pre>${escaparHTML(

                            JSON.stringify(

                                simbolica,

                                null,

                                2

                            )

                        )}</pre>

                    `;

                }





                const elementoAutomata =

                    obtenerElemento(

                        "semana7Automata"

                    );





                if (elementoAutomata) {



                    elementoAutomata.innerHTML = `

                        <pre>${escaparHTML(

                            JSON.stringify(

                                automata,

                                null,

                                2

                            )

                        )}</pre>

                    `;

                }





                const elementoIntegrado =

                    obtenerElemento(

                        "semana7Integrado"

                    );





                if (elementoIntegrado) {



                    elementoIntegrado.innerHTML = `

                        <pre>${escaparHTML(

                            JSON.stringify(

                                integrado,

                                null,

                                2

                            )

                        )}</pre>

                    `;

                }





            } catch (error) {



                mostrarToast(

                    error.message,

                    "error"

                );

            }

        }

    );

}





// ==========================================================

// SEMANA 8

// ==========================================================



const semana8DropZone =

    obtenerElemento(

        "semana8DropZone"

    );





const semana8InputArchivo =

    obtenerElemento(

        "semana8Archivo"

    );





const semana8ArchivoSeleccionado =

    obtenerElemento(

        "semana8ArchivoSeleccionado"

    );





const semana8NombreArchivo =

    obtenerElemento(

        "semana8NombreArchivo"

    );





const semana8TamanoArchivo =

    obtenerElemento(

        "semana8TamanoArchivo"

    );





const btnQuitarArchivoSemana8 =

    obtenerElemento(

        "btnQuitarArchivoSemana8"

    );





const btnAnalizarSemana8 =

    obtenerElemento(

        "btnAnalizarSemana8"

    );





const semana8Procesando =

    obtenerElemento(

        "semana8Procesando"

    );





let archivoActualSemana8 = null;





const extensionesSemana8 = [

    ".pdf",

    ".png",

    ".jpg",

    ".jpeg",

    ".webp"

];





const TAMANO_MAXIMO_SEMANA8 =

    15 * 1024 * 1024;





// ==========================================================

// VALIDAR ARCHIVO SEMANA 8

// ==========================================================



function validarArchivoSemana8(

    archivo

) {



    if (!archivo) {



        return {

            valido:

                false,



            mensaje:

                "No se seleccionó ningún archivo."

        };

    }





    const nombre =

        archivo.name.toLowerCase();





    const extensionValida =

        extensionesSemana8.some(

            extension =>

                nombre.endsWith(

                    extension

                )

        );





    if (!extensionValida) {



        return {

            valido:

                false,



            mensaje:

                (

                    "Formato no permitido. " +

                    "Utilice PDF, PNG, JPG, JPEG o WEBP."

                )

        };

    }





    if (

        archivo.size >

        TAMANO_MAXIMO_SEMANA8

    ) {



        return {

            valido:

                false,



            mensaje:

                "El archivo supera el límite de 15 MB."

        };

    }





    return {

        valido:

            true

    };

}





// ==========================================================

// SELECCIONAR ARCHIVO

// ==========================================================



function seleccionarArchivoSemana8(

    archivo

) {



    const validacion =

        validarArchivoSemana8(

            archivo

        );





    if (!validacion.valido) {



        archivoActualSemana8 = null;



        mostrarToast(

            validacion.mensaje,

            "error"

        );



        return;

    }





    archivoActualSemana8 =

        archivo;





    if (

        semana8NombreArchivo

    ) {



        semana8NombreArchivo.textContent =

            archivo.name;

    }





    if (

        semana8TamanoArchivo

    ) {



        semana8TamanoArchivo.textContent =

            formatearTamano(

                archivo.size

            );

    }





    mostrarElemento(

        semana8ArchivoSeleccionado

    );





    limpiarResultadoSemana8();

}





// ==========================================================

// QUITAR ARCHIVO

// ==========================================================



function quitarArchivoSemana8() {



    archivoActualSemana8 =

        null;





    if (

        semana8InputArchivo

    ) {



        semana8InputArchivo.value =

            "";

    }





    ocultarElemento(

        semana8ArchivoSeleccionado

    );





    limpiarResultadoSemana8();

}





// ==========================================================

// CLICK DROPZONE

// ==========================================================



if (

    semana8DropZone &&

    semana8InputArchivo

) {



    semana8DropZone.addEventListener(

        "click",

        () => {



            semana8InputArchivo.click();

        }

    );

}





// ==========================================================

// INPUT ARCHIVO

// ==========================================================



if (

    semana8InputArchivo

) {



    semana8InputArchivo.addEventListener(

        "change",

        evento => {



            const archivo =

                evento.target.files?.[0];





            if (archivo) {



                seleccionarArchivoSemana8(

                    archivo

                );

            }

        }

    );

}





// ==========================================================

// DRAG AND DROP

// ==========================================================



if (

    semana8DropZone

) {



    [

        "dragenter",

        "dragover"

    ].forEach(

        eventoNombre => {



            semana8DropZone.addEventListener(

                eventoNombre,

                evento => {



                    evento.preventDefault();



                    evento.stopPropagation();



                    semana8DropZone.classList.add(

                        "dragging"

                    );

                }

            );

        }

    );





    [

        "dragleave",

        "drop"

    ].forEach(

        eventoNombre => {



            semana8DropZone.addEventListener(

                eventoNombre,

                evento => {



                    evento.preventDefault();



                    evento.stopPropagation();



                    semana8DropZone.classList.remove(

                        "dragging"

                    );

                }

            );

        }

    );





    semana8DropZone.addEventListener(

        "drop",

        evento => {



            const archivo =

                evento.dataTransfer

                    ?.files?.[0];





            if (archivo) {



                seleccionarArchivoSemana8(

                    archivo

                );

            }

        }

    );

}





// ==========================================================

// QUITAR ARCHIVO

// ==========================================================



if (

    btnQuitarArchivoSemana8

) {



    btnQuitarArchivoSemana8.addEventListener(

        "click",

        evento => {



            evento.preventDefault();



            evento.stopPropagation();



            quitarArchivoSemana8();

        }

    );

}





// ==========================================================

// LIMPIAR RESULTADO SEMANA 8

// ==========================================================



function limpiarResultadoSemana8() {



    ocultarElemento(

        obtenerElemento(

            "resultadoSemana8"

        )

    );





    ocultarElemento(

        obtenerElemento(

            "resultadoSemana8PDF"

        )

    );





    ocultarElemento(

        obtenerElemento(

            "resultadoSemana8Imagen"

        )

    );





    ocultarElemento(

        obtenerElemento(

            "semana8InterpretacionClinica"

        )

    );





    ocultarElemento(

        obtenerElemento(

            "semana8OCR"

        )

    );

}





// ==========================================================

// CARGAR RESUMEN SEMANA 8

// ==========================================================



async function cargarResumenSemana8() {



    try {



        const datos =

            await apiJSON(

                "/api/semana8/resumen"

            );





        const resultado =

            datos.resultado || {};





        const evidencia =

            resultado.evidencia ||

            resultado.base ||

            {};





        const ontologia =

            resultado.ontologia ||

            {};





        const accuracy =

            resultado.accuracy;





        const elementoAccuracy =

            obtenerElemento(

                "semana8Accuracy"

            );





        if (elementoAccuracy) {



            elementoAccuracy.textContent =

                accuracy !== null &&

                accuracy !== undefined

                    ? porcentaje(

                        accuracy

                    )

                    : "--";

        }





        const documentos =

            obtenerElemento(

                "semana8Documentos"

            );





        if (documentos) {



            documentos.textContent =

                valorSeguro(

                    evidencia.documentos,

                    0

                );

        }





        const resultados =

            obtenerElemento(

                "semana8Resultados"

            );





        if (resultados) {



            resultados.textContent =

                valorSeguro(

                    evidencia.resultados_extraidos,

                    0

                );

        }





        const imagenes =

            obtenerElemento(

                "semana8Imagenes"

            );





        if (imagenes) {



            imagenes.textContent =

                valorSeguro(

                    evidencia.imagenes_reconocidas,

                    0

                );

        }





        const nodos =

            obtenerElemento(

                "semana8Nodos"

            );





        if (nodos) {



            nodos.textContent =

                valorSeguro(

                    ontologia.nodos,

                    0

                );

        }





        const relaciones =

            obtenerElemento(

                "semana8Relaciones"

            );





        if (relaciones) {



            relaciones.textContent =

                valorSeguro(

                    ontologia.relaciones,

                    0

                );

        }





    } catch (error) {



        console.error(

            "Error resumen Semana 8:",

            error

        );

    }

}





// ==========================================================

// ESTADO CLÍNICO

// ==========================================================



function claseEstadoClinico(

    estado

) {



    const normalizado =

        normalizarTexto(

            estado

        );





    if (

        normalizado ===

        "dentro de referencia"

    ) {



        return "status-normal";

    }





    if (

        normalizado === "alto"

    ) {



        return "status-high";

    }





    if (

        normalizado === "bajo"

    ) {



        return "status-low";

    }





    return "status-unknown";

}





// ==========================================================

// ETIQUETA DE ESTADO

// ==========================================================



function crearBadgeEstado(

    estado

) {



    const texto =

        valorSeguro(

            estado,

            "NO EVALUABLE"

        );





    return `

        <span class="

            clinical-status

            ${claseEstadoClinico(texto)}

        ">

            ${escaparHTML(texto)}

        </span>

    `;

}





// ==========================================================

// MAPA DE RESULTADOS INTERPRETADOS

// ==========================================================



function crearMapaInterpretacion(

    interpretacion

) {



    const mapa =

        new Map();





    const resultados =

        interpretacion?.resultados ||

        [];





    resultados.forEach(

        resultado => {



            const clave =

                normalizarTexto(

                    resultado.examen

                );





            if (clave) {



                mapa.set(

                    clave,

                    resultado

                );

            }

        }

    );





    return mapa;

}





// ==========================================================

// MOSTRAR RESULTADO PDF

// ==========================================================



function mostrarResultadoPDFSemana8(

    respuesta

) {



    const resultado =

        respuesta.resultado ||

        {};





    mostrarElemento(

        obtenerElemento(

            "resultadoSemana8"

        )

    );





    mostrarElemento(

        obtenerElemento(

            "resultadoSemana8PDF"

        )

    );





    ocultarElemento(

        obtenerElemento(

            "resultadoSemana8Imagen"

        )

    );





    const titulo =

        obtenerElemento(

            "semana8ResultadoTitulo"

        );





    if (titulo) {



        titulo.textContent =

            "Documento médico procesado";

    }





    const tipo =

        obtenerElemento(

            "semana8ResultadoTipo"

        );





    if (tipo) {



        tipo.textContent =

            "PDF";

    }





    // ======================================================

    // DATOS DEL PACIENTE

    // ======================================================



    const paciente =

        resultado.paciente ||

        {};





    const campoPaciente =

        obtenerElemento(

            "semana8Paciente"

        );





    if (campoPaciente) {



        campoPaciente.textContent =

            valorSeguro(

                paciente.nombre,

                "No detectado"

            );

    }





    const identificacion =

        obtenerElemento(

            "semana8Identificacion"

        );





    if (identificacion) {



        identificacion.textContent =

            valorSeguro(

                paciente.identificacion,

                "No detectada"

            );

    }





    const fecha =

        obtenerElemento(

            "semana8Fecha"

        );





    if (fecha) {



        fecha.textContent =

            valorSeguro(

                paciente.fecha,

                "No detectada"

            );

    }





    const tipoDocumento =

        obtenerElemento(

            "semana8TipoDocumento"

        );





    if (tipoDocumento) {



        tipoDocumento.textContent =

            valorSeguro(

                resultado.tipo_documento,

                "No identificado"

            );

    }





    // ======================================================

    // OCR

    // ======================================================



    const alertaOCR =

        obtenerElemento(

            "semana8OCR"

        );





    if (

        resultado.requiere_ocr

    ) {



        mostrarElemento(

            alertaOCR

        );



    } else {



        ocultarElemento(

            alertaOCR

        );

    }





    // ======================================================

    // INTERPRETACIÓN

    // ======================================================



    const interpretacion =

        resultado.interpretacion_clinica ||

        null;





    const mapaInterpretacion =

        crearMapaInterpretacion(

            interpretacion

        );





    // ======================================================

    // TABLA EXÁMENES

    // ======================================================



    const examenes =

        resultado.examenes ||

        [];





    const cantidad =

        obtenerElemento(

            "semana8CantidadExamenes"

        );





    if (cantidad) {



        cantidad.textContent =

            examenes.length;

    }





    const tabla =

        obtenerElemento(

            "semana8TablaExamenes"

        );





    if (tabla) {



        if (

            examenes.length === 0

        ) {



            tabla.innerHTML = `

                <tr>

                    <td

                        colspan="6"

                        class="empty-cell"

                    >

                        No se detectaron resultados

                        de laboratorio.

                    </td>

                </tr>

            `;



        } else {



            tabla.innerHTML =

                examenes

                    .map(examen => {



                        const interpretado =

                            mapaInterpretacion.get(

                                normalizarTexto(

                                    examen.examen

                                )

                            );





                        const estado =

                            interpretado?.estado ||

                            "NO EVALUABLE";





                        return `

                            <tr>



                                <td>

                                    <strong>

                                        ${escaparHTML(

                                            valorSeguro(

                                                examen.examen

                                            )

                                        )}

                                    </strong>

                                </td>



                                <td>

                                    ${escaparHTML(

                                        valorSeguro(

                                            examen.resultado

                                        )

                                    )}

                                </td>



                                <td>

                                    ${escaparHTML(

                                        valorSeguro(

                                            examen.unidad

                                        )

                                    )}

                                </td>



                                <td>

                                    ${escaparHTML(

                                        valorSeguro(

                                            examen.referencia

                                        )

                                    )}

                                </td>



                                <td>

                                    ${crearBadgeEstado(

                                        estado

                                    )}

                                </td>



                                <td>

                                    ${escaparHTML(

                                        valorSeguro(

                                            examen.pagina

                                        )

                                    )}

                                </td>



                            </tr>

                        `;

                    })

                    .join("");

        }

    }





    // ======================================================

    // INTERPRETACIÓN CLÍNICA

    // ======================================================



    mostrarInterpretacionClinica(

        interpretacion,

        resultado.requiere_ocr

    );





    // ======================================================

    // EVIDENCIA

    // ======================================================



    const sqlite =

        obtenerElemento(

            "semana8EstadoSQLite"

        );





    if (sqlite) {



        sqlite.textContent =

            resultado.evidencia_sqlite

                ? "Registrada"

                : "No registrada";

    }





    const ontologia =

        obtenerElemento(

            "semana8EstadoOntologia"

        );





    if (ontologia) {



        ontologia.textContent =

            resultado.ontologia_actualizada

                ? "Actualizada"

                : "Sin actualizar";

    }

}





// ==========================================================

// MOSTRAR INTERPRETACIÓN CLÍNICA

// ==========================================================



function mostrarInterpretacionClinica(

    interpretacion,

    requiereOCR = false

) {



    const contenedor =

        obtenerElemento(

            "semana8InterpretacionClinica"

        );





    if (

        requiereOCR ||

        !interpretacion

    ) {



        ocultarElemento(

            contenedor

        );



        return;

    }





    mostrarElemento(

        contenedor

    );





    // ======================================================

    // CONTADORES

    // ======================================================



    const evaluados =

        obtenerElemento(

            "clinicaEvaluados"

        );





    if (evaluados) {



        evaluados.textContent =

            valorSeguro(

                interpretacion.resultados_evaluados,

                0

            );

    }





    const normales =

        obtenerElemento(

            "clinicaNormales"

        );





    if (normales) {



        normales.textContent =

            valorSeguro(

                interpretacion.normales,

                0

            );

    }





    const altos =

        obtenerElemento(

            "clinicaAltos"

        );





    if (altos) {



        altos.textContent =

            valorSeguro(

                interpretacion.altos,

                0

            );

    }





    const bajos =

        obtenerElemento(

            "clinicaBajos"

        );





    if (bajos) {



        bajos.textContent =

            valorSeguro(

                interpretacion.bajos,

                0

            );

    }





    const noEvaluables =

        obtenerElemento(

            "clinicaNoEvaluables"

        );





    if (noEvaluables) {



        noEvaluables.textContent =

            valorSeguro(

                interpretacion.no_evaluables,

                0

            );

    }





    // ======================================================

    // HALLAZGOS

    // ======================================================



    mostrarHallazgosClinicos(

        interpretacion.hallazgos ||

        []

    );





    // ======================================================

    // CONDICIONES

    // ======================================================



    mostrarCondicionesClinicas(

        interpretacion.posibles_condiciones ||

        []

    );





    // ======================================================

    // CONCLUSIÓN

    // ======================================================



    const conclusion =

        obtenerElemento(

            "clinicaConclusion"

        );





    if (conclusion) {



        conclusion.textContent =

            valorSeguro(

                interpretacion.conclusion,

                "Sin conclusión disponible."

            );

    }





    // ======================================================

    // ADVERTENCIA

    // ======================================================



    const advertencia =

        obtenerElemento(

            "clinicaAdvertencia"

        );





    if (advertencia) {



        advertencia.textContent =

            valorSeguro(

                interpretacion.advertencia,

                (

                    "Esta interpretación es orientativa " +

                    "y no constituye un diagnóstico médico."

                )

            );

    }

}





// ==========================================================

// MOSTRAR HALLAZGOS

// ==========================================================



function mostrarHallazgosClinicos(

    hallazgos

) {



    const contenedor =

        obtenerElemento(

            "clinicaHallazgos"

        );





    if (!contenedor) {

        return;

    }





    if (

        !Array.isArray(

            hallazgos

        ) ||

        hallazgos.length === 0

    ) {



        contenedor.innerHTML = `

            <div class="clinical-empty">



                <strong>

                    Sin alteraciones detectadas

                </strong>



                <p>

                    No se identificaron resultados

                    fuera de los rangos de referencia

                    evaluables.

                </p>



            </div>

        `;



        return;

    }





    contenedor.innerHTML =

        hallazgos

            .map(hallazgo => {



                const estado =

                    valorSeguro(

                        hallazgo.estado,

                        "NO EVALUABLE"

                    );





                return `

                    <article class="clinical-finding">



                        <div class="clinical-finding-header">



                            <strong>

                                ${escaparHTML(

                                    valorSeguro(

                                        hallazgo.examen

                                    )

                                )}

                            </strong>



                            ${crearBadgeEstado(

                                estado

                            )}



                        </div>



                        <div class="clinical-finding-data">



                            <span>

                                Resultado:

                                <strong>

                                    ${escaparHTML(

                                        valorSeguro(

                                            hallazgo.resultado

                                        )

                                    )}



                                    ${escaparHTML(

                                        valorSeguro(

                                            hallazgo.unidad,

                                            ""

                                        )

                                    )}

                                </strong>

                            </span>



                            <span>

                                Referencia:

                                <strong>

                                    ${escaparHTML(

                                        valorSeguro(

                                            hallazgo.referencia

                                        )

                                    )}

                                </strong>

                            </span>



                        </div>



                    </article>

                `;

            })

            .join("");

}





// ==========================================================

// MOSTRAR CONDICIONES CLÍNICAS

// ==========================================================



function mostrarCondicionesClinicas(

    condiciones

) {



    const contenedor =

        obtenerElemento(

            "clinicaCondiciones"

        );





    if (!contenedor) {

        return;

    }





    if (

        !Array.isArray(

            condiciones

        ) ||

        condiciones.length === 0

    ) {



        contenedor.innerHTML = `

            <div class="clinical-empty">



                <strong>

                    Sin patrones alterados

                </strong>



                <p>

                    No se identificaron condiciones

                    específicas asociadas con los

                    resultados evaluados.

                </p>



            </div>

        `;



        return;

    }





    contenedor.innerHTML =

        condiciones

            .map(condicion => {



                const examenes =

                    Array.isArray(

                        condicion.examenes_relacionados

                    )

                        ? condicion

                            .examenes_relacionados

                            .join(", ")

                        : valorSeguro(

                            condicion.examenes_relacionados,

                            "No especificados"

                        );





                const nivel =

                    valorSeguro(

                        condicion.nivel,

                        "orientativo"

                    );





                return `

                    <article class="clinical-condition">



                        <div class="clinical-condition-header">



                            <div>



                                <span class="condition-label">

                                    Posible condición

                                </span>



                                <h4>

                                    ${escaparHTML(

                                        valorSeguro(

                                            condicion.condicion

                                        )

                                    )}

                                </h4>



                            </div>



                            <span class="condition-level">

                                ${escaparHTML(

                                    nivel

                                )}

                            </span>



                        </div>





                        <p>

                            ${escaparHTML(

                                valorSeguro(

                                    condicion.descripcion

                                )

                            )}

                        </p>





                        <div class="condition-exams">



                            <span>

                                Exámenes relacionados

                            </span>



                            <strong>

                                ${escaparHTML(

                                    examenes

                                )}

                            </strong>



                        </div>



                    </article>

                `;

            })

            .join("");

}





// ==========================================================

// MOSTRAR RESULTADO DE IMAGEN

// ==========================================================



function mostrarResultadoImagenSemana8(

    respuesta

) {



    const resultado =

        respuesta.resultado ||

        {};





    mostrarElemento(

        obtenerElemento(

            "resultadoSemana8"

        )

    );





    mostrarElemento(

        obtenerElemento(

            "resultadoSemana8Imagen"

        )

    );





    ocultarElemento(

        obtenerElemento(

            "resultadoSemana8PDF"

        )

    );





    ocultarElemento(

        obtenerElemento(

            "semana8InterpretacionClinica"

        )

    );





    const titulo =

        obtenerElemento(

            "semana8ResultadoTitulo"

        );





    if (titulo) {



        titulo.textContent =

            "Imagen reconocida por MLP";

    }





    const tipo =

        obtenerElemento(

            "semana8ResultadoTipo"

        );





    if (tipo) {



        tipo.textContent =

            "IMAGEN";

    }





    const prediccion =

        obtenerElemento(

            "semana8Prediccion"

        );





    if (prediccion) {



        prediccion.textContent =

            valorSeguro(

                resultado.prediccion

            );

    }





    const confianza =

        obtenerElemento(

            "semana8Confianza"

        );





    if (confianza) {



        confianza.textContent =

            porcentaje(

                resultado.confianza

            );

    }





    const accuracy =

        obtenerElemento(

            "semana8AccuracyResultado"

        );





    if (accuracy) {



        accuracy.textContent =

            porcentaje(

                resultado.accuracy_modelo

            );

    }





    const sqliteID =

        obtenerElemento(

            "semana8SQLiteImagen"

        );





    if (sqliteID) {



        sqliteID.textContent =

            valorSeguro(

                resultado.reconocimiento_id

            );

    }





    const sqlite =

        obtenerElemento(

            "semana8EstadoSQLite"

        );





    if (sqlite) {



        sqlite.textContent =

            resultado.evidencia_sqlite

                ? "Registrada"

                : "No registrada";

    }





    const ontologia =

        obtenerElemento(

            "semana8EstadoOntologia"

        );





    if (ontologia) {



        ontologia.textContent =

            resultado.ontologia_actualizada

                ? "Actualizada"

                : "Sin actualizar";

    }

}





// ==========================================================

// ANALIZAR ARCHIVO SEMANA 8

// ==========================================================



if (

    btnAnalizarSemana8

) {



    btnAnalizarSemana8.addEventListener(

        "click",

        async () => {



            if (!archivoActualSemana8) {



                mostrarToast(

                    "Primero seleccione un archivo.",

                    "error"

                );



                return;

            }





            const validacion =

                validarArchivoSemana8(

                    archivoActualSemana8

                );





            if (!validacion.valido) {



                mostrarToast(

                    validacion.mensaje,

                    "error"

                );



                return;

            }





            const formData =

                new FormData();





            formData.append(

                "archivo",

                archivoActualSemana8

            );





            ocultarElemento(

                obtenerElemento(

                    "resultadoSemana8"

                )

            );





            mostrarElemento(

                semana8Procesando

            );





            btnAnalizarSemana8.disabled =

                true;





            try {



                const respuesta =

                    await fetch(

                        "/api/semana8/archivo",

                        {

                            method:

                                "POST",



                            body:

                                formData

                        }

                    );





                let datos;





                try {



                    datos =

                        await respuesta.json();



                } catch {



                    throw new Error(

                        "El servidor no devolvió una respuesta JSON válida."

                    );

                }





                if (

                    !respuesta.ok ||

                    datos.ok === false

                ) {



                    throw new Error(

                        datos.error ||

                        datos.detalle ||

                        "No fue posible analizar el archivo."

                    );

                }





                const paqueteSemana8 =
                    datos.resultado ||
                    datos;


                const tipo =
                    normalizarTexto(
                        paqueteSemana8.tipo
                    );


                const respuestaSemana8 = {
                    ...datos,
                    tipo:
                        paqueteSemana8.tipo,
                    resultado:
                        paqueteSemana8.resultado ||
                        paqueteSemana8
                };


                if (
                    tipo === "pdf"
                ) {

                    mostrarResultadoPDFSemana8(
                        respuestaSemana8
                    );

                } else {

                    mostrarResultadoImagenSemana8(
                        respuestaSemana8
                    );

                }





                mostrarToast(

                    "Archivo analizado correctamente.",

                    "success"

                );





                await cargarResumenSemana8();





                const resultado =

                    obtenerElemento(

                        "resultadoSemana8"

                    );





                if (resultado) {



                    resultado.scrollIntoView({

                        behavior:

                            "smooth",



                        block:

                            "start"

                    });

                }





            } catch (error) {



                mostrarToast(

                    error.message,

                    "error"

                );





                console.error(

                    error

                );





            } finally {



                ocultarElemento(

                    semana8Procesando

                );





                btnAnalizarSemana8.disabled =

                    false;

            }

        }

    );

}





// ==========================================================

// ACTUALIZAR RESUMEN SEMANA 8

// ==========================================================



const btnActualizarSemana8 =

    obtenerElemento(

        "btnActualizarSemana8"

    );





if (

    btnActualizarSemana8

) {



    btnActualizarSemana8.addEventListener(

        "click",

        async () => {



            await cargarResumenSemana8();





            mostrarToast(

                "Evidencia actualizada.",

                "success"

            );

        }

    );

}


// ==========================================================

// SEMANA 9

// ==========================================================

let archivoActualSemana9 = null;
let urlPreviewSemana9 = null;


const semana9DropZone =
    obtenerElemento(
        "semana9DropZone"
    );

const semana9Archivo =
    obtenerElemento(
        "semana9Archivo"
    );

const semana9ArchivoSeleccionado =
    obtenerElemento(
        "semana9ArchivoSeleccionado"
    );

const btnQuitarArchivoSemana9 =
    obtenerElemento(
        "btnQuitarArchivoSemana9"
    );

const btnAnalizarSemana9 =
    obtenerElemento(
        "btnAnalizarSemana9"
    );

const semana9Procesando =
    obtenerElemento(
        "semana9Procesando"
    );


function validarArchivoSemana9(
    archivo
) {

    if (!archivo) {

        return {
            valido: false,
            mensaje:
                "Seleccione una imagen."
        };

    }


    const extension =
        archivo.name
            .split(".")
            .pop()
            .toLowerCase();


    const permitidas = [
        "png",
        "jpg",
        "jpeg",
        "webp",
        "bmp",
        "tif",
        "tiff"
    ];


    if (
        !permitidas.includes(
            extension
        )
    ) {

        return {
            valido: false,
            mensaje:
                "Formato no permitido para Semana 9."
        };

    }


    const maximo =
        20 * 1024 * 1024;


    if (
        archivo.size > maximo
    ) {

        return {
            valido: false,
            mensaje:
                "La imagen supera el límite de 20 MB."
        };

    }


    return {
        valido: true,
        mensaje: ""
    };

}


function limpiarSemana9() {

    archivoActualSemana9 =
        null;


    if (
        urlPreviewSemana9
    ) {

        URL.revokeObjectURL(
            urlPreviewSemana9
        );

        urlPreviewSemana9 =
            null;

    }


    if (
        semana9Archivo
    ) {

        semana9Archivo.value =
            "";

    }


    ocultarElemento(
        semana9ArchivoSeleccionado
    );


    ocultarElemento(
        obtenerElemento(
            "semana9VistaPrevia"
        )
    );


    ocultarElemento(
        obtenerElemento(
            "resultadoSemana9"
        )
    );


    const preview =
        obtenerElemento(
            "semana9Preview"
        );


    if (preview) {

        preview.removeAttribute(
            "src"
        );

    }

}


function seleccionarArchivoSemana9(
    archivo
) {

    const validacion =
        validarArchivoSemana9(
            archivo
        );


    if (
        !validacion.valido
    ) {

        mostrarToast(
            validacion.mensaje,
            "error"
        );

        return;

    }


    archivoActualSemana9 =
        archivo;


    const nombre =
        obtenerElemento(
            "semana9NombreArchivo"
        );


    if (nombre) {

        nombre.textContent =
            archivo.name;

    }


    const tamano =
        obtenerElemento(
            "semana9TamanoArchivo"
        );


    if (tamano) {

        tamano.textContent =
            formatearTamano(
                archivo.size
            );

    }


    mostrarElemento(
        semana9ArchivoSeleccionado
    );


    if (
        urlPreviewSemana9
    ) {

        URL.revokeObjectURL(
            urlPreviewSemana9
        );

    }


    urlPreviewSemana9 =
        URL.createObjectURL(
            archivo
        );


    const preview =
        obtenerElemento(
            "semana9Preview"
        );


    if (preview) {

        preview.src =
            urlPreviewSemana9;

    }


    mostrarElemento(
        obtenerElemento(
            "semana9VistaPrevia"
        )
    );


    ocultarElemento(
        obtenerElemento(
            "resultadoSemana9"
        )
    );

}


if (
    semana9DropZone &&
    semana9Archivo
) {

    semana9DropZone.addEventListener(
        "click",
        () => {

            semana9Archivo.click();

        }
    );


    semana9Archivo.addEventListener(
        "change",
        evento => {

            const archivo =
                evento.target.files?.[0];

            if (archivo) {

                seleccionarArchivoSemana9(
                    archivo
                );

            }

        }
    );


    [
        "dragenter",
        "dragover"
    ].forEach(
        eventoNombre => {

            semana9DropZone.addEventListener(
                eventoNombre,
                evento => {

                    evento.preventDefault();

                    semana9DropZone.classList.add(
                        "dragging"
                    );

                }
            );

        }
    );


    [
        "dragleave",
        "drop"
    ].forEach(
        eventoNombre => {

            semana9DropZone.addEventListener(
                eventoNombre,
                evento => {

                    evento.preventDefault();

                    semana9DropZone.classList.remove(
                        "dragging"
                    );

                }
            );

        }
    );


    semana9DropZone.addEventListener(
        "drop",
        evento => {

            const archivo =
                evento.dataTransfer
                    ?.files?.[0];

            if (archivo) {

                seleccionarArchivoSemana9(
                    archivo
                );

            }

        }
    );

}


if (
    btnQuitarArchivoSemana9
) {

    btnQuitarArchivoSemana9.addEventListener(
        "click",
        limpiarSemana9
    );

}


function renderComparacionSigmaSemana9(
    comparacion
) {

    const contenedor =
        obtenerElemento(
            "semana9ComparacionSigma"
        );


    if (!contenedor) {

        return;

    }


    const datos =
        Array.isArray(
            comparacion
        )
            ? comparacion
            : [];


    if (!datos.length) {

        contenedor.innerHTML = `
            <div class="empty-state">
                No hay comparación de sigma disponible.
            </div>
        `;

        return;

    }


    const maximo =
        Math.max(
            ...datos.map(
                item =>
                    Number(
                        item.pixeles_borde
                    ) || 0
            ),
            1
        );


    contenedor.innerHTML =
        datos
            .map(item => {

                const bordes =
                    Number(
                        item.pixeles_borde
                    ) || 0;


                const ancho =
                    Math.max(
                        4,
                        (
                            bordes /
                            maximo
                        ) * 100
                    );


                return `
                    <div class="week9-sigma-item">
                        <div class="week9-sigma-head">
                            <strong>
                                Sigma ${escaparHTML(
                                    valorSeguro(
                                        item.sigma
                                    )
                                )}
                            </strong>

                            <span>
                                ${bordes.toLocaleString("es-CO")}
                                bordes
                            </span>
                        </div>

                        <div class="week9-sigma-track">
                            <div
                                class="week9-sigma-fill"
                                style="width: ${ancho.toFixed(2)}%;"
                            >
                            </div>
                        </div>

                        <small>
                            ${escaparHTML(
                                valorSeguro(
                                    item.porcentaje_borde,
                                    0
                                )
                            )}% de la imagen
                        </small>
                    </div>
                `;

            })
            .join("");

}


function renderRegionesSemana9(
    regiones
) {

    const tabla =
        obtenerElemento(
            "semana9TablaRegiones"
        );


    if (!tabla) {

        return;

    }


    const datos =
        Array.isArray(
            regiones
        )
            ? regiones.slice(
                0,
                10
            )
            : [];


    if (!datos.length) {

        tabla.innerHTML = `
            <tr>
                <td
                    colspan="5"
                    class="empty-cell"
                >
                    No se detectaron regiones que cumplan
                    el área mínima seleccionada.
                </td>
            </tr>
        `;

        return;

    }


    tabla.innerHTML =
        datos
            .map(
                (region, indice) => `
                    <tr>
                        <td>
                            ${escaparHTML(
                                valorSeguro(
                                    region.etiqueta,
                                    indice + 1
                                )
                            )}
                        </td>

                        <td>
                            ${Number(
                                region.area || 0
                            ).toLocaleString(
                                "es-CO"
                            )}
                        </td>

                        <td>
                            ${escaparHTML(
                                Array.isArray(
                                    region.centroide
                                )
                                    ? region.centroide.join(
                                        ", "
                                    )
                                    : "--"
                            )}
                        </td>

                        <td>
                            ${escaparHTML(
                                valorSeguro(
                                    region.solidez
                                )
                            )}
                        </td>

                        <td>
                            ${escaparHTML(
                                valorSeguro(
                                    region.excentricidad
                                )
                            )}
                        </td>
                    </tr>
                `
            )
            .join("");

}


function mostrarResultadoSemana9(
    resultado
) {

    const contenedor =
        obtenerElemento(
            "resultadoSemana9"
        );


    mostrarElemento(
        contenedor
    );


    const sigma =
        obtenerElemento(
            "semana9ResultadoSigma"
        );


    if (sigma) {

        sigma.textContent =
            valorSeguro(
                resultado.sigma
            );

    }


    const umbral =
        obtenerElemento(
            "semana9Umbral"
        );


    if (umbral) {

        const valor =
            Number(
                resultado.umbral_otsu
            );


        umbral.textContent =
            Number.isFinite(
                valor
            )
                ? valor.toFixed(
                    6
                )
                : "--";

    }


    const bordes =
        obtenerElemento(
            "semana9Bordes"
        );


    if (bordes) {

        bordes.textContent =
            Number(
                resultado.pixeles_borde ||
                0
            )
            .toLocaleString(
                "es-CO"
            );

    }


    const porcentajeBorde =
        obtenerElemento(
            "semana9PorcentajeBorde"
        );


    if (
        porcentajeBorde
    ) {

        porcentajeBorde.textContent =
            `${
                Number(
                    resultado.porcentaje_borde ||
                    0
                ).toFixed(4)
            }%`;

    }


    const regiones =
        obtenerElemento(
            "semana9Regiones"
        );


    if (regiones) {

        regiones.textContent =
            valorSeguro(
                resultado.regiones_detectadas,
                0
            );

    }


    const evidencia =
        obtenerElemento(
            "semana9Evidencia"
        );


    if (evidencia) {

        evidencia.src =
            resultado.evidencia_visual_url ||
            resultado.evidencia_visual ||
            "";

    }


    const regionPrincipal =
        resultado.region_principal ||
        {};


    const regionContenedor =
        obtenerElemento(
            "semana9RegionPrincipal"
        );


    const regionVacia =
        obtenerElemento(
            "semana9RegionPrincipalVacia"
        );


    if (
        regionPrincipal.archivo ||
        regionPrincipal.archivo_url
    ) {

        mostrarElemento(
            regionContenedor
        );

        ocultarElemento(
            regionVacia
        );


        const imagenRegion =
            obtenerElemento(
                "semana9RegionImagen"
            );


        if (imagenRegion) {

            imagenRegion.src =
                regionPrincipal.archivo_url ||
                regionPrincipal.archivo;

        }


        const area =
            obtenerElemento(
                "semana9RegionArea"
            );


        if (area) {

            area.textContent =
                Number(
                    regionPrincipal.area ||
                    0
                )
                .toLocaleString(
                    "es-CO"
                );

        }


        const bbox =
            obtenerElemento(
                "semana9RegionBBox"
            );


        if (bbox) {

            bbox.textContent =
                Array.isArray(
                    regionPrincipal.bbox
                )
                    ? regionPrincipal.bbox.join(
                        ", "
                    )
                    : "--";

        }


    } else {

        ocultarElemento(
            regionContenedor
        );

        mostrarElemento(
            regionVacia
        );

    }


    renderComparacionSigmaSemana9(
        resultado.comparacion_sigma
    );


    renderRegionesSemana9(
        resultado.regiones
    );

}


if (
    btnAnalizarSemana9
) {

    btnAnalizarSemana9.addEventListener(
        "click",
        async () => {

            const validacion =
                validarArchivoSemana9(
                    archivoActualSemana9
                );


            if (
                !validacion.valido
            ) {

                mostrarToast(
                    validacion.mensaje,
                    "error"
                );

                return;

            }


            const sigma =
                Number(
                    obtenerElemento(
                        "semana9Sigma"
                    )?.value
                );


            const areaMinima =
                Number(
                    obtenerElemento(
                        "semana9AreaMinima"
                    )?.value
                );


            if (
                !Number.isFinite(
                    sigma
                ) ||
                sigma <= 0
            ) {

                mostrarToast(
                    "Sigma debe ser mayor que cero.",
                    "error"
                );

                return;

            }


            if (
                !Number.isInteger(
                    areaMinima
                ) ||
                areaMinima < 1
            ) {

                mostrarToast(
                    "El área mínima debe ser un entero mayor o igual a 1.",
                    "error"
                );

                return;

            }


            const formData =
                new FormData();


            formData.append(
                "archivo",
                archivoActualSemana9
            );


            formData.append(
                "sigma",
                String(
                    sigma
                )
            );


            formData.append(
                "area_minima",
                String(
                    areaMinima
                )
            );


            ocultarElemento(
                obtenerElemento(
                    "resultadoSemana9"
                )
            );


            mostrarElemento(
                semana9Procesando
            );


            btnAnalizarSemana9.disabled =
                true;


            try {

                const datos =
                    await apiJSON(
                        "/api/semana9/imagen",
                        {
                            method:
                                "POST",

                            body:
                                formData
                        }
                    );


                const paquete =
                    datos.resultado ||
                    datos;


                const resultado =
                    paquete.resultado ||
                    paquete;


                mostrarResultadoSemana9(
                    resultado
                );


                mostrarToast(
                    "Imagen procesada correctamente.",
                    "success"
                );


                const salida =
                    obtenerElemento(
                        "resultadoSemana9"
                    );


                if (salida) {

                    salida.scrollIntoView({
                        behavior:
                            "smooth",

                        block:
                            "start"
                    });

                }


            } catch (error) {

                mostrarToast(
                    error.message,
                    "error"
                );


                console.error(
                    "Error Semana 9:",
                    error
                );


            } finally {

                ocultarElemento(
                    semana9Procesando
                );


                btnAnalizarSemana9.disabled =
                    false;

            }
        }
    );

}


// ==========================================================

// ASISTENTE IA

// ==========================================================

const formAsistente =
    obtenerElemento(
        "formAsistente"
    );


function agregarMensajeAsistente(
    tipo,
    mensaje
) {

    const contenedor =
        obtenerElemento(
            "assistantMessages"
        );


    if (!contenedor) {
        return;
    }


    const elemento =
        document.createElement(
            "div"
        );


    elemento.className =
        `assistant-message ${tipo}`;


    const avatar =
        tipo === "user"
            ? "TÚ"
            : "IA";


    elemento.innerHTML = `
        <div class="message-avatar">
            ${avatar}
        </div>

        <div class="message-content">
            <strong>
                ${
                    tipo === "user"
                        ? "Usuario"
                        : "HIS_IA"
                }
            </strong>

            <p>
                ${escaparHTML(
                    mensaje
                )}
            </p>
        </div>
    `;


    contenedor.appendChild(
        elemento
    );


    contenedor.scrollTop =
        contenedor.scrollHeight;

}


if (
    formAsistente
) {

    formAsistente.addEventListener(
        "submit",
        async evento => {

            evento.preventDefault();


            const input =
                obtenerElemento(
                    "mensajeAsistente"
                );


            const mensaje =
                input?.value.trim();


            if (!mensaje) {
                return;
            }


            agregarMensajeAsistente(
                "user",
                mensaje
            );


            input.value =
                "";


            try {

                const datos = await apiJSON(
                    "/api/asistente",
                    {
                        method:
                            "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify({
                                consulta:
                                    mensaje
                            })
                    }
                );


                const resultado =
                    datos.resultado ||
                    datos.respuesta ||
                    {};


                let respuesta;


                if (
                    typeof resultado ===
                    "string"
                ) {

                    respuesta =
                        resultado;

                } else {

                    const reglas =
                        Array.isArray(
                            resultado.reglas
                        )
                            ? resultado.reglas.join(
                                ", "
                            )
                            : "Sin regla específica";


                    respuesta = [
                        `Categoría: ${
                            valorSeguro(
                                resultado.clase,
                                "No identificada"
                            )
                        }`,
                        `Acciones: ${reglas}`,
                        `Información relacionada: ${
                            valorSeguro(
                                resultado.evidencia,
                                "Sin evidencia"
                            )
                        }`,
                        `Similitud: ${
                            resultado.similitud !==
                            undefined
                                ? Number(
                                    resultado.similitud
                                ).toFixed(
                                    3
                                )
                                : "--"
                        }`
                    ].join(
                        "\n"
                    );

                }


                agregarMensajeAsistente(
                    "bot",
                    respuesta
                );


            } catch (error) {

                agregarMensajeAsistente(
                    "bot",
                    "No fue posible procesar la consulta."
                );


                mostrarToast(
                    error.message,
                    "error"
                );

            }
        }
    );

}


// ==========================================================

// INICIALIZACIÓN

// ==========================================================



document.addEventListener(

    "DOMContentLoaded",

    () => {



        cambiarSeccion(

            "inicio"

        );





        cargarResumenSemana8();

    }

);
