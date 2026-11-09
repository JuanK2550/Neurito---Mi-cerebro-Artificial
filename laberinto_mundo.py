"""Mapas, búsqueda BFS experta y simulación independiente de Pygame."""
from collections import deque
from dataclasses import dataclass
import heapq
import random

# (fila, columna), orden fijo de desempate
DIRECCIONES = ((-1, 0), (1, 0), (0, -1), (0, 1))
NOMBRES = ('ARRIBA', 'ABAJO', 'IZQUIERDA', 'DERECHA')
MAPAS = (
    (
        '#########',
        '#...#...#',
        '#.#.#.#.#',
        '#.#...#.#',
        '#.###.#.#',
        '#...#...#',
        '###.#.###',
        '#.......#',
        '#########',
    ),
    (
        '#########',
        '#...#...#',
        '#.#...#.#',
        '#...#...#',
        '###.#.###',
        '#...#...#',
        '#.#...#.#',
        '#...#...#',
        '#########',
    ),
    (
        '#########',
        '#.......#',
        '#.###.#.#',
        '#...#.#.#',
        '###.#...#',
        '#...###.#',
        '#.#.....#',
        '#.......#',
        '#########',
    ),
)


def libres(mapa):
    return [(f, c) for f, fila in enumerate(mapa) for c, v in enumerate(fila) if v == '.']


def vecino(pos, accion):
    df, dc = DIRECCIONES[accion]
    return pos[0] + df, pos[1] + dc


def valido(mapa, pos):
    f, c = pos
    return 0 <= f < len(mapa) and 0 <= c < len(mapa[0]) and mapa[f][c] != '#'


def distancias_bfs(mapa, meta):
    """Distancia real por celdas hasta la comida, calculada SOLO por el profesor BFS."""
    dist = {meta: 0}
    cola = deque([meta])
    while cola:
        actual = cola.popleft()
        for a in range(4):
            siguiente = vecino(actual, a)
            if valido(mapa, siguiente) and siguiente not in dist:
                dist[siguiente] = dist[actual] + 1
                cola.append(siguiente)
    return dist


def accion_experta(mapa, origen, dist):
    """BFS indica el siguiente movimiento que reduce la distancia real a la meta."""
    if origen not in dist or dist[origen] == 0:
        return None
    opciones = [(dist.get(vecino(origen, a), 10**9), a) for a in range(4)]
    minimo, accion = min(opciones)
    assert minimo < dist[origen]
    return accion


def primer_paso(padre, origen, meta):
    """Recorre el camino encontrado desde la meta hacia atrás y devuelve su primer movimiento."""
    paso = meta
    while padre[paso] != origen:
        paso = padre[paso]
    return DIRECCIONES.index((paso[0] - origen[0], paso[1] - origen[1]))


def accion_dfs(mapa, origen, meta):
    """Experto DFS: sigue un camino hasta el fondo antes de probar otro (no garantiza el más corto)."""
    pila, padre = [origen], {origen: None}
    while pila:
        actual = pila.pop()
        if actual == meta:
            return primer_paso(padre, origen, meta)
        for a in reversed(range(4)):  # explora primero ARRIBA, igual que el orden de BFS
            siguiente = vecino(actual, a)
            if valido(mapa, siguiente) and siguiente not in padre:
                padre[siguiente] = actual
                pila.append(siguiente)
    return None


def accion_astar(mapa, origen, meta):
    """Experto A*: camino más corto guiado por la distancia Manhattan hasta la comida."""
    def estimar(p):
        return abs(p[0] - meta[0]) + abs(p[1] - meta[1])
    abiertos, costo, padre, orden = [(estimar(origen), 0, origen)], {origen: 0}, {origen: None}, 0
    while abiertos:
        _, _, actual = heapq.heappop(abiertos)
        if actual == meta:
            return primer_paso(padre, origen, meta)
        for a in range(4):
            siguiente = vecino(actual, a)
            nuevo = costo[actual] + 1
            if valido(mapa, siguiente) and nuevo < costo.get(siguiente, 10**9):
                costo[siguiente], padre[siguiente] = nuevo, actual
                orden += 1
                heapq.heappush(abiertos, (nuevo + estimar(siguiente), orden, siguiente))
    return None


@dataclass
class Laberinto:
    indice: int = 0
    semilla: int = 99

    def __post_init__(self):
        self.azar = random.Random(self.semilla)
        self.exitos = 0
        self.pasos = 0
        self.choques = 0
        self.reiniciar(self.indice)

    def reiniciar(self, indice=None):
        if indice is not None:
            self.indice = indice % len(MAPAS)
        self.mapa = MAPAS[self.indice]
        celdas = libres(self.mapa)
        self.meta = self.azar.choice(celdas)
        opciones = [p for p in celdas if p != self.meta and p in distancias_bfs(self.mapa, self.meta)]
        self.posicion = self.azar.choice(opciones)
        self.visitadas = {self.posicion: 1}
        self.pasos = 0
        self.intentos = 0
        self.terminado = False
        self.ultimo = None

    def mover(self, accion):
        self.ultimo = accion
        self.intentos += 1
        nuevo = vecino(self.posicion, accion)
        if not valido(self.mapa, nuevo):
            self.choques += 1
            return 'pared'
        self.posicion = nuevo
        self.pasos += 1
        self.visitadas[nuevo] = self.visitadas.get(nuevo, 0) + 1
        if nuevo == self.meta:
            self.exitos += 1
            self.terminado = True
            return 'comida'
        return 'avanza'


def elegir_accion(red, mundo, visitas, asistido):
    """Argmax puro; asistencia opcional para paredes y visitas repetidas."""
    probs = red.probabilidades(mundo.indice, mundo.posicion, mundo.meta)
    if not asistido:
        return int(probs.argmax()), probs
    opciones = [
        (float(probs[a]) - 0.35 * visitas.get(vecino(mundo.posicion, a), 0), -a, a)
        for a in range(4) if valido(mundo.mapa, vecino(mundo.posicion, a))
    ]
    return max(opciones)[2], probs
