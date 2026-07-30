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
