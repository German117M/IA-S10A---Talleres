# Semana 04 - Marco tecnológico de la Inteligencia Artificial

## 1. Búsqueda A*

### Descripción
Se implementó el algoritmo A* sobre una cuadrícula con obstáculos. El objetivo es encontrar una ruta válida desde el estado inicial hasta la meta utilizando el menor costo posible.

### Representación del problema

- Estado inicial: posición `(0, 0)`.
- Meta: posición `(4, 4)`.
- Estado: coordenada actual dentro de la cuadrícula.
- Acción: desplazarse arriba, abajo, izquierda o derecha.
- Transición: pasar de una posición válida a una posición vecina.
- Costo: cada movimiento tiene costo 1.
- Heurística: distancia Manhattan entre la posición actual y la meta.

A* utiliza:

`f(n) = g(n) + h(n)`

donde:

- `g(n)` representa el costo acumulado.
- `h(n)` representa la estimación del costo restante.
- `f(n)` determina qué estado se analiza primero.

### Resultado

Costo obtenido:

`8`

El resultado es razonable porque la ruta debe desplazarse desde `(0,0)` hasta `(4,4)` evitando los obstáculos existentes en la cuadrícula.

---

## 2. Minimax

### Descripción
Se implementó Minimax en un juego de tres en línea. El objetivo es seleccionar la mejor posición disponible para el jugador X suponiendo que el jugador O también toma decisiones racionales.

### Representación

- Estado: configuración actual del tablero.
- Acción: colocar una marca en una casilla vacía.
- Jugador MAX: X.
- Jugador MIN: O.
- Estado terminal: victoria de X, victoria de O o empate.
- Utilidad:
  - X gana = 1
  - Empate = 0
  - O gana = -1

### Resultado

Tablero utilizado:

`['X', 'O', 'X', 'O', 'X', ' ', ' ', ' ', 'O']`

Mejor posición para X:

`6`

La posición 6 es correcta porque permite completar una diagonal y obtener una victoria para X.

---

## 3. Comparación

A* y Minimax exploran diferentes posibilidades, pero se utilizan para problemas distintos.

A* busca una solución de menor costo en un espacio de estados donde no existe un adversario racional.

Minimax se utiliza en problemas adversariales, donde MAX busca maximizar el resultado y MIN intenta minimizarlo.

---

## 4. Limitaciones

La búsqueda A* depende de la representación del problema y de la calidad de la heurística utilizada.

Minimax puede aumentar considerablemente su número de evaluaciones cuando existen muchas jugadas posibles.

La poda alfa-beta permite reducir la cantidad de ramas evaluadas por Minimax sin modificar la decisión final.