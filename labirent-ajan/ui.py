"""Matplotlib üzerinde masaüstü labirent arayüzü; arama mantığından bağımsızdır."""
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import FancyBboxPatch
from matplotlib.widgets import Button, Slider

BG, PANEL, TEXT, MUTED = '#0b1220', '#111e31', '#edf3fc', '#9aadc7'
ACCENT = '#36d6ab'


def build_ui(app, COLORS, ROWS, COLS):
    app.fig = plt.figure(figsize=(15, 9), facecolor=BG)
    app.fig.canvas.manager.set_window_title('Labirent Ajanı • Yol Bulma Laboratuvarı')
    app.fig.text(.045, .946, 'LABİRENT / AJAN', color=ACCENT, fontsize=11, weight='bold')
    app.fig.text(.045, .894, 'Bir yol çiz. Bir çözüm keşfet.', color=TEXT, fontsize=26, weight='bold')
    app.fig.text(.045, .859, 'Duvarları düzenle, algoritmaları karşılaştır ve ajanın yolculuğunu izle.',
                 color=MUTED, fontsize=11)

    def card(x, y, w, h):
        app.fig.add_artist(FancyBboxPatch((x, y), w, h,
            boxstyle='round,pad=0.008,rounding_size=0.012',
            transform=app.fig.transFigure, facecolor=PANEL, edgecolor='#23334b', zorder=0))

    app.metrics = {}
    for x, key, label in ((.045, 'grid', 'LABİRENT'), (.225, 'walls', 'DUVAR KARESİ'),
                          (.405, 'path', 'EN KISA YOL'), (.585, 'visited', 'ANİMASYONDA İNCELENEN')):
        card(x, .767, .151, .064)
        app.fig.text(x+.009, .812, label, color=MUTED, fontsize=8)
        app.metrics[key] = app.fig.text(x+.009, .78, '—', color=TEXT, fontsize=17, weight='bold')
    card(.045, .344, .691, .394)
    app.ax = app.fig.add_axes([.053, .358, .675, .366])
    app.image = app.ax.imshow(app.pixels(), cmap=ListedColormap(COLORS), vmin=0, vmax=6,
                              interpolation='nearest')
    app.ax.set_xticks([x-.5 for x in range(COLS+1)], minor=True)
    app.ax.set_yticks([x-.5 for x in range(ROWS+1)], minor=True)
    app.ax.grid(which='minor', color='#28394f', linewidth=.45)
    app.ax.tick_params(which='both', bottom=False, left=False, labelbottom=False, labelleft=False)
    for spine in app.ax.spines.values():
        spine.set_visible(False)
    app.ax.text(1, 10, 'B', color=BG, weight='bold', fontsize=8, ha='center', va='center')
    app.ax.text(48, 10, 'H', color=BG, weight='bold', fontsize=8, ha='center', va='center')
    for i, (label, color) in enumerate(zip(('Başlangıç', 'Hedef', 'Ajan', 'İncelenen', 'Yol', 'Duvar'),
                                         (COLORS[4], COLORS[5], COLORS[6], COLORS[2], COLORS[3], COLORS[1]))):
        app.fig.text(.05+i*.112, .322, '●', color=color, fontsize=11)
        app.fig.text(.065+i*.112, .322, label, color=MUTED, fontsize=9)
    app.status = app.fig.text(.045, .282, '', color=ACCENT, fontsize=12, weight='bold')
    app.info = app.fig.text(.045, .258, '', color=MUTED, fontsize=9)
    app.fig.text(.045, .215, 'ALGORİTMA KARŞILAŞTIRMASI', color=TEXT, fontsize=10, weight='bold')
    app.comparison_ax = app.fig.add_axes([.045, .076, .691, .122])
    app.comparison_ax.axis('off')
    app.comparison = app.comparison_ax.table(
        cellText=[['BFS', '—', '—'], ['A*', '—', '—'], ['Hibrit · BFS + D* Lite', '—', '—']],
        colLabels=['Algoritma', 'İncelenen kare', 'Yol / adım'],
        cellLoc='left', bbox=[0, 0, 1, 1], colWidths=[.44, .28, .28])
    app.comparison.auto_set_font_size(False)
    app.comparison.set_fontsize(10)
    app.comparison_results = {}
    for (row, col), cell in app.comparison.get_celld().items():
        cell.set_edgecolor('#23334b')
        cell.set_facecolor('#1d2d44' if row == 0 else PANEL)
        cell.get_text().set_color(MUTED if row == 0 else TEXT)
        cell.PAD = .08
    app.fig.text(.045, .048, 'Aynı harita ve konum • Son planın sonuçları • Hibrit, değişikliklerde önceki bilgiyi kullanır.',
                 color=MUTED, fontsize=8)

    card(.766, .048, .19, .891)
    app.fig.text(.78, .904, 'KONTROL PANELİ', color=TEXT, fontsize=12, weight='bold')
    app.fig.text(.78, .866, '01  Bir arama başlat', color=MUTED, fontsize=10)
    app.buttons = []

    def button(rect, label, callback, primary=False):
        ax = app.fig.add_axes(rect)
        widget = Button(ax, label, color=ACCENT if primary else '#203149',
                        hovercolor='#75e8c9' if primary else '#304866')
        widget.label.set_color(BG if primary else TEXT)
        widget.label.set_fontsize(10)
        widget.label.set_weight('bold')
        for spine in ax.spines.values():
            spine.set_visible(False)
        widget.on_clicked(callback)
        app.buttons.append(widget)
        return widget

    button([.78, .796, .161, .048], 'Hibrit başlat  [1]', lambda _: app.begin('hybrid'), True)
    button([.78, .742, .076, .04], 'BFS  [2]', lambda _: app.begin('bfs'))
    button([.865, .742, .076, .04], 'A*  [3]', lambda _: app.begin('astar'))
    app.pause_button = button([.78, .688, .161, .038], 'Duraklat', app.pause)
    app.fig.text(.78, .648, 'Arama animasyonu hızı', color=MUTED, fontsize=10)
    app.slider = Slider(app.fig.add_axes([.785, .615, .137, .015]), '', 1, 50,
                        valinit=12, valstep=1, color=ACCENT, track_color='#304866')
    app.slider.valtext.set_color(TEXT)
    app.slider.valtext.set_fontsize(9)
    app.slider.on_changed(lambda value: setattr(app, 'speed', int(value)))
    app.fig.text(.78, .556, '02  Labirenti düzenle', color=MUTED, fontsize=10)
    app.wall_button = button([.78, .498, .076, .04], 'Duvar [D]', lambda _: app.set_tool('wall'))
    app.erase_button = button([.865, .498, .076, .04], 'Silgi [E]', lambda _: app.set_tool('erase'))
    app.fig.text(.78, .433, 'Sol tıkla veya sürükle.\nSağ tık her zaman duvar siler.',
                 color=MUTED, fontsize=9, linespacing=1.7)
    button([.78, .366, .161, .038], 'Örnek labirente dön  [R]', app.reset)
    button([.78, .315, .161, .038], 'Tüm duvarları temizle', app.clear)
    app.fig.text(.78, .260, 'NASIL ÇALIŞIR?', color=ACCENT, fontsize=9, weight='bold')
    app.fig.text(.78, .139, 'Hibriti başlat, sonra ajanın\nönüne yeni bir duvar çiz.\nD* Lite rotayı günceller.\n\nGeçit yoksa silgiyle yol aç.',
                 color=MUTED, fontsize=9, linespacing=1.7)
    app.fig.text(.78, .082, 'BOŞLUK  Duraklat / devam et', color=MUTED, fontsize=8)


def refresh_ui(app):
    app.metrics['grid'].set_text('20 × 50')
    app.metrics['walls'].set_text(str(len(app.walls)))
    app.metrics['path'].set_text(str(len(app.result.path)-1) + ' adım' if app.result and app.result.path else '—')
    app.metrics['visited'].set_text(str(len(app.visited)))
    titles = {'idle': 'Hazır. İlk yolculuğunu başlat.', 'search': 'Arama adımları gösteriliyor…',
              'path': 'En kısa yol çiziliyor…', 'walk': 'Ajan hedefe ilerliyor…',
              'done': 'Hedefe ulaşıldı.', 'blocked': 'Geçit bulunamadı. Bir duvar silerek yol aç.'}
    app.status.set_text('Duraklatıldı. Devam etmek için Boşluk tuşuna bas.'
                        if not app.running and app.result else titles[app.phase])
    app.status.set_color('#fb7b87' if app.phase == 'blocked' else ACCENT)
    if app.result:
        method = app.hybrid.last_method if app.mode == 'hybrid' else {'bfs': 'BFS', 'astar': 'A* · Manhattan uzaklığı'}[app.mode]
        app.info.set_text(f'{method}  •  İncelenen kareler mor, bulunan yol sarı gösterilir.')
    else:
        app.info.set_text('Sol tık: seçili araç  •  Sağ tık: sil  •  B: başlangıç  •  H: hedef')
    app.pause_button.label.set_text('Duraklat  [Boşluk]' if app.running else 'Devam et  [Boşluk]')
    for tool, widget in (('wall', app.wall_button), ('erase', app.erase_button)):
        widget.color = '#345c60' if app.edit_tool == tool else '#203149'
        widget.ax.set_facecolor(widget.color)
    for row, method in enumerate(('bfs', 'astar', 'hybrid'), 1):
        for col in range(3):
            app.comparison[row, col].set_facecolor('#1b3a3e' if app.result and app.mode == method else PANEL)
