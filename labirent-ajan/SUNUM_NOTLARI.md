# Proje 3 — Kısa sunum akışı

## 2–3 dakikalık demo

1. `python main.py` ile aç. Gridin 20×50 ve 9 duvar şeritli olduğunu göster.
2. BFS çalıştır: mor arama alanını, sarı yolu ve hareket eden ajanı göster. 155 adım ve 802 kareyi belirt.
3. A* çalıştır: yine 155 adım, 747 kare. Daha az kare her zaman daha kısa yol demek değildir; ikisi de optimaldir.
4. Hibrit başlat. Ajan hareket ederken önündeki sarı kareye duvar ekle. Ajanın yerinde kaldığını, D* Lite durum satırını ve yeni rotayı göster.
5. Geçidi kapat; yol yok durumunu göster. Sağ tıklamayla geçidi aç ve yeniden planlamayı göster.
6. `docs/comparison.png` ve `docs/results.csv` ile sabit senaryodaki sonuçları açıkla.
7. `python -m unittest -v` ile testleri çalıştır.

## Anlaşılması gereken noktalar

- **Neden BFS?** Dört yönlü, eşit maliyetli gridde en kısa yolu garanti eder; hedef köklü tam BFS mesafe alanını da verir.
- **Hibrit nerede?** BFS'nin hesapladığı uzaklıklar doğrudan D* Lite g/rhs tablolarını başlatır. Harita değişince bu tablolar silinmez.
- **D* Lite dinamik olarak ne yapıyor?** Değişen kenarların etkilediği tutarsızlıkları öncelik kuyruğunda onarır. Ajanın ilerlemesi km anahtar düzeltmesiyle hesaba katılır.
- **A* ile farkı?** Bu uygulamadaki A* her çağrıda sıfırdan arar. D* Lite önceki aramanın durumunu taşır.
- **Neden ilk hibrit plan 838, BFS 802?** Hibrit gelecekteki onarımlar için tam alan hesaplar; tekil BFS hedefe ulaştığında durur. Başlangıç maliyeti sonuçlarda gösterilmiştir.
- **Hibritte 0 kare nasıl mümkün?** Önceki mesafe alanı hâlâ geçerlidir; kuyruktan köşe işlenmeden yol çıkarılır. Bu, sıfır CPU zamanı demek değildir.
- **Her durumda daha iyi mi?** Hayır. Geçidin tamamen kapanması örneğinde 429 kare onarır; BFS 428 kare işler. Avantaj değişikliğin yerine ve büyüklüğüne bağlıdır.
- **Optimalite neyi kapsıyor?** Her harita anındaki mevcut konumdan hedefe en kısa yol. Gelecekteki değişikliklerin tamamı için toplam seyahat optimumu iddia edilmez.
- **Veri nereden?** Projeye ait sentetik `data/maze.json`; üretim kodu `generate_maze.py`. Harici veri gerekmiyor.

## Teslimden önce

- Ayrı GitHub reposunun bağlantısını teslim formuna ekle.
- README'deki ekran görüntüleri ve veri bağlantısını aç.
- Actions testlerini kontrol et.
- Yerel bilgisayarda pencereyi açıp tıklama/sürüklemeyi dene.
- BFS, A*, g/rhs, km ve ölçüm tanımlarını kendi cümlelerinle açıklayabilecek kadar kodu incele.
