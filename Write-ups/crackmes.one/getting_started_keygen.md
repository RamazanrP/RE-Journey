# Getting Started Keygen Static Analysis (TR & ENG)

##  Introduction & Objective

In this challenge, we are given a compiled Linux executable. When executed, it prompts the user for two inputs: a string (with no spaces) and a corresponding "correct number". Without access to the source code, the objective is to use static analysis to reverse-engineer the hidden algorithm, understand how the target number is calculated, and write a custom keygen to bypass the security check.

##  Step 1: Execution and Overcoming Permission Issues

Initially, the downloaded file lacked execution privileges. In Linux, we must explicitly grant executable permissions before interacting with the binary.

```bash
$ chmod +x getting_started_keygen
$ ./getting_started_keygen
Enter a string of characters (no spaces): test
Enter correct number (no spaces): 123
Bro, what are you trying to do?

```

Inputting random values immediately terminates the program. It was time to load the binary into **Ghidra** to understand its internal logic.

##  Step 2: Static Analysis in Ghidra

After decompiling the `main` function in Ghidra, we located the success message: `"OMG! You did it! :3"`. To reach this branch, the program requires us to pass a specific condition:

```c
if (local_7c == iVar1) {
    std::operator<<((ostream *)std::cout, "OMG! You did it! :3");
}

```

* `local_7c`: The integer number we input in the terminal.
* `iVar1`: A calculated value returned by a function named `FUN_001014b0`.

The program takes our initial string, processes it through `FUN_001014b0`, and expects us to input the exact numerical result of that process.

##  Step 3: Deconstructing the Algorithm

Diving into `FUN_001014b0`, we discovered a `do-while` loop handling the cryptographic logic. Two variables play critical roles here:

1. **`lVar3` (The Index Counter):** It increments by 1 in each loop iteration, serving as a pointer to fetch the next character from our string and the next byte from the secret key.
2. **`iVar4` (The Accumulator):** This variable starts at 0 and stores the rolling sum of our calculations. It is the final value returned to the main function.

The core encryption logic is a simple XOR operation:

```c
iVar4 = iVar4 + ((int)*pcVar1 ^ *puVar2);

```

The program takes the ASCII value of our character (`*pcVar1`), XORs (`^`) it with a static byte from memory (`*puVar2`), and adds the result to the accumulator (`iVar4`).

##  Step 4: Extracting the Secret Key from Memory

To reproduce the math, we needed the secret bytes stored at the pointer `&DAT_00104020`. Switching to Ghidra's **Listing (Assembly) View** and jumping to `DAT_00104020`, we observed how the pointer iterates in 4-byte chunks.

By reading the memory addresses, we extracted the 5-byte XOR key:

* `00104020`: **`0x04`**
* `00104024`: **`0x4f`**
* `00104028`: **`0x81`**
* `0010402c`: **`0xab`**
* `00104030`: **`0xfe`**

##  Step 5: The Math & Writing the Keygen

A crucial realization here is that **there is no single static password**. The required number is dynamically generated based on the string we provide.

Let's say we choose the 5-letter string **`cyber`**. Here is the manual, under-the-hood math the CPU performs:

* `c` (99) ^ `0x04` = **103**
* `y` (121) ^ `0x4f` = **54**
* `b` (98) ^ `0x81` = **227**
* `e` (101) ^ `0xab` = **206**
* `r` (114) ^ `0xfe` = **140**
* **Total Accumulator (`iVar4`):** 103 + 54 + 227 + 206 + 140 = **730**

To automate this, we wrote a Python one-liner to act as our Keygen. It calculates the correct integer for any 5-character string we choose.

```bash
$ python3 -c 's="cyber"; k=[0x04, 0x4f, 0x81, 0xab, 0xfe]; print(f"String: {s} | Number: {sum(ord(s[i])^k[i] for i in range(5))}")'

String: cyber | Number: 730

```

##  Step 6: Exploitation & Flag

Armed with a valid combination (`cyber` and `730`), we executed the program one last time to bypass the check.

```bash
$ ./getting_started_keygen
Enter a string of characters (no spaces): cyber
Enter correct number (no spaces): 730
OMG! You did it! :3

```

Challenge successfully reverse-engineered and cracked!
# Key Takeaways (What I Learned)
This challenge was a great introduction to static analysis and algorithmic reverse engineering. Here are my main takeaways:

1. C++ String Structures in Decompilers: I learned how decompilers represent high-level C++ std::string objects. Discovering that param_1[1] (the second element in the memory structure) acted as the string's length property was a valuable insight into memory layouts.

2. Memory Navigation & Pointer Arithmetic: I practiced navigating Ghidra's Assembly/Listing view to track down hardcoded data (DAT_00104020). I saw firsthand how a pointer incrementing in a loop correlates to reading sequential bytes directly from the binary's memory.

3. The "Keygen" Mindset: Perhaps the biggest realization was the paradigm shift from finding "the" password to understanding the algorithm. I learned that cryptographic checks can have infinite valid input pairs. You don't always have to search for a static password; sometimes you just reverse the math and generate your own valid key.
##  Giriş ve Hedef

Bu görevde, bizden boşluksuz bir string ve doğru sayıyı  girmemizi isteyen bir Linux çalıştırılabilir dosyası (executable) ile karşı karşıyaydık. Amacımız, kaynak koduna sahip olmadığımız bu programın arka planda sayıyı nasıl hesapladığını statik analiz yöntemleriyle bulmak ve doğru kombinasyonu girerek başarı mesajına ulaşmaktı.

##  Adım 1: İlk İnceleme

İndirdiğimiz dosya başlangıçta çalıştırılabilir (executable) iznine sahip değildi. Güvenlik mekanizmasını aşmak ve dosyayı çalıştırabilmek için öncelikle terminalde şu yetki komutunu kullandık:

* `chmod +x getting_started_keygen`

Dosyayı `./getting_started_keygen` komutuyla çalıştırdığımızda, program bizden sırasıyla iki şey istedi:

1. `Enter a string of characters (no spaces):`
2. `Enter correct number (no spaces):`

Yanlış değerler girdiğimizde program kapanıyordu. Şifreleme mantığını çözmek için dosyayı Ghidra'ya yüklemeye karar verdik.

##  Adım 2: Ghidra ile Statik Analiz (Decompile)

Ghidra'da programın ana fonksiyonunu (entry) decompile ettik. Başarı mesajı olan `"OMG! You did it! :3"` satırını bulduk. Bu mesajın ekrana gelmesi için kodda şu kritik kontrolün geçilmesi gerekiyordu:

`if (local_7c == iVar1)`

Buradaki `local_7c` bizim konsoldan girdiğimiz sayıydı. `iVar1` ise, ilk adımda girdiğimiz kelimenin `FUN_001014b0` isimli bir fonksiyondan geçtikten sonra aldığı sonuçtu. Demek ki şifreleme algoritması bu fonksiyonun içinde gizliydi.

##  Adım 3: Şifreleme Algoritmasının Kalbine İnme

`FUN_001014b0` fonksiyonunun içine girdiğimizde, programın girdiğimiz kelimenin harflerini tek tek işleyen bir `do-while` döngüsü kullandığını fark ettik.

Algoritmanın iki temel kuralı vardı:

1. Girdiğimiz kelimenin uzunluğu koda göre kısıtlanmıştı (Tam 5 karakterlik bir kelime hedefleniyordu).
2. Döngü içinde şu matematiksel işlem yapılıyordu: Girdiğimiz kelimenin her bir harfinin ASCII değeri, bellekte sabit olarak duran bir adres (`DAT_00104020`) ile **XOR** (`^`) işlemine sokuluyor ve çıkan sonuçlar birbiriyle toplanıyordu.

##  Adım 4: Bellekten Gizli Anahtarı Çıkarmak

Algoritmayı çözmüştük ama o sabit adresteki byte'ları (keygen) bulmamız gerekiyordu. Ghidra'da Listing görünümüne geçip `DAT_00104020` adresine zıpladık.

Burada programın XOR işlemi için kullandığı 5 baytlık gizli anahtarı tespit ettik:
`0x04, 0x4f, 0x81, 0xab, 0xfe`

##  Adım 5: Kendi Keygen'imizi Yazmak (Exploitation)

Algoritmayı ve anahtarı bildiğimize göre, 5 harfli herhangi bir kelimenin programda hangi sayıyı üreteceğini hesaplayabilirdik. Hedef kelime olarak "cyber"ı seçtik.

Python kullanarak bu kelimenin harflerini bellekten kopardığımız anahtarla XOR'layıp toplayan tek satırlık bir script yazdık:
```bash
$ python3 -c 's="cyber"; k=[0x04, 0x4f, 0x81, 0xab, 0xfe]; print(f"String: {s} | Number: {sum(ord(s[i])^k[i] for i in range(5))}")'

```
Python scripti, "cyber" kelimesi için gereken doğru sayının **730** olduğunu hesapladı.

##  Adım 6: Final

Terminale dönüp programı son kez çalıştırdık:

* Kelime sorusuna: `cyber`
* Sayı sorusuna: `730`

Cevaplarını verdik. Arka plandaki matematiksel eşleşme tam olarak sağlandığı için programın koruması aşıldı ve ekranda o beklenen tebrik mesajı belirdi:
**`OMG! You did it! :3`**
# Bana Neler Kattı? (Ana Çıkarımlar)
Bu görev, statik analiz ve algoritmik tersine mühendislik dünyasına harika bir giriş oldu. Bu süreçte şunları öğrendim:

1. Decompiler'da Bellek Yapılarını Okumak: C++ std::string nesnelerinin decompile edilmiş kodda bellekte nasıl temsil edildiğini gördüm. Özellikle param_1[1] ifadesinin aslında string'in "uzunluğunu (length)" kontrol ettiğini öğrenmek, yüksek seviyeli dillerin arka planda nasıl çalıştığını anlamamı sağladı.

2. Bellekte Gezinme ve Pointer Mantığı: Ghidra'nın Assembly (Listing) görünümünde gezinmeyi ve programa sabit olarak gömülmüş gizli verileri (DAT_00104020) bulmayı pratik ettim. C dilindeki bir pointer'ın (göstericinin) döngü içinde artmasının, bellekteki baytların sırayla okunması anlamına geldiğini yaşayarak (ve o 5 adresi tek tek bularak!) gördüm.

3. "Keygen" Felsefesi ve Dinamik Şifreler: En büyük aydınlanmam, programı geçmek için "tek ve kesin" bir şifre olmadığını fark etmek oldu. Şifreleme algoritmalarının sonsuz sayıda geçerli kombinasyon kabul edebileceğini gördüm. Statik bir şifre aramak yerine, arka plandaki matematiği tersine çevirip kendi geçerli anahtarımı (keygen) nasıl üretebileceğimi öğrendim.
---
