# The Wired (Level 2)

## Introduction and Objective

After the Windows `.exe` adventure in the first level, this time I faced a Linux ELF file. My objective seemed simple: find the hidden flag inside the file. However, "The Wired" was cleverly designed enough to make me run around in its own labyrinth for hours, block my debug commands with `ptrace` protections, and mock me by giving me fake flags. It also had nice references to the Serial Experiments Lain anime.

## Step 1: Infiltrating the Real Main Function

When I threw the file into Ghidra and started the analysis, I encountered the `entry` (`_start`) function, which is the classic entry point of Linux executables. Taking the lesson I learned from the first level, I didn't drown in the compiler boilerplate codes. Knowing that the first parameter (`&LAB_001010c0`) passed directly to the `__libc_start_main` function was the real `main` function, I teleported to the actual battlefield.

## Dead End #1: The `0xCC` Trap and Wrong Export

While examining the real `main` codes, I saw a massive if block: `if (FUN_00101380[*plVar1] == (code)0xcc)`.

I thought the program was looking for a debugger and would print the flag to the screen if it found a software breakpoint (`0xcc` - INT 3). Thinking the code was simple, I decided to do Patching via Ghidra. I patched the program by changing the `JZ` instruction to `JNZ`. When I ran it, the program not giving me the flag was the first dead end.

## Dead End #2: GDB, PIE, and ASLR

Since patching didn't work, I decided to give the program what it wanted and do dynamic analysis with GDB. However, due to Linux's security mechanisms:

1. **Permission Denied:** At first, I had to grant the file execute permission with `chmod +x`.
2. **Cannot access memory (PIE):** I tried to set a breakpoint via GDB at the static address (`0x101380`) I got from Ghidra, but I received an error. Because the program had PIE (Position Independent Executable) protection, Linux threw the program to a random place in memory every time it ran.
3. **Offset Calculation:** To overcome this obstacle, I froze the program with `starti`. I found the real base address with `info proc mappings` and set my trap at the correct address by calculating the offset (`0x1380`) myself.

After calculating all the addresses correctly and releasing the program with `continue`, a bitter message appeared on the screen:
`[-] The Wired denies debugging`

A hidden function running at the beginning of the program detected that GDB was watching me using the `ptrace` system and forced the program to commit suicide. Dynamic analysis had completely collapsed.

## Dead End #3: Obfuscation and Fake Flag

Upon this, I turned to static analysis, to crack the cipher on paper with Python.

* I collected and combined the program's decryption key from different addresses (like `DAT_0012f6ca`): **`.gnu.version`**
* Then, I extracted the 31-byte ciphertext located at the `0x12f6d0` address.
* I XORed these two pieces of data using the Python script I wrote.

When I ran the code, what fell onto the screen was not a flag, but a massive mocking message hidden in the code by the author for those doing static analysis like me: `[-] The Wired denies debun...`. This was the fake flag.

## Final Step and Victory

I returned to the source code in Ghidra and went down to the actual dark zone (`FUN_00101380`) that the fake flag loop bypassed. The real algorithm was right there:

1. **Argument Check:** The program expected 1 extra argument like `./thewired <password>` to run, verifying this with the `argc == 2` logic via the `if (param_1 == 2)` line.
2. **Real Ciphertext:** I saw a hidden data block of exactly **173 bytes** at the `0x104060` address.
3. **Cryptographic Solution:** I obtained this 173-byte actual data from Ghidra. Going to Python again, I XORed this block I found with the `.gnu.version` key.

And the moment I wrote the Python script in the terminal, the hours of research yielded the final result on the screen:

```text
====================
      THE WIRED             
================================

ACCESS GRANTED

Welcome to The Wired.

Everyone is connected.

[ONLINE]

```

## What Did It Teach Me? (My Takeaways)

* I learned to calculate the dynamic offset (`starti` and `info proc mappings`) to bypass PIE/ASLR protections with GDB.
* I experienced firsthand how malware evades analysis using `ptrace`.
* I realized through experience that when solving a crackme or malware, I shouldn't jump at the first `0xcc` or XOR loop I find, as authors can leave a "Fake Flag/Rabbit Hole".
* When everything else was blocked, I understood the platform-independent power of static analysis and Python.

# The Wired (Seviye 2 Zorluk)

##  Giriş ve Hedef

İlk seviyedeki Windows `.exe` macerasından sonra, bu kez karşımızda bir Linux ELF dosyası vardı. Amacımız basit görünüyordu: Dosyanın içindeki gizli bayrağı bulmak. Ancak "The Wired", beni saatlerce kendi labirentinde koşturacak, ptrace korumalarıyla debug komutlarımı engelleyecek ve bana fake flagler vererek benimle dalga geçecek kadar zekice tasarlanmıştı. Ayrıca Lain animesine güzel göndermeleri de vardı.

##  Adım 1: Gerçek Main Fonksiyonuna Sızmak

Dosyayı Ghidra'ya atıp analize başladığımda, Linux çalıştırılabilir dosyalarının klasik giriş noktası olan `entry` (`_start`) fonksiyonuyla karşılaştım. İlk seviyeden aldığım dersle derleyici kodlarında boğulmadım. Doğrudan `__libc_start_main` fonksiyonuna verilen ilk parametrenin (`&LAB_001010c0`) gerçek `main` fonksiyonu olduğunu bilerek asıl savaş alanına ışınlandım.

##  Çıkmaz Sokak #1: `0xCC` Tuzağı ve Yanlış Export

Gerçek `main` kodlarını incelerken devasa bir if bloğu gördüm: `if (FUN_00101380[*plVar1] == (code)0xcc)`.

Programın bir debugger (hata ayıklayıcı) aradığını ve yazılımsal kesme noktası (`0xcc` - INT 3) bulursa bayrağı ekrana basacağını düşündüm. Kodu basit sanarak Ghidra üzerinden Patching'e karar verdim. `JZ` komutunu `JNZ` yaparak programı yamaladım. Çalıştırdığımda ise programın bana bayrağı vermemesi, ilk çıkmaz sokaktı.

##  Çıkmaz Sokak #2: GDB, PIE ve ASLR

Madem yama işe yaramadı, programın istediğini verip GDB ile dinamik analiz yapayım dedim. Ancak Linux'un güvenlik mekanizmaları yüzünden:

1. **Permission Denied:** İlk başta dosyaya `chmod +x` ile çalışma izni vermeliydik.
2. **Cannot access memory (PIE):** Ghidra'dan aldığım statik adrese (`0x101380`) GDB üzerinden breakpoint koymaya çalıştım ancak hata aldım. Çünkü programda PIE (Position Independent Executable) koruması vardı ve Linux programı her çalıştırdığında bellekte rastgele bir yere atıyordu.
3. **Offset Hesaplama:** Bu engeli aşmak için programı `starti` ile dondurdum. `info proc mappings` ile gerçek taban adresini bulup offset (`0x1380`) hesaplamasını kendim yaparak doğru adrese tuzağımı kurdum. Ve şu mesaj ekrana geldi:

Bütün adresleri doğru hesaplayıp programı `continue` ile serbest bıraktığımda ekranda acı bir mesaj belirdi:
`[-] The Wired denies debugging`

Programın başında çalışan gizli bir fonksiyon, `ptrace` sistemiyle GDB'nin beni izlediğini tespit etmiş ve programı intihar ettirmişti. Dinamik analiz tamamen çökmüştü.

##  Çıkmaz Sokak #3: Obfuscation ve Fake Flag

Bunun üzerine statik analize, Python ile şifreyi kağıt üzerinde kırmaya yöneldim.

* Programın şifre çözme anahtarını farklı adreslerden (`DAT_0012f6ca` vb.) toplayıp birleştirdim: **`.gnu.version`**
* Ardından `0x12f6d0` adresindeki 31 byte'lık şifreli metni çıkardım.
* Yazdığım Python scripti ile bu iki veriyi XOR işlemine soktum.

Kodu çalıştırdığımda ekrana düşen şey bir bayrak değil, yazarın benim gibi statik analiz yapanlar için koda gizlediği büyük bir dalga geçme mesajıydı: `[-] The Wired denies debun...`. Sahte bayrak buydu.

##  Son Adım ve Zafer

Tekrar Ghidra'daki kaynak koduna döndüm ve o sahte bayrak döngüsünün pas geçtiği asıl karanlık bölgeye (`FUN_00101380`) indim. İşte gerçek algoritma oradaydı:

1. **Argüman Kontrolü:** Program, çalışması için `./thewired <şifre>` şeklinde 1 adet ekstra argüman bekliyordu (`argc == 2`).
2. **Gerçek Şifreli Metin:** `0x104060` adresinde tam **173 byte'lık** gizli bir veri bloğu gördüm.
3. **Kriptografik Çözüm:** Bu 173 byte'lık asıl veriyi Ghidra'dan elde ettim. Yine Python'a giderek, bulduğum bu bloğu `.gnu.version` anahtarıyla tekrar XOR işlemine soktum.

Ve terminalde Python scriptini yazdığım an, saatler süren araştırma nihai sonucu ekrana verdi:

```text
====================
      THE WIRED             
================================

ACCESS GRANTED

Welcome to The Wired.

Everyone is connected.

[ONLINE]

```

##  Bana Neler Kattı? (Çıkarımlarım)

* GDB ile PIE/ASLR korumalarını aşmak için dinamik offset (`starti` ve `info proc mappings`) hesaplamayı öğrendim.
* Zararlı yazılımların `ptrace` kullanarak analizden nasıl kaçtıklarını yaşayarak gördüm.
* Bir crackme veya malware çözerken, bulduğum ilk `0xcc` veya XOR döngüsüne atlamamam gerektiğini, yazarların "Fake Flag/Rabbit Hole" bırakabileceğini tecrübeyle kavradım.
* Her şey tıkandığında, statik analiz ve Python'un platformdan bağımsız gücünü anladım.
* Kodun içindeki if (param_1 == 2) satırı, programın komut satırından fazladan bir argüman (yani şifreyi) beklediğini, C dilindeki argc == 2 mantığıyla kontrol ediyordu.
---
