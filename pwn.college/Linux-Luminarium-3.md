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

## Silly Shenanigans Modülü 

Bu modül, sistemdeki kullanıcıların başlangıç script'leri (`.bashrc`), paylaşılan dizinler, süreç argümanları ve dosya izinleri gibi zafiyetlerden nasıl yararlanılabileceğini öğretti. Her seviye, farklı bir saldırı vektörünü ve bunlara karşı alınabilecek önlemleri tecrübe ettirdi.

---

## 1. `.bashrc` Sömürüsü

`.bashrc` dosyası, kullanıcı shelli her başlatıldığında otomatik olarak çalıştırılır. Eğer bu dosyaya yazma izniniz varsa, içine komut ekleyerek hedef kullanıcının oturumunda kod çalıştırabilirsiniz.

- **Yöntem:** `.bashrc` dosyasının sonuna `cat /flag` gibi bir komut eklemek.
- **Sonuç:** Zardus giriş yaptığında flag ekrana basılır.
- **Önlem:** `.bashrc` dosyasını sadece sahibinin yazabilmesi için `chmod 600` ile korumak.

---

## 2. İnteraktif Programları Taklit Etme (`flag_checker` örneği)

Eğer hedef kullanıcı bir programı interaktif olarak çalıştırıp içine hassas veri (örneğin flag) giriyorsa, bu programı taklit ederek veriyi yakalayabilirsiniz.

- **Yöntem:** `.bashrc` içine `flag_checker` adında bir fonksiyon veya alias tanımlamak. Bu taklit, önce programın çıktısını taklit eder (`echo "Type the flag"`), sonra kullanıcının girdiğini okur (`read`) ve ekrana basar.
- **Sonuç:** Zardus flag'i manuel girdiğinde, taklit fonksiyon bu girdiyi yakalar ve size gösterir.
- **Önlem:** Hassas verileri interaktif olarak girmekten kaçınmak veya programın bütünlüğünü doğrulamak (hash kontrolü vb.).

---

## 3. World-Writable Dizinler ve Dosya Silme/Yeniden Oluşturma

Eğer bir dizin world-writable ise, o dizindeki dosyaları (dosyanın kendi izinleri ne olursa olsun) silebilir veya taşıyabilirsiniz.

- **Yöntem:** Zardus'un home dizini world-writable olduğu için `.bashrc` dosyasını sildik ve yerine kendi içeriğimizi yazdık. Ancak orijinal `.bashrc` içeriğini kaybetmemek için önce yedekledik.
- **Sorun:** Dosya sahipliği değiştiği için yazma izni kazandık, ama dosya sahibi `zardus` olarak kaldıysa yazamayabiliriz.
- **Çözüm:** Dosyayı sildikten sonra yeni dosya oluşturduğumuzda sahibi `hacker` olur, böylece istediğimizi ekleyebiliriz.
- **Önlem:** World-writable dizinlerde `sticky bit` (`chmod +t`) kullanmak, böylece dosyaları yalnızca sahiplerinin silmesini sağlamak.

---

## 4. Sembolik Link ile Dosya Yönlendirme (`ln -s`)

Sembolik link, bir dosyayı başka bir dosyaya yönlendiren özel bir dosya türüdür. Eğer bir dizine yazma izniniz varsa, bu dizindeki bir dosyayı link ile değiştirebilirsiniz.

- **Yöntem:** `/tmp/collab/evil-commands.txt` dosyasını sildik ve yerine `/home/zardus/.bashrc` dosyasına sembolik link oluşturduk.
- **Sonuç:** Zardus, `evil-commands.txt` dosyasına `cat /flag` eklediğinde, bu aslında `.bashrc` dosyasının sonuna eklenmiş oldu. Zardus tekrar giriş yaptığında `.bashrc` çalıştı ve flag geldi.
- **Önlem:** Paylaşılan dizinlerde `sticky bit` kullanmak ve sembolik link oluşturmayı kısıtlamak (mount seçenekleri ile).

---

## 5. Süreç Argümanları ile Şifre Görme (`ps aux`)

Bir program çalıştırıldığında, komut satırı argümanları `ps` ile görülebilir. Eğer bu argümanlar hassas veri içeriyorsa (örneğin şifre), bu veri sızdırılabilir.

- **Yöntem:** Zardus'un bir otomasyon script'ini çalıştırdığını ve şifresini argüman olarak verdiğini varsaydık. `ps aux | grep zardus` ile bu süreci ve argümanlarını listeledik. Şifreyi bulup `su zardus` ile geçiş yaptık.
- **Sonuç:** Zardus'un `sudo` yetkisini kullanarak flag'i okuduk.
- **Önlem:** Hassas bilgiler asla komut satırı argümanı olarak verilmemeli; bunun yerine ortam değişkenleri veya interaktif girdi kullanılmalıdır.

---

## 6. World-Readable `.bashrc` ve API Anahtarları

`.bashrc` dosyası varsayılan olarak world-readable (herkes tarafından okunabilir) olabilir. Eğer bu dosyada API anahtarları veya şifreler saklanıyorsa, sistemdeki diğer kullanıcılar bunları okuyabilir.

- **Yöntem:** `cat /home/zardus/.bashrc` ile dosyayı okuduk ve `FLAG_GETTER_API_KEY` değerini bulduk. Ardından `flag_getter --xxx <anahtar>` çalıştırarak flag'i aldık.
- **Önlem:** Hassas veriler `.bashrc`'de saklanmamalı; bunun yerine `chmod 600` ile korunan ayrı bir dosyada tutulmalı veya bir şifre yöneticisi kullanılmalıdır.

---

## Modülden Çıkarılan Genel Dersler

- **Başlangıç script'leri (`.bashrc`)** güçlü araçlardır; hem kullanıcı hem de saldırgan için.
- **Dosya izinleri** (world-writable, world-readable) çoğu zaman göz ardı edilir, ancak büyük güvenlik açıklarına yol açar.
- **Sembolik linkler** ve **sticky bit** gibi özellikler, dosya sistemi güvenliğinde kritik rol oynar.
- **Süreç argümanları** asla hassas veri içermemelidir; `ps` ile herkes görebilir.
- Paylaşımlı ortamlarda, kullanıcılar kendi dosyalarının izinlerini ve hangi verileri açığa çıkardıklarını dikkatlice değerlendirmelidir.

Bu modül, sistem güvenliğinin sadece yetkilerle değil, aynı zamanda kullanıcı davranışları ve varsayılan ayarlarla da ilgili olduğunu öğretti.
