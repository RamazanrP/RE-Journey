# 🐧 pwn.college - Chaining Commands Modülü

Bu modül, tek tek komut girmenin ötesine geçerek birden fazla komutu bir dosyada toplamayı (shell script), bu dosyaları çalıştırmanın farklı yollarını ve basit mantıksal akışları öğretti.


## 1. Shell Script Oluşturma ve Çalıştırma

Birden fazla komutu sırayla çalıştırmak için bunları bir `.sh` dosyasına yazdım.

- **Oluşturma:** `echo "/challenge/xxx" > x.sh` ile.
- **Çalıştırma:** `xxxx x.sh` komutu ile dosyadaki komutlar satır satır işletilir.
- **Mantık:** Her satır bağımsız bir komuttur ve sırayla çalıştırılır. Aynı satıra yazılan komutlar argüman olarak algılanır, bu yüzden alt alta yazmak doğru yöntemdir.


## 2. Script Çıktısını Yönlendirme ve Piping

Bir scriptin çıktısı, tıpkı tek bir komutun çıktısı gibi yönlendirilebilir veya başka bir programa aktarılabilir.

- `bash script.sh * /challenge/solve` ile betiğin tüm çıktısını (`stdout`) doğrudan hedef programa gönderdim.
- Artık `>` , `>>` , `2>` , `|` gibi yönlendirme araçlarını scriptlerle de kullanabiliriz.

## 3. Executable Scripts

Her seferinde `bash script.sh` yazmak yerine betiği doğrudan çalıştırmayı öğrendim.

- **Çalıştırılabilir Yapma:** `xxxxx +x script.sh`
- **Çalıştırma:** `./script.sh` veya `/home/hacker/script.sh`


### Kritik Hata ve Çözümü: `Permission denied`

**Olay:**  
Kök dizininde (`/`) bir script oluşturup (`/script.sh`) çalıştırmak istediğimde `bash: script.sh: Permission denied` hatası aldım.

**Neden?**  
Kök dizin (`/`), normal kullanıcılar için genellikle `noexec` (çalıştırma yasak) seçeneğiyle bağlanır. Bu, sistem güvenliğinin bir parçasıdır. Bunu karşılaşrak öğrenmiş oldum.

**Çözüm:**  
`cd ~` komutu ile ev dizinine (`/home/hacker`) geçtim. `~` (tilde) işareti, o anki kullanıcının ev dizinini temsil eder. Ev dizininde çalıştırma izni olduğu için `./script.sh` sorunsuz çalıştı.


## 4. Shebang (`#!`) ile Interpreter Belirtme

Bir scriptin hangi yorumlayıcı (interpreter) ile çalışacağını dosyanın en başında belirtebiliriz.

- **Kullanımı:** `#!/bin/bash` (dosyanın ilk satırı olmalı, öncesinde boşluk veya satır olmamalı.)
- **Etkisi:** Dosya çalıştırıldığında (`./script.sh`), işletim sistemi bu satırı okuyup belirtilen programa (`bash`) yönlendirir. Artık `bash` yazmak zorunda kalmayız.


## 5. Betik Argümanları (`$1`, `$2`)

Betik çalıştırılırken verilen argümanlara erişmeyi öğrendim.

- `$1` : İlk argüman
- `$2` : İkinci argüman
- **Örnek:** `echo "$2 $1"` betiği, verilen iki argümanı ters sırada yazdırır.

## 6. Koşullu İfadeler (`if-elif-else`)

Betiklerde karar mekanizmaları kurmayı öğrendim.

- **Sözdizimi:**
  ```bash
  if [ "$1" == "xxx" ]; then
      echo "college"
  elif [ "$1" == "xxxx" ]; then
      echo "planet"
  else
      echo "unknown"
  fi
  ```
- **Kritik Kurallar:**
  - `if`, `[` ve `]` arasında mutlaka boşluk olmalıdır.
  - `then` ve `fi` ayrı satırlarda veya `;` ile ayrılmış olmalıdır.
  - `fi`, `if`'in tersidir ve blok sonunu belirtir.

## Pondering PATH Modülü 

Bu modül, Linux bash komutları nasıl bulduğunu anlamak ve bu mekanizmayı kendi lehimize nasıl kullanabileceğimizi öğrenmek üzerineydi. PATH ortam değişkeni, bu odanın core komutuydu.

## 1. PATH Nedir ve Nasıl Çalışır?

PATH, shellin komut çalıştırılmak istendiğinde hangi dizinlerde arama yapacağını belirten iki nokta (:) ile ayrılmış bir dizin listesidir.

- `echo $PATH` ile mevcut PATH içeriği görüntülenir.
- Varsayılan PATH genellikle `/usr/local/bin`, `/usr/bin`, `/bin`, `/usr/sbin`, `/sbin` gibi sistem dizinlerini içerir.
- Bir komut yazıldığında (örneğin `ls`), kabuk bu dizinleri sırayla tarar ve ilk bulduğu çalıştırılabilir dosyayı çalıştırır.
- Eğer komut bulunamazsa `command not found` hatası alınır.

## 2. PATH’i Değiştirmenin Etkileri

PATH değişkeni geçici olarak değiştirilebilir. Bu, sadece o anki komut veya oturum için geçerlidir.

- `PATH=/yeni/dizin` şeklinde atama yapılırsa, eski PATH tamamen silinir ve sadece belirtilen dizin kullanılır.
- `export PATH=/yeni/dizin:$PATH` şeklinde atama yapılırsa, yeni dizin başa eklenir ve eski PATH korunur.

Bu modülde, PATH’i değiştirerek sistemin davranışını nasıl etkileyebileceğimizi deneyimledik.

## 3. Komutları Devre Dışı Bırakma (PATH’i Boşaltma)

PATH’i boşaltmak, kabuğun hiçbir komutu bulamamasına neden olur. Bu yöntem, bir programın belirli bir komutu çalıştırmasını engellemek için kullanılabilir.

- `PATH=` şeklinde boş atama yapılıp hemen ardından hedef program çalıştırılırsa, o program içinde çağrılan komutlar (örneğin `rm`) bulunamaz ve program beklenen işlemi gerçekleştiremez.
- Bu sayede, flag dosyasını silmeye çalışan bir programın silme işlemi **engellenebilir**.

## 4. Kendi Komutlarımızı Oluşturma ve PATH’e Ekleme

Kendi script'lerimizi, sadece isimlerini yazarak çalıştırabilmek için bu script'lerin bulunduğu dizini PATH’e eklememiz gerekir.

- Önce bir dizin oluşturulur (örneğin `~/bin`).
- Bu dizine, istenen isimde bir script dosyası yazılır ve çalıştırılabilir yapılır (`chmod +x`).
- Script'in içine, yapmasını istediğimiz işlemler (örneğin flag’i okuma) yazılır.
- Daha sonra PATH bu dizini gösterecek şekilde ayarlanır ve hedef program çalıştırılır.

Bu yöntem, bir programın çağırdığı komutu (örneğin `win` veya `rm`) kendi script'imizle değiştirmemizi sağlar.


## 5. PATH Değişikliğinde Karşılaşılan Sorunlar ve Çözümleri

PATH tamamen değiştirildiğinde, `cat`, `ls`, `echo` gibi temel komutlar da bulunamaz. Bu durumu aşmak için üç temel yöntem vardır:

- **Mutlak yol kullanmak:** Hangi komut kullanılacaksa, o komutun tam dosya yolu (`/bin/cat`, `/usr/bin/cat` gibi) script içinde doğrudan yazılır. Bu sayede PATH’ten bağımsız çalışır.
- **read builtin’ini kullanmak:** `read`, bash’in yerleşik bir komutudur ve PATH’ten etkilenmez. Dosya içeriğini `read` ile okuyup değişkene atayabiliriz.
- **Eski PATH’i korumak:** Yeni dizini eski PATH’in başına veya sonuna ekleyerek (`export PATH=~/bin:$PATH`) diğer komutların çalışmaya devam etmesi sağlanır.

Bu modülde özellikle `which` komutu ile bir programın tam yolunu bulmayı öğrendik. Örneğin `which cat` ile `cat`’in nerede olduğunu tespit edip mutlak yolda kullandık.

---

## 6. Pratikte Karşılaşılan Zorluklar ve Çözümleri

### A. `PATH=/dizin /program` yazımında boşluk hatası

- Hatalı kullanım: `PATH= /dizin /program` (boşluk var)
- Bu durumda kabuk, `PATH=` (boş) ve `/dizin` (komut olarak) şeklinde yorumlar ve “Is a directory” hatası verir.
- Doğru kullanım: `PATH=/dizin /program` (boşluksuz)

### B. Script içinde `cat` bulunamaması

- PATH sadece kendi dizinimizi gösterdiğinde `cat` çağrılamaz.
- Çözüm: Script içinde `cat` yerine `read` kullanmak veya `cat`’in mutlak yolunu yazmak.

### C. Programın `rm` ile flag silmesini engelleme

- `rm` komutunu kendi script'imizle değiştirdik.
- Bu script, flag’i okuyup ekrana bastı, hiçbir dosya silmedi.
- PATH’i kendi dizinimize yönlendirerek `/challenge/run`’un bizim `rm`’mizi bulmasını sağladık.

---

## 7. Son Challenge’ın Çözüm Mantığı

Son challenge’da `/challenge/run`, `rm` ile flag’i siliyordu. Çözüm:

- Sahte bir `rm` script'i oluşturuldu. Bu script, flag’i okuyup ekrana bastı.
- PATH, bu script'in bulunduğu dizini gösterecek şekilde ayarlandı.
- `/challenge/run` çalıştırıldığında `rm` olarak bizim script'imiz çalıştı ve flag silinmeden okundu.

---

## 8. Modülden Çıkarılan Dersler

- PATH, kabuğun komut arama mekanizmasının temelidir.
- PATH’i manipüle ederek sistem davranışını kontrol edebiliriz.
- Bir programın çağırdığı komutları kendi script'lerimizle değiştirebiliriz.
- Bu teknik, ileride yetki yükseltme (privilege escalation) ve command injection gibi güvenlik konularında kritik rol oynar.
- Mutlak yol kullanımı, PATH değişikliklerinden etkilenmemenin en garantili yoludur.
- `read` gibi bash builtin’leri, PATH’ten bağımsız çalıştığı için güvenli alternatifler sunar.
