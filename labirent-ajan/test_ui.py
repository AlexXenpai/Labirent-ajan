"""Grafik ekranı gerektirmeden gerçek Matplotlib fare olaylarını test eder."""
import unittest
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseEvent, KeyEvent
from main import App, START, GOAL, load_map


class InterfaceTests(unittest.TestCase):
    def setUp(self):
        self.app = App()
        self.app.fig.canvas.draw()
        self.app.animation.event_source.stop()
        # Testte yalnızca çizimi atla; olaylar ve uygulama mantığı gerçek.
        self.app.refresh = lambda: None

    def tearDown(self):
        plt.close(self.app.fig)

    def mouse(self, cell, button, name='button_press_event'):
        x, y = self.app.ax.transData.transform((cell[1], cell[0]))
        event = MouseEvent(name, self.app.fig.canvas, x, y, button=button)
        self.app.fig.canvas.callbacks.process(name, event)

    def test_mouse_add_drag_erase_and_protected_cells(self):
        for cell in (START, GOAL):
            self.mouse(cell, 1)
            self.assertNotIn(cell, self.app.walls)
        self.mouse((1,1), 1)
        self.mouse((1,2), 1, 'motion_notify_event')
        self.assertTrue({(1,1),(1,2)} <= self.app.walls)
        self.mouse((1,1), 3)
        self.assertNotIn((1,1), self.app.walls)

    def test_dynamic_change_while_agent_is_moving(self):
        app = self.app
        app.begin('hybrid')
        for _ in range(1500):
            app.tick(None)
            if app.agent != START:
                break
        self.assertNotEqual(app.agent, START)
        position = app.agent
        engine = app.hybrid.engine
        obstacle = app.result.path[app.walk+2]
        self.mouse(obstacle, 1)
        self.assertEqual(app.agent, position)
        self.assertIs(app.hybrid.engine, engine)
        self.assertIn('D* Lite', app.hybrid.last_method)
        self.assertNotIn(obstacle, app.result.path)
        self.mouse(position, 1)
        self.assertNotIn(position, app.walls)
        for _ in range(2000):
            app.tick(None)
            if app.phase == 'done':
                break
        self.assertEqual(app.agent, GOAL)

    def test_replanned_wall_stays_visible(self):
        app = self.app
        app.begin('hybrid')
        obstacle = app.result.path[1]
        self.mouse(obstacle, 1)
        self.assertIn(obstacle, app.result.expanded)
        for _ in range(1500):
            app.tick(None)
            self.assertEqual(app.pixels()[obstacle[0]][obstacle[1]], 1)
            if app.phase == 'done':
                break
        self.assertEqual(app.agent, GOAL)

    def test_pause_no_path_recovery_and_clear(self):
        app = self.app
        app.walls = {(r,3) for r in range(20)}
        app.begin('hybrid')
        self.assertFalse(app.result.path)
        for _ in range(100):
            app.tick(None)
        self.assertEqual(app.phase, 'blocked')
        app.pause(None)
        self.mouse((10,3), 3)
        self.assertTrue(app.result.path)
        self.assertFalse(app.running)  # Düzenleme duraklatmayı bozmamalı.
        app.clear(None)
        self.assertFalse(app.walls)
        self.assertEqual(len(app.result.path)-1, 47)

    def test_keys_modes_reset_and_speed(self):
        app = self.app
        for key, mode in [('1','hybrid'), ('2','bfs'), ('3','astar')]:
            app.fig.canvas.callbacks.process('key_press_event', KeyEvent('key_press_event', app.fig.canvas, key=key))
            self.assertEqual(app.mode, mode)
            self.assertEqual(app.agent, START)
        self.mouse((1,1),1)
        self.assertIsNone(app.result)
        app.slider.set_val(30)
        self.assertEqual(app.speed,30)
        app.reset(None)
        self.assertEqual(app.walls,load_map())
        self.assertEqual(app.hybrid.plans,0)

    def test_eraser_tool_and_dashboard(self):
        app = self.app
        # Bu test gerçek panel güncellemesini de denetler.
        app.refresh = lambda: App.refresh(app)
        self.mouse((1, 1), 1)
        app.key(KeyEvent('key_press_event', app.fig.canvas, key='e'))
        self.mouse((1, 1), 1)
        self.assertNotIn((1, 1), app.walls)
        app.key(KeyEvent('key_press_event', app.fig.canvas, key='d'))
        self.mouse((1, 1), 1)
        self.assertIn((1, 1), app.walls)
        self.assertEqual(app.metrics['walls'].get_text(), str(len(app.walls)))
        app.begin('astar')
        for row, method in ((1, 'bfs'), (2, 'astar')):
            result = app.comparison_results[method]
            self.assertEqual(app.comparison[row, 1].get_text().get_text(), str(len(result.expanded)))
        app.pause(None)
        self.assertIn('Duraklatıldı', app.status.get_text())
        app.reset(None)
        self.assertEqual(app.comparison[1, 1].get_text().get_text(), '—')


if __name__ == '__main__':
    unittest.main()
