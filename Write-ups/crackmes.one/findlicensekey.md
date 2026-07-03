# [Write-up] FindLicenseKey Eng & Tr

## 1. Introduction and Target Analysis

The C code I encountered in this challenge, unlike the previous vulnerable programs, was a "License Validation" system, and its author had explicitly forbidden padding. The program expected an external argument (username) upon execution, generated a specific license key for this name, and compared the key I entered externally with the one it generated. My objective was not to brute-force the system, but to examine the program's other functions to reverse-engineer this encryption algorithm and write my own "Keygen" script.

## 2. Static Analysis

When I first examined the code via Ghidra, I encountered a large number of seemingly confusing numbers and memory allocations at first glance. Progressing step by step, I mapped out that these numbers actually formed the skeleton of the program as follows:

* **`local_118` (264 Byte):** The buffer where the program stored the *real and correct* license key generated specifically for my name in the background.
* **`local_218` (256 Byte):** The memory space where the test key I entered via the terminal keyboard was saved.
* **`0x18` (Number 24):** The limit value in the `for` loop of the encryption algorithm. This indicated that the program generated a password exactly 24 characters long (and thus required a username of exactly 24 characters to avoid drifting into garbage data in memory).
* **`0x3e` (Number 62):** The length of the custom alphabet the program used as an encryption pool. This number was used for the mathematical modulo (mod 62) operation in the algorithm.

## 3. Challenges Encountered: Why I Didn't Choose to Exploit (Pwn)

Based on my previous pwn experiences, I could have considered sending a much larger payload into the 256-byte `local_218` space to execute a Buffer Overflow and take control of the system. However, the author had designed the program to be secure against these attacks:

1. **Secure Input Control (`%255s`):** When prompting me for the license key, the program used the `__isoc23_scanf("%255s", local_218);` function. The `%255s` format specifier here ensured that no matter how long the text I typed into the terminal was, it only read the first 255 characters, effectively preventing a buffer overflow at the software level.
2. **Stack Protection (`__stack_chk_fail`):** If I somehow managed to exceed the limit, the program would detect this and safely terminate itself without executing malicious code.

## 4. Reverse Engineering the Encryption Algorithm

Upon entering the program's main encryption engine, I discovered that instead of standard cryptography, a custom alphabet manipulation was being performed. The algorithm operated on the following logic:

* It took the ASCII numerical value of each letter of the username I entered.
* It added this value to the current step number (`i`) of the loop.
* It took the modulo 62 of the resulting sum and used this number as an index to select the corresponding letter from the 62-character custom alphabet embedded in the program.

## 5. Solution: Writing My Own Keygen Script

```python
user = "RegisteredLicenseUser123" # We learned that it must be exactly 24 characters long!
abc = "QAZPLWSXOKMEYDCIJNRFVUHBTGqpalzmwoeirutyskdjfhgxncbv1750284369"
# Take the ASCII value of the character (ord) and add the loop step (i)
# Find the index in the alphabet by taking the modulo 62 (0x3e) of the sum
key = "".join(abc[(i + ord(c)) % 62] for i, c in enumerate(user))

print(key)

```

I copied the valid key I obtained when I ran this code. After launching the main program with the `./findlicensekey RegisteredLicenseUser123` argument, I pasted this key where prompted and saw the `Key validated` message on the screen.

## 6. What Did It Teach Me?

* **The `%255s` Reality:** While looking for security vulnerabilities, I practically saw at the code level how even generally known dangerous functions like `scanf` become immune to Buffer Overflow attacks by being restricted with simple format specifiers like `%255s`.
* **Getting Lost in Numbers and Finding the Logic:** Initially, the numerous size and limit values I encountered, such as `256`, `264`, `0x18`, and `0x3e`, confused me quite a bit. However, as the static analysis deepened, I learned to map out that these values represented memory boundaries, loop conditions, and alphabet indices. This analytical process taught me to stay calm and take notes instead of blindly diving into the code.

## 1. Giriş ve Hedef Analizi

Bu görevde karşıma çıkan C kodu, daha önceki zafiyetli programların aksine bir "Lisans Anahtarı Doğrulama" (License Validation) sistemiydi ve yazarı açıkça paddingi yasaklamıştı. Program, çalıştırılırken dışarıdan bir argüman (kullanıcı adı) bekliyor, bu isme özel bir lisans anahtarı üretiyor ve benim dışarıdan girdiğim anahtarla kendi ürettiğini karşılaştırıyordu. Amacım, sistemi kaba kuvvetle kırmak yerine, programın diğer fonksiyonlarına bakıp bu şifreleme algoritmasını çözmek ve kendi "Keygen" scriptimi yazmaktı.

## 2. Statik Analiz

Ghidra üzerinden kodu ilk incelediğimde, ilk bakışta kafa karıştırıcı duran bol miktarda sayı ve hafıza alanıyla karşılaştım. Adım adım ilerleyerek bu sayıların aslında programın iskeletini oluşturduğunu şöyle haritalandırdım:

* **`local_118` (264 Byte):** Programın arka planda benim ismime özel olarak ürettiği *gerçek ve doğru* lisans anahtarını sakladığı tampon buffer.
* **`local_218` (256 Byte):** Terminalden klavyeyle deneme amaçlı girdiğim anahtarın kaydedildiği alan.
* **`0x18` (24 Sayısı):** Şifreleme algoritmasının `for` döngüsündeki sınır değeri. Bu, programın tam olarak 24 karakterlik bir şifre ürettiğini (ve dolayısıyla hafızada çöp verilere kaymamak için tam 24 karakterlik bir kullanıcı adına ihtiyaç duyduğunu) gösteriyordu.
* **`0x3e` (62 Sayısı):** Programın şifreleme havuzu olarak kullandığı özel alfabenin uzunluğu. Bu sayı, algoritmadaki matematiksel mod (mod 62) işlemi için kullanılıyordu.

## 3. Karşılaşılan Engeller: Neden Exploit (Pwn) Tercih Etmedim?

Önceki pwn tecrübelerimden yola çıkarak 256 byte'lık `local_218` alanına çok daha büyük bir veri gönderip Buffer Overflow yapmayı ve sistemi kontrol etmeyi düşünebilirdim. Ancak yazar, programı bu saldırılara karşı güvenli tasarlamıştı:

1. **Güvenli Girdi Kontrolü (`%255s`):** Program benden lisans anahtarını isterken `__isoc23_scanf("%255s", local_218);` fonksiyonunu kullanmıştı. Buradaki `%255s` format belirleyicisi, ben terminale ne kadar uzun bir metin yazarsam yazayım, sadece ilk 255 karakteri okuyarak hafıza taşmasını yazılımsal olarak önlüyordu.
2. **Yığın Koruması (`__stack_chk_fail`):** Olur da bir şekilde sınırı aşarsam, program bunu fark edip zararlı kod çalıştırmadan kendini güvenli bir şekilde kapatıyordu.

## 4. Şifreleme Algoritmasının Çözülmesi

Programın asıl şifreleme motoruna girdiğimde, standart bir kriptografi yerine özel bir alfabe manipülasyonu yapıldığını tespit ettim. Algoritma şu mantıkla çalışıyordu:

* Girdiğim kullanıcı adının her bir harfinin ASCII sayısal değerini alıyordu.
* Bu değeri, döngünün o anki adım numarasıyla (`i`) topluyordu.
* Çıkan sonucu 62'ye före modunu alıp bu sayıyı, programın içine gömülü 62 karakterlik özel alfabedeki ilgili harfi seçmek için indeks olarak kullanıyordu.

## 5. Çözüm: Kendi Keygen Scriptini Yazmak

```python
user = "RegisteredLicenseUser123" # Öğrendik ki 24 karakter uzunluğunda olmalı!
abc = "QAZPLWSXOKMEYDCIJNRFVUHBTGqpalzmwoeirutyskdjfhgxncbv1750284369"
# Karakterin ASCII değerini al (ord) ve döngü adımı (i) ile topla
# Toplamın 62'ye (0x3e) göre modunu alarak alfabedeki indeksi bul
key = "".join(abc[(i + ord(c)) % 62] for i, c in enumerate(user))

print(key)

```

Bu kodu çalıştırdığımda elde ettiğim geçerli anahtarı kopyaladım. Asıl programı `./findlicensekey RegisteredLicenseUser123` argümanıyla başlattıktan sonra, benden istenen yere bu anahtarı yapıştırdım ve ekranda `Key validated` mesajını gördüm.

## 6. Bana Neler Kattı?

* **`%255s` Gerçeği:** Güvenlik zafiyeti ararken, `scanf` gibi genel olarak tehlikeli bilinen fonksiyonların bile `%255s` gibi basit format belirleyicilerle sınırlandırılarak Buffer Overflow saldırılarına karşı nasıl bağışıklık kazandığını kod seviyesinde uygulamalı olarak gördüm.
* **Sayılarda Kaybolup Mantığı Bulmak:** Başlangıçta karşıma çıkan `256`, `264`, `0x18`, `0x3e` gibi çok sayıdaki boyut ve sınır değeri kafamı oldukça karıştırdı. Ancak statik analiz derinleştikçe bu değerlerin bellek sınırlarını, döngü koşullarını ve alfabe indekslerini temsil ettiğini haritalandırmayı öğrendim. Bu analitik süreç, koda dalmayıp sakince notlar çıkarmayı öğretti.
