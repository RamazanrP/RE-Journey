# [Write-up] Selfkey XOR Solution via CyberChef (ENG & TR)  

## 1. Introduction and Target Analysis

In this study, a Linux ELF binary file that expects a password (Access Code) from the user and dynamically verifies it at runtime was examined. It was determined that the program uses a custom-designed "XOR Checksum" algorithm instead of standard hash functions (MD5, SHA, etc.) to resist brute-force attacks. The objective is to decipher the underlying mathematics the program executes in the background and obtain the valid password.

---

## 2. Static Analysis

In the static analysis performed via Ghidra, it was observed that the main mechanism verifying the input is divided into two functions (`FUN_001010b0` and `FUN_00101220`):

1. **Length and Memory Constraint:** The program allocates exactly 25 bytes of space in memory using `malloc(0x1a)`. This indicates that the valid password must strictly be 25 characters long.
2. **Checksum Generation (Single-Byte Vulnerability):** The program subjects all characters of the input entered from the terminal to a sequential XOR (`^`) operation with one another. Regardless of how long or complex the input is, the result is a **single-byte (between 0-255)** cumulative key.
3. **Final Comparison (`strcmp`):** This generated single-byte key is used to decrypt a hardcoded 25-byte encrypted hex array in memory. Then, `strcmp` compares the original text entered by the user from the terminal with the internally decrypted text. If a match is achieved, the vault opens.

---

## 3. Mathematical Collision

The system's biggest trap lies precisely within the `strcmp` function. The 25-byte secret array in memory is designed in such a way that its own cumulative XOR sum is `0x00`.

Mathematically, this means: When an input of 25 characters in length with any checksum value (0-255) is fed into the system, the program decrypts the internal text using that checksum key, and **the checksum value of the decrypted text automatically remains the same.** In other words, there is not just one correct password in the program; theoretically, there are exactly 256 different passwords (though most contain non-printable, meaningless ASCII characters) that can unlock the vault.

---

## 4. CyberChef Operation

Once it was understood that the key point of the algorithm was a weak 1-byte key space, instead of writing a custom script, the **CyberChef** tool developed by GCHQ was used to speed up the process.

**Step 1: Data Extraction**
The 25-byte encrypted hex array was extracted from Ghidra's memory analysis and placed into the "Input" section of CyberChef:
`79 47 6e 7d 6a 61 47 6b 6c 6a 77 76 7f 47 68 79 6b 6b 6f 77 6a 7c 2d 28 2f`

**Step 2: Recipe Setup**
The following operations were chained sequentially on CyberChef:

* **`From Hex`:** Used to convert the raw input into a byte array.
* **`XOR Brute Force`:** The Key Length was set to `1`, ensuring all possibilities between 00-FF were scanned within seconds.
* **`Regular Expression (Regex)`:** The condition `[A-Za-z0-9_]{15,}` was added to filter out meaningless (non-printable) characters that would break the terminal from among the 256 different results.

**Step 3: Conclusion**
After applying the Regex filter, only a single clean and readable line remained out of the 256 possibilities:
`Key = 38: a_very_strong_password507`

When the `./selfkey a_very_strong_password507` command was executed via the terminal, the verification was successful, and the analysis was completed upon receiving the `You cracked the password` message from the program.

---

## 5. Takeaways and Lessons Learned

* **Importance of Cryptographic Key Space:** If input complexity is not preserved in an encryption mechanism and entropy is reduced to a single byte (8-bit) via methods like checksums, the algorithm succumbs to brute-force attacks within seconds.
* **Tool Selection in Reverse Engineering:** In moments where operational speed is critical, manipulating data flows with visual processing engines like CyberChef provides a significant time advantage for the analyst.

## 1. Giriş ve Hedef Analizi

Bu çalışmada, kullanıcıdan bir parola (Access Code) bekleyen ve bunu runtime'da dinamik olarak doğrulayan bir Linux ELF binary dosyası incelenmiştir. Programın brute-force saldırılarına karşı koymak için standart hash fonksiyonları (MD5, SHA vb.) yerine, özel olarak tasarlanmış bir "XOR Checksum" algoritması kullandığı tespit edilmiştir. Hedef, programın arka planda işlettiği bu matematiği deşifre edip geçerli parolayı elde etmektir.

## 2. Statik Analiz

Ghidra üzerinden gerçekleştirilen statik analizde, girdiyi doğrulayan ana mekanizmanın iki fonksiyona (`FUN_001010b0` ve `FUN_00101220`) bölündüğü görülmüştür:

1. **Uzunluk ve Bellek Kısıtlaması:** Program `malloc(0x1a)` ile bellekte tam olarak 25 byte'lık bir alan ayırmaktadır. Bu durum, geçerli parolanın kesinlikle 25 karakter uzunluğunda olması gerektiğini göstermektedir.
2. **Checksum Üretimi (Tek Byte'lık Zafiyet):** Program, terminalden girilen girdinin tüm karakterlerini birbiriyle ardışık olarak XOR (`^`) işlemine sokmaktadır. Girdi ne kadar uzun veya karmaşık olursa olsun, sonuç olarak ortaya **tek byte'lık (0-255 arası)** bir kümülatif anahtar çıkmaktadır.
3. **Nihai Karşılaştırma (`strcmp`):** Üretilen bu tek byte'lık anahtar, hafızaya sabitlenmiş 25 byte'lık şifreli bir hex dizisini çözmek için kullanılır. Ardından `strcmp`, kullanıcının terminalden girdiği orijinal metin ile, programın içeride çözdüğü metni karşılaştırır. Eşleşme sağlanırsa kasa açılır.

## 3. Matematiksel Çarpışma (Collision)

Sistemin en büyük tuzağı tam olarak `strcmp` fonksiyonunda yatmaktadır. Hafızadaki 25 byte'lık gizli dizi öyle bir kurgulanmıştır ki, kendi kümülatif XOR toplamı `0x00`'dır.

Matematiksel olarak bunun anlamı şudur: Sisteme 25 karakter uzunluğunda, herhangi bir checksum değerine sahip (0-255) bir girdi verildiğinde, program o checksum anahtarıyla içerideki metni çözer ve **çözülen metnin checksum değeri de otomatik olarak aynı kalır.** Yani programda tek bir doğru şifre yoktur; teorik olarak kasanın kilidini açabilecek tam 256 farklı (fakat çoğu terminalde yazılamayan anlamsız ASCII karakterleri içeren) şifre bulunmaktadır.

## 4. CyberChef Operasyonu

Algoritmanın kilit noktasının 1 byte'lık zayıf bir anahtar uzayı olduğu anlaşıldığında, özel bir script yazmak yerine süreci hızlandırmak adına GCHQ tarafından geliştirilen **CyberChef** aracı kullanılmıştır.

**Adım 1: Veri Çıkarımı**
Ghidra'nın bellek analizinden 25 byte'lık şifreli hex dizisi çıkarılarak CyberChef'in "Input" bölümüne yerleştirilmiştir:
`79 47 6e 7d 6a 61 47 6b 6c 6a 77 76 7f 47 68 79 6b 6b 6f 77 6a 7c 2d 28 2f`

**Adım 2: İşlem Zinciri (Recipe) Kurulumu**
CyberChef üzerinde sırasıyla şu işlemler zincirlenmiştir:

* **`From Hex`:** Ham girdiyi byte dizisine çevirmek için kullanıldı.
* **`XOR Brute Force`:** Anahtar uzunluğu (Key Length) `1` olarak ayarlandı ve 00-FF arasındaki tüm ihtimallerin saniyeler içinde taranması sağlandı.
* **`Regular Expression (Regex)`:** Çıkan 256 farklı sonucun içindeki terminali bozacak anlamsız (non-printable) karakterleri filtrelemek için `[A-Za-z0-9_]{15,}` koşulu eklendi.

**Adım 3: Sonuç**
Regex filtresi uygulandıktan sonra, 256 ihtimal arasından geriye yalnızca temiz ve okunabilir tek bir satır kalmıştır:
`Key = 38: a_very_strong_password507`

Terminal üzerinden `./selfkey a_very_strong_password507` komutu çalıştırıldığında doğrulama başarılı olmuş ve programdan `You cracked the password` mesajı alınarak analiz tamamlanmıştır.

## 5. Çıkarımlar ve Alınan Dersler

* **Kriptografik Anahtar Uzayının Önemi:** Bir şifreleme mekanizmasında, girdi karmaşıklığı korunmaz ve checksum gibi yöntemlerle entropi tek bir byte'a (8-bit) düşürülürse, algoritma kaba kuvvet saldırılarına saniyeler içinde yenik düşer.
* **Tersine Mühendislikte Araç Seçimi:** Operasyonel hızın kritik olduğu anlarda, veri akışını CyberChef gibi görsel işleme motorlarıyla manipüle etmek analiste zaman avantajı sağlar.
