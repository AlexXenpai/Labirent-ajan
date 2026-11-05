"""Gerçek uygulama durumlarından hızlandırılmış demo GIF'i üretir."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseEvent
from PIL import Image
from main import App, ROOT


def record():
    app = App()
    app.animation.event_source.stop()
    app.fig.set_dpi(70)
    app.fig.canvas.draw()
    frames = []
    draw = app.refresh
    app.refresh = lambda: None  # Yalnızca kaydedilen karelerde yeniden çiz.

    def capture(repeat=1):
        draw()
        frame = Image.frombytes('RGBA', app.fig.canvas.get_width_height(), app.fig.canvas.buffer_rgba()).convert('RGB')
        frames.extend([frame] * repeat)

    app.begin('hybrid')
    capture(4)
    while app.phase != 'walk':
        for _ in range(6):
            app.tick(None)
        capture()
    for _ in range(3):
        app.tick(None)
    obstacle = app.result.path[app.walk+3]
    x, y = app.ax.transData.transform((obstacle[1], obstacle[0]))
    event = MouseEvent('button_press_event', app.fig.canvas, x, y, button=1)
    app.fig.canvas.callbacks.process('button_press_event', event)
    assert obstacle in app.walls and obstacle not in app.result.path
    capture(6)
    while app.phase != 'walk':
        for _ in range(6):
            app.tick(None)
        capture()
    draw()
    app.fig.savefig(ROOT/'docs/dynamic.png',dpi=130)
    while app.phase != 'done':
        for _ in range(5):
            app.tick(None)
        capture()
    capture(8)
    frames[0].save(ROOT/'docs/demo.gif',save_all=True,append_images=frames[1:],duration=110,loop=0,optimize=True)
    plt.close(app.fig)
    print(f'docs/demo.gif: {len(frames)} kare; engel: {obstacle}')


if __name__=='__main__':
    record()
