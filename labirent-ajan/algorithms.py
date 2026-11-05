"""Dört yönlü, birim maliyetli grid üzerinde saf arama fonksiyonları."""
from collections import deque
from dataclasses import dataclass
import heapq
from itertools import count

@dataclass
class Result:
    path: list
    expanded: list
    discovered: int


def neighbors(cell, walls, rows, cols):
    r, c = cell
    for n in ((r, c+1), (r+1, c), (r, c-1), (r-1, c)):
        if 0 <= n[0] < rows and 0 <= n[1] < cols and n not in walls:
            yield n


def search(start, goal, walls, rows=20, cols=50, method='bfs'):
    if method not in ('bfs', 'astar'):
        raise ValueError('method bfs veya astar olmalı')
    if any(not (0 <= p[0] < rows and 0 <= p[1] < cols) or p in walls
           for p in (start, goal)):
        return Result([], [], 0)
    parent, costs, expanded = {start: None}, {start: 0}, []
    serial = count()
    heuristic = lambda p: abs(p[0]-goal[0]) + abs(p[1]-goal[1])
    queue = deque([start]) if method == 'bfs' else [(heuristic(start), 0, next(serial), start)]
    closed = set()
    while queue:
        if method == 'bfs':
            current = queue.popleft()
        else:
            _, _, _, current = heapq.heappop(queue)
        if current in closed:
            continue
        closed.add(current)
        expanded.append(current)
        if current == goal:
            path = []
            while current is not None:
                path.append(current)
                current = parent[current]
            return Result(path[::-1], expanded, len(parent))
        for n in neighbors(current, walls, rows, cols):
            new_cost = costs[current] + 1
            if n not in costs or new_cost < costs[n]:
                costs[n], parent[n] = new_cost, current
                if method == 'bfs':
                    queue.append(n)
                else:
                    heapq.heappush(queue, (new_cost+heuristic(n), heuristic(n), next(serial), n))
    return Result([], expanded, len(parent))


INF = float('inf')


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class DStarLite:
    """BFS mesafe alanıyla başlatılmış D* Lite.

    g/rhs değerleri ve öncelik kuyruğu yeniden planlamalar arasında korunur.
    Kaynak: Koenig & Likhachev (2002), Figure 3, basic D* Lite.
    Standart sonsuz-değer başlangıcı yerine tam ters BFS alanı kullanılır.
    """
    def __init__(self, start, goal, walls, rows=20, cols=50):
        self.rows, self.cols = rows, cols
        self.start = self.last_start = start
        self.goal, self.walls = goal, set(walls)
        self.km = 0
        self.g = {(r, c): INF for r in range(rows) for c in range(cols)}
        self.rhs = self.g.copy()
        self.heap, self.active = [], {}
        self.serial = count()
        # BFS hedef köklüdür; yönsüz gridde başlangıca en kısa yolu verir.
        self.seed_expanded = []
        queue = deque([goal])
        self.g[goal] = 0
        while queue:
            u = queue.popleft()
            self.seed_expanded.append(u)
            for v in neighbors(u, self.walls, rows, cols):
                if self.g[v] == INF:
                    self.g[v] = self.g[u] + 1
                    queue.append(v)
        # Tam mesafe alanında her köşe yerel tutarlıdır: g == rhs.
        self.rhs = self.g.copy()
        self.last_pops = 0
        self.last_updates = 0

    def adjacent(self, u):
        """Değişen duvarın iki ucunu da güncellemek için geometrik komşular."""
        return neighbors(u, set(), self.rows, self.cols)

    def key(self, u):
        best = min(self.g[u], self.rhs[u])
        return (best + manhattan(self.start, u) + self.km, best)

    def insert(self, u):
        key, serial = self.key(u), next(self.serial)
        self.active[u] = (key, serial)
        heapq.heappush(self.heap, (*key, serial, u))

    def discard_stale(self):
        while self.heap:
            a, b, serial, u = self.heap[0]
            if self.active.get(u) == ((a, b), serial):
                break
            heapq.heappop(self.heap)

    def top_key(self):
        self.discard_stale()
        return self.heap[0][:2] if self.heap else (INF, INF)

    def update_vertex(self, u):
        self.last_updates += 1
        if u in self.walls:
            self.rhs[u] = INF
        elif u == self.goal:
            self.rhs[u] = 0
        else:
            self.rhs[u] = min((1 + self.g[v] for v in
                              neighbors(u, self.walls, self.rows, self.cols)), default=INF)
        self.active.pop(u, None)
        if self.g[u] != self.rhs[u]:
            self.insert(u)

    def repair(self):
        """Yalnızca mevcut başlangıcın en kısa yolu için gereken tutarsızlıkları onar."""
        expanded = []
        while self.top_key() < self.key(self.start) or self.rhs[self.start] != self.g[self.start]:
            self.discard_stale()
            if not self.heap:
                raise RuntimeError('Tutarsız başlangıç için boş D* Lite kuyruğu')
            a, b, _, u = heapq.heappop(self.heap)
            self.active.pop(u, None)
            self.last_pops += 1
            old_key = (a, b)
            if old_key < self.key(u):
                self.insert(u)
            elif self.g[u] > self.rhs[u]:
                expanded.append(u)
                self.g[u] = self.rhs[u]
                for p in self.adjacent(u):
                    self.update_vertex(p)
            else:
                expanded.append(u)
                self.g[u] = INF
                self.update_vertex(u)
                for p in self.adjacent(u):
                    self.update_vertex(p)
        # Kuyrukta tembel silmeden kalan kayıtların sınırsız birikmesini önle.
        if len(self.heap) > 4 * max(1, len(self.active)) + 100:
            self.heap = [(*key, serial, u) for u, (key, serial) in self.active.items()]
            heapq.heapify(self.heap)
        return list(dict.fromkeys(expanded))

    def path(self):
        if self.g[self.start] == INF or self.start in self.walls:
            return []
        route, seen = [self.start], {self.start}
        while route[-1] != self.goal:
            u = route[-1]
            v = min(neighbors(u, self.walls, self.rows, self.cols),
                    key=lambda n: (self.g[n], manhattan(n, self.goal), n), default=None)
            if v is None or self.g[v] == INF or v in seen:
                raise RuntimeError('D* Lite alanından geçerli yol çıkarılamadı')
            route.append(v)
            seen.add(v)
        return route

    def replan(self, start, walls):
        self.last_pops = self.last_updates = 0
        self.km += manhattan(self.last_start, start)
        self.start = self.last_start = start
        new_walls = set(walls)
        changed = self.walls ^ new_walls
        self.walls = new_walls
        affected = set(changed)
        for cell in changed:
            affected.update(self.adjacent(cell))
        for cell in sorted(affected):
            self.update_vertex(cell)
        expanded = self.repair()
        return Result(self.path(), expanded, len(affected | set(expanded)))


class HybridPlanner:
    """İlk plan ve D* Lite durumu ters BFS ile; sonraki planlar artımlı D* Lite."""
    def __init__(self):
        self.reset()

    def reset(self):
        self.engine = None
        self.plans = 0
        self.total_expanded = 0
        self.total_pops = 0
        self.last_method = None

    def plan(self, start, goal, walls, rows=20, cols=50):
        if any(not (0 <= p[0] < rows and 0 <= p[1] < cols) or p in walls
               for p in (start, goal)):
            raise ValueError('Başlangıç ve hedef grid içinde ve engelsiz olmalı')
        if any(not (0 <= r < rows and 0 <= c < cols) for r, c in walls):
            raise ValueError('Duvar koordinatları grid içinde olmalı')
        if self.engine is None or (goal, rows, cols) != (self.engine.goal, self.engine.rows, self.engine.cols):
            self.reset()
            self.engine = DStarLite(start, goal, walls, rows, cols)
            self.last_method = 'BFS (ters mesafe alanı)'
            result = Result(self.engine.path(), self.engine.seed_expanded.copy(),
                            len(self.engine.seed_expanded))
        else:
            self.last_method = 'D* Lite (artımlı onarım)'
            result = self.engine.replan(start, walls)
            self.total_pops += self.engine.last_pops
        self.plans += 1
        self.total_expanded += len(result.expanded)
        return result
