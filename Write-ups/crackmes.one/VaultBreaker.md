# [Write-up] VaultBreaker - C++ Qt GUI Analysis and XOR Decryption

## 1. Introduction and Target Analysis

In this analysis, unlike traditional command-line interface (CLI) based vulnerable programs, `VaultBreaker`, a graphical user interface (GUI) application developed using **C++** and the **Qt framework**, was examined. The main objective of the program is to request an Access Code from the user and verify this password in the background.

Since GUI applications contain massive amounts of boilerplate code and memory management blocks during static analysis, it necessitated changing the conventional top-to-bottom code reading strategy.

---

## 2. Common Pitfalls in GUI Analysis (Important Warnings)

There are three major pitfalls that beginners in reverse engineering (or those with CLI pwn experience) frequently fall into when dealing with such interface programs. Avoiding these traps during analysis saves time:

* **Trap 1: Looking for Vulnerabilities in the `main` Function**
While everything revolves around `main` in CLI programs, in Qt applications, `main` simply draws the interface and enters an infinite loop with `QApplication::exec()`. It is necessary to look for the password control mechanism outside of `main`.
* **Trap 2: Attempting Buffer Overflows on Interface Inputs**
Trying to overflow the application's Stack usually fails. Qt stores text as dynamically sized `QString` objects. Therefore, simple Stack Overflows, like those in classic `gets()` or `scanf()` vulnerabilities, do not work on interface elements.
* **Trap 3: Getting Lost in Memory Management Code**
Blocks like `LOCK()`, `UNLOCK()`, and `QArrayData::deallocate` are constantly seen in the Ghidra output. These are Qt's garbage collection routines that clean up the RAM after a text displayed on the screen is no longer needed. These lines should be ignored during analysis.

---

## 3. Tracking Dynamic Signals

To understand the program's structure, instead of reading the code line by line, I acted with the logic of "Event-Driven Programming":

1. **Finding the Visual Trigger:** Which background function was the "Unlock" button I clicked on the screen connected to? By filtering the Symbol Tree, I determined that this button directly triggered the `MainWindow::OnUnlockClicked` function.
2. **Descending to the Decision Mechanism:** When I entered the button's function, the only line among all the interface code that stood out and required our attention was: `uVar2 = CheckPassword(...)`. The text entered by the user was taken and sent to this function.
3. **Reaching the Core:** The actual encryption algorithm and the `0` (Red Screen/Error) or `1` (Green Screen) return values that determine the program's fate were entirely inside the `CheckPassword` function.

---

## 4. Cryptographic Core and XOR Analysis

Let's examine the `CheckPassword` function more deeply. The system relies on these three simple steps:

1. **Length Check:** The program restricted my input with an `if (length == 10)` check to see if the password I entered was exactly **10 characters** long. Inputs of the wrong size were immediately rejected.
2. **Static Key (XOR):** 10 bytes of data were taken from an array named `kEncoded` embedded as a global variable in memory. Each of these bytes was subjected to an **XOR (`^`)** operation with the static hex value `0x5a`, generating the original password in memory on the fly.
3. **Comparison:** This decrypted password was compared against my inputted value via `memcmp`.

---

## 5. Decrypting the Password

Due to the symmetrical nature of the XOR operation *(Encrypted Data ^ Key = Original Data)*, I extracted those 10 hex values sequentially from Ghidra's Data section: `15 2a 69 34 09 69 29 3b 37 3f`.

To automate the analysis process, I wrote a simple Python script.

**Terminal Execution Screen and Output:**

```bash
kali@linux:~/VaultBreaker$ cat solve_xor.py 
kEncoded = [0x15, 0x2a, 0x69, 0x34, 0x09, 0x69, 0x29, 0x3b, 0x37, 0x3f]
cozulmus_sifre = ""

for byte in kEncoded:
    cozulmus_sifre += chr(byte ^ 0x5a)

print(f"[+] Password: {cozulmus_sifre}")

kali@linux:~/VaultBreaker$ python3 solve_xor.py 
[+] Password: Op3nS3same

```

When I entered the password (`Op3nS3same`) into the interface, I received the success message and successfully completed the analysis.

---

## 6. Takeaways

This challenge was a great example that required an analyst not just to read the code, but to **filter** it. Being able to see the big picture in C++ based interface programs, tracking bitwise operators (`^`, `<<`), and not getting lost in unnecessary memory management functions significantly advanced my static analysis skills.

# [Write-up] VaultBreaker - C++ Qt GUI Analizi ve XOR Şifre Çözümü

## 1. Giriş ve Hedef Analizi

Bu analizde, geleneksel komut satırı (CLI) tabanlı zafiyetli programların aksine, **C++** ve **Qt framework'ü** kullanılarak geliştirilmiş bir grafik arayüz (GUI) uygulaması olan `VaultBreaker` incelenmiştir. Programın temel amacı, kullanıcıdan bir Access Code istemek ve bu şifreyi arka planda doğrulamaktır.

GUI uygulamaları, statik analiz sırasında devasa boyutlarda başlangıç kodları (boilerplate) ve hafıza yönetimi blokları barındırdığı için alışılagelmiş yukarıdan aşağıya kod okuma stratejisinin değiştirilmesini zorunlu kılmıştır.

---

## 2. GUI Analizinde Sık Düşülen Tuzaklar (Önemli Uyarılar)

Tersine mühendisliğe yeni başlayanların (veya CLI pwn tecrübesi olanların) bu tarz arayüz programlarında sıkça düştüğü üç büyük tuzak vardır. Analiz sırasında bu tuzaklara düşmemek zaman kazandırır:

* **Tuzak 1: `main` Fonksiyonunda Zafiyet Aramak**
CLI programlarında her şey `main` içinde dönerken, Qt uygulamalarında `main` sadece arayüzü çizer ve `QApplication::exec()` ile sonsuz bir döngüye girer. Şifre kontrol mekanizmasını `main` dışında aramak gerektir.
* **Tuzak 2: Arayüz Girdilerinde Buffer Overflow Denemek**
Uygulamanın Stack'ini taşırmaya çalışmak genellikle başarısız olur. Qt, metinleri dinamik olarak boyutlandırılan `QString` objeleri olarak tutar. Bu nedenle klasik `gets()` veya `scanf()` zafiyetlerindeki gibi basit Stack Overflow arayüz elementlerinde işe yaramaz.
* **Tuzak 3: Hafıza Yönetimi Kodlarında Kaybolmak**
Ghidra çıktısında sürekli olarak `LOCK()`, `UNLOCK()`, `QArrayData::deallocate` blokları görülür. Bunlar, Qt'nin ekranda gösterilen bir yazının işi bittikten sonra RAM'i temizleme (Garbage Collection) rutinleridir. Bu satırlar analiz sırasında görmezden gelinmelidir.

---

## 3. Dinamik Sinyalleri Takip Etmek

Programın yapısını anlamak için kodu satır satır okumak yerine, "Olay Güdümlü Programlama" (Event-Driven Programming) mantığıyla hareket ettim:

1. **Görsel Tetikleyiciyi Bulmak:** Ekranda tıkladığım "Unlock" butonu arka planda hangi fonksiyona bağlıydı? Symbol Tree'yi filtreleyerek bu butonun doğrudan `MainWindow::OnUnlockClicked` fonksiyonunu tetiklediğini tespit ettim.
2. **Karar Mekanizmasına İnmek:** Buton fonksiyonunun içine girdiğimde, tüm arayüz kodlarının arasında göze çarpan ve de dikkat etmemiz gereken tek satır: `uVar2 = CheckPassword(...)`. Kullanıcının yazdığı metin alınıp bu fonksiyona gönderiliyordu.
3. **Çekirdeğe Ulaşmak:** Asıl şifreleme algoritması ve programın kaderini belirleyen `0` (Kırmızı Ekran/Hata) veya `1` (Yeşil Ekran) dönüş değerleri tamamen `CheckPassword` fonksiyonunun içindeydi.

---

## 4. Kriptografik Çekirdek ve XOR Analizi

`CheckPassword` fonksiyonunu daha derinden inceleyelim. Sistem şu üç basit adıma dayanıyor:

1. **Uzunluk Kontrolü:** Program, girdiğim şifrenin tam olarak **10 karakter** olup olmadığını `if (length == 10)` kontrolüyle sınırlıyordu. Yanlış boyuttaki girdiler doğrudan reddediliyordu.
2. **Statik Anahtar (XOR):** Hafızada global değişken olarak gömülü `kEncoded` isimli bir dizideki 10 byte'lık veri alınıyordu. Bu verilerin her biri, `0x5a` sabit hex değeriyle **XOR (`^`)** işlemine sokularak orijinal şifre anlık olarak bellekte oluşturuluyordu.
3. **Karşılaştırma:** Çözülen bu şifre, benim girdiğim değerle `memcmp` üzerinden kıyaslanıyordu.

---

## 5. Şifrenin Çözülmesi

XOR işleminin simetrik doğası gereği *(Şifreli Veri ^ Anahtar = Orijinal Veri)*, Ghidra'nın Data bölümünden o 10 hex değerini sırayla çıkardım: `15 2a 69 34 09 69 29 3b 37 3f`.

Analiz sürecini otomatize etmek adına basit bir Python scripti yazdım.

**Terminal Çalıştırma Ekranı ve Çıktı:**

```bash
kali@linux:~/VaultBreaker$ cat solve_xor.py 
kEncoded = [0x15, 0x2a, 0x69, 0x34, 0x09, 0x69, 0x29, 0x3b, 0x37, 0x3f]
cozulmus_sifre = ""

for byte in kEncoded:
    cozulmus_sifre += chr(byte ^ 0x5a)

print(f"[+] Şifre: {cozulmus_sifre}")

kali@linux:~/VaultBreaker$ python3 solve_xor.py 
[+] Şifre: Op3nS3same

```

Şifreyi (`Op3nS3same`) arayüze girdiğimde başarı mesajını alarak analizi başarıyla tamamladım.

---

## 6. Çıkarımlar

Bu görev, bir analistin kodu sadece okumasını değil, **filtrelemesini** gerektiren harika bir örnekti. C++ tabanlı arayüz programlarında büyük resmi okuyabilmek, bit düzeyinde operatörlerin (`^`, `<<`) izini sürmek ve gereksiz bellek yönetimi fonksiyonlarında kaybolmamak, statik analiz yeteneklerimi önemli ölçüde ileriye taşıdı.
