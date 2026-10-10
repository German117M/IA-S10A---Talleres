"use strict";

document.addEventListener("DOMContentLoaded", () => {

    let imagenReferencia = null;
    let imagenComparacion = null;

    let urlReferencia = null;
    let urlComparacion = null;


    // ======================================================
    // UTILIDADES
    // ======================================================

    function el(id) {
        return document.getElementById(id);
    }

    function setText(id, value) {
        const nodo = el(id);
        if (nodo) nodo.textContent = value;
    }

    function show(id) {
        const nodo = el(id);
        if (nodo) nodo.hidden = false;
    }

    function hide(id) {
        const nodo = el(id);
        if (nodo) nodo.hidden = true;
    }

    function toast(msg, tipo = "info") {
        console.log(`[Semana10 ${tipo}] ${msg}`);
        if (typeof window.mostrarToast === "function") {
            window.mostrarToast(msg, tipo);
        } else {
            alert(msg);
        }
    }

    function validarImagen(file) {
        if (!file) {
            toast("Seleccione una imagen válida.", "error");
            return false;
        }

        const permitidas = ["png", "jpg", "jpeg", "webp", "bmp", "tif", "tiff"];
        const extension = file.name.split(".").pop().toLowerCase();

        if (!permitidas.includes(extension)) {
            toast("Formato no permitido.", "error");
            return false;
        }

        if (file.size > 10 * 1024 * 1024) {
            toast("La imagen supera los 10 MB.", "error");
            return false;
        }

        return true;
    }

    function actualizarBotonComparar() {
        const btn = el("btnCompararSemana10");
        if (!btn) return;
        btn.disabled = !(imagenReferencia && imagenComparacion);
    }


    // ======================================================
    // REFERENCIA
    // ======================================================

    function cargarReferencia(file) {
        if (!validarImagen(file)) return;

        imagenReferencia = file;

        if (urlReferencia) {
            URL.revokeObjectURL(urlReferencia);
        }

        urlReferencia = URL.createObjectURL(file);

        const preview = el("semana10Preview");
        if (preview) preview.src = urlReferencia;

        setText("semana10FileName", file.name);
        hide("semana10UploadEmpty");
        show("semana10PreviewContainer");

        const btnAnalizar = el("btnAnalizarSemana10");
        if (btnAnalizar) btnAnalizar.disabled = false;

        actualizarBotonComparar();
    }

    function limpiarReferencia() {
        imagenReferencia = null;

        const input = el("semana10ImageInput");
        if (input) input.value = "";

        if (urlReferencia) {
            URL.revokeObjectURL(urlReferencia);
            urlReferencia = null;
        }

        const preview = el("semana10Preview");
        if (preview) preview.removeAttribute("src");

        show("semana10UploadEmpty");
        hide("semana10PreviewContainer");

        const btnAnalizar = el("btnAnalizarSemana10");
        if (btnAnalizar) btnAnalizar.disabled = true;

        actualizarBotonComparar();
    }


    // ======================================================
    // COMPARACIÓN
    // ======================================================

    function cargarComparacion(file) {
        if (!validarImagen(file)) return;

        imagenComparacion = file;

        if (urlComparacion) {
            URL.revokeObjectURL(urlComparacion);
        }

        urlComparacion = URL.createObjectURL(file);

        const preview = el("semana10ComparacionPreview");
        if (preview) preview.src = urlComparacion;

        setText("semana10ComparacionFileName", file.name);
        hide("semana10ComparacionEmpty");
        show("semana10ComparacionPreviewContainer");

        actualizarBotonComparar();
    }

    function limpiarComparacion() {
        imagenComparacion = null;

        const input = el("semana10ComparacionInput");
        if (input) input.value = "";

        if (urlComparacion) {
            URL.revokeObjectURL(urlComparacion);
            urlComparacion = null;
        }

        const preview = el("semana10ComparacionPreview");
        if (preview) preview.removeAttribute("src");

        show("semana10ComparacionEmpty");
        hide("semana10ComparacionPreviewContainer");
        hide("resultadoComparacionSemana10");

        actualizarBotonComparar();
    }


    // ======================================================
    // ANALIZAR IMAGEN 1
    // ======================================================

    async function analizarReferencia() {
        if (!imagenReferencia) {
            toast("Primero seleccione la imagen de referencia.", "error");
            return;
        }

        const btn = el("btnAnalizarSemana10");
        if (btn) btn.disabled = true;

        show("semana10Procesando");

        try {
            const formData = new FormData();
            formData.append("archivo", imagenReferencia, imagenReferencia.name);
            formData.append("area_minima", el("semana10AreaMinima")?.value || "50");
            formData.append("radio_lbp", el("semana10RadioLBP")?.value || "2");

            const response = await fetch("/api/semana10/imagen", {
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.error || "No fue posible analizar la imagen.");
            }

            const paquete = data.resultado || {};
            const resultado = paquete.resultado || paquete;

            setText("semana10Umbral", Number(resultado.umbral_otsu || 0).toFixed(4));
            setText("semana10Regiones", resultado.regiones ?? "-");
            setText("semana10AreaMedia", Number(resultado.area_media || 0).toFixed(2));
            setText("semana10Desviacion", Number(resultado.desviacion_area || 0).toFixed(2));
            setText("semana10Dimension", resultado.dimension_vector ?? "-");
            setText("semana10AreaMinimaResultado", resultado.area_minima ?? "-");
            setText("semana10RadioResultado", resultado.radio_lbp ?? "-");
            setText("semana10PuntosLBP", resultado.puntos_lbp ?? "-");
            setText("semana10RegionesTotales", resultado.regiones_totales ?? "-");

            const hist = el("semana10Histograma");
            if (hist) {
                hist.src = "/api/semana10/histograma?t=" + Date.now();
            }

            show("resultadoSemana10");

            toast("Características extraídas correctamente.", "success");

        } catch (error) {
            console.error(error);
            toast(error.message, "error");
        } finally {
            hide("semana10Procesando");
            if (btn) btn.disabled = !imagenReferencia;
        }
    }


    // ======================================================
    // CONCLUSIÓN
    // ======================================================

    function generarConclusion(resultado) {
        const similitud = resultado.similitud || {};

        const global = Number(similitud.global || 0);
        const intensidad = Number(similitud.intensidad || 0);
        const textura = Number(similitud.textura || 0);
        const regiones = Number(similitud.regiones || 0);

        const tipo = el("semana10TipoEstudio")?.value || "general";

        const componentes = [
            { nombre: "la distribución de intensidades", valor: intensidad },
            { nombre: "los patrones de textura", valor: textura },
            { nombre: "las regiones detectadas", valor: regiones }
        ];

        componentes.sort((a, b) => a.valor - b.valor);

        const cambioPrincipal = componentes[0].nombre;

        if (global >= 85) {
            return "La imagen evaluada presenta una alta similitud con la referencia. No se observan diferencias visuales globales importantes. La mayor variación se encuentra en " + cambioPrincipal + ". Este resultado es experimental y no constituye un diagnóstico médico.";
        }

        if (tipo === "hueso") {
            if (global >= 65) {
                return "La imagen presenta diferencias moderadas respecto a la referencia ósea. La principal variación se encuentra en " + cambioPrincipal + ". El patrón podría ser compatible con una alteración estructural leve, aunque el sistema no puede confirmar una fractura.";
            }

            return "La imagen presenta diferencias visuales importantes respecto a la referencia ósea. La principal variación se encuentra en " + cambioPrincipal + ". En esta comparación experimental, el patrón es compatible con una posible alteración estructural del hueso, que podría corresponder a una fractura u otro cambio anatómico.";
        }

        if (tipo === "rinon") {
            return "La comparación identifica diferencias respecto a la referencia renal, principalmente en " + cambioPrincipal + ". Estas diferencias pueden indicar una posible alteración estructural, pero no permiten establecer una enfermedad específica.";
        }

        if (tipo === "pulmon") {
            return "La comparación identifica diferencias respecto a la referencia pulmonar, principalmente en " + cambioPrincipal + ". El patrón puede indicar una posible alteración pulmonar, pero no permite determinar una causa específica.";
        }

        return "La imagen presenta diferencias visuales respecto a la referencia, principalmente en " + cambioPrincipal + ". El sistema identifica una posible alteración visual, pero esta comparación no constituye un diagnóstico médico.";
    }


    // ======================================================
    // COMPARAR
    // ======================================================

    async function compararImagenes() {

        if (!imagenReferencia) {

            toast(
                "Seleccione la imagen de referencia.",
                "error"
            );

            return;
        }


        if (!imagenComparacion) {

            toast(
                "Seleccione la imagen a comparar.",
                "error"
            );

            return;
        }


        const btn =
            el(
                "btnCompararSemana10"
            );


        if (btn) {

            btn.disabled =
                true;

        }


        show(
            "semana10ComparacionProcesando"
        );


        try {

            // ==================================================
            // NOMBRES SEGUROS PARA SAFARI
            // ==================================================

            function prepararArchivo(
                archivo,
                nombreBase
            ) {

                const partes =
                    archivo.name.split(".");


                let extension =
                    "png";


                if (
                    partes.length > 1
                ) {

                    extension =
                        partes
                            .pop()
                            .toLowerCase();

                }


                const nombreSeguro =
                    `${nombreBase}.${extension}`;


                return new File(
                    [
                        archivo
                    ],
                    nombreSeguro,
                    {
                        type:
                            archivo.type
                            ||
                            "application/octet-stream",

                        lastModified:
                            archivo.lastModified
                            ||
                            Date.now()
                    }
                );

            }


            const referenciaSegura =
                prepararArchivo(
                    imagenReferencia,
                    "referencia_semana10"
                );


            const comparacionSegura =
                prepararArchivo(
                    imagenComparacion,
                    "comparacion_semana10"
                );


            // ==================================================
            // FORMULARIO
            // ==================================================

            const formData =
                new FormData();


            /*
             * No enviamos los nombres originales.
             * Safari recibe nombres simples y seguros.
             */

            formData.append(
                "referencia",
                referenciaSegura
            );


            formData.append(
                "comparacion",
                comparacionSegura
            );


            formData.append(
                "area_minima",
                String(
                    el(
                        "semana10AreaMinima"
                    )?.value
                    ||
                    50
                )
            );


            formData.append(
                "radio_lbp",
                String(
                    el(
                        "semana10RadioLBP"
                    )?.value
                    ||
                    2
                )
            );


            console.log(
                "Semana 10 - enviando comparación..."
            );


            console.log(
                "Referencia:",
                referenciaSegura.name
            );


            console.log(
                "Comparación:",
                comparacionSegura.name
            );


            // ==================================================
            // PETICIÓN
            // ==================================================

            const response =
                await fetch(
                    "/api/semana10/comparar",
                    {
                        method:
                            "POST",

                        body:
                            formData,

                        credentials:
                            "same-origin",

                        cache:
                            "no-store"
                    }
                );


            console.log(
                "Semana 10 - HTTP:",
                response.status
            );


            /*
             * Primero leemos texto.
             * Así, si Flask devuelve HTML o un error,
             * podremos verlo claramente.
             */

            const respuestaTexto =
                await response.text();


            console.log(
                "Semana 10 - respuesta:",
                respuestaTexto
            );


            let data;


            try {

                data =
                    JSON.parse(
                        respuestaTexto
                    );

            }

            catch (errorJSON) {

                console.error(
                    "Respuesta no JSON:",
                    respuestaTexto
                );


                throw new Error(
                    "El servidor no devolvió una respuesta JSON válida."
                );

            }


            if (
                !response.ok
                ||
                !data.success
            ) {

                throw new Error(
                    data.error
                    ||
                    `Error HTTP ${response.status}`
                );

            }


            // ==================================================
            // EXTRAER RESULTADO
            // ==================================================

            const paquete =
                data.resultado
                ||
                {};


            const resultado =
                paquete.resultado
                ||
                paquete;


            const similitud =
                resultado.similitud
                ||
                {};


            const global =
                Number(
                    similitud.global
                    ||
                    0
                );


            // ==================================================
            // RESULTADOS
            // ==================================================

            setText(
                "semana10SimilitudGlobal",
                `${global.toFixed(1)}%`
            );


            setText(
                "semana10DiferenciaGlobal",
                `${
                    Number(
                        similitud.diferencia
                        ||
                        0
                    ).toFixed(1)
                }%`
            );


            setText(
                "semana10SimilitudIntensidad",
                `${
                    Number(
                        similitud.intensidad
                        ||
                        0
                    ).toFixed(1)
                }%`
            );


            setText(
                "semana10SimilitudTextura",
                `${
                    Number(
                        similitud.textura
                        ||
                        0
                    ).toFixed(1)
                }%`
            );


            setText(
                "semana10SimilitudRegiones",
                `${
                    Number(
                        similitud.regiones
                        ||
                        0
                    ).toFixed(1)
                }%`
            );


            setText(
                "semana10NivelComparacion",
                resultado.nivel
                ||
                ""
            );


            setText(
                "semana10RefOtsu",
                Number(
                    resultado.referencia
                        ?.umbral_otsu
                    ||
                    0
                ).toFixed(4)
            );


            setText(
                "semana10CompOtsu",
                Number(
                    resultado.comparacion
                        ?.umbral_otsu
                    ||
                    0
                ).toFixed(4)
            );


            setText(
                "semana10RefRegiones",
                resultado.referencia
                    ?.regiones
                ??
                "-"
            );


            setText(
                "semana10CompRegiones",
                resultado.comparacion
                    ?.regiones
                ??
                "-"
            );


            // ==================================================
            // CONCLUSIÓN
            // ==================================================

            setText(
                "semana10ConclusionComparacion",
                generarConclusion(
                    resultado
                )
            );


            // ==================================================
            // BARRA GLOBAL
            // ==================================================

            const barra =
                el(
                    "semana10SimilitudGlobalBarra"
                );


            if (barra) {

                barra.style.width =
                    `${
                        Math.max(
                            0,
                            Math.min(
                                global,
                                100
                            )
                        )
                    }%`;

            }


            show(
                "resultadoComparacionSemana10"
            );


            toast(
                "Comparación completada correctamente.",
                "success"
            );


        }

        catch (error) {

            console.error(
                "ERROR SEMANA 10:",
                error
            );


            console.error(
                "Tipo:",
                error?.name
            );


            console.error(
                "Mensaje:",
                error?.message
            );


            console.error(
                "Stack:",
                error?.stack
            );


            toast(
                (
                    error?.message
                    ||
                    String(
                        error
                    )
                ),
                "error"
            );

        }

        finally {

            hide(
                "semana10ComparacionProcesando"
            );


            actualizarBotonComparar();

        }

    }


    // ======================================================
    // EVENTOS
    // ======================================================


    const inputRef = el("semana10ImageInput");
    const btnRef = el("btnSeleccionarSemana10");
    const btnLimpiarRef = el("btnLimpiarSemana10");
    const btnAnalizar = el("btnAnalizarSemana10");

    const inputComp = el("semana10ComparacionInput");
    const btnComp = el("btnSeleccionarComparacionSemana10");
    const btnLimpiarComp = el("btnLimpiarComparacionSemana10");
    const btnComparar = el("btnCompararSemana10");

    if (btnRef && inputRef) {
        btnRef.onclick = (e) => {
            e.preventDefault();
            inputRef.click();
        };
    }

    if (inputRef) {
        inputRef.onchange = () => {
            const file = inputRef.files?.[0];
            if (file) cargarReferencia(file);
        };
    }

    if (btnLimpiarRef) {
        btnLimpiarRef.onclick = (e) => {
            e.preventDefault();
            limpiarReferencia();
        };
    }

    if (btnAnalizar) {
        btnAnalizar.onclick = async (e) => {
            e.preventDefault();
            await analizarReferencia();
        };
    }

    if (btnComp && inputComp) {
        btnComp.onclick = (e) => {
            e.preventDefault();
            inputComp.click();
        };
    }

    if (inputComp) {
        inputComp.onchange = () => {
            const file = inputComp.files?.[0];
            if (file) cargarComparacion(file);
        };
    }

    if (btnLimpiarComp) {
        btnLimpiarComp.onclick = (e) => {
            e.preventDefault();
            limpiarComparacion();
        };
    }

    if (btnComparar) {
        btnComparar.onclick = async (e) => {
            e.preventDefault();
            await compararImagenes();
        };
    }

    actualizarBotonComparar();

    console.log("Semana 10 cargada correctamente.");
});
