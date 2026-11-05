"""Mevcut kod ve benchmark sonuçlarından 16:9 proje sunumu üretir."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch
from PIL import Image

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / 'sunum'
PDF = BASE / 'Labirent_Ajani_Sunum.pdf'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'pdf.fonttype': 42})
BG, INK, MUTED, BLUE, TEAL = '#F4F7FB', '#14263D', '#54657B', '#1769B3', '#087F8C'
figs, notes = [], []
records = list(csv.DictReader((BASE/'docs/results.csv').open(encoding='utf-8')))

def txt(ax, x, y, s, size=20, color=INK, weight='normal', **kwargs):
    return ax.text(x, y, s, fontsize=size, color=color, fontweight=weight,
                   va='top', transform=ax.transAxes, **kwargs)

def page(title, sub, note):
    n = len(figs)+1
    f = plt.figure(figsize=(16,9), facecolor=BG)
    ax = f.add_axes([0,0,1,1]); ax.axis('off')
    ax.plot([.055,.945],[.89,.89],color=BLUE,lw=3,transform=ax.transAxes)
    txt(ax,.055,.96,'LABİRENTTE YOL BULAN AJAN  /  BFS + D* LITE + A*',11,BLUE,'bold')
    txt(ax,.055,.85,title,30,weight='bold')
    txt(ax,.055,.775,sub,15,MUTED)
    txt(ax,.055,.055,'Python / Matplotlib • Proje sunumu • Kasım 2026',10,MUTED)
    txt(ax,.945,.055,f'{n:02d} / 16',10,MUTED,ha='right')
    figs.append(f); notes.append(f'## {n}. {title}\n\n{note}\n')
    return f,ax

def card(ax,x,y,w,h,title,body):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.012',facecolor='white',edgecolor='#DFE7F0',transform=ax.transAxes))
    txt(ax,x+.02,y+h-.025,title,21,BLUE,'bold')
    txt(ax,x+.02,y+h-.105,body,17,linespacing=1.55)

def row(ax,y,name,file,purpose,usage):
    txt(ax,.07,y,name,20,BLUE,'bold')
    txt(ax,.93,y,file,13,MUTED,ha='right')
    txt(ax,.07,y-.055,purpose,16)
    txt(ax,.07,y-.105,usage,14,MUTED)

def table(f,headers,data,bbox):
    ax=f.add_axes(bbox); ax.axis('off')
    t=ax.table(cellText=data,colLabels=headers,cellLoc='center',bbox=[0,0,1,1])
    t.auto_set_font_size(False);t.set_fontsize(16)
    for (r,c),cell in t.get_celld().items():
        cell.set_edgecolor('white');cell.set_linewidth(2)
        cell.set_facecolor('#DDEAF7' if r==0 else ('white' if r%2 else '#E8F2F0'))
        cell.get_text().set_color(INK)
    return t

f,a=page('Labirentte yol bulan ajan','Statik aramadan değişen engellere uyum sağlayan bir sisteme',
'Bu projede amaç yalnızca yolu çizmek değil, harita değiştiğinde ajanın mevcut konumundan yeni en kısa yolu bulmaktır. BFS başlangıç bilgisini oluşturur; D* Lite bu bilgiyi sonraki değişikliklerde kullanır. A* karşılaştırma yöntemidir.')
txt(a,.065,.66,'Duvarları çiz. En kısa yolu bul.\nHarita değişince rotayı güncelle.',31,weight='bold',linespacing=1.5)
for x,t,b in [(.065,'20 × 50 grid','1.000 karelik çalışma alanı'),(.365,'Hibrit planlama','BFS + artımlı D* Lite'),(.665,'Görsel karşılaştırma','A* ve BFS kare sayıları')]:card(a,x,.22,.26,.21,t,b)

f,a=page('Projenin amacı ve kuralları','Eşit maliyetli, dört yönlü hareket üzerinde en kısa yol',
'Her hareket bir adım maliyetindedir; çapraz hareket yoktur. Örnek haritada 9 geçitli duvar sütunu ve 162 duvar karesi vardır. Minimum 8 engel şartı örnek haritayla sağlanır; kullanıcı deney yapmak için duvarları silebilir. Başlangıç, hedef ve ajanın bulunduğu kare duvar yapılamaz.')
card(a,.065,.38,.40,.31,'Harita ve etkileşim','20 satır × 50 sütun\n9 geçitli engel sütunu; 162 duvar\nFareyle duvar ekleme ve silme')
card(a,.525,.38,.40,.31,'Arama ve hareket','Başlangıç → hedef\nYukarı / aşağı / sağ / sol\nHer geçişin maliyeti: 1 adım')
txt(a,.075,.27,'Başlangıç: (10, 1)    Hedef: (10, 48)    [satır, sütun; 0’dan başlayan indeks]',17,BLUE)
txt(a,.075,.18,'Harita: data/maze.json   •   Örnek harita üretimi: generate_maze.py',17,MUTED)

f,a=page('Uygulamanın yeni arayüzü','Kontrol paneli, canlı sayaçlar ve algoritma karşılaştırması',
'Sağda algoritma düğmeleri, duraklatma, hız ve çizim araçları var. B başlangıcı, H hedefi gösterir. Üstteki incelenen sayaç animasyonda gösterilen kareleri sayar; alt tablo tamamlanmış aramanın toplamıdır. Ekran görüntüsü güncel uygulamanın örnek haritadaki sonucudur.')
ax=f.add_axes([.07,.105,.86,.62]);ax.imshow(Image.open(BASE/'docs/screenshot.png'));ax.axis('off')

f,a=page('BFS ve A* nasıl çalışıyor?','İki yöntem de bu gridde en kısa yolu bulur; arama sıraları farklıdır.',
'BFS başlangıca uzaklığına göre katman katman ilerler. A* gidilen yol maliyetine hedefe tahmini uzaklığı ekler. Manhattan uzaklığı dört yönlü birim maliyetli grid için uygundur. Bu kodda A* eşit toplam maliyette hedefe daha yakın kareyi önce seçer. Daha az kare incelemek daha kısa yol bulmak anlamına gelmez.')
card(a,.065,.34,.40,.35,'BFS • Genişlik öncelikli arama','FIFO kuyruk: deque\nÖnce yakın katmanlar incelenir.\nHedef bulununca arama durur.\nEşit maliyetli gridde optimal yol.')
card(a,.525,.34,.40,.35,'A* • Hedefe yönelik arama','Öncelik kuyruğu: heapq\nf(n) = g(n) + h(n)\ng: başlangıçtan gelen maliyet\nh: Manhattan uzaklığı')
txt(a,.075,.23,'h(n) = |satır − hedef_satır| + |sütun − hedef_sütun|',20,TEAL,'bold')
txt(a,.075,.14,'Kod: algorithms.py → search(..., method="bfs") veya method="astar"',16,MUTED)

f,a=page('Hibrit yöntemde iki algoritma birleşiyor','BFS’nin oluşturduğu bilgi, D* Lite’ın başlangıç durumu olur.',
'Hibrit ilk çağrıda hedeften ters BFS yaparak erişilebilen bütün karelerin hedefe uzaklığını hesaplar. Bu değerler g ve rhs tablolarına aktarılır. Sonraki değişikliklerde aynı DStarLite nesnesi tutulur. replan değişen duvarları bulur ve repair gerekli tutarsızlıkları onarır. Yeni hedef veya grid boyutu yeni başlangıç gerektirir.')
for x,t,b in [(.065,'01  İlk plan','Hedeften ters BFS\nTam mesafe alanı\ng ve rhs tablolarını başlat'),(.365,'02  Harita değişimi','Ajanın konumunu koru\nDeğişen duvarları belirle\nİlgili komşuları güncelle'),(.665,'03  D* Lite onarımı','Önceki bilgiyi kullan\nGerekli maliyetleri düzelt\nYeni en kısa yolu çıkar')]:card(a,x,.36,.26,.33,t,b)
txt(a,.075,.24,'Akış: HybridPlanner.plan() → DStarLite.replan() → repair() → path()',18,BLUE)
txt(a,.075,.14,'BFS / A* düğmeleri sıfırdan arar; hibrit düzenleme sırasında eski durumu korur.',17,MUTED)

f,a=page('İlk haritada ölçülen sonuçlar','Aynı başlangıç, aynı hedef ve aynı duvarlar',
'Bu sayılar benchmark.py yeniden çalıştırılarak doğrulandı. Üç yöntemin yolu 155 adımdır. A* BFS’den 55 kare daha az işler. Hibrit ilk planda tam ters mesafe alanını hesapladığı için daha çok kare işler; avantajını dinamik güncellemelerde arıyoruz. İncelenen kare sayısı işlem süresi ölçümü değildir.')
initial=records[:3]
table(f,['Algoritma','İncelenen kare','Yol / adım'],[[r['algorithm'],r['expanded_unique'],r['path_steps']] for r in initial],[.075,.38,.85,.29])
diff=int(initial[0]['expanded_unique'])-int(initial[1]['expanded_unique'])
txt(a,.075,.28,f'A*: aynı en kısa yol, BFS’ye göre {diff} kare daha az inceleme.',22,TEAL,'bold')
txt(a,.075,.18,'Hibrit ilk planda tam mesafe alanı kurar; tekil BFS hedefe ulaşınca durur.\nÖlçüt: plan başına işlenen farklı kare sayısı; süre veya toplam işlem sayısı değildir.',17,MUTED,linespacing=1.5)

f,a=page('Harita değiştiğinde ne oluyor?','Aynı değişiklik dizisinde, aynı mevcut konumdan karşılaştırma',
'İlk planın ardından ajan 3 adım ilerletilir. Sonra yoluna bir duvar eklenir, silinir, bir geçit tamamen kapanır ve tekrar açılır. Bu sabit deneyde engel ekleme 6, silme 5 kare onarımı gerektirir. Sıfır kare, önceki alanın yeterli olduğunu belirtir; sıfır süre demek değildir. Geçit kapanırken hibrit 429, BFS 428 kare işler; hibrit her durumda daha az çalışmaz.')
events=[]
for i in range(3,len(records),3):
    group=records[i:i+3];events.append([group[0]['event']]+[r['expanded_unique'] for r in group])
table(f,['Senaryo','BFS','A*','Hibrit'],events,[.065,.30,.87,.40])
txt(a,.075,.22,'0 kare: mevcut mesafe alanıyla yol çıkarılabildi; sıfır işlem süresi değildir.',17,BLUE)
txt(a,.075,.14,'Hibritin avantajı değişikliğe bağlıdır. Geçit kapandığında üç yöntem de yol bulamaz.',17,MUTED)

f,a=page('Projenin dosya yapısı','Arama mantığı, kullanıcı olayları ve görsel tasarım ayrı tutulur.',
'algorithms.py grafik arayüzden bağımsızdır. main.py uygulama durumunu ve olayları yönetir. ui.py tasarımı oluşturur ve sayaçları günceller. Harita JSON dosyasından yüklenir. benchmark.py karşılaştırma çıktıları üretir. Testler algoritma ve arayüz seviyesinde ayrılmıştır.')
table(f,['Dosya','Görevi'],[
['algorithms.py','BFS, A*, D* Lite ve hibrit planlayıcı'],['main.py','Fare / klavye olayları ve animasyon akışı'],['ui.py','Kontrol paneli, sayaçlar ve sonuç tablosu'],['generate_maze.py / data/maze.json','Örnek haritanın üretimi ve verisi'],['benchmark.py','Aynı senaryoların CSV / grafik karşılaştırması'],['test_algorithms.py / test_ui.py','Doğruluk ve kullanıcı etkileşimi testleri']], [.075,.16,.85,.54])

f,a=page('Teknik ek • Temel arama fonksiyonları','algorithms.py: geçerli komşular → arama → sonuç',
'neighbors bir üreteçtir; yalnızca grid içinde ve duvar olmayan dört yönlü komşuları verir. search yönteme göre deque veya heap kullanır. parent sözlüğüyle hedeften başlangıca geri giderek yolu kurar ve ters çevirir. Result bir veri sınıfıdır: path yol, expanded işlenen kareler, discovered ise keşfedilen sayıdır. Karşılaştırma discovered yerine len(expanded) kullanır.')
row(a,.70,'neighbors(cell, walls, rows, cols)','algorithms.py','Grid dışını ve duvarları eleyerek geçerli dört komşuyu üretir.','Kullanım: BFS, A* ve D* Lite komşu kareleri bu fonksiyonla gezer.')
row(a,.51,'search(start, goal, walls, ..., method)','algorithms.py','BFS veya A* çalıştırır; parent kayıtlarıyla en kısa yolu yeniden oluşturur.','Çıktı: Result(path, expanded, discovered). Yol yoksa path boş listedir.')
row(a,.32,'manhattan(a, b)','algorithms.py','İki karenin satır ve sütun farklarının mutlak değerlerini toplar.','D* Lite öncelik anahtarında kullanılır; search() içinde aynı sezgi yerel olarak hesaplanır.')

f,a=page('Teknik ek • Hibrit planı yöneten fonksiyonlar','Planlayıcı aynı arama bilgisini çağrılar arasında saklar.',
'plan giriş koordinatlarını ve duvarları denetler. Motor yoksa veya hedef/grid değişirse yeni DStarLite kurulur. Aksi durumda replan çağrılır. reset motoru ve istatistikleri temizler. DStarLite kurucusundaki BFS hedef köklüdür; her erişilebilir hücreye hedefe uzaklığını yazar. Arayüzde yeni bir algoritma başlatmak ajanı başlangıca götürür; dinamik düzenleme bunu yapmaz.')
row(a,.70,'HybridPlanner.plan(...)','algorithms.py','İlk çağrıda ters BFS başlatır; sonraki çağrılarda D* Lite ile yeniden planlar.','Hedef veya grid boyutu değişirse motor yenilenir; diğer güncellemelerde korunur.')
row(a,.51,'HybridPlanner.reset()','algorithms.py','Motoru, plan sayısını ve toplam inceleme istatistiklerini sıfırlar.','Kullanım: yeni arama başlatılırken veya örnek haritaya dönülürken.')
row(a,.32,'DStarLite.__init__(...)','algorithms.py','Hedeften BFS ile mesafe alanını hesaplar; g ve rhs değerlerini eşit başlatır.','Bu mesafe alanı ilk yolun çıkarılmasında ve sonraki artımlı onarımlarda kullanılır.')

f,a=page('Teknik ek • D* Lite yolunu nasıl onarır?','g: tutulan maliyet    rhs: komşular üzerinden hesaplanan aday maliyet',
'replan eski ve yeni duvar kümelerinin simetrik farkını alır. update_vertex hücrenin rhs değerini yeniler; g ile farklıysa öncelik kuyruğuna koyar. repair mevcut başlangıcın en kısa yolunu belirlemek için gerekli işlemleri yapar, bütün hücreleri baştan hesaplamak zorunda değildir. km ajanın yer değiştirmesini anahtar hesabına taşır. path komşuların hedef maliyetlerine göre rotayı çıkarır.')
row(a,.70,'DStarLite.replan(start, walls)','algorithms.py','Değişen duvarları ve komşularını belirler; ajan konumunu ve km değerini günceller.','Sıra: update_vertex() → repair() → path().')
row(a,.55,'DStarLite.update_vertex(u)','algorithms.py','rhs değerini yeniler; g ≠ rhs olan kareyi onarım kuyruğuna ekler.','Duvar için sonsuz maliyet, hedef için sıfır maliyet kullanılır.')
row(a,.40,'DStarLite.repair()','algorithms.py','Öncelik sırasıyla gerekli tutarsız maliyetleri düzeltir.','Mevcut başlangıcın yolu için yeterli koşullar sağlandığında durur.')
row(a,.25,'DStarLite.path()','algorithms.py','Hedefe maliyeti düşük komşuları izleyerek güncel rotayı çıkarır.','Başlangıç erişilemezse boş liste döndürür; döngü oluşmasını denetler.')

f,a=page('Teknik ek • Kullanıcıdan algoritmaya','main.py: bir düğme veya fare olayı planlamayı tetikler.',
'begin seçili algoritmayı çalıştırır, aynı konumdan BFS ve A* karşılaştırmasını hesaplar, animasyonu arama aşamasına döndürür. edit tıklamayı grid koordinatına çevirir; korunan hücreleri engeller. Hibrit aktifken replan=True kullanarak ajanı yerinde bırakır. BFS/A* modunda harita değişikliği eski sonucu temizler; kullanıcı yeniden başlatır. set_tool sol tuşun duvar mı silgi mi olduğunu belirler.')
row(a,.70,'App.begin(mode, replan=False)','main.py','Aramayı çalıştırır, karşılaştırma sonuçlarını hazırlar ve animasyonu başlatır.','replan=True ise ajan konumu ve önceki hibrit motor korunur.')
row(a,.51,'App.edit(event)','main.py','Fare konumunu kareye çevirir; duvar ekler veya siler.','Başlangıç, hedef ve ajan korunur. Hibrit aktifse otomatik yeniden planlanır.')
row(a,.32,'App.set_tool(tool)','main.py','Sol fare düğmesinin duvar çizme veya silgi işlevini seçer.','D: duvar, E: silgi. Sağ tık seçili araçtan bağımsız olarak duvar siler.')

f,a=page('Teknik ek • Animasyonun aşamaları','Arama sonucu hesaplanır, ardından adımlar sırayla gösterilir.',
'Arama hesaplaması animasyon başlamadan önce tamamlanır. tick hesaplanan expanded ve path listelerini zaman içinde gösterir. Arama mor, yol sarı, ajan açık mavi renktedir. pause durumu korur. Yeni duvar eklenince eski animasyonun listeleri yenilenir. Yol yoksa blocked aşamasına geçilir; hibritte geçit açılması yeniden planlamayı tetikler.')
for x,t,b in [(.065,'search','İşlenen kareleri göster\nHız: kare / animasyon adımı\nMor arama alanı'),(.365,'path','Bulunan yolu sırayla çiz\nBaşlangıçtan hedefe\nSarı rota'),(.665,'walk','Ajanı rota üzerinde ilerlet\nHedefte: done\nYol yoksa: blocked')]:card(a,x,.39,.26,.29,t,b)
row(a,.29,'App.tick(_)','main.py','FuncAnimation zamanlayıcısında arama, yol ve hareket aşamalarını ilerletir.','Duraklatılmışsa işlem yapmaz. Son aşamada ajan hedefe ulaşır.')
txt(a,.075,.12,'App.pause(): dur / devam    •    App.reset(): örnek haritaya dön    •    App.clear(): duvarları sil',14,TEAL)

f,a=page('Teknik ek • Ekranı oluşturan fonksiyonlar','ui.py tasarımı, main.py veri ve uygulama durumunu yönetir.',
'build_ui figürü, labirent eksenini, sayaçları, düğmeleri ve karşılaştırma tablosunu kurar. refresh_ui durum metnini ve seçili araç/algoritma vurgusunu günceller. App.refresh tablonun sayısal sonuçlarını ve görüntüyü yeniler. pixels duvarları ziyaret renklerinin üzerine çizerek dinamik engellerin görünür kalmasını sağlar.')
row(a,.70,'build_ui(app, COLORS, ROWS, COLS)','ui.py','Labirenti, kontrol panelini, sayaçları, düğmeleri ve karşılaştırma tablosunu kurar.','App.__init__ içinde bir kez çağrılır; düğmeleri ilgili olay fonksiyonlarına bağlar.')
row(a,.51,'refresh_ui(app)','ui.py','Sayaçları, durum mesajını, seçili aracı ve algoritma satırının vurgusunu günceller.','App.refresh() üzerinden her görsel güncellemede çağrılır.')
row(a,.32,'App.pixels() ve App.refresh()','main.py','Durumu renk matrisine dönüştürür; görüntüyü ve tablodaki sayıları yeniler.','Duvarlar arama renklerinin üstünde kalır; başlangıç, hedef ve ajan ayrıca işaretlenir.')

f,a=page('Doğrulama ve projenin sınırları','Doğru yol, dinamik güncelleme ve kullanıcı etkileşimi ayrı ayrı denetlenir.',
'Mevcut test paketinde 13 test bulunuyor. Rastgele haritalarda BFS ile A* yol uzunlukları karşılaştırılır. Hibritte 40 senaryo ve her birinde 36 plan ile hareket/değişiklik dizileri sınanır. Yolun komşuluk ve duvar kurallarına uyduğu doğrulanır. Arayüz testleri ekran açmadan gerçek Matplotlib olaylarıyla çalışır; bu, Windows ekranında elle kullanım testinin aynısı değildir. Dinamik optimalite o anki harita ve konum içindir.')
card(a,.065,.36,.40,.33,'13 otomatik test','Rastgele haritalarda yol doğruluğu\nEngel ekleme, silme ve geçit açma\nFare, silgi, duraklatma, sayaçlar\nDuvarların görünür kalması')
card(a,.525,.36,.40,.33,'Ne iddia ediyoruz?','Anlık haritada en kısa yol\nÖnceki bilgiyle yeniden planlama\nHer senaryoda daha hızlı değil\nKare sayısı, süre ölçümü değil')
txt(a,.075,.25,'Çalıştırma: python -m unittest discover -v',19,BLUE,'bold')
txt(a,.075,.15,'Karşılaştırma: python benchmark.py → docs/results.csv ve docs/comparison.png',17,MUTED)

f,a=page('Canlı demo • 2–3 dakikalık akış','Önce sabit harita, ardından dinamik engel değişimi',
'Proje klasöründe py main.py çalıştır. Önce BFS ve A* ile tablodaki eşit yol uzunluğunu ve farklı kare sayılarını göster. Hibriti başlat; arama animasyonu bitince mavi ajan ilerlerken önündeki sarı kareye duvar çiz. Ajanın yerinde kaldığını ve D* Lite ile rotanın yenilendiğini göster. Bir geçidi kapatıp tekrar açarak yol yok durumunu anlat. Sunumu “BFS ilk bilgiyi kurar, D* Lite değişeni onarır, A* karşılaştırma sağlar” cümlesiyle tamamla.')
steps=[('1  Aç','Proje klasöründe: py main.py'),('2  Karşılaştır','BFS ve A* çalıştır; aynı yol uzunluğu, farklı kare sayılarını göster.'),('3  Değiştir','Hibriti başlat; ajan ilerlerken önüne duvar çiz.'),('4  Yeniden yol bul','D* Lite güncellemesini izle; silgiyle geçidi tekrar aç.')]
for y,(title,body) in zip([.69,.55,.41,.27],steps):
    txt(a,.075,y,title,21,BLUE,'bold');txt(a,.075,y-.055,body,18)
txt(a,.075,.13,'BFS ilk bilgiyi kurar. D* Lite değişeni onarır. A* karşılaştırma sağlar.',20,TEAL,'bold')

assert len(figs)==16
OUT.mkdir(exist_ok=True)
with PdfPages(PDF) as pdf:
    pdf.infodict().update(Title='Labirentte Yol Bulan Ajan — Proje ve Fonksiyonlar', Subject='BFS, A*, D* Lite, arayüz ve animasyon')
    for i,f in enumerate(figs,1):
        pdf.savefig(f);f.savefig(OUT/f'slide_{i:02d}.png',dpi=80);plt.close(f)
canvas=Image.new('RGB',(1280,360*8),'#dce2ea')
for i in range(16):
    with Image.open(OUT/f'slide_{i+1:02d}.png') as im:
        im=im.convert('RGB');im.thumbnail((640,360));canvas.paste(im,((i%2)*640,(i//2)*360))
canvas.save(OUT/'preview.jpg')
(OUT/'KONUSMACI_NOTLARI.md').write_text('# Labirent Ajanı — Konuşmacı Notları\n\n16 slayt: ilk 8 slayt proje anlatımı, 9–14 teknik ek, 15 testler, 16 canlı demo.\n\n'+'\n'.join(notes),encoding='utf-8')
print(f'{PDF}\n16 sayfa • {PDF.stat().st_size:,} bayt')
