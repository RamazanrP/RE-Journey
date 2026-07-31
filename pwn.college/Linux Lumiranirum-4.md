# 🐧 Daring Destruction Z Raporu

Bu modül, sistem kaynaklarını tüketen saldırıları (Fork Bomb, Disk Doldurma) ve sistem dosyalarını tamamen silmenin (`rm -rf`) yıkıcı etkilerini, ayrıca bu yıkım sonrasında hayatta kalmayı (builtin komutları kullanarak) öğretti.

## 1. Fork Bomb

**Amaç:** `/challenge/check` programına, sistemin artık yeni süreç oluşturamadığını (process table'ın dolu olduğunu) gösterip flag'i aldırmak.

**Mantık:** Bir script yazıp, bu script'in kendisini sürekli arka planda (`&`) iki kopya halinde çağırması. Bu, üstel bir şekilde çoğalarak sistemin süreç tablosunu doldurur.

**Uygulama Adımları:**

1.  `tmux` oturumu başlat (çünkü bombayı çalıştırdıktan sonra aynı terminalde başka komut çalıştırmak neredeyse imkansız hale gelir):
    ```bash
    tmux
    ```
2.  Ekranı iki bölmeye ayır (`Ctrl+B` sonra `%`).
3.  İlk bölmede `/challenge/check`'i çalıştır:
    ```bash
    /challenge/check
    ```
    *(Bu program beklemeye başlar, süreç tablosunun dolmasını izler.)*
4.  Diğer bölmeye geç (`Ctrl+B` sonra sağ ok tuşu) ve Fork Bomb'u başlat.
    **Kullanılan Komut (Klasik Fork Bomb):**
    ```bash
    :(){ :|:& };:
    ```
    *(Bu komut, `:` adında bir fonksiyon tanımlar. Fonksiyon, kendini arka planda iki kez çağırır (`:|:&`). `;:` ile fonksiyon hemen tetiklenir.)*

    **Alternatif Script Yöntemi (Daha okunabilir):**
    ```bash
    echo -e '#!/bin/bash\nblahblah &\nblahblah &' > boom.sh
    chmod +x boom.sh
    ./boom.sh
    ```
    *(Her iki yöntem de aynı sonucu verir; sistem donana kadar süreç sayısı katlanarak artar.)*

5.  Birkaç saniye içinde `/challenge/check` bölmesinde flag görünecektir.

## 2. Disk Space Doomsday

**Amaç:** `/home/hacker` dizinini tamamen doldurarak `/challenge/check`'in 1 MB'lık geçici bir dosya oluşturmasını engellemek, ardından alanı temizleyip ikinci kontrolde flag'i almak.

**Mantık:** `dd` komutu ile `/dev/zero` (sonsuz sıfır akışı) dosyasını okuyarak büyük bir dosya oluşturup diski doldurmak.

**Uygulama Adımları:**

1.  Önce `/home/hacker` dizininin ne kadar yer kapladığını kontrol et (Bu challenge'da özel olarak *** MB olarak ayarlanmıştı):
    ```bash
    df -h /home/hacker
    ```
    *(Çıktı: `tmpfs ***M 4.0K ***M 1% /home/hacker` → *** MB boş alan var.)*

2.  Diski doldurmak için tam *** MB veya biraz daha büyük bir dosya oluştur:
    ```bash
    dd if=/dev/zero of=/home/hacker/bigfile bs=1M count=***
    ```
    
3.  İlk kontrolü çalıştır (Artık disk dolu olduğu için 1 MB dosya oluşturamaz ve başarısız olur):
    ```bash
    /challenge/check
    ```
    *(Bu aşamada `Plenty of space remains` yazısı gelmez; disk dolu olduğu için farklı bir uyarı verir veya doğrudan "free the space" der.)*

4.  Oluşturduğumuz dosyayı silerek alanı temizle:
    ```bash
    ** /home/hacker/bigfile
    ```

5.  İkinci kontrolü çalıştır (Artık diskte yer var, 1 MB dosyayı oluşturabilir ve flag'i basar):
    ```bash
    /challenge/check
    ```

**`dd` Komutunun Kaynağı (Öğrenme Linki):**  
Bu komut, GNU Coreutils paketinin bir parçasıdır. Detaylı dokümantasyonu için:
https://www.gnu.org/software/coreutils/manual/html_node/dd-invocation.html

---

## 3. `rm -rf /` ve `--no-preserve-root` (Sistem Silme)

**Amaç:** Sistemdeki tüm dosyaları silerek `/challenge/check`'in "yıkımı" görmesini sağlamak ve flag'i almak.

**Mantık:** `rm -rf /` komutu ile tüm dosya sistemini silmek. Ancak modern sistemler bu komutu korur (`--preserve-root`).

**Uygulama Adımları:**

1.  `tmux` ile yine iki bölme aç.
2.  İlk bölmede `/challenge/check`'i başlat:
    ```bash
    /challenge/check
    ```
3.  İkinci bölmede `rm` komutunu, korumayı aşacak şekilde çalıştır:
    ```bash
    rm -rf --xx-preserve-root /
    ```
    *(Eğer `--xx-preserve-root` kullanmazsan, hata alırsın: `rm: it is dangerous to operate recursively on '/'`.)*

4.  Terminalde "Permission denied", "No such file" gibi binlerce hata akar. Sistem kullanılamaz hale gelir. `/challenge/check` bu süreci izler ve flag'i basar.

---

## 4. `cat`'siz Hayat (Builtin `read` ile Okuma)

**Amaç:** `rm -rf /` sonrası sistem çökmüşken, `cat` komutu çalışmadığı için flag'i manuel olarak okumak.

**Mantık:** `cat` harici bir programdır (`/bin/cat`) ve dosya sistemi silindiği için bulunamaz. Ancak `read`, bash'in **yerleşik (builtin)** bir komutudur ve dosya sisteminden bağımsız çalışır.

**Uygulama Adımları:**

1.  Aynı silme işlemini (`rm -rf --xx-preserve-root /`) tekrarla, `/challenge/check` flag dosyasını geri yüklesin.
2.  `cat` çalışmadığı için, `read` ile dosyayı oku:
    ```bash
    read -r flag < /flag && echo "$xxxx"
    ```

**Neden `read` özel?**
-   **Harici Programlar:** `ls`, `cat`, `rm`, `cp` → `/bin/` veya `/usr/bin/` altında dosya olarak bulunurlar. Dosya sistemi silinince yok olurlar.
-   **Builtin'ler:** `read`, `echo`, `cd`, `export`, `alias`, `pwd` → Bash'in kendi kodunun içinde yer alırlar. Çalışmak için harici bir dosyaya ihtiyaç duymazlar.

---

## 5. `ls`'siz Hayat (`echo *` ile Globbing)

**Amaç:** `/challenge/check` flag'i rastgele isimli bir dosyaya  koyduğunda, `ls` çalışmadığı için bu dosyayı bulup okumak.

**Mantık:** `ls` harici bir programdır. Ancak `echo` builtin'dir. `echo *` kullanarak, bash'in joker karakter genişletme (globbing) özelliğinden yararlanırız. Shell, `*` işaretini görünce mevcut dosyaları listeler ve bunları `echo`'ya argüman olarak verir.

**Uygulama Adımları:**

1.  `rm -rf --xx-preserve-root /` ile sistemi sil. `/challenge/check` rastgele isimli flag dosyasını `/` dizinine koysun.
2.  Root dizine geç (builtin olduğu için çalışır):
    ```bash
    cd /
    ```
3.  Rastgele dosyayı bulmak için `echo *` kullan:
    ```bash
    echo *
    ```
4.  Bulduğun dosyayı `read` ile oku:
    ```bash
    read -r flag < blahblah && echo "$flag"
    ```


## Modülden Çıkarılan Dersler

-   **Fork Bomb (`:(){ :|:& };:`)** sistem kaynaklarını tüketir; process limitleri (`ulimit -u`) ile önlenebilir.
-   **`dd`** ile disk doldurma, dosya sistemi limitlerini test etmek için kullanılır. `if=/dev/zero` ve `of=` ile çıktı dosyası belirtilir.
-   **`rm -rf --xx-preserve-root /`** sadece test ortamlarında denenmeli; gerçek sistemlerde asla kullanılmamalıdır.
-   **Builtin komutlar** (`read`, `echo`, `cd`) sistem çökmüş olsa bize yardım edebilir.
-   **`echo *`** ile `ls` olmadan dosya listeleme, shellin globbing özelliğinin gücünü gösterir.

Bu modül, Linux'un en temel katmanlarına dokunmamı ve sistemin ne kadar kırılgan, ama aynı zamanda ne kadar kurtarılabilir olduğunu anlamamı sağladı.
