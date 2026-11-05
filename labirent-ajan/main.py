"""Çalıştır: python main.py | Ekran görüntüsü: python main.py --screenshot"""
import argparse
import json
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from algorithms import search, HybridPlanner

ROOT = Path(__file__).resolve().parent
ROWS, COLS = 20, 50
START, GOAL = (10, 1), (10, 48)
COLORS = ['#152238', '#52647d', '#344779', '#f6c766', '#36d6ab', '#fb7b87', '#70d9ff']


def load_map():
    data = json.loads((ROOT / 'data/maze.json').read_text())
    return {tuple(p) for p in data['walls']}


class App:
    def __init__(self):
        self.walls = load_map()
        self.agent = START
        self.hybrid = HybridPlanner()
        self.result = None
        self.visited, self.route = set(), []
        self.index = self.walk = 0
        self.phase = 'idle'
        self.running = True
        self.speed = 12
        self.mode = 'hybrid'
        self.message = 'Sol fare: duvar | Sağ fare: sil | Sürükleyebilirsiniz'
        self.edit_tool = 'wall'
        from ui import build_ui
        build_ui(self, COLORS, ROWS, COLS)
        self.fig.canvas.mpl_connect('button_press_event', self.edit)
        self.fig.canvas.mpl_connect('motion_notify_event', self.edit)
        self.fig.canvas.mpl_connect('key_press_event', self.key)
        self.refresh()
        self.animation = FuncAnimation(self.fig, self.tick, interval=35, cache_frame_data=False)

    def pixels(self):
        grid = [[0]*COLS for _ in range(ROWS)]
        # D* Lite yeni duvar hücresini de işleyebilir; duvar görünür kalmalı.
        for points, color in ((self.visited, 2), (self.route, 3), (self.walls, 1)):
            for r, c in points:
                grid[r][c] = color
        grid[START[0]][START[1]] = 4
        grid[GOAL[0]][GOAL[1]] = 5
        if self.agent != START:
            grid[self.agent[0]][self.agent[1]] = 6
        return grid

    def refresh(self):
        if self.result is None:
            self.comparison_results = {}
        for row, method in enumerate(('bfs', 'astar', 'hybrid'), start=1):
            result = self.comparison_results.get(method)
            self.comparison[row, 1].get_text().set_text(
                str(len(result.expanded)) if result is not None else '—')
            self.comparison[row, 2].get_text().set_text(
                ('Yol yok' if not result.path else str(len(result.path)-1))
                if result is not None else '—')
        self.image.set_data(self.pixels())
        from ui import refresh_ui
        refresh_ui(self)
        self.fig.canvas.draw_idle()

    def begin(self, mode, replan=False):
        was_running = self.running
        self.mode = mode
        if not replan:
            self.agent = START
            self.hybrid.reset()
        self.result = (self.hybrid.plan(self.agent, GOAL, self.walls) if mode == 'hybrid'
                       else search(self.agent, GOAL, self.walls, method=mode))
        bfs = search(self.agent, GOAL, self.walls)
        astar = search(self.agent, GOAL, self.walls, method='astar')
        self.comparison_results = {'bfs': bfs, 'astar': astar}
        if mode == 'hybrid':
            self.comparison_results['hybrid'] = self.result
        self.visited, self.route = set(), []
        self.index = self.walk = 0
        self.phase, self.running = 'search', was_running if replan else True
        length = len(self.result.path)-1 if self.result.path else 'Yol yok'
        used = self.hybrid.last_method if mode == 'hybrid' else mode
        name = 'BFS + D* LITE' if mode == 'hybrid' else {'bfs': 'BFS', 'astar': 'A*'}[mode]
        status = f'{length} adım' if self.result.path else 'YOL YOK — duvar silerek geçit açabilirsiniz'
        self.message = (f'{name}  |  {used}  |  {status}\n'
                        'Tablo: aynı harita ve konumdan son plan; incelenen kare = kuyruktan alınıp işlenen farklı kare.\n'
                        'BFS ve A* sıfırdan arar; hibrit, değişikliklerde önceki bilgiyi kullanır.  |  1: Hibrit, 2: BFS, 3: A*')
        self.refresh()

    def tick(self, _):
        if not self.running or not self.result:
            return
        if self.phase == 'search':
            self.visited.update(self.result.expanded[self.index:self.index+self.speed])
            self.index += self.speed
            if self.index >= len(self.result.expanded):
                self.phase = 'path' if self.result.path else 'blocked'
        elif self.phase == 'path':
            self.route = self.result.path[:self.walk+1]
            self.walk += 1
            if self.walk >= len(self.result.path):
                self.phase, self.walk = 'walk', 0
        elif self.phase == 'walk':
            self.agent = self.result.path[self.walk]
            self.walk += 1
            if self.walk >= len(self.result.path):
                self.phase = 'done'
        else:
            return
        self.refresh()

    def edit(self, event):
        if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            return
        if event.button not in (1, 3):
            return
        cell = (int(event.ydata+.5), int(event.xdata+.5))
        if not (0 <= cell[0] < ROWS and 0 <= cell[1] < COLS) or cell in (START, GOAL, self.agent):
            return
        before = cell in self.walls
        if event.button == 1 and self.edit_tool == 'wall':
            self.walls.add(cell)
        else:
            self.walls.discard(cell)
        if before == (cell in self.walls):
            return
        if self.result and self.mode == 'hybrid':
            self.begin('hybrid', replan=True)
        else:
            self.result, self.phase = None, 'idle'
            self.visited, self.route = set(), []
            self.message = 'Harita değişti. Bir algoritma başlatın.'
            self.refresh()

    def set_tool(self, tool):
        self.edit_tool = tool
        self.refresh()

    def pause(self, _):
        self.running = not self.running
        self.refresh()

    def reset(self, _):
        self.agent, self.walls = START, load_map()
        self.result, self.phase = None, 'idle'
        self.visited, self.route = set(), []
        self.hybrid.reset()
        self.message = 'Örnek labirent yüklendi. Bir algoritma seçin.'
        self.refresh()

    def clear(self, _):
        if not self.walls:
            return
        self.walls.clear()
        if self.result and self.mode == 'hybrid':
            self.begin('hybrid', replan=True)
        else:
            self.result, self.phase = None, 'idle'
            self.visited, self.route = set(), []
            self.message = 'Tüm duvarlar silindi. Bir algoritma seçin.'
            self.refresh()

    def key(self, event):
        if event.key in ('1', '2', '3'):
            self.begin({'1': 'hybrid', '2': 'bfs', '3': 'astar'}[event.key])
        elif event.key == ' ':
            self.pause(None)
        elif event.key in ('d', 'e'):
            self.set_tool('wall' if event.key == 'd' else 'erase')
        elif event.key == 'r':
            self.reset(None)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--screenshot', action='store_true')
    args = parser.parse_args()
    app = App()
    if args.screenshot:
        app.begin('hybrid')
        app.animation.event_source.stop()
        app.phase = 'done'
        app.agent = GOAL
        app.visited = set(app.result.expanded)
        app.route = app.result.path
        app.refresh()
        (ROOT / 'docs').mkdir(exist_ok=True)
        app.fig.savefig(ROOT / 'docs/screenshot.png', dpi=150)
        plt.close(app.fig)
    else:
        plt.show()
