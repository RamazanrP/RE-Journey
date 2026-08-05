# Stonks Crackme Write-up (ENG & TR)

## English

### Overview

The binary `stonks` is a stock market simulator where the goal is to reach a **net worth greater than 2000€**. The program provides three main commands:

* `buy [count]` → purchase shares
* `sell [count]` → sell shares (**locked behind license**)
* `run` → simulate the market

At first glance, the intended gameplay is to buy low, sell high, and eventually reach the target. However, the real challenge lies in **unlocking the `sell` functionality**, which is restricted by a license check.

### Initial Recon

Using `file`:

```
ELF 64-bit, RISC-V, statically linked, not stripped
```

This indicates:

* Reverse engineering required
* Symbols are not stripped → easier analysis

### Blocking Point: `sell`

When executing:

```
./stonks sell 1
```

We get:

```
Selling is a premium feature
License number:
```

This clearly indicates a **license validation mechanism**.

### License Validation Logic

From reversing:

#### 1. Prime Check → `FUN_00103860`

This function checks whether the input is a **prime number**:

```c
if (param_1 % uVar1 == 0) return 0;
return 1;
```

Requirement #1: The license key must be **prime**

#### 2. Core Validation → `FUN_00103940`

```c
if ((isPrime(param_2)) && ((param_2 * CONST) & 0x7f) == 1)
```

### Understanding the Math

Key condition:

```
(param_2 * CONST) & 0x7f == 1
```

Since:

```
0x7f = 127 → mask → equivalent to mod 128
```

This becomes:

```
(param_2 * CONST) % 128 == 1
```

### Simplification

From the binary:

```
CONST = 0x283d = 10301
```

Reduce modulo 128:

```
10301 % 128 = 61
```

Final equation:

```
(param_2 * 61) % 128 == 1
```

### Solving

We need:

* `param_2` is **prime**
* `(param_2 * 61) ≡ 1 (mod 128)`

This is a **modular inverse problem**.

Solution:

```
param_2 = 149
```

149 is prime
(149 * 61) % 128 = 1

### Exploitation

```
./stonks sell 1
149
```

Output:

```
Product registered successfully!
```

### Reaching the Goal

Once selling is unlocked:

* Use `buy` and `sell` strategically
* Or simply let `run` increase value

Internally:

```c
if (money > 1999) → WIN
```

### Final Result

After reaching >2000€:

```
[ACCESS GRANTED]
FLAG{...}
```

### Notes

This crackme was not conceptually hard, but:

* Long
* Required patience
* Required connecting multiple functions

## Türkçe

### Genel Bakış

`stonks` binary’si bir borsa simülasyonudur. Gerçekten de şimdiye kadarki en uzun crackme'ydi. Amaç, **2000€ üstü net değer elde etmek**

Komutlar:

* `buy [count]` → hisse al
* `sell [count]` → hisse sat (**lisans gerek**)
* `run` → simülasyonu çalıştır

### Kritik Nokta: `sell`

```
./stonks sell 1
```

çıktı:

```
Selling is a premium feature
License number:
```

Satış yapmak için **lisans gerekiyor**

### Lisans Kontrolü

#### 1. Asallık Kontrolü → `FUN_00103860`

Bu fonksiyon:

sayının **asal olup olmadığını kontrol eder**

Şart 1: License key **asal olmalı**

#### 2. Asıl Check → `FUN_00103940`

```c
(param_2 * CONST) & 0x7f == 1
```

### Matematiksel Açılım

```
& 0x7f → mod 128
```

Yani:

```
(param_2 * CONST) % 128 == 1
```

### Sadeleştirme

```
CONST = 0x283d = 10301
10301 % 128 = 61
```

Denklem:

```
(param_2 * 61) % 128 == 1
```

### Çözüm

Koşullar:

* param_2 asal olmalı
* mod denklemini sağlamalı

Çözüm: `149`

### Kullanım

```
sell 1
149
```

→ Lisans aktif

### Win Condition

Kodda:

```c
if (money > 1999)
```

2000€ üstü → kazan

### Sonuç

* Lisans bypass edildi
* Sell açıldı
* Para kasıldı
* Flag alındı

### Not

Bu crackme:

* Zor değil ama **çok yorucu**
* Uzun analiz gerektiriyor
* Fonksiyonları bağlamak kritik olan şeydi
