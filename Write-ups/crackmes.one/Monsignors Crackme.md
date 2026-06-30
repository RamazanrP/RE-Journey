# Monsignors Crackme

## Introduction and Objective

Our objective in this task was to find the correct password that the executable file at hand expected from me. However, this time, rather than solving the encryption algorithm, we learned how to evade the traps hidden among the codes by the compilers and reach the actual logic of the program.

## Step 1: Loading into Ghidra and Manual Analysis

We imported the file into Ghidra, opened the CodeBrowser window, and had it analyzed.

## The Compiler Boilerplate Trap!

While navigating through the codes, I came across functions containing complex loops named `__do_global_ctors` and `__main`. At first, I thought the encryption logic of the program lay here.

However, as a result of my investigations, I learned a reverse engineering lesson: These were not the codes written by the programmer, but rather the startup codes automatically added by the compiler (GCC/MinGW) to prepare the memory and global variables before the program runs. This wasn't our actual target!

## Step 2: XREF

Instead of wasting time in the compiler code, we used the `__main` function as a signpost. Using Ghidra's **XREF (Cross-References)** feature, we searched for where the `__main` function was called.

We found the glowing **`main:140001530(c)`** reference in the list and by double-clicking on it, we teleported to the actual heart of the program, that is, the real `main` function written by the programmer.

## Step 3: Discovery of the Vulnerability

When we reached the real `main` function, the code was extremely clean and simple. The program was asking us for a password (`local_48`) using `scanf`. And then it committed one of the greatest deadly sins in cybersecurity:

```c
iVar1 = strcmp(local_48, "secret");

```

Instead of encrypting or hashing the word we entered, the program was comparing it directly with the word **`"secret"`** embedded as plaintext inside the code. We had found the password!

## Step 4: The Operating System Barrier and the Victory of Static Analysis

After finding the password, I wanted to test the program by running it with the `./` command in the Kali Linux terminal, but I received an error. Because phrases like `__cdecl` and `CRTStartup` that we saw during decompilation indicated that this file was actually an `.exe` file compiled for Windows. Linux couldn't run this natively.

**However, the real victory was here:** We didn't even need to run the program! Thanks to static analysis and reverse engineering, we successfully infiltrated even a file belonging to a different operating system and extracted the password without executing a single line of code.

---

## What Did It Teach Me?

This task gave me some important skills in terms of thinking like a reverse engineer:

1. **Evading the Compiler Trap (Boilerplate Detection):** I learned that not every complex function I see is the actual algorithm, and that compilers (like `__do_global_ctors`, `__main`, etc.) generate automatic codes to initialize the program. I experienced not getting bogged down in unnecessary code.
2. **The Power of XREF:** I realized that when I get lost inside the program, using XREF to find where a function is called from is the most effective shortcut that takes me directly to the actual target (the real `main` function).
3. **The Danger of Hardcoded Passwords:** I saw with my own eyes what a massive security vulnerability it creates to write critical data or passwords (`"secret"`) as plaintext into the source code (checking it with `strcmp`).
4. **No Need to Execute:** The fact that the program was in Windows `.exe` format did not stop me from hacking it in Kali Linux. I understood the platform-independent power of static analysis by experiencing it firsthand.

# Monsignors Crakme

##  Giriş ve Hedef

Bu görevdeki amacımız, elimizdeki çalıştırılabilir dosyanın (executable) benden beklediği doğru şifreyi bulmaktı. Ancak bu sefer şifreleme algoritmasını çözmekten ziyade, derleyicilerin (compiler) kodların arasına sakladığı tuzaklardan kaçmayı ve programın asıl mantığına ulaşmayı öğrendik.

##  Adım 1: Ghidra'ya Yükleme ve Manuel Analiz

Dosyayı Ghidra'ya import edip CodeBrowser penceresini açtık, analiz ettirdik.

##  Compiler Boilerplate Tuzağı!

Kodların arasında gezinirken `__do_global_ctors` ve `__main` adında karmaşık döngüler barındıran fonksiyonlara denk geldim. İlk başta programın şifreleme mantığının burada yattığını düşündüm.

Ancak incelemelerim sonucunda bir tersine mühendislik dersi aldım: Bunlar programcının yazdığı kodlar değil, derleyicinin (GCC/MinGW) program çalışmadan önce belleği ve global değişkenleri hazırlamak için otomatik olarak eklediği başlatma (startup) kodlarıydı. Asıl hedefimiz burası değilmiş!

##  Adım 2: XREF

Derleyici kodunda zaman kaybetmek yerine `__main` fonksiyonunu bir yol tabelası olarak kullandık. Ghidra'nın **XREF (Cross-References)** özelliğini kullanarak `__main` fonksiyonunun çağrıldığı yeri aradık.

Listede parlayan **`main:140001530(c)`** referansını bulduk ve üzerine çift tıklayarak programın asıl kalbine, yani programcının yazdığı gerçek `main` fonksiyonuna ışınlandık.

##  Adım 3: Zafiyetin Keşfi

Gerçek `main` fonksiyonuna ulaştığımızda kod son derece temiz ve basitti. Program `scanf` ile bizden bir parola (`local_48`) istiyordu. Ve ardından siber güvenlikteki en büyük ölümcül günahlardan birini yapıyordu:

```c
iVar1 = strcmp(local_48, "secret");

```

Program, bizim girdiğimiz kelimeyi şifrelemek veya hashlemek yerine, doğrudan kodun içine plaintext olarak gömülmüş **`"secret"`** kelimesiyle karşılaştırıyordu. Şifreyi bulmuştuk!

##  Adım 4: İşletim Sistemi Engeli ve Statik Analizin Zaferi

Şifreyi bulduktan sonra Kali Linux terminalinde `./` komutuyla programı çalıştırıp denemek istedim ancak hata aldım. Çünkü decompile sırasında gördüğümüz `__cdecl` ve `CRTStartup` gibi ibareler, bu dosyanın aslında Windows için derlenmiş bir `.exe` dosyası olduğunu gösteriyordu. Linux bunu doğal yollarla çalıştıramazdı.

**Ancak asıl zafer buradaydı:** Programı çalıştırmamıza gerek bile kalmamıştı! Statik analiz ve tersine mühendislik sayesinde, farklı bir işletim sistemine ait bir dosyanın bile içine sızıp, tek satır kod çalıştırmadan şifreyi başarıyla çekip almıştık.

---

##  Bana Neler Kattı?

Bu görev, bir tersine mühendis gibi düşünmek açısından bana bazı önemli yetenekler kazandırdı:

1. **Derleyici Tuzağından Kaçmak (Boilerplate Tespiti):** Her gördüğüm karmaşık fonksiyonun asıl algoritma olmadığını, derleyicilerin (`__do_global_ctors`, `__main` vb.) programı başlatmak için otomatik kodlar ürettiğini öğrendim. Gereksiz kodlarda boğulmamayı tecrübe ettim.
2. **XREF Gücü:** Programın içinde kaybolduğumda, bir fonksiyonun nerelerden çağrıldığını bulmak için XREF kullanmanın beni doğrudan asıl hedefe (gerçek `main` fonksiyonuna) ulaştıran en etkili kısayol olduğunu kavradım.
3. **Hardcoded Şifrelerin Tehlikesi:** Kritik verilerin veya şifrelerin (`"secret"`) kaynak kodun içine düz metin olarak yazılmasının (`strcmp` ile kontrol edilmesi) ne kadar büyük bir güvenlik açığı yarattığını kendi gözlerimle gördüm.
4. **Çalıştırmaya Gerek Yok:** Programın Windows `.exe` formatında olması, benim onu Kali Linux'ta hacklememe engel olmadı. Statik analizin platformdan bağımsız gücünü yaşayarak anladım.

---
