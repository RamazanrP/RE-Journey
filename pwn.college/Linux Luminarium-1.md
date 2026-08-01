# 🐧 pwn.college - Günlük Z Raporu (Öğrendiklerim & Takıldıklarım)

Bu rapor, pwn.college üzerinde "White Belt" (Beyaz Kuşak) seviyesini tamamlarken edindiğim bilgileri, kullandığım araçları ve yaşadığım zorlukları içeriyor. Amacım, doğrudan flag çözümlerini değil, öğrenme sürecimi ve kullandığım teknikleri not almak. Çünkü çözüm yazmak yasak :)

---

## 1. File Globbing 

Terminalde dosyalarla çalışırken tek tek isim yazmak yerine **joker karakterler** kullanmayı öğrendim. Bu, özellikle `/challenge/files` gibi dizinlerde hedef dosyaları bulmak için çok işime yaradı.

-   **`*` (Yıldız) :** Herhangi bir karakter dizisiyle eşleşir (hiçbir karakter de olabilir).
    -   Örnek: `*p*` → Dosya adında 'p' harfi geçen **tüm** dosyaları bulur.
-   **`?` (Soru İşareti) :** Tam olarak **tek bir** karakterle eşleşir.
    -   Örnek: `/c?allenge` → `/challenge` dizinine giderken 'c' yerine '?' koyarak 'h' ile eşleşmesini sağladım (karakter sayısı sınırlamasını aşmak için).
-   **`[]` (Köşeli Parantez) :** İçindeki karakterlerden **herhangi biriyle** (veya aralıkla) eşleşir.
    -   Örnek: `file_[bash]` → `file_b`, `file_a`, `file_s`, `file_h` dosyalarını tek seferde yakalar.
-   **`[^]` veya `[!]` (Olumsuzlama) :** Belirtilen karakterler dışındakilerle eşleşir.
    -   Örnek: `[^pwn]*` → Dosya adı 'p', 'w' veya 'n' ile başlamıyorsa eşleşir.

> **Çıkarım:** `ls` yapmadan dosyaları filtreleyebilmek, ileride yazacağım exploit'lerde bana çok zaman kazandıracak.

---

## 2. Yardım Sistemleri: `man` ve `help`

Komutların ne işe yaradığını ve hangi gizli parametreleri aldığını öğrenmek için yardım sayfalarına bakmayı öğrendim.

-   **`man` (Manual) :** Programlar için kapsamlı kılavuz sayfalarını açar.
    -   Örnek: `man challenge` ile `/challenge/challenge` programının gizli `--xxxxx` seçeneğini buldum.
    -   **Arama:** `/flag` yazıp `n` tuşuyla sonraki eşleşmelere giderek metin içinde arama yaptım.
-   **`man -k` (Apropos) :** Kılavuz adını bilmediğimde veritabanında arama yapar.
    -   Örnek: `man -k challenge` → Rastgele isimlendirilmiş man sayfasını (`xyz123` gibi) bularak gizli argümanı okudum.
-   **`help` :** Shell'in içine gömülü (builtin) komutlar için kullanılır (cd, echo vb.).
    -   Örnek: `help challenge` ile builtin olan challenge komutunun nasıl kullanılacağını öğrendim.

---

## 3. Practicing Piping (Çıktı ve Hata Yönetimi)

Linux'ta her şey bir dosyadır. Ekran çıktısını (stdout) ve hata mesajlarını (stderr) yönlendirmeyi öğrendim. Dosya tanımlayıcıları: **1** (stdout) ve **2** (stderr).

-   **`>` (Truncate) :** Standart çıktıyı (FD 1) bir dosyaya yazar, dosya varsa **sıfırlanır**.
    -   Örnek: `/challenge/run > myflag` → Flag'i `myflag` dosyasına kaydettim.
-   **`>>` (Append) :** Standart çıktıyı dosyanın **sonuna ekler** (üzerine yazmaz).
    -   Örnek: Flag'in iki yarısını birleştirmek için kullandım.
-   **`2>` :** Standart hata mesajlarını (FD 2) dosyaya yönlendirir.
    -   Örnek: `/challenge/run > myflag 2> instructions` → Çıktıyı ve hataları ayrı dosyalara ayırdım.
-   **`2>&1` :** Hata akışını (stderr), çıktı akışına (stdout) yönlendirir. Böylece `|` (pipe) ile aktarılabilir hale gelir.
    -   Örnek: `/challenge/run 2>&1 | grep pwn` → Hataların içinde gizlenen flag'i grep ile yakaladım.
-   **`&>` :** Hem stdout hem de stderr'i aynı dosyaya yönlendirir (kısaltma).

---

## 4. Pipeline (Boru Hattı) ve Filtreleme

Bir komutun çıktısını diğerine aktarmak için `|` (pipe) kullandım. Bu, veri akışını düzenlemenin temelidir.

-   **`|` (Pipe) :** Soldaki komutun **stdout** çıktısını, sağdaki komutun **stdin**'ine bağlar.
-   **`grep` :** Belirtilen kalıbı içeren satırları filtreler.
    -   Örnek: `/challenge/run | grep pwn.college` → 100.000 satır içinden sadece flag'i buldum.
-   **`grep -v` :** Belirtilen kalıbı **içermeyen** satırları gösterir (Invert match).
    -   Örnek: `/challenge/run | grep -v DECOY` → İçinde "DECOY" yazan sahte flag'leri eleyip gerçek flag'i aldım.
-   **`sed` (Stream Editor) :** Metin akışı üzerinde değiştirme işlemi yapar.
    -   Örnek: `/challenge/run | sed 's/FAKEFLAG//g'` → Flag'in arasına sıkıştırılmış `FAKEFLAG` ibaresini sildim (hiçbir şeyle değiştirdim).

---

## 5. Veriyi Çoğaltma ve Karşılaştırma

Bazen boru hattında aradaki veriyi görmek veya iki çıktıyı karşılaştırmak gerekir.

-   **`tee` (T borusu) :** Gelen veriyi **hem dosyaya yazar**, **hem de standart çıktıya (stdout) iletir**. Böylece veriyi bölerek hem gözlemleyip hem sonraki komuta gönderebilirim.
    -   Örnek: `/challenge/pwn | tee pwn_output | /challenge/college` → `pwn`'ün ne istediğini `pwn_output` dosyasına bakarak öğrendim.
    -   İleri seviye: `tee >(/challenge/the) >(/challenge/planet)` ile aynı veriyi iki farklı programa aynı anda gönderdim.
-   **`diff` :** İki dosya veya akış arasındaki **farklılıkları** gösterir.
    -   Örnek: `diff <(/challenge/print_decoys) <(/challenge/print_decoys_and_flag)` → Sahte flag'ler arasına karışmış tek bir farklı satırı (gerçek flag) bularak hedefe ulaştım.

> **Process Substitution (`<()` ve `>()`) :** Bir komutun çıktısını sanki bir dosyaymış gibi başka bir komuta parametre olarak vermemi sağladı. Bu, `diff` ve `tee` ile çok güçlü bir kombinasyon oluşturuyor.

---

## 6. FIFO (Named Pipes - Kalıcı Boru)

Geçici boruların (pipe) ötesine geçerek, dosya sistemi üzerinde kalıcı olan **FIFO** dosyaları oluşturmayı öğrendim.

-   **`mkfifo` :** Kalıcı bir isimli boru oluşturur.
    -   Örnek: `mkfifo /tmp/flag_fifo`
-   **Bloklama (Blocking) Mantığı :** FIFO'ya yazmak için, aynı anda bir okuyucunun (reader) da bağlanması gerekir. Yoksa yazma işlemi sonsuza kadar bekler (bloklanır).
    -   Çözüm: `cat /tmp/flag_fifo &` (okuyucuyu arka planda çalıştırdım) ve ardından `/challenge/run > /tmp/flag_fifo` yazarak veriyi ilettim.

---

## 7. Diğer Araçlar

-   **`&` (Arka Plan) :** Uzun süren veya bloklanan işlemleri arka planda (`&`) çalıştırarak terminali kilitlemekten kurtuldum.
-   **`-` ve `--` (Argümanlar) :** Programlara parametre göndermek için kullanılır. `--help` ile yardım menüsünü, `--version` ile sürüm bilgisini, `-p` (`--print-value`) ile gizli değerleri öğrendim.
-   **Tab Completion (Sekme Tamamlama) :** Uzun dosya veya komut isimlerini yazarken `Tab` tuşuna basarak otomatik tamamlattım. `/challenge/pwn` yazıp `Tab`'a basarak `/challenge/pwncollege`'e ulaştım. İki kez `Tab` basarak olası tüm seçenekleri listeledim.

---

## 8. Takıldığım ve Zorlandığım Noktalar

1.  **Desktop'ta Kopyala-Yapıştır:** pwn.college'un Desktop ortamında doğrudan `Ctrl+V` çalışmıyor. Sol kenardaki ok tıklanıp "Clipboard" menüsü açılarak, dışarıdan kopyalanan metnin bu pencere içine `Ctrl+V` yapılıp ardından terminale sağ tıklanıp "Paste" yapılması gerektiğini anlamak zaman aldı.
2.  **Privileged (Sudo) Modu:** İlk başta `sudo cat /challenge/secret` yapmam gerektiğini unutup sadece `cat` yazdım ve "Permission Denied" hatası aldım. Root yetkisiyle okumam gerektiğini fark etmek biraz vakit kaybettirdi.
3.  **FIFO Bloklaması:** FIFO oluşturduğumda komutun donması çok şaşırtıcıydı. Okuyucu olmadan yazılamayacağını (bloklama) öğrenene kadar iki terminal arasında gidip geldim.

#  Shell Variables Odası

Bugün, veri akışlarını yönlendirmenin ötesine geçerek **Shell Değişkenleri** ve **Standart Girdi (stdin) Okuma** konularını derinlemesine işledim. Bu odada, program çıktılarını değişkenlere atmayı ve dosyaları doğrudan shell içinde okumayı öğrendim.

---

## 1. Değişken Yazdırma ve Atama

Shell'de her şey bir değişkende saklanabilir. En temel işlemler:

-   **Yazdırma:** Değişkenin başına `$` ekleyerek `echo` ile basarım.
    -   Örnek: `echo $XXXX` → XXXX değişkeninin içeriğini gösterir.
-   **Atama:** Boşluk olmadan `İSİM=DEĞER` şeklinde atama yapılır.
    -   Örnek: `XXX=COLLEGE`
-   **Değerde Boşluk (Quoting):** Eğer değer boşluk içeriyorsa, mutlaka tırnak içine alınmalıdır.
    -   Örnek: `PWN="COLLEGE XXXX"` (Yoksa shell `XXXX`'ı komut sanar).

---

## 2. Exporting (Ortam Değişkenleri)

Varsayılan olarak atanan değişkenler sadece mevcut shell'de bulunur. `/challenge/run` gibi alt süreçler bu değişkenleri görmez.

-   **Export (Dışa Aktarma):** Değişkeni alt süreçlere taşımak için `export` kullanılır.
    -   Örnek: `export XXX=COLLEGE` → `/challenge/run` artık `XXX` değişkenini görebilir.
-   **Görmek için:** Tüm export edilmiş değişkenleri `env` komutu ile listeleyebilirim.
    -   Örnek: `env | grep XXXX` → Ortamda gizlenmiş flag'i bulur.

---

## 3. Command Substitution

Bir komutun çıktısını doğrudan değişkene atamak için `$(komut)` yapısını kullandım.

-   **Klasik Yöntem:** `PWN=$(cat /xxxx)` → `cat` ile dosyayı okuyup değişkene atar.
-   **Not:** Eski yöntem olan `` `komut` `` (backtick) yerine `$(komut)` kullanmak çok daha güvenli ve iç içe (nested) kullanıma uygundur.
    -   Örnek: `$(find / -name xxxx)` içinde kullanmak çok daha kolaydır.

---

## 4. Read ile Kullanıcı Girdisi Okuma

`read` komutu, standart girdiden (genelde klavye) bir satır okur ve belirtilen değişkene atar.

-   **Kullanımı:** Terminalde `read XXX` yazarım, shell beni bekler. `COLLEGE` yazıp Enter'a basarım. Artık `XXX` değişkeni `COLLEGE` değerini taşır.

---

## 5. Read ile Dosya Okuma 

Önceki seviyelerde sıkça `VAR=$(cat dosya)` yapıyorduk. Ancak bu, gereksiz yere ekstra bir `cat` programı çalıştırmaktır. Shell bunu çok daha verimli yapabilir. Bunu gördüm.

-   **Verimli Yöntem:** `read` komutunun standart girdisini (`stdin`) dosyaya yönlendiririm.
    -   Örnek: `read XXX < /challenge/read_me`
    -   Bu komut, `cat` çalıştırmadan dosyayı doğrudan shell'in iç fonksiyonlarıyla okur ve `XXX` değişkenine atar. Bu, hem daha hızlı hem de "Useless Use of Cat" (UUOC) hatasından kaçınmanın doğru yoludur.

---

## Özet ve Kazanımlar

-   `export` ve `env` ile değişken kapsamını (scope) anladım.
-   Tırnak işaretlerinin (`" "`) boşluklu değerler için hayati önem taşıdığını pekiştirdim.
-   `$(...)` ile çalıştırma ikamesini ve `read` ile dosya okuma arasındaki farkı netleştirdim.
-   Bir program çalıştırmak yerine shell'in yerleşik (builtin) özelliklerini kullanmanın sistem kaynakları açısından daha verimli olduğunu öğrendim.
