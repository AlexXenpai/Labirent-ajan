"""Aynı değişiklik dizisini üç yöntemle karşılaştırır; CSV ve PNG üretir."""
import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from algorithms import HybridPlanner, search

ROOT = Path(__file__).resolve().parent


def run():
    data = json.loads((ROOT/'data/maze.json').read_text())
    walls = {tuple(p) for p in data['walls']}
    start, goal = tuple(data['start']), tuple(data['goal'])
    hybrid = HybridPlanner()
    records = []

    def measure(event):
        results = {'BFS': search(start,goal,walls),
                   'A*': search(start,goal,walls,method='astar'),
                   'Hibrit': hybrid.plan(start,goal,walls)}
        lengths = {len(result.path) for result in results.values()}
        if len(lengths) != 1:
            raise AssertionError(f'Algoritmaların yol uzunluğu farklı: {event}')
        for name, result in results.items():
            records.append({'event':event, 'algorithm':name,
                            'path_steps':len(result.path)-1 if result.path else -1,
                            'expanded_unique':len(result.expanded),
                            'queue_pops':hybrid.engine.last_pops if name=='Hibrit' and hybrid.plans>1 else len(result.expanded),
                            'vertex_updates':hybrid.engine.last_updates if name=='Hibrit' else 0,
                            'start_row':start[0], 'start_col':start[1]})
        return results['Hibrit']

    first = measure('İlk plan')
    start = first.path[3]
    moved = measure('Ajan 3 adım ilerledi')
    obstacle = moved.path[4]
    walls.add(obstacle)
    measure('Yola engel eklendi')
    walls.remove(obstacle)
    measure('Engel silindi')
    added_barrier = {(r,25) for r in range(20)} - walls
    walls.update(added_barrier)
    measure('Geçit tamamen kapandı')
    walls.difference_update(added_barrier)
    measure('Geçit yeniden açıldı')
    (ROOT/'docs').mkdir(exist_ok=True)
    with (ROOT/'docs/results.csv').open('w',newline='',encoding='utf-8') as output:
        writer = csv.DictWriter(output,fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)
    fig, ax = plt.subplots(figsize=(12,5))
    events = [r['event'] for r in records[::3]]
    for i,(name,color) in enumerate([('BFS','#64748b'),('A*','#38bdf8'),('Hibrit','#8b5cf6')]):
        heights = [r['expanded_unique'] for r in records if r['algorithm']==name]
        bars=ax.bar([n+(i-1)*.25 for n in range(len(events))],heights,width=.25,label=name,color=color)
        ax.bar_label(bars,padding=3,fontsize=9)
    ax.set_xticks(range(len(events)),['İlk\nplan','Ajan\nilerledi','Engel\neklendi','Engel\nsilindi','Geçit\nkapandı','Geçit\naçıldı'])
    ax.set_ylabel('Plan başına işlenen benzersiz kare')
    ax.set_title('BFS / A* / BFS + D* Lite — aynı harita ve mevcut konum')
    ax.legend()
    ax.set_ylim(0, max(r['expanded_unique'] for r in records)*1.15)
    fig.tight_layout()
    fig.savefig(ROOT/'docs/comparison.png',dpi=140)
    plt.close(fig)
    for r in records:
        print(f"{r['event']:<24} {r['algorithm']:<7} adım={r['path_steps']:>3} kare={r['expanded_unique']:>3}")
    return records


if __name__=='__main__':
    run()
