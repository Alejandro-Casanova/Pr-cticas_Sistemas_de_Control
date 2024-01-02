# Prácticas de la Asignatura "Sistemas de Control"
## Máster en Software de Sistemas Distribuidos y Empotrados

### 1. EJERCICIO DE CONTROL PID.
A partir del siguiente modelo de un motor de corriente continua, desarrollar el controlador PID, ajustando sus parámetros a partir de sus índices de rendimiento.

### 2. EJERCICIO DE ALGORITMOS GENÉTICOS.
Sobre el controlador PID desarrollado en la práctica anterior, desarrollar un algoritmo genético que sea capaz de optimizar el valor de las ganancias Kp, Ki y Kd, a fin de obtener el controlador con mejor rendimiento posible.
Para ello, se debe:
- Definir la función de fitness
- Ajustar los pesos de la función de fitness
- Definir el tamaño del cromosoma
- Definir el tamaño de la población
- La selección se realizará por torneo: definir el valor de T
- Especificar el número de generaciones del algoritmo genético
- Especificar los ratios de mutación y cruce del algoritmo genético

### 3. Práctica en ROS
El algoritmo genético de la práctica anterior debe estar integrado en un paquete de ROS2. En dicho paquete se debe definir un nodo, en el cual implementará dicho algoritmo. Para cada miembro de la población se debe hacer una llamada de servicio al nodo que simula el controlador y el motor, que responderá con los índices de rendimiento de la respuesta. Con dichos índices se calculará el fitness de ese individuo, que luego se utilizará como parámetro del algoritmos genético.