# Proyecto de Inteligencia Artificial

## Descripción

Este repositorio contiene el desarrollo acumulativo de las actividades realizadas en la asignatura de **Inteligencia Artificial**.

Cada semana se integran nuevos conceptos, técnicas y ejercicios, manteniendo el código, datos, reportes y evidencias dentro de un mismo repositorio.

Además de las actividades semanales, se desarrolla el proyecto **HIS_IA**, un asistente de Inteligencia Artificial orientado al apoyo de procesos relacionados con información clínica dentro de un HIS.

## Proyecto HIS_IA

Actualmente HIS_IA integra:

* Clasificación de información clínica mediante reglas y palabras clave.
* Machine Learning para estimar prioridad de revisión.
* Búsqueda A* para organizar la revisión de resultados y estudios.
* Uso de estados, acciones, costos y heurísticas.
* Integración progresiva de los temas vistos durante el semestre.

## Tecnologías utilizadas

* Python 3
* Pandas
* NumPy
* scikit-learn
* Matplotlib
* Git
* GitHub
* Visual Studio Code

## Estructura

```text
ia_semestre/
├── data/
├── reports/
├── src/
├── proyecto_his/
│   ├── data/
│   │   └── datos_his.csv
│   ├── models/
│   ├── reports/
│   └── src/
│       └── his_ia.py
├── tests/
├── requirements.txt
├── .gitignore
└── README.md
```

## Ejecución de HIS_IA

Activar el entorno virtual en macOS:

```bash
source .venv/bin/activate
```

Ejecutar el proyecto:

```bash
python3 proyecto_his/src/his_ia.py
```

## Funciones actuales

1. Analizar información clínica.
2. Evaluar prioridad de revisión.
3. Gestionar revisión de resultados y estudios.
4. Salir.

## Desarrollo acumulativo

El proyecto continuará evolucionando semana a semana, incorporando nuevas técnicas de Inteligencia Artificial de acuerdo con los temas vistos en clase.

## Autor

German Manrique
Sebastian Ortiz