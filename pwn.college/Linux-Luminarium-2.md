# 🐧 pwn.college Günlük Z Raporu: Data Manipulation & Process and Jobs

Bu raporda, **(Data Manipulation** ve **Process and Jobs** odalarında öğrendiğim tüm kritik komutları, karşılaştığım zorlukları ve çözüm yöntemlerini derledim.

---

## Modül 1: Data Manipulation

Bu modülde amaç, komut çıktılarındaki (stdout) ham veriyi istenilen formata sokmak, gereksiz karakterleri temizlemek ve sadece flag'i yakalamaktı. İşte öğrenip kullandığım üç silah:

### 1. `tr` (Translate / Delete) - Karakter Dönüştürücü ve Silici
`tr`, metin akışındaki karakterleri birebir eşleştirerek değiştirir veya tamamen siler. 

- **Büyük/Küçük Harf Ters Çevirme (Case Swapping):**
  `/challenge/run` flag'i basarken harflerin case'ini ters çeviriyordu (`A`->`a`, `a`->`A`). Bunu düzeltmek için:
  ```bash
  /challenge/run | tr 'X-Xx-x' 'x-xX-X'
  ```
  => *Mantık:* Soldaki setteki her karakteri, sağdaki setteki birebir aynı sıradaki karakterle değiştir.

- **Karakter Silme (Delete):**
  Bazı zorluklarda flag'in arasına saçma sapan `^` ve `%` işaretleri serpiştirilmişti. Bunlardan kurtulmak için:
  ```bash
  /challenge/run | tr -d 'XX'
  ```

### 2. `head` - Dosyanın Başından Okuma
Devasa çıktılar içinde sadece ilk birkaç satıra ihtiyacımız olduğunda kurtarıcımız oldu.

- **İlk 7 Satırı Almak:**
  ```bash
  /challenge/pwn | xxxx -x 7 | /blah/blah
  ```
=> *Mantık:* `head -n 7` komutu, gelen verinin sadece ilk 7 satırını kesip alır ve boru hattının (`|`) devamına gönderir.

### 3. `cut` - Sütun/Alan Kesme
Veriler belirli bir ayraçla (delimiter) ayrılmış sütunlar halinde geliyorsa, sadece istediğimiz sütunu almak için `cut` kullandım.

- **2. Alanı Almak (Boşluk ayraçlı):**
  `/challenge/run` çıktısı `Sayı Flag` şeklindeydi. Sadece flag karakterlerini almak için:
  ```bash
  /challenge/run | cut -d ' ' -x x | tr -d 'xx'
  ```
  => *Mantık:* `-d ' '` boşluğu ayraç sayar, `-x x` ikinci alanı alır. Sonundaki `tr -d 'xx'` ise tüm satır sonlarını silerek karakterleri yan yana birleştirir.

---

## Modül 2: Process and Jobs

Bu modül terminalin ötesine geçerek, işletim sisteminde çalışan süreçleri (process) nasıl göreceğimizi, durduracağımızı, öldüreceğimizi ve arka planda nasıl yöneteceğimizi öğretti.

### 1. Süreçleri Listeleme ve Bulma (`ps`)
Çalışan süreçleri görmek ve gizli dosya isimlerini bulmak için kullandım.

- **Tam Komut Satırlarını Görme:**
  Varsayılan `ps` çıktıyı kısaltır. Bunu engellemek için `ww` ekleriz.
  ```bash
  ps -xxxx | grep /challenge
  ```
  => *Mantık:* `/challenge` dizininde çalışan, ismi rastgele değiştirilmiş dosyayı bu komutla bulup çalıştırdık.

### 2. Süreçleri Sonlandırma (`kill`, `pkill`, `Ctrl+C`)
Bir süreci durdurmanın (terminate) birkaç yolu vardır.

- **PID ile Öldürme (`kill`):**
  `ps`'den bulduğumuz PID'i (Process ID) kullanarak süreci sonlandırırız.
  ```bash
  kill -9 1234
  ```
- **İsme Göre Öldürme (`pkill`):**
  `decoy` adında bir süreç varsa hepsini toplu öldürmek için:
  ```bash
  pkill -f xxxxx
  ```
  => *Takıldığım Nokta:* Eğer birden fazla decoy süreci varsa, `pkill` bazen hepsini yakalamayabiliyor. O yüzden `ps -xxxx | grep xxxxx` ile manuel PID'leri bulup `kill -9 PID1 PID2 PID3` yapmak daha garanti.

- **Ön Plandaki Süreci Kesme (`Ctrl+C`):**
  Terminali kilitleyen bir programı durdurmanın en hızlı yolu.

### 3. Süreçleri Askıya Alma ve Devam Ettirme (`Ctrl+Z`, `fg`, `bg`)
Bir süreci tamamen öldürmeden durdurup arkaya almak veya tekrar öne getirmek.

- **Askıya Alma (Suspend):** `Ctrl + Z`
- **Ön Plana Alma (Foreground):** `fg`
- **Arka Plana Alma (Background):** `bg`
  ```bash
  /challenge/run
  Ctrl+Z       # Süreç durdu
  bg           # Süreç arka planda çalışmaya devam etti (flag verdi ama çıktı karıştı)
  fg           # Süreci tekrar ön plana aldım
  ```

### 4. Doğrudan Arka Planda Başlatma (`&`)
Bir süreci önce çalıştırıp sonra `Ctrl+Z`+`bg` yapmak yerine, komutun sonuna `&` ekleyerek doğrudan arka planda başlatabiliriz.

```bash
/challenge/run x
```

### 5. Exit Codes ( $? )
Her komut bittiğinde başarılıysa `0`, başarısızsa `0` dışı bir sayı (genelde `1`) döndürür. En son çalışan komutun çıkış kodunu `$?` ile okuruz.

```bash
/challenge/xxx-code   # 246 çıkış koduyla kapandı diyelim
/challenge/xxxxxx-code xx   # Buraya 246 argüman olarak gitti ve flag'i verdi
```

---

## Püf Noktaları ve Takıldığım Yerler

1.  **FIFO (Named Pipe) Bloklaması:** Süreç odasında FIFO'ya yazmaya çalışırken program dondu. Bunun sebebi, FIFO'yu okuyan bir sürecin (`cat`) olmamasıydı. `cat /tmp/flag_fifo &` ile okuyucuyu arka plana alarak bu blokajı aştım.
2.  **`pkill`'in Yetersizliği:** Tüm decoy'ları öldürmek için `pkill -f decoy` yetmedi. `ps auxww | grep decoy` yapıp kalan PID'leri manuel `kill -9` ile temizlemek zorunda kaldım. 
3.  **Arka Plan Çıktı Karmaşası:** `bg` veya `&` ile çalışan programların çıktıları shell prompt'una karışabiliyor. Birkaç kez `Enter` basmak veya terminali yukarı kaydırmak çözüm oldu.
