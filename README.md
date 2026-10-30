# Neurito

Neurito es un ajolote con tres necesidades: hambre, energía y aburrimiento. Una red neuronal (3 → 6 → 3) las recibe y decide si debe **comer**, **dormir** o **jugar**.

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