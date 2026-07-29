# 🐧 pwn.college Günlük Z Raporu: Data Manipulation & Process and Jobs

Bu raporda, **(Data Manipulation** ve **Process and Jobs** odalarında öğrendiğim tüm kritik komutları, karşılaştığım zorlukları ve çözüm yöntemlerini derledim.


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
=> Mantık: `head -n 7` komutu, gelen verinin sadece ilk 7 satırını kesip alır ve boru hattının (`|`) devamına gönderir.

### 3. `cut` - Sütun/Alan Kesme
Veriler belirli bir ayraçla (delimiter) ayrılmış sütunlar halinde geliyorsa, sadece istediğimiz sütunu almak için `cut` kullandım.

- **2. Alanı Almak (Boşluk ayraçlı):**
  `/challenge/run` çıktısı `Sayı Flag` şeklindeydi. Sadece flag karakterlerini almak için:
  ```bash
  /challenge/run | cut -d ' ' -x x | tr -d 'xx'
  ```
  => Mantık: `-d ' '` boşluğu ayraç sayar, `-x x` ikinci alanı alır. Sonundaki `tr -d 'xx'` ise tüm satır sonlarını silerek karakterleri yan yana birleştirir.

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
  => Mantık: `/challenge` dizininde çalışan, ismi rastgele değiştirilmiş dosyayı bu komutla bulup çalıştırdık.

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
  => Takıldığım Nokta: Eğer birden fazla decoy süreci varsa, `pkill` bazen hepsini yakalamayabiliyor. O yüzden `ps -xxxx | grep xxxxx` ile manuel PID'leri bulup `kill -9 PID1 PID2 PID3` yapmak daha garanti.

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

## Modül 3:# Perceiving Permissions

Bu modül, Linux'ta dosya sahipliği, grup üyeliği ve erişim izinlerini anlamak ve manipüle etmek üzerine kuruluydu.

---

## 1. Sahipliği Değiştirmek: `chown` ve `chgrp`

- **`chown` (Change Owner):** Bir dosyanın sahibini (user) değiştirir.
  - Kullanım: `chown [yeni_sahip] [dosya]`
  - Normalde root yetkisi gerektirir, ancak bu odada özel izinle `hacker` olarak kullanabildim.
- **`chgrp` (Change Group):** Bir dosyanın grup sahipliğini değiştirir.
  - Kullanım: `chgrp [yeni_grup] [dosya]`
  - `/flag` dosyasının grubunu `hacker` yapıp okudum.

---

## 2. İzinleri Değiştirmek: `chmod` Temelleri

Dosya izinleri üç kategoriye ayrılır: **user (sahip)**, **group (grup)**, **other (diğer kullanıcılar)**.
Her kategori için üç temel hak: **r** (read/okuma), **w** (write/yazma), **x** (execute/çalıştırma).

- **`r`** : Dosyayı okuma (veya dizini listeleme)
- **`w`** : Dosyayı değiştirme (veya dizinde dosya oluşturma/silme)
- **`x`** : Dosyayı program olarak çalıştırma (veya dizine `cd` ile girme)

### İzinleri Ekleme/Çıkarma (`+` / `-`)

- `chmod u+r dosya` → Sahibine okuma izni ekler.
- `chmod g-wx dosya` → Gruptan yazma ve çalıştırma izinlerini kaldırır.
- `chmod o+x dosya` → Diğer kullanıcılara çalıştırma izni ekler.
- `chmod a-rwx dosya` → Herkesten tüm izinleri kaldırır.

**Örnek (8 Turlu Pratik):**
Her turda `/challenge/run` belirli bir izin değişikliği istedi. Örneğin:
- `chmod o+w /challenge/pwn` (world'e yazma izni ekle)
- `chmod g+rx,o+x /challenge/pwn` (gruba rx, world'e x ekle)
- `chmod u-rx,o-rx /challenge/pwn` (sahibinden ve dünyadan rx kaldır)

### İzinleri Doğrudan Atama (`=`)

`=` operatörü, belirtilen kategorideki tüm izinleri **sıfırlar ve yeniden yazar**. Bu, ekleme/çıkarmadan daha radikal bir değişimdir.

- `chmod u=rwx,g=rx,o=- dosya`
- Zincirleme (virgül ile): `chmod u=rw,g=r dosya`

**Pratikte Karşılaştıklarım:**
- Hedef: `-wxrwxr--` → `chmod u=wx,g=rwx,o=r`
- Hedef: `rw-rwx--x` → `chmod u=rw,g=rwx,o=x`
- Hedef: `--xrwxrwx` → `chmod u=x,g=rwx,o=rwx`
- Hedef: `-w----rw-` → `chmod u=w,g=-,o=rw`

---

## 3. Özel İzinler: SUID (Set User ID)

`ls -l` çıktısında çalıştırma biti (`x`) yerine **`s`** görürsek, bu dosyanın **SUID** (Set User ID) bitine sahip olduğunu gösterir.

- **SUID:** Programı çalıştıran kullanıcı kim olursa olsun, program sahibinin (genelde root) yetkileriyle çalışır.
- **Kullanımı:** `chmod xxx /challenge/getroot`
- **Amaç:** `/challenge/getroot` programına SUID ekleyerek root shell elde ettim ve `/flag` dosyasını okudum.

---

## 4. Takıldığım ve Dikkat Ettiğim Noktalar

1. **`=` ile `+/-` Arasındaki Fark:** Başta `=` kullanmayı unutup sürekli `+/-` ekledim, izinler tam oturmadı. `=` ile sıfırdan atama yapmak çoğu turda kurtarıcı oldu.
2. **Zincirleme İzin Verme:** Virgülle ayırarak farklı kategorilere farklı izinler atamak (`u=rwx,g=rw,o=x`) özellikle `=` ile çalışırken çok işe yaradı.

---
Bugünün `Program Misuse` için güzel bir temel olduğuna inanıyorum.
