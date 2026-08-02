# CrackMe Write-up — argc (ENG & TR)

## Overview

This is a very simple crackme, but it highlights an important concept in reverse engineering:  
**understanding how program arguments (`argv`) are stored and accessed in memory.**

While solving it, I initially overthought pointer arithmetic due to `char**` usage, but the actual logic turned out to be much simpler

## Step 1 — Understanding Parameters

Ghidra shows:

```c
int param_1
long param_2
```

But in reality, this is:

```c
int argc
char **argv
```

So:

* `param_1` → `argc`
* `param_2` → `argv`

## Step 2 — Argument Check

```c
if (param_1 == 3)
```

The program expects exactly **3 arguments**:

```bash
./argc arg1 arg2
```

Where:

* `argv[0]` → program name (`./argc`)
* `argv[1]` → first input
* `argv[2]` → second input


## Step 3 — The Critical Line

```c
strcmp(*(char **)(param_2 + 8), *(char **)(param_2 + 0x10));
```

This looks confusing at first but breaking it down:

### Memory Layout (64-bit)

Each pointer = **8 bytes**

| Expression       | Meaning |
| ---------------- | ------- |
| `param_2 + 0`    | argv[0] |
| `param_2 + 8`    | argv[1] |
| `param_2 + 0x10` | argv[2] |

So this becomes:

```c
strcmp(argv[1], argv[2]);
```

## Step 4 — What `strcmp` Does

```c
strcmp(a, b) == 0
```

Means:

=> Strings `a` and `b` are exactly the same

## Step 5 — Key Insight

At first, it may seem like the program is checking a hidden password.
It's as if the first input has to match the characters after the 8th one, and the second input has to match the characters after the 16th one, but actually:
there is **no hardcoded password**.

The program only checks:

=> Are the two inputs identical?


## Solution

Any identical arguments will pass:

```bash
./argc a a
```

## Result

When inputs match:

```text
correct!
```

## Lessons Learned

### 1. Pointer Arithmetic Matters

Offsets like:

* `+8`
* `+0x10`

indicate **64-bit architecture** (8-byte pointers).

### 2. Don’t Overthink `char **`

Seeing:

```c
(char **)
```

can make things look more complex than they are.

In this case, it’s just accessing:

```c
argv[index]
```

## Final Thoughts

Even though this crackme is simple, it reinforces a critical RE mindset:

* Not every challenge hides a secret
* Sometimes the logic itself *is* the challenge

This one was a good reminder to stay grounded and not overcomplicate pointer-based code.

# CrackMe Write-up — argc (TR)

## Genel Bakış

Bu crackme oldukça basit, ancak reverse engineering açısından önemli bir noktayı hatırlatıyor:  
program argümanlarının (`argv`) bellekte nasıl tutulduğu ve erişildiği.

Çözerken başlangıçta `char **` ve pointer arithmetic yüzünden fazla düşündüm, fakat aslında mantık oldukça basitti.

## Analiz

Ghidra’da `main` fonksiyonu şu şekilde görünüyor:

`main(int param_1, long param_2)`

Buradaki gerçek karşılık:

- `param_1` → `argc`
- `param_2` → `argv`

## Argüman Kontrolü

Program şu kontrolü yapıyor:

`param_1 == 3`

Yani program tam olarak 3 argüman bekliyor:

- `argv[0]` → program adı
- `argv[1]` → birinci input
- `argv[2]` → ikinci input

## Kritik Nokta

Kilit satır:

`strcmp(*(char **)(param_2 + 8), *(char **)(param_2 + 0x10))`

İlk bakışta karmaşık görünüyor, ama aslında şu anlama geliyor:

- `param_2 + 8` → `argv[1]`
- `param_2 + 0x10` → `argv[2]`

Yani bu ifade:

`strcmp(argv[1], argv[2])`

## strcmp Ne Yapıyor?

`strcmp(a, b) == 0` demek:

→ iki string tamamen aynı

## Asıl Mantık

Başta gizli bir şifre aranıyor gibi görünüyor. Sanki girilen ilk inputun 8. karakterden sonrası ile ikinci inputun 16. karakterinden sonrası aynı olmak zorundaymış gibi ama aslında:

→ program herhangi bir şifre kontrol etmiyor

Sadece şunu kontrol ediyor:

→ girilen iki input aynı mı?


## Çözüm

Herhangi iki aynı değer çalışır:

`./argc a a`  
`./argc hello hello`

## Sonuç

Eğer iki input aynıysa program başarı mesajı verir.

## Öğrenilenler

### 1. Pointer Arithmetic Yanıltabilir

`+8` ve `+0x10` offset’leri:

→ 64-bit sistemde pointer boyutunun 8 byte olduğunu gösterir

### 2. `char **` Her Zaman Karmaşık Değildir

`(char **)` görünce fazla derine inmek kolaydır.

Ama çoğu zaman bu sadece:

`argv[index]`

demektir.

## Son Not

Bu crackme basit olsa da önemli bir şeyi hatırlatıyor:

- Her zaman gizli veri aranmaz  
- Bazen çözüm, doğrudan programın mantığındadır  

Bu da gereksiz overthinking yapmamayı öğreten güzel bir örnek oldu.
