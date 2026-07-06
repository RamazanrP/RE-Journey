# [Write-up] Good Girl (Matrix-Byte Operations) ENG & TR

## English Version

### 1. Introduction and Target Analysis

First, an honest confession: I wanted to solve this crackme challenge purely because of its name! :D
In this task, a Linux binary that expects a specific number of arguments from the user and validates them using a background mathematical process was analyzed. Instead of relying on complex cryptographic functions, the author designed a custom "Subset Sum" puzzle using our inputs as coordinates. The ultimate goal is to provide the correct numbers to output the "good girl!" message.

### 2. Static Analysis and the 2D Matrix Illusion

The decompile output indicates that the primary framework of the program relies on a 16-element, one-dimensional (1D) array named `local_68`. However, the core logic is hidden inside the specific formula used to fetch elements from this array:

`local_68[(long)(int)lVar2 + (long)(int)lVar1 * 4]`

The formula `(Column + Row * 4)` is a universal and elegant concept in computer science used to represent a sanal 2D matrix inside a flat, 1D memory space. The author structured this 16-element array as a hidden 4x4 grid. The two arguments provided by the user (Row and Column) are converted from strings to long integers via the `strtol` function, acting as coordinates to extract target values from this dynamic grid.

The structured 4x4 Matrix contains the following values:

* **Row 0:** `11`, `13`, `23`, `-7`
* **Row 1:** `-27`, `107`, `-53`, `41`
* **Row 2:** `67`, `-51`, `253`, `-143`
* **Row 3:** `-119`, `101`, `401`, `-391`

### 3. Argument Processing and Pointer Arithmetic

Another elegant software practice implemented by the author is the method of parsing arguments. Instead of using traditional loop indices (`argv[i]`), the program performs direct pointer arithmetic on memory:

* `param_2 + 8`: Skips the first 8 bytes in a 64-bit architecture (which holds the program name) and points directly to the user inputs.
* `puVar4 + 2`: Moves the pointer forward by 2 units to read inputs in pairs (Row and Column) rather than individually.
* `param_2 + 0x48`: Sets the 72nd byte (`0x48`), which represents the total memory occupied by 9 arguments (1 program name + 4 coordinate pairs), as a strict boundary to safely terminate the loop.

### 4. Victory Condition and Solution

The condition `if (iVar6 == 0)` at the end of the loop defines the rule clearly: We must select exactly 4 numbers from the 4x4 matrix such that their mathematical sum equals exactly **0** (zero).

Upon inspecting the grid, the cleanest combination satisfying this constraint is:
`11 (0,0) + 23 (0,2) + (-7) (0,3) + (-27) (1,0) = 0`

Executing the binary with these coordinates yields the successful exploit:

**Terminal Output:**

```bash
./good-girl 0 0 0 2 0 3 1 0
good girl!

```

### 5. Takeaways

This crackme serves as an excellent demonstration of how a solid validation mechanism can be built without relying on traditional cryptography (XOR, MD5, etc.). Visualizing how flat 1D arrays can be manipulated mathematically into a 2D matrix illusion, along with analyzing argument parsing via 64-bit pointer arithmetic, significantly reinforces core lower-level software engineering paradigms.

---

## Türkçe Sürüm

### 1. Giriş ve Hedef Analizi

Öncelikle bir itirafla başlayayım: Bu crackme dosyasını sadece ismi sebebiyle çözmek istedim :D
Bu görevde, kullanıcısından belirli sayıda argüman bekleyen ve bunları arka planda matematiksel bir işleme tabi tutarak doğrulayan bir Linux binary dosyası incelenmiştir. Programın temel amacı, karmaşık şifreleme algoritmaları kullanmak yerine girdilerimizi bir alt küme toplamı (Subset Sum) bulmacasına dönüştürerek doğru koordinatları bulmamızı sağlamaktır. Hedefimiz, "good girl!" mesajını tetiklemek için istenen sayıları doğru kombinasyonla girmektir.

### 2. Statik Analiz ve 2D Matris İllüzyonu

Decompile işlemi sonucunda, programın temel iskeletinin `local_68` adında 16 elemanlı tek boyutlu (1D) bir diziye dayandığı görülmüştür. Ancak asıl veri akışı, programın bu diziden eleman okurken kullandığı şu formülde gizlidir:

`local_68[(long)(int)lVar2 + (long)(int)lVar1 * 4]`

Bu formül (`Sütun + Satır * 4`), bilgisayar bilimlerinde **tek boyutlu bir belleği, sanal bir 2 boyutlu (2D) matrismiş gibi kullanmanın** çok zarif ve evrensel bir yöntemidir. Yazar, 16 elemanlı bu diziyi aslında 4x4 boyutunda gizli bir grid olarak tasarlamıştır. Verilen iki argüman (Satır ve Sütun), `strtol` fonksiyonu ile metinden sayıya dönüştürülmekte ve bu sanal matristeki hedef sayıyı çekmek için birer koordinat olarak kullanılmaktadır.

Oluşturulan 4x4 Matrisin değerleri şöyledir:

* **Satır 0:** `11`, `13`, `23`, `-7`
* **Satır 1:** `-27`, `107`, `-53`, `41`
* **Satır 2:** `67`, `-51`, `253`, `-143`
* **Satır 3:** `-119`, `101`, `401`, `-391`

### 3. Argüman İşleme ve Pointer Aritmetiği

Yazarın kodlama pratiğindeki bir diğer şık detay, argümanları ayrıştırma yöntemidir. Geleneksel döngü indeksleri (`argv[i]`) yerine, bellek üzerinde doğrudan Pointer (İşaretçi) matematiği yapılmıştır:

* `param_2 + 8`: 64-bit mimaride ilk 8 byte olan programın kendi adını atlayıp doğrudan kullanıcı girdilerine ulaşır.
* `puVar4 + 2`: Girdileri tek tek değil, "Satır" ve "Sütun" çiftleri halinde okuyabilmek için işaretçiyi 2 birim ileri taşır.
* `param_2 + 0x48`: 9 argümanın (1 program adı + 4 satır-sütun çifti) bellekte kapladığı toplam alan olan 72. byte'ı (`0x48`) bir bariyer olarak belirleyip döngünün güvenli bir şekilde sonlanmasını sağlar.

### 4. Zafer Şartı ve Çözüm

Kodun sonundaki `if (iVar6 == 0)` şartı, kuralları net bir şekilde ortaya koymaktadır: 4x4 matristen öyle 4 adet sayı seçilmelidir ki, bu sayıların toplamı tam olarak **0** (sıfır) etsin.

Matris incelendiğinde, bu şartı sağlayan en temiz kombinasyon şu şekilde belirlenmiştir:
`11 (0,0) + 23 (0,2) + (-7) (0,3) + (-27) (1,0) = 0`

Bu koordinatları sırasıyla argüman olarak programa vererek nihai sonuca ulaşılmıştır:

**Terminal Çıktısı:**

```bash
./good-girl 0 0 0 2 0 3 1 0
good girl!

```

### 5. Çıkarımlar

Bu crackme; karmaşık kriptografik fonksiyonlar (XOR, MD5 vb.) olmadan da bir doğrulama mekanizmasının nasıl kurgulanabileceğini gösteren şık bir örnektir. Özellikle tek boyutlu dizilerin (1D Arrays) bellek üzerinde matematiksel bir illüzyonla nasıl 2D matrislere dönüştürüldüğünü uygulamalı olarak görmek ve 64-bit mimaride argümanların işaretçi matematiğiyle nasıl tarandığını analiz etmek, C dilinin hafıza yönetimi konusundaki vizyonu önemli ölçüde pekiştirmiştir.
