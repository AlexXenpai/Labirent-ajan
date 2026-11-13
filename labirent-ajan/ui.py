"""Matplotlib tabanlı labirent görünümü ve kontrolleri."""
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.transforms import Affine2D
from matplotlib.widgets import Button, Slider


WIDTH, HEIGHT = 1360, 760
BG, PAPER, BORDER = '#f1f0eb', '#fffefa', '#e1e3df'
INK, MUTED = '#172637', '#526271'
TEAL, MINT = '#0b675b', '#e0f1e9'
BUTTON, HOVER = '#eef1f1', '#e0e7e8'
GRID, WALL, VISITED = '#192535', '#8191a6', '#393653'
ROUTE, START, GOAL, AGENT = '#ffce72', '#72e6b6', '#ff929f', '#75d8ff'
COLORS = [GRID, WALL, VISITED, '#333c49', GRID, GRID, '#333c49']
PHASES = {
    'idle': 'Başlamaya hazır',
    'search': 'Kareler taranıyor',
    'path': 'Rota çiziliyor',
    'walk': 'Ajan hedefe ilerliyor',
    'done': 'Hedefe ulaşıldı',
    'blocked': 'Geçit kapalı',
}


def build_ui(app, rows, cols, start, goal):
    with plt.rc_context({'toolbar': 'None'}):
        app.fig = plt.figure(figsize=(WIDTH / 100, HEIGHT / 100), facecolor=BG)
    fig = app.fig
    fig.canvas.manager.set_window_title('Labirentte Yol Bulan Ajan')
    design = Affine2D()
    transform = design + fig.transFigure
    axes, sizes = [], []

    def label(x, y, value, size=10, color=INK, weight='normal', align='left'):
        artist = fig.text(x, y, value, transform=transform, ha=align, va='center',
                          fontsize=size, color=color, weight=weight)
        sizes.append((artist.set_fontsize, size))
        return artist

    def panel(x, y, w, h):
        fig.add_artist(FancyBboxPatch(
            (x, y), w, h, transform=transform, zorder=0,
            boxstyle='round,pad=0,rounding_size=13',
            linewidth=.8, facecolor=PAPER, edgecolor=BORDER))

    def rule(x, y, w):
        fig.add_artist(Rectangle((x, y), w, 1, transform=transform,
                                 zorder=0, linewidth=0, facecolor=BORDER))

    def region(x, y, w, h):
        ax = fig.add_axes([0, 0, .01, .01])
        axes.append((ax, x, y, w, h))
        return ax

    label(32, 42, 'Labirentte Yol Bulan Ajan', 24, weight='bold')
    label(33, 77, 'BFS + D* Lite ile dinamik yol planlama', 10.5, MUTED)

    panel(32, 104, 994, 478)
    app.status_dot = label(53, 130, '●', 9, TEAL)
    app.status = label(72, 130, '', 11, weight='bold')
    label(897, 130, f'{rows} × {cols}', 9.5, MUTED, align='right')
    label(915, 130, '·', 10, MUTED, align='center')
    app.metrics = {'walls': label(958, 130, '', 9.5, INK, 'bold', 'right')}
    label(966, 130, 'duvar', 9.5, MUTED)

    board_width = 952
    app.ax = region(53, 151, board_width, board_width * rows / cols)
    app.image = app.ax.imshow(app.pixels(), cmap=ListedColormap(COLORS),
                              vmin=0, vmax=len(COLORS) - 1, interpolation='nearest')
    boundaries = [((col - .5, -.5), (col - .5, rows - .5)) for col in range(cols + 1)]
    boundaries += [((-.5, row - .5), (cols - .5, row - .5)) for row in range(rows + 1)]
    app.ax.add_collection(LineCollection(boundaries, colors='#536278', alpha=.39,
                                         linewidths=.44, zorder=2))
    app.ax.set_axis_off()
    app.route_line, = app.ax.plot([], [], color=ROUTE, linewidth=2.7,
                                 solid_capstyle='round', solid_joinstyle='round', zorder=3)
    sizes.append((app.route_line.set_linewidth, 2.7))
    for (row, col), glyph, color in ((start, 'B', START), (goal, 'H', GOAL)):
        marker, = app.ax.plot(col, row, 'o', color=color, markersize=10.2,
                              markeredgewidth=0, zorder=4)
        sizes.append((marker.set_markersize, 10.2))
        character = app.ax.text(col, row, glyph, color=INK, weight='bold',
                                ha='center', va='center', fontsize=6, zorder=5)
        sizes.append((character.set_fontsize, 6))
    app.agent_marker, = app.ax.plot([], [], 'o', color=AGENT, markeredgecolor=INK,
                                    markeredgewidth=.9, markersize=7.7, zorder=6)
    sizes.append((app.agent_marker.set_markersize, 7.7))

    legend = ((53, 'B', START, 'Başlangıç'), (197, 'H', GOAL, 'Hedef'),
              (314, '●', AGENT, 'Ajan'), (422, '■', WALL, 'Duvar'),
              (543, '■', '#9a88bb', 'Taranan kare'), (707, '━', ROUTE, 'Rota'))
    for x, icon, color, title in legend:
        fig.add_artist(FancyBboxPatch((x, 544), 23, 23, transform=transform, zorder=0,
                                     boxstyle='round,pad=0,rounding_size=4',
                                     linewidth=0, facecolor=GRID))
        label(x + 11.5, 555.5, icon, 8.5, color, 'bold', 'center')
        label(x + 31, 555.5, title, 9, MUTED)

    panel(32, 598, 994, 130)
    label(53, 621, 'Son plan', 12, weight='bold')
    app.info = label(53, 645, '', 9, MUTED)
    label(53, 676, 'En kısa yol', 8.5, MUTED)
    label(197, 676, 'Animasyonda taranan', 8.5, MUTED)
    app.metrics['path'] = label(53, 704, '', 15, weight='bold')
    app.metrics['visited'] = label(197, 704, '', 15, weight='bold')
    fig.add_artist(Rectangle((372, 616), 1, 94, transform=transform,
                             zorder=0, linewidth=0, facecolor=BORDER))
    label(397, 621, 'Algoritma karşılaştırması', 12, weight='bold')
    app.comparison_ax = region(397, 640, 608, 73)
    app.comparison_ax.axis('off')
    app.comparison = app.comparison_ax.table(
        cellText=[['BFS', '—', '—'], ['A*', '—', '—'], ['Hibrit · BFS + D* Lite', '—', '—']],
        colLabels=['Algoritma', 'İncelenen kare', 'Yol (adım)'],
        colLoc='left', cellLoc='left', bbox=[0, 0, 1, 1], colWidths=[.46, .30, .24])
    app.comparison.auto_set_font_size(False)
    app.comparison_results = {}
    for (row, col), cell in app.comparison.get_celld().items():
        cell.set_linewidth(.65)
        cell.set_edgecolor(PAPER)
        cell.PAD = .05
        cell_text = cell.get_text()
        cell_text.set_color(MUTED if row == 0 else INK)
        cell_text.set_weight('bold' if row == 0 else 'normal')
        sizes.append((cell_text.set_fontsize, 8 if row == 0 else 9))

    panel(1048, 104, 280, 624)
    label(1067, 130, 'Arama', 12, weight='bold')
    app.buttons = []

    def button(rect, title, callback, shortcut=None, primary=False):
        ax = region(*rect)
        color, hover = (TEAL, '#084e45') if primary else (BUTTON, HOVER)
        widget = Button(ax, title, color=color, hovercolor=hover)
        widget.label.set_x(.06 if rect[2] > 150 else .11)
        widget.label.set_ha('left')
        widget.label.set_color(PAPER if primary else INK)
        widget.label.set_weight('bold')
        sizes.append((widget.label.set_fontsize, 11 if primary else 9))
        if shortcut:
            key = ax.text(.94 if rect[2] > 150 else .89, .5, shortcut, ha='right',
                          va='center', transform=ax.transAxes,
                          color='#dcf8ef' if primary else MUTED)
            sizes.append((key.set_fontsize, 8))
        for spine in ax.spines.values():
            spine.set_visible(False)
        widget.on_clicked(callback)
        app.buttons.append(widget)
        return widget

    button((1067, 151, 242, 44), 'Hibrit başlat', lambda _: app.begin('hybrid'), '1', primary=True)
    button((1067, 204, 116, 35), 'BFS', lambda _: app.begin('bfs'), '2')
    button((1193, 204, 116, 35), 'A*', lambda _: app.begin('astar'), '3')

    rule(1067, 260, 242)
    label(1067, 284, 'Duvarları düzenle', 12, weight='bold')
    app.wall_button = button((1067, 305, 116, 36), 'Duvar', lambda _: app.set_tool('wall'), 'D')
    app.erase_button = button((1193, 305, 116, 36), 'Silgi', lambda _: app.set_tool('erase'), 'E')
    label(1067, 360, 'Sol tıkla veya sürükle.', 9, MUTED)
    label(1067, 380, 'Sağ tuşla duvar sil.', 9, MUTED)
    button((1067, 401, 242, 34), 'Örnek labirente dön', app.reset, 'R')
    button((1067, 443, 242, 34), 'Tüm duvarları temizle', app.clear)

    rule(1067, 498, 242)
    label(1067, 522, 'Animasyon', 12, weight='bold')
    label(1067, 551, 'Arama hızı', 9, MUTED)
    app.slider = Slider(region(1072, 567, 211, 15), '', 1, 50, valinit=app.speed,
                        valstep=1, color=TEAL, track_color='#dce4e3',
                        handle_style={'facecolor': PAPER, 'edgecolor': TEAL, 'size': 9})
    app.slider.valtext.set_color(MUTED)
    sizes.append((app.slider.valtext.set_fontsize, 9))
    app.slider.on_changed(lambda value: setattr(app, 'speed', int(value)))
    app.pause_button = button((1067, 604, 242, 35), 'Duraklat', app.pause, 'Boşluk')
    label(1067, 671, 'Hibrit çalışırken rotaya duvar ekle.', 9, MUTED)
    label(1067, 690, 'Ajan, bulunduğu yerden yeni yol bulur.', 9, MUTED)

    def fit_layout(_=None):
        width, height = fig.get_size_inches() * 100
        scale = min(width / WIDTH, height / HEIGHT)
        x_margin = (1 - WIDTH * scale / width) / 2
        y_margin = (1 - HEIGHT * scale / height) / 2
        x_scale, y_scale = scale / width, scale / height
        design.clear().scale(x_scale, -y_scale).translate(x_margin, 1 - y_margin)
        for ax, x, y, w, h in axes:
            ax.set_position([x_margin + x * x_scale, 1 - y_margin - (y + h) * y_scale,
                             w * x_scale, h * y_scale])
        for set_size, base in sizes:
            set_size(base * scale)
    fit_layout()
    fig.canvas.mpl_connect('resize_event', fit_layout)


def refresh_ui(app, start, goal):
    app.metrics['walls'].set_text(str(len(app.walls)))
    path = app.result.path if app.result else []
    app.metrics['path'].set_text(f'{len(path) - 1} adım' if path else 'Yol yok' if app.result else '—')
    app.metrics['visited'].set_text(str(len(app.visited)) if app.result else '—')
    paused = not app.running and app.result
    app.status.set_text('Duraklatıldı' if paused else PHASES[app.phase])
    app.status_dot.set_color('#ba4654' if app.phase == 'blocked' else '#976420' if paused else TEAL)
    method = {'bfs': 'BFS', 'astar': 'A* · Manhattan uzaklığı', 'hybrid': app.hybrid.last_method}
    app.info.set_text(method[app.mode] if app.result else 'Bir arama başlat.')
    app.pause_button.label.set_text('Duraklat' if app.running else 'Devam et')

    if app.route:
        rows, cols = zip(*app.route)
        app.route_line.set_data(cols, rows)
    else:
        app.route_line.set_data([], [])
    row, col = app.agent
    app.agent_marker.set_data([], [])
    if app.agent == goal:
        app.agent_marker.set_data([col], [row])
        app.agent_marker.set_markerfacecolor('none')
        app.agent_marker.set_markeredgecolor(AGENT)
    elif app.agent != start:
        app.agent_marker.set_data([col], [row])
        app.agent_marker.set_markerfacecolor(AGENT)
        app.agent_marker.set_markeredgecolor(INK)

    for tool, widget in (('wall', app.wall_button), ('erase', app.erase_button)):
        selected = app.edit_tool == tool
        color = MINT if selected else BUTTON
        if widget.color != color:
            widget.color = color
            widget.hovercolor = '#d2ebdf' if selected else HOVER
            widget.ax.set_facecolor(color)
            widget.label.set_color(TEAL if selected else INK)

    for row, mode in enumerate(('bfs', 'astar', 'hybrid')):
        for col in range(3):
            app.comparison[row + 1, col].set_facecolor(
                MINT if app.result and app.mode == mode else '#f3f5f3')
    for col in range(3):
        app.comparison[0, col].set_facecolor(PAPER)
