# Neurito

Neurito es un ajolote con tres necesidades: hambre, energía y aburrimiento. Una red neuronal (3 → 6 → 3) las recibe y decide si debe **comer**, **dormir** o **jugar**.

El proyecto tiene dos partes:
- **Neurito 1.0** (`main.py`): la mascota que decide qué necesita.
- **Neurito 2.0** (`saltar.py`): Neurito aprende a saltar obstáculos. Ver [más abajo](#neurito-20-aprende-a-saltar).

## Cómo funciona

1. **Datos de práctica:** el programa crea 3000 situaciones al azar. Para cada una, la acción correcta es la de la necesidad más fuerte entre hambre, cansancio (1 − energía) y aburrimiento.
2. **Entrenamiento:** la red repasa esos ejemplos 1200 veces y en cada vuelta corrige un poco sus pesos para equivocarse menos. En la consola se ve cómo baja la pérdida.
3. **Prueba:** después la red se evalúa con 1000 situaciones nuevas y acierta el 99.4 %.
4. **Neurito en pantalla:** con las teclas cambias sus necesidades. La red muestra qué tan segura está de cada acción (en %) y Neurito hace la que tenga el valor más alto.

### Estados de Neurito

| Estado | Cuándo aparece |
|---|---|
| Comer | El hambre es la necesidad más fuerte |
| Dormir | El cansancio es la necesidad más fuerte (poca energía) |
| Jugar | El aburrimiento es la necesidad más fuerte |
| Neutral | Todo está tranquilo: hambre menor a 40 %, energía mayor a 60 % y aburrimiento menor a 40 % |
| **Carrera F1** | Al presionar **F**: Neurito maneja su carro de F1, toma una curva y celebra con la bandera a cuadros. Se quita presionando **F** otra vez |

Neurito no juega a partir de un porcentaje fijo de aburrimiento. Hace la acción de la necesidad **más fuerte**: si el aburrimiento está en 50 % pero el hambre y el cansancio están más bajos, igual elige jugar.

El modo F1 y el estado neutral son solo de la pantalla, no salidas nuevas de la red. Si se cumple la condición de neutral, la pantalla lo muestra aunque la red tenga una acción con el porcentaje más alto. Mientras Neurito corre, la red sigue calculando sus tres porcentajes.

## Cómo usarlo

```bash
uv run main.py
```

| Tecla | Qué hace |
|---|---|
| H / J | Sube / baja el hambre |
| E / D | Sube / baja la energía |
| A / S | Sube / baja el aburrimiento |
| R | Pone valores al azar |
| N | Vuelve al estado tranquilo |
| F | Activa / desactiva el modo F1 |
| Esc | Salir |

## Experimentos

**1. Dos necesidades fijas y la tercera variando: ¿cuándo cambia la acción?**
Cambia justo cuando la necesidad que varía supera a la más fuerte de las otras dos. Con energía en 0.5 (cansancio 0.5) y aburrimiento en 0.3, Neurito duerme mientras el hambre está por debajo de 0.5 y empieza a comer a partir de ese punto. La red puso el cambio en 0.499, prácticamente el mismo valor de la regla.

**2. Prioridades casi iguales: ¿cómo cambia Softmax?**
Cuando dos necesidades están casi empatadas, Softmax reparte la probabilidad casi a la mitad. Por ejemplo, con hambre 0.6, cansancio 0.6 (energía 0.4) y aburrimiento 0.2 sale 49.7 % Comer y 50.3 % Dormir. Si una necesidad domina claramente, la probabilidad llega casi al 100 %. En pantalla Neurito elige una sola acción, pero en los empates la red realmente está dudando.

**3. Capa oculta de 3, 6, 10 o 20 neuronas**
Se cambia el `6` en `W1`, `b1` y `W2` por el nuevo número de neuronas.

| Neuronas | Pérdida | Precisión |
|---|---|---|
| 3 | 0.16 | 96.3 % |
| 6 | 0.12 | 99.4 % |
| 10 | 0.13 | 99.3 % |
| 20 | 0.12 | 98.8 % |

Estos resultados salen con la semilla 42 que trae el código. Con otras semillas, la red de 3 neuronas es inestable y a veces baja hasta 61 %, mientras que con 6 o más se mantiene por encima del 92 %.

Con 3 neuronas la red se queda corta. Con 6 ya funciona bien, y a partir de 10 agregar más neuronas casi no mejora nada.

**4. Épocas y tasa de aprendizaje**
Las épocas son el `1200` de `range(1200)` y la tasa de aprendizaje es el `0.1` que multiplica los gradientes.
- **Épocas:** con 100 épocas acierta el 77 %, con 1200 el 99.4 % y con 6000 el 99.6 %. Primero mejora rápido y luego se estanca.
- **Tasa de aprendizaje:**
  - Con 0.001 casi no aprende (se estanca).
  - Entre 0.1 y 0.5 aprende de forma estable.
  - Con 1.0 la pérdida empieza a oscilar.
  - Con 5 o más el entrenamiento se vuelve inestable y la red termina respondiendo lo mismo para todo.

**5. ¿Qué necesitaría una cuarta acción?**
Tres cosas:
- **Una necesidad nueva que la justifique.** Por ejemplo, "ganas de competir" para la acción *Correr en F1*.
- **Ejemplos con esa etiqueta.** La regla que genera los datos tiene que incluir la nueva necesidad, para que haya casos en los que la respuesta correcta sea la acción nueva, y en una cantidad parecida a las otras acciones.
- **Una salida más en la red:** las entradas pasan de 3 a 4 y las salidas también, de 3 a 4.

Sin ejemplos de la acción nueva, la red nunca aprendería a elegirla.

## Explica tus resultados

**¿En qué se diferencian pesos y sesgos?**
Los pesos son los números que multiplican cada entrada y dicen cuánto importa cada una; en Neurito hay 36, uno por cada conexión. Los sesgos son un número extra por neurona que se suma al resultado y mueve el punto desde el que la neurona se activa; hay 9. Ambos empiezan con valores iniciales y se van ajustando durante el entrenamiento.

**¿Por qué el cansancio es 1 − energía?**
Porque para comparar las necesidades todas deben significar "más alto = más urgente". La energía funciona al revés: mucha energía significa que Neurito no necesita dormir. Al restarla de 1, poca energía se convierte en mucho cansancio y ya se puede comparar con el hambre y el aburrimiento.

**¿Qué hace ReLU y qué hace Softmax?**
- **ReLU** está en la capa oculta: deja pasar los valores positivos y convierte los negativos en 0. Eso permite que la red aprenda patrones que no son simples líneas rectas.
- **Softmax** está en la salida: convierte las tres puntuaciones finales en probabilidades que suman 1, para poder compararlas y elegir la mayor.

**¿Por qué una precisión alta puede ser engañosa?**
Porque el 99 % solo mide qué tan bien copia la red la regla con la que se crearon los datos, no si esa regla es buena. Además:
- Los errores se concentran en los casos casi empatados, donde la precisión baja a cerca del 87 % (consideramos casi empate cuando las dos necesidades más fuertes se diferencian en menos de 0.02).
- La red siempre elige una acción, aunque Neurito no necesite nada.
- Los datos de prueba vienen del mismo generador que los de entrenamiento, así que no muestran cómo se comportaría la red con datos distintos.
---

# Neurito 2.0: aprende a saltar

Ahora Neurito corre por una pista y le llegan obstáculos a distintas velocidades. Una red neuronal (3 → 12 → 1) decide **cuándo saltar**.

## Cómo funciona

1. **Lo que ve la red:** la distancia al obstáculo, su velocidad y el tiempo que falta para que llegue (distancia ÷ velocidad).
2. **Lo que responde:** un número entre 0 y 1. Si es 0.5 o más, Neurito salta.
3. **Cómo aprende:** se crean 5000 ejemplos. Un ejemplo se marca como "saltar" si al obstáculo le faltan entre **7 y 13 fotogramas** para llegar; si no, se marca "esperar". La mitad de los ejemplos son de saltar, para que la red no aprenda a decir siempre "esperar".
4. **Cómo se prueba:** con 1500 ejemplos nuevos y viendo cuántos obstáculos esquiva en el juego.

## Cómo usarlo

```bash
uv run saltar.py
```

| Tecla | Qué hace |
|---|---|
| 1 | Entrena una época |
| 2 | Entrena cien épocas |
| 3 | Activa / pausa el entrenamiento continuo |
| A | Cambia entre control automático (la red) y manual |
| Espacio | Salta (en modo manual) |
| C | Reinicia la pista y los contadores |
| R | Reinicia el cerebro (borra lo aprendido) |
| Esc | Salir |

## Experimentos

Los resultados del juego son de 2.5 minutos de partida (4500 fotogramas).

**1. El juego sin entrenar**
Neurito **nunca salta**: en 5 minutos esquivó 0 obstáculos y chocó 59 veces. Aun así la red marca 44.9 % de precisión, porque acierta todos los casos de "esperar" sin saber hacer nada más.

**2. Entrenar de cien en cien épocas**

| Épocas | Pérdida | Precisión | Esquivados | Choques |
|---|---|---|---|---|
| 0 | — | 44.9 % | 0 | 30 |
| 100 | 0.260 | 91.2 % | 36 | 1 |
| 300 | 0.207 | 92.3 % | 37 | 0 |
| 500 | 0.137 | 94.1 % | 37 | 0 |
| 1000 | 0.057 | 97.8 % | 37 | 0 |
| 3000 | 0.022 | 99.1 % | 37 | 0 |

Con solo 100 épocas Neurito ya esquiva casi todo, y desde 300 no vuelve a chocar. Después la pérdida y la precisión siguen mejorando, pero en el juego ya no se nota ningún cambio.

**3. Neuronas ocultas: 3, 12 o 24** (3000 épocas)
Se cambia `ocultas=12` en `salto_modelo.py`.

| Neuronas | Precisión entrenamiento | Precisión prueba |
|---|---|---|
| 3 | 94.0 % | 93.7 % |
| 12 | 99.3 % | 99.1 % |
| 24 | 99.4 % | 99.3 % |

En los tres casos la precisión con datos nuevos es casi igual a la de entrenamiento, así que la red **generaliza bien** y no memoriza. Con 3 neuronas le falta capacidad para marcar bien los bordes de la ventana. Con 24 casi no mejora frente a 12. En el juego, las tres esquivan todos los obstáculos.

**4. Tasa de aprendizaje: 0.01, 0.8 o 1.2** (3000 épocas)
Se cambia `tasa=0.8` en `salto_modelo.py`.
- **0.01:** converge demasiado lento. Al final la pérdida sigue en 0.31 y la precisión en 88.6 %. En el juego **choca contra todo** (0 esquivados).
- **0.8:** la pérdida baja de forma estable y nunca sube.
- **1.2:** converge más rápido (99.6 %), pero la pérdida sube y baja 291 veces en el camino, porque los pasos son tan grandes que a veces se pasan del mínimo.

**5. Cambiar la ventana de salto**
En el juego, Neurito salta en el primer momento en que entra en la ventana, así que lo que más importa es el **límite superior**. Un salto dura unos 37 fotogramas, y Neurito queda por encima del obstáculo más o menos entre el fotograma 5 y el 32 del salto.

| Ventana (fotogramas) | Esquivados | Choques | ¿Compatible con la física? |
|---|---|---|---|
| 1 a 4 | 0 | 30 | No: salta tan tarde que no alcanza a subir |
| 2 a 5 | 37 | 0 | Sí, pero muy justo |
| 7 a 13 (original) | 37 | 0 | Sí |
| 12 a 16 | 37 | 0 | Sí, en el límite |
| 12 a 18 | 28 | 6 | A medias: falla con obstáculos lentos |
| 14 a 20 | 0 | 27 | No: salta tan pronto que cae antes del obstáculo |

Con la ventana de 14 a 20, la red aprendió la regla con un **98.9 % de precisión** y aun así chocó las 27 veces. La red aprendió bien, pero lo que le enseñaron no sirve con esta física.

## Pregunta central: ¿por qué una red puede tener buena precisión y aun así chocar?

Porque la precisión y el juego miden cosas distintas:

- **La precisión cuenta ejemplos sueltos; el juego depende de un solo momento.** Para esquivar basta con acertar el fotograma exacto en que se salta. Ese momento cae justo en el borde de la ventana (Neurito salta cuando faltan entre 13 y 14 fotogramas), y en los bordes la red acierta solo el **51.5 %**, frente al **98.6 %** lejos de ellos.
- **Un solo error a destiempo basta para chocar.** Con tasa 0.01 la red tiene 88.6 % de precisión, pero se equivoca diciendo "saltar" demasiado pronto: salta cuando faltan unos 18 fotogramas, cae antes del obstáculo y choca las 27 veces.
- **La regla puede no servir para la física.** Con la ventana de 14 a 20, la red copia la regla al 98.9 %, pero esa regla hace que Neurito salte antes de tiempo.
- **Los datos de práctica no son iguales al juego.** En el entrenamiento la mitad de los ejemplos son de "saltar"; en el juego casi todos los fotogramas son de "esperar", y la red solo se juega la partida en unos pocos.

En resumen: una precisión alta dice que la red **copia bien la regla**, no que Neurito **juegue bien**. Para eso también hace falta que la regla sea compatible con la física del salto.
