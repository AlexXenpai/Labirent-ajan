# Labirent Ajanı — Konuşmacı Notları

16 slayt: ilk 8 slayt proje anlatımı, 9–14 teknik ek, 15 testler, 16 canlı demo.

## 1. Labirentte yol bulan ajan

Bu projede amaç yalnızca yolu çizmek değil, harita değiştiğinde ajanın mevcut konumundan yeni en kısa yolu bulmaktır. BFS başlangıç bilgisini oluşturur; D* Lite bu bilgiyi sonraki değişikliklerde kullanır. A* karşılaştırma yöntemidir.

## 2. Projenin amacı ve kuralları

Her hareket bir adım maliyetindedir; çapraz hareket yoktur. Örnek haritada 9 geçitli duvar sütunu ve 162 duvar karesi vardır. Minimum 8 engel şartı örnek haritayla sağlanır; kullanıcı deney yapmak için duvarları silebilir. Başlangıç, hedef ve ajanın bulunduğu kare duvar yapılamaz.

## 3. Uygulamanın yeni arayüzü

Sağda algoritma düğmeleri, duraklatma, hız ve çizim araçları var. B başlangıcı, H hedefi gösterir. Üstteki incelenen sayaç animasyonda gösterilen kareleri sayar; alt tablo tamamlanmış aramanın toplamıdır. Ekran görüntüsü güncel uygulamanın örnek haritadaki sonucudur.

## 4. BFS ve A* nasıl çalışıyor?

BFS başlangıca uzaklığına göre katman katman ilerler. A* gidilen yol maliyetine hedefe tahmini uzaklığı ekler. Manhattan uzaklığı dört yönlü birim maliyetli grid için uygundur. Bu kodda A* eşit toplam maliyette hedefe daha yakın kareyi önce seçer. Daha az kare incelemek daha kısa yol bulmak anlamına gelmez.

## 5. Hibrit yöntemde iki algoritma birleşiyor

Hibrit ilk çağrıda hedeften ters BFS yaparak erişilebilen bütün karelerin hedefe uzaklığını hesaplar. Bu değerler g ve rhs tablolarına aktarılır. Sonraki değişikliklerde aynı DStarLite nesnesi tutulur. replan değişen duvarları bulur ve repair gerekli tutarsızlıkları onarır. Yeni hedef veya grid boyutu yeni başlangıç gerektirir.

## 6. İlk haritada ölçülen sonuçlar

Bu sayılar benchmark.py yeniden çalıştırılarak doğrulandı. Üç yöntemin yolu 155 adımdır. A* BFS’den 55 kare daha az işler. Hibrit ilk planda tam ters mesafe alanını hesapladığı için daha çok kare işler; avantajını dinamik güncellemelerde arıyoruz. İncelenen kare sayısı işlem süresi ölçümü değildir.

## 7. Harita değiştiğinde ne oluyor?

İlk planın ardından ajan 3 adım ilerletilir. Sonra yoluna bir duvar eklenir, silinir, bir geçit tamamen kapanır ve tekrar açılır. Bu sabit deneyde engel ekleme 6, silme 5 kare onarımı gerektirir. Sıfır kare, önceki alanın yeterli olduğunu belirtir; sıfır süre demek değildir. Geçit kapanırken hibrit 429, BFS 428 kare işler; hibrit her durumda daha az çalışmaz.

## 8. Projenin dosya yapısı

algorithms.py grafik arayüzden bağımsızdır. main.py uygulama durumunu ve olayları yönetir. ui.py tasarımı oluşturur ve sayaçları günceller. Harita JSON dosyasından yüklenir. benchmark.py karşılaştırma çıktıları üretir. Testler algoritma ve arayüz seviyesinde ayrılmıştır.

## 9. Teknik ek • Temel arama fonksiyonları

neighbors bir üreteçtir; yalnızca grid içinde ve duvar olmayan dört yönlü komşuları verir. search yönteme göre deque veya heap kullanır. parent sözlüğüyle hedeften başlangıca geri giderek yolu kurar ve ters çevirir. Result bir veri sınıfıdır: path yol, expanded işlenen kareler, discovered ise keşfedilen sayıdır. Karşılaştırma discovered yerine len(expanded) kullanır.

## 10. Teknik ek • Hibrit planı yöneten fonksiyonlar

plan giriş koordinatlarını ve duvarları denetler. Motor yoksa veya hedef/grid değişirse yeni DStarLite kurulur. Aksi durumda replan çağrılır. reset motoru ve istatistikleri temizler. DStarLite kurucusundaki BFS hedef köklüdür; her erişilebilir hücreye hedefe uzaklığını yazar. Arayüzde yeni bir algoritma başlatmak ajanı başlangıca götürür; dinamik düzenleme bunu yapmaz.

## 11. Teknik ek • D* Lite yolunu nasıl onarır?

replan eski ve yeni duvar kümelerinin simetrik farkını alır. update_vertex hücrenin rhs değerini yeniler; g ile farklıysa öncelik kuyruğuna koyar. repair mevcut başlangıcın en kısa yolunu belirlemek için gerekli işlemleri yapar, bütün hücreleri baştan hesaplamak zorunda değildir. km ajanın yer değiştirmesini anahtar hesabına taşır. path komşuların hedef maliyetlerine göre rotayı çıkarır.

## 12. Teknik ek • Kullanıcıdan algoritmaya

begin seçili algoritmayı çalıştırır, aynı konumdan BFS ve A* karşılaştırmasını hesaplar, animasyonu arama aşamasına döndürür. edit tıklamayı grid koordinatına çevirir; korunan hücreleri engeller. Hibrit aktifken replan=True kullanarak ajanı yerinde bırakır. BFS/A* modunda harita değişikliği eski sonucu temizler; kullanıcı yeniden başlatır. set_tool sol tuşun duvar mı silgi mi olduğunu belirler.

## 13. Teknik ek • Animasyonun aşamaları

Arama hesaplaması animasyon başlamadan önce tamamlanır. tick hesaplanan expanded ve path listelerini zaman içinde gösterir. Arama mor, yol sarı, ajan açık mavi renktedir. pause durumu korur. Yeni duvar eklenince eski animasyonun listeleri yenilenir. Yol yoksa blocked aşamasına geçilir; hibritte geçit açılması yeniden planlamayı tetikler.

## 14. Teknik ek • Ekranı oluşturan fonksiyonlar

build_ui figürü, labirent eksenini, sayaçları, düğmeleri ve karşılaştırma tablosunu kurar. refresh_ui durum metnini ve seçili araç/algoritma vurgusunu günceller. App.refresh tablonun sayısal sonuçlarını ve görüntüyü yeniler. pixels duvarları ziyaret renklerinin üzerine çizerek dinamik engellerin görünür kalmasını sağlar.

## 15. Doğrulama ve projenin sınırları

Mevcut test paketinde 13 test bulunuyor. Rastgele haritalarda BFS ile A* yol uzunlukları karşılaştırılır. Hibritte 40 senaryo ve her birinde 36 plan ile hareket/değişiklik dizileri sınanır. Yolun komşuluk ve duvar kurallarına uyduğu doğrulanır. Arayüz testleri ekran açmadan gerçek Matplotlib olaylarıyla çalışır; bu, Windows ekranında elle kullanım testinin aynısı değildir. Dinamik optimalite o anki harita ve konum içindir.

## 16. Canlı demo • 2–3 dakikalık akış

Proje klasöründe py main.py çalıştır. Önce BFS ve A* ile tablodaki eşit yol uzunluğunu ve farklı kare sayılarını göster. Hibriti başlat; arama animasyonu bitince mavi ajan ilerlerken önündeki sarı kareye duvar çiz. Ajanın yerinde kaldığını ve D* Lite ile rotanın yenilendiğini göster. Bir geçidi kapatıp tekrar açarak yol yok durumunu anlat. Sunumu “BFS ilk bilgiyi kurar, D* Lite değişeni onarır, A* karşılaştırma sağlar” cümlesiyle tamamla.
