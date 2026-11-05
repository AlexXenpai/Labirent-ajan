import random
import unittest
from algorithms import search, HybridPlanner

class SearchTests(unittest.TestCase):
    def valid(self, result, walls, start, goal):
        if result.path:
            self.assertEqual(result.path[0], start)
            self.assertEqual(result.path[-1], goal)
            self.assertFalse(set(result.path) & walls)
            for a,b in zip(result.path, result.path[1:]):
                self.assertEqual(abs(a[0]-b[0])+abs(a[1]-b[1]),1)

    def test_random_maps(self):
        rng=random.Random(42)
        for _ in range(60):
            walls={(r,c) for r in range(20) for c in range(50)
                   if rng.random()<.28 and (r,c) not in ((0,0),(19,49))}
            a=search((0,0),(19,49),walls)
            b=search((0,0),(19,49),walls,method='astar')
            self.assertEqual(len(a.path),len(b.path))
            self.valid(a,walls,(0,0),(19,49))
            self.valid(b,walls,(0,0),(19,49))

    def test_dynamic_replan(self):
        planner=HybridPlanner()
        first=planner.plan((2,0),(2,5),set(),5,6)
        self.assertIn('BFS', planner.last_method)
        current=first.path[1]
        walls={first.path[2]}
        changed=planner.plan(current,(2,5),walls,5,6)
        self.assertIn('D* Lite', planner.last_method)
        self.valid(changed,walls,current,(2,5))
        self.assertEqual(len(changed.path),len(search(current,(2,5),walls,5,6).path))
        self.assertEqual(planner.total_expanded,len(first.expanded)+len(changed.expanded))

    def test_blocked_and_identical(self):
        for method in ('bfs','astar'):
            self.assertEqual(search((0,0),(0,2),{(0,1)},1,3,method).path,[])
            self.assertEqual(search((0,0),(0,0),set(),1,1,method).path,[(0,0)])

    def test_incremental_random_sequences(self):
        # 40 farklı harita, her birinde 35 değişiklik; ajan da hareket eder.
        rng = random.Random(2026)
        for scenario in range(40):
            rows, cols = 12, 18
            start, goal = (0, 0), (rows-1, cols-1)
            walls = {(r,c) for r in range(rows) for c in range(cols)
                     if rng.random() < .23 and (r,c) not in (start, goal)}
            planner = HybridPlanner()
            for step in range(36):
                result = planner.plan(start, goal, walls, rows, cols)
                oracle = search(start, goal, walls, rows, cols)
                self.assertEqual(len(result.path), len(oracle.path), (scenario, step))
                self.valid(result, walls, start, goal)
                if result.path and len(result.path) > 1 and rng.random() < .7:
                    start = result.path[1]
                for _ in range(rng.randint(1, 5)):
                    cell = (rng.randrange(rows), rng.randrange(cols))
                    if cell not in (start, goal):
                        walls.symmetric_difference_update({cell})

    def test_disconnect_reconnect_and_shortcut(self):
        planner = HybridPlanner()
        start, goal = (2,0), (2,6)
        initial = planner.plan(start, goal, set(), 5, 7)
        engine = planner.engine
        barrier = {(r,3) for r in range(5)}
        self.assertFalse(planner.plan(start, goal, barrier, 5, 7).path)
        barrier.remove((0,3))
        detour = planner.plan(start, goal, barrier, 5, 7)
        self.assertGreater(len(detour.path), len(initial.path))
        shortcut = planner.plan(start, goal, set(), 5, 7)
        self.assertEqual(len(shortcut.path), len(initial.path))
        self.assertIs(engine, planner.engine)  # Eski arama durumu gerçekten korunur.

    def test_unchanged_map_reuses_field(self):
        planner = HybridPlanner()
        first = planner.plan((0,0), (4,6), set(), 5, 7)
        result = planner.plan(first.path[1], (4,6), set(), 5, 7)
        self.assertEqual(result.expanded, [])
        self.assertEqual(planner.engine.last_pops, 0)
        self.valid(result, set(), first.path[1], (4,6))

    def test_hybrid_start_goal_and_validation(self):
        planner = HybridPlanner()
        self.assertEqual(planner.plan((0,0),(0,0),set(),1,1).path,[(0,0)])
        self.assertEqual(planner.plan((0,0),(0,0),set(),1,1).path,[(0,0)])
        with self.assertRaises(ValueError):
            planner.plan((0,0),(0,0),{(0,0)},1,1)
        with self.assertRaises(ValueError):
            planner.plan((0,0),(0,0),{(1,0)},1,1)

if __name__=='__main__':
    unittest.main()
