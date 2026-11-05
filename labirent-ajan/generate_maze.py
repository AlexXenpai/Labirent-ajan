"""Örnek veri setini ağ erişimi olmadan yeniden üretir."""
import json
from pathlib import Path


def make_maze():
    walls = []
    for i, col in enumerate(range(5, 46, 5)):
        gap = 3 if i % 2 == 0 else 16
        walls.extend((row, col) for row in range(20) if row not in (gap, gap+1))
    return {'rows': 20, 'cols': 50, 'start': [10, 1], 'goal': [10, 48], 'walls': walls}


if __name__ == '__main__':
    target = Path(__file__).resolve().parent / 'data/maze.json'
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(make_maze(), indent=2), encoding='utf-8')
    print(f'Oluşturuldu: {target.name}; 20x50, {len(make_maze()["walls"])} engelli kare')
