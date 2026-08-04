# CrackMe Write-up — argc (Corrected) (ENG & TR)

# 🇬🇧 English

## Overview

At first glance, this crackme appears to be a simple argument comparison challenge.  
However, there is a hidden twist in how the program handles `argc`, which makes the solution less straightforward than expected.

---

## Initial Analysis

From decompilation:

```c
int main(int argc, char **argv)
````

The program performs:

```c
if (argc == 3) {
    if (strcmp(argv[1], argv[2]) == 0) {
        puts(flag);
    }
}
```

This suggests:

→ The program expects exactly 2 user arguments
→ And both must be identical

So a natural attempt would be:

```bash
./argc a a
```

However, this does **not work**.

## Investigating the Issue

Despite providing correct arguments, the program outputs:

```
please try again...
```

This indicates that:

→ `argc == 3` condition is **not satisfied**

## Hidden Behavior in `_start`

Looking at the program entry point:

```c
__libc_start_main(main, argc >> 1, ...)
```

This is the key detail.

→ `argc` is shifted right by 1
→ Meaning: `argc = argc / 2`

## Impact of argc Manipulation

The program checks:

```c
if (argc == 3)
```

But this is after shifting.

So we must solve:

```
real_argc >> 1 = 3
```

Possible values:

| Real argc | After shift |
| --------- | ----------- |
| 6         | 3           |
| 7         | 3           |

## Translating to User Input

Remember:

→ `argc = number of arguments + 1`

So:

* argc = 6 → 5 arguments
* argc = 7 → 6 arguments

## Final Condition

To pass the program:

1. Provide enough arguments so that:

   ```
   argc >> 1 == 3
   ```

2. Ensure:

   ```
   argv[1] == argv[2]
   ```

## Solution

Example:

```bash
./argc A A B C D
```

Here:

* Total argc = 6 → (6 >> 1) = 3 
* `argv[1] == argv[2]` → A == A 


## Result

```
correct!
```

## Key Takeaways

* Program behavior can be altered before reaching `main`
* `_start` may manipulate arguments
* Always verify assumptions about `argc`
* Simple logic can hide subtle tricks

## Final Note

This challenge is not about string comparison alone, but about:

→ understanding program initialization flow

---

# 🇹🇷 Türkçe

## Genel Bakış

İlk bakışta bu crackme basit bir argüman karşılaştırması gibi görünüyor.
Ancak programın `argc` değerini değiştirmesi nedeniyle çözüm beklenenden daha farklıymış.

---

## İlk Analiz

Program şu kontrolü yapıyor:

```c
if (argc == 3)
```

ve ardından:

```c
strcmp(argv[1], argv[2])
```

Buradan şu çıkarım yapılır:

→ 2 argüman girilmeli
→ bu iki argüman aynı olmalı

Ama:

```bash
./argc a a
```

çalışmadığını fark ettim.

## Sorunun Kaynağı

Program doğru input verilmesine rağmen hata verir.

Bu da şunu gösterir:

→ `argc == 3` şartı sağlanmıyor

## `_start` İçindeki Trick

Program başlangıcında:

```c
__libc_start_main(main, argc >> 1, ...)
```

bulunur.

Yani:

* `argc` sağa kaydırılıyor → `argc = argc / 2`

## Etkisi

Program aslında şunu kontrol ediyor:

```
(argc / 2) == 3
```

Yani gerçek `argc` 6 veya 7 olmalı

## Kullanıcı Input’una Çeviri

`argc = arg sayısı + 1`

Buna göre:

* argc = 6 → 5 argüman
* argc = 7 → 6 argüman

## Doğru Koşul

Programı geçmek için:

1. Yeterli sayıda argüman verilmeli
2. İlk iki argüman **aynı** olmalı

## Çözüm

```bash
./argc A A B C D
```

* argc = 6 → 6 >> 1 = 3 => Kabul edilir
* argv[1] == argv[2] => Kabul edilir

---

## Sonuç

```
correct!
```

## Öğrenilenler

* `main` öncesi davranış önemli olabilir
* `_start` fonksiyonu göz ardı edilmemeli
* `argc` her zaman göründüğü gibi değildir

## Son Not

Bu challenge aslında şunu öğretiyor:

→ sadece kodu değil, programın nasıl başlatıldığını da analiz et
