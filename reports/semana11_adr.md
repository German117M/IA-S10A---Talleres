# ADR Semana 11 - Selección de modelo para HIS_IA

## Contexto

HIS_IA utiliza Machine Learning para determinar la prioridad de un caso a partir de las variables edad, documentos pendientes, resultados pendientes e imágenes pendientes.

Para la Semana 11 se compararon tres modelos utilizando exactamente el mismo conjunto de datos, la misma división de entrenamiento y prueba y random_state=42.

Se utilizaron 100 registros: 75 para entrenamiento y 25 para prueba.

## Opciones evaluadas

- Logistic Regression
- Random Forest
- MLPClassifier

## Evidencia

| Modelo | Accuracy | Tiempo de entrenamiento |
|---|---:|---:|
| MLPClassifier | 96.00 % | 0.0543 s |
| Random Forest | 96.00 % | 0.1294 s |
| Logistic Regression | 92.00 % | 0.0049 s |

La evidencia completa está almacenada en:

artifacts/benchmark.csv

## Decisión

Se selecciona Random Forest como modelo recomendado para el componente de prioridad de HIS_IA.

## Justificación

Random Forest y MLP obtuvieron el mayor accuracy, con un 96 %.

Aunque MLP presentó un menor tiempo de entrenamiento, la diferencia absoluta de tiempo es pequeña para el tamaño actual del proyecto.

Random Forest ofrece un equilibrio favorable entre precisión, capacidad para representar relaciones no lineales, explicabilidad y facilidad de mantenimiento.

Logistic Regression fue el modelo más rápido, pero obtuvo una precisión inferior del 92 %.

Por estas razones, Random Forest representa actualmente el mejor equilibrio para HIS_IA.

## Consecuencias

### Ventajas

- Accuracy del 96 %.
- Capacidad para manejar relaciones no lineales.
- Mayor facilidad de interpretación que una red neuronal.
- Integración sencilla con el entorno Python y scikit-learn utilizado por HIS_IA.

### Costos

- Entrena más lentamente que Logistic Regression y MLP en esta prueba.
- Es más complejo que la línea base Logistic Regression.
- Requiere mantener y evaluar un conjunto de múltiples árboles.

## Conclusión

Semana 11 permitió comprobar que seleccionar un modelo no consiste únicamente en escoger el algoritmo más avanzado o el más rápido.

La decisión se tomó utilizando evidencia obtenida mediante un benchmark común para las tres alternativas.

Para las condiciones actuales de HIS_IA se recomienda Random Forest, con un accuracy del 96 %, debido a su equilibrio entre desempeño, explicabilidad y mantenibilidad.
