# Orbit Fold - Crackme Write-up (ENG)

### Introduction

In this challenge, our goal was to recover the accepted flag from the `Orbit Fold` binary.

The binary accepts the flag either as a command-line argument or through standard input. Instead of trying random inputs, we started with static analysis in Ghidra and followed the validation logic until we could mathematically reverse it.

The final flag is:

```text
CMO{orbit_folded_twice}
```

## 1. Starting with the Main Function

The main validation function begins with:

```c
puts("Orbit Fold - recover the accepted flag.");
```

The program then obtains the input either from `argv[1]` or from `stdin`.

The first important condition is:

```c
sVar6 = strlen(__s);

if (sVar6 == 0x17) {
```

`0x17` is decimal `23`.

Therefore, the accepted flag must contain exactly:

```text
23 characters
```

This gives us our first constraint.

---

## 2. The Weighted Checksum

After checking the length, the program calculates:

```c
lVar7 = 1;
iVar9 = 0;

do {
    lVar3 = lVar7 + -1;
    iVar5 = (int)lVar7;
    lVar7 = lVar7 + 1;

    iVar9 = iVar9 + (uint)(byte)__s[lVar3] * iVar5;

} while (lVar7 != 0x18);
```

This can be rewritten as:

```text
checksum =
    flag[0]  * 1  +
    flag[1]  * 2  +
    flag[2]  * 3  +
    ...
    flag[22] * 23
```

The result must satisfy:

```c
if ((short)iVar9 == 0x728a)
```

So we have another constraint:

```text
Σ(flag[i] × (i + 1)) = 0x728a
```

`0x728a` is:

```text
29322
```

At this point, we know:

- Flag length = 23
- Weighted checksum = `29322`

However, this alone is not enough to recover the flag.

---

## 3. Finding the Lookup Tables

The next interesting part is:

```c
pbVar10 = &DAT_001020a0;
bVar11 = 0;

do {
    bVar1 = *pbVar10;
    ...
} while (pbVar10 != (byte *)0x1020b7);
```

The difference between the two addresses is:

```text
0x1020b7 - 0x1020a0 = 0x17
```

Again, 23 bytes.

We inspected `.rodata`:

```bash
objdump -s -j .rodata orbit_fold | grep -A8 -B2 2080
```

This gave us:

```text
2080 3e2cc350 b267f859 0314fa19 1581ca96
2090 856d3da8 1bd1f900 00000000 00000000
20a0 07001303 0e16050b 01110914 060d0210
20b0 0815040c 120a0f
```

Therefore:

### `DAT_00102080`

The first 23 bytes are:

```text
3e 2c c3 50 b2 67 f8 59
03 14 fa 19 15 81 ca 96
85 6d 3d a8 1b d1 f9
```

### `DAT_001020a0`

```text
07 00 13 03 0e 16 05 0b
01 11 09 14 06 0d 02 10
08 15 04 0c 12 0a 0f
```

The second table contains every number from `0` to `22` exactly once.

This is important because it means that every flag position will eventually be checked.

---

## 4. Understanding `DAT_001020a0`

The loop starts with:

```text
07 00 13 03 0e 16 ...
```

So the first iteration uses:

```text
x = 7
```

The second iteration uses:

```text
x = 0
```

The third:

```text
x = 19
```

and so on.

The value `x` is used as:

```c
__s[bVar1]
```

Therefore, the table determines which flag character is being checked.

For example:

```text
07 → flag[7]
00 → flag[0]
13 → flag[19]
03 → flag[3]
```

The table is simply a permutation of the flag indices.

---

## 5. Rewriting the Validation Formula

The important part of the loop is:

```c
bVar4 = bVar1 * '\a' + 0x31 ^ __s[bVar1];

bVar2 = bVar1 % 5 + 1 & 7;

bVar11 = bVar11 |
    (bVar4 << bVar2 | bVar4 >> 8 - bVar2)
    + (bVar1 * '\r' ^ 0x5a)
    ^ (&DAT_00102080)[bVar1];
```

Instead of reading the decompiler output directly, we rewrite it.

Let:

```text
x = table1[i]
```

Then:

```text
A = (x × 7 + 0x31) XOR flag[x]
```

The rotation amount is:

```text
shift = (x % 5) + 1
```

Then:

```text
R = ROL8(A, shift)
```

The next value is:

```text
C = (x × 13) XOR 0x5a
```

Finally:

```text
result = (R + C) XOR table2[x]
```

and the program performs:

```text
bVar11 = bVar11 | result
```

At the end:

```c
if (bVar11 == 0)
```

must be true.

---

## 6. Why We Can Reverse the Calculation

This is the key observation.

The accumulator starts at:

```c
bVar11 = 0;
```

and only receives values through bitwise OR:

```c
bVar11 |= result;
```

For the final value to remain zero, every `result` must have a zero low byte.

Therefore, for each `x`:

```text
result = 0
```

So:

```text
(R + C) XOR table2[x] = 0
```

which means:

```text
R + C = table2[x]
```

Therefore:

```text
R = table2[x] - C
```

Now we can reverse the rotation:

```text
A = ROR8(R, shift)
```

And finally:

```text
flag[x] = (x × 7 + 0x31) XOR A
```

The important part is that we are not brute-forcing the flag.

We are reversing the transformation.

---

## 7. Solving the First Character

The first value in `DAT_001020a0` is:

```text
0x07
```

Therefore:

```text
x = 7
```

We are solving:

```text
flag[7]
```

First:

```text
x × 7 + 0x31
= 7 × 7 + 0x31
= 49 + 49
= 98
= 0x62
```

The rotation amount is:

```text
(7 % 5) + 1
= 3
```

Next:

```text
x × 13
= 7 × 13
= 91
= 0x5b
```

Then:

```text
0x5b XOR 0x5a = 0x01
```

From the first table:

```text
DAT_00102080[7] = 0x59
```

The validation condition becomes:

```text
(ROL8(0x62 XOR flag[7], 3) + 0x01) XOR 0x59 = 0
```

Therefore:

```text
ROL8(0x62 XOR flag[7], 3) + 0x01 = 0x59
```

So:

```text
ROL8(0x62 XOR flag[7], 3) = 0x58
```

Reverse the rotation:

```text
0x62 XOR flag[7] = ROR8(0x58, 3)
```

```text
ROR8(0x58, 3) = 0x11
```

Therefore:

```text
flag[7] = 0x62 XOR 0x11
```

which gives:

```text
flag[7] = 0x73
```

ASCII:

```text
's'
```

So we have recovered:

```text
flag[7] = 's'
```

The same process can be applied to every value in `DAT_001020a0`.

---

## 8. Automating the Reversal

Instead of calculating all 23 characters manually, we translated the mathematical reversal into Python.

```python
table = [
    0x3e, 0x2c, 0xc3, 0x50, 0xb2, 0x67, 0xf8, 0x59,
    0x03, 0x14, 0xfa, 0x19, 0x15, 0x81, 0xca, 0x96,
    0x85, 0x6d, 0x3d, 0xa8, 0x1b, 0xd1, 0xf9
]

indices = [
    0x07, 0x00, 0x13, 0x03, 0x0e, 0x16, 0x05, 0x0b,
    0x01, 0x11, 0x09, 0x14, 0x06, 0x0d, 0x02, 0x10,
    0x08, 0x15, 0x04, 0x0c, 0x12, 0x0a, 0x0f
]

flag = ['?'] * 23

def ror8(value, shift):
    return ((value >> shift) | (value << (8 - shift))) & 0xff

for x in indices:
    shift = (x % 5) + 1

    constant = ((x * 13) ^ 0x5a) & 0xff

    rotated = (table[x] - constant) & 0xff

    A = ror8(rotated, shift)

    base = (x * 7 + 0x31) & 0xff

    flag[x] = chr(base ^ A)

print(''.join(flag))
```

Running:

```bash
python3 solve.py
```

produced:

```text
CMO{orbit_folded_twice}
```

---

## 9. Final Verification

The recovered flag is:

```text
CMO{orbit_folded_twice}
```

It contains exactly 23 characters, satisfying:

```text
strlen(flag) == 0x17
```

The weighted checksum also satisfies:

```text
Σ(flag[i] × (i + 1)) = 0x728a
```

The individual table-based transformations evaluate to zero, so:

```text
bVar11 == 0
```

and the program reaches:

```text
Correct. Submit that flag to claim your points.
```

### Final Flag

```text
CMO{orbit_folded_twice}
```

---

# Orbit Fold - Crackme Write-up (TR)

### Giriş

Bu challenge'da amacımız `Orbit Fold` binary'sinin kabul ettiği flag'i statik analiz kullanarak bulmaktı.

İlk olarak Ghidra üzerinden binary'nin flag kontrolünü gerçekleştiren fonksiyonu inceledik. Programın rastgele input kabul etmediğini, flag üzerinde birkaç matematiksel dönüşüm uyguladığını gördük.

Sonunda elde ettiğimiz flag:

```text
CMO{orbit_folded_twice}
```

## 1. Main Fonksiyonu

İlk önemli kontrol:

```c
sVar6 = strlen(__s);

if (sVar6 == 0x17) {
```
Yani flag'in  23 karakter olması gerekiyor.

## 2. Birikerek Artan Checksum

Daha sonra program flag üzerinde bir checksum hesaplıyor:

```c
lVar7 = 1;
iVar9 = 0;

do {
    lVar3 = lVar7 + -1;
    iVar5 = (int)lVar7;
    lVar7 = lVar7 + 1;

    iVar9 = iVar9 + (uint)(byte)__s[lVar3] * iVar5;

} while (lVar7 != 0x18);
```

Bunu daha anlaşılır şekilde:

```text
checksum =
    flag[0]  × 1  +
    flag[1]  × 2  +
    flag[2]  × 3  +
    ...
    flag[22] × 23
```

şeklinde yazabiliriz.

Program daha sonra:

```c
if ((short)iVar9 == 0x728a)
```

kontrolünü yapıyor.

Dolayısıyla ikinci ipucumuz:

```text
Σ(flag[i] × (i + 1)) = 0x728a
```

`0x728a` decimal olarak:

```text
29322
```

## 3. Lookup Table'ları Bulmak

Kodun devamındaki:

```c
pbVar10 = &DAT_001020a0;
bVar11 = 0;

do {
    bVar1 = *pbVar10;
    ...
} while (pbVar10 != (byte *)0x1020b7);
```

Başlangıç ve bitiş adreslerini çıkardığımızda:

```text
0x1020b7 - 0x1020a0 = 0x17
```

yani burada da 23 byte işleniyor.

Bu noktada `.rodata` (read-only data) bölümünü inceledik (veya Listing kısmından 001020a0 adresine de gidebilirsiniz:

```bash
objdump -s -j .rodata orbit_fold | grep -A8 -B2 2080
```

Sonuç:

```text
2080 3e2cc350 b267f859 0314fa19 1581ca96
2090 856d3da8 1bd1f900 00000000 00000000
20a0 07001303 0e16050b 01110914 060d0210
20b0 0815040c 120a0f
```

Buradan iki tabloyu elde ediyoruz.

### `DAT_00102080`

İlk 23 byte:

```text
3e 2c c3 50 b2 67 f8 59
03 14 fa 19 15 81 ca 96
85 6d 3d a8 1b d1 f9
```

### `DAT_001020a0`

```text
07 00 13 03 0e 16 05 0b
01 11 09 14 06 0d 02 10
08 15 04 0c 12 0a 0f
```

## 4. `DAT_001020a0` Ne İşe Yarıyor?

İkinci tabloya baktığımızda:

```text
07 00 13 03 0e 16 05 0b
01 11 09 14 06 0d 02 10
08 15 04 0c 12 0a 0f
```

içerisinde `0` ile `22` arasındaki **bütün sayıların birer kez** bulunduğunu görüyoruz.

Bu değerler doğrudan flag index'i olarak kullanılıyor.

Örneğin ilk değer:

```text
07
```

olduğu için ilk iterasyonda:

```c
__s[7]
```

kontrol ediliyor. Yani tablo aslında flag karakterlerinin kontrol edilme sırasını belirliyor.

## 5. Kontrol Formülünü Sadeleştirmek

Ghidra'nın verdiği kritik kısım:

```c
bVar4 = bVar1 * '\a' + 0x31 ^ __s[bVar1];

bVar2 = bVar1 % 5 + 1 & 7;

bVar11 = bVar11 |
    (bVar4 << bVar2 | bVar4 >> 8 - bVar2)
    + (bVar1 * '\r' ^ 0x5a)
    ^ (&DAT_00102080)[bVar1];
```

Bunu değişkenlerle daha okunabilir hale getirelim.

`x = bVar1` olsun.

İlk işlem:

```text
A = (x × 7 + 0x31) XOR flag[x]
```

Rotate miktarı:

```text
shift = (x % 5) + 1
```

Sonra:

```text
R = ROL8(A, shift)
```

Bir sonraki sabit:

```text
C = (x × 13) XOR 0x5a
```

Son işlem:

```text
result = (R + C) XOR DAT_00102080[x]
```

Program bunu:

```text
bVar11 |= result
```

ile result'a ekliyor.

Ve son kontrol:

```c
if (bVar11 == 0)
```

şeklinde.

## 6. Formülü Tersine Çevirmek

Buradaki en önemli nokta `bVar11` değişkeninin nasıl kullanıldığı.

Başlangıçta:

```c
bVar11 = 0;
```

ve her iterasyonda:

```c
bVar11 |= result;
```

yapılıyor.

Sonunda:

```c
bVar11 == 0
```

olması gerekiyor.

OR işleminde herhangi bir iterasyonda `result` sıfırdan farklı bir bit içerirse result **sıfır kalamaz**.

Dolayısıyla her karakter için result 0 olmalı.

Formülümüz:

```text
(R + C) XOR table[x] = 0
```

olduğuna göre:

```text
R + C = table[x]
```

Buradan:

```text
R = table[x] - C
```

elde ediyoruz.

`R`, `ROL8(A, shift)` olduğuna göre rotate işlemini tersine çevirelim:

```text
A = ROR8(R, shift)
```

Son olarak:

```text
A = (x × 7 + 0x31) XOR flag[x]
```

olduğu için:

```text
flag[x] = (x × 7 + 0x31) XOR A
```

elde ediyoruz.

Böylece brute force yapmadan her karakteri doğrudan hesaplayabiliriz.

## 7. İlk Karakteri Elle Çözmek

İlk değer:

```text
DAT_001020a0[0] = 0x07
```

Bu nedenle `x = 7` ve çözdüğümüz karakter `flag[7]` oluyor.

İlk sabit:

```text
x × 7 + 0x31
```
Yani 0x62 

Rotate miktarı:

```text
(7 % 5) + 1
= 3
```

Diğer sabit:

```text
7 × 13
= 91
= 0x5b
```

Sonra XOR:

```text
0x5b XOR 0x5a = 0x01
```

Tablodan:

```text
DAT_00102080[7] = 0x59
```

Kontrol:

```text
(ROL8(0x62 XOR flag[7], 3) + 0x01) XOR 0x59 = 0
```

olmalı.

Buradan:

```text
ROL8(0x62 XOR flag[7], 3) = 0x58
```

Rotate işlemini tersine çeviriyoruz:

```text
0x62 XOR flag[7] = ROR8(0x58, 3)
```

ve:

```text
ROR8(0x58, 3) = 0x11
```

Dolayısıyla:

```text
flag[7] = 0x62 XOR 0x11
```

Sonuç:

```text
flag[7] = 0x73
```

ASCII karşılığı:

```text
s
```

Yani:

```text
flag[7] = 's'
```

Aynı işlemi 23 index'in tamamına uygulayabiliriz.

## 8. Python ile Flag'i Çıkarmak

23 karakteri elle hesaplamak yerine, tersine çevirdiğimiz işlemleri Python'a aktarıyoruz:

```python
table = [0x3e, 0x2c, 0xc3, 0x50, 0xb2, 0x67, 0xf8, 0x59,
        0x03, 0x14, 0xfa, 0x19, 0x15, 0x81, 0xca, 0x96,
        0x85, 0x6d, 0x3d, 0xa8, 0x1b, 0xd1, 0xf9 ]

indices = [0x07, 0x00, 0x13, 0x03, 0x0e, 0x16, 0x05, 0x0b,
          0x01, 0x11, 0x09, 0x14, 0x06, 0x0d, 0x02, 0x10,
          0x08, 0x15, 0x04, 0x0c, 0x12, 0x0a, 0x0f ]

flag = ['?'] * 23

def ror8(value, shift):
    return ((value >> shift) | (value << (8 - shift))) & 0xff

for x in indices:
    shift = (x % 5) + 1

    constant = ((x * 13) ^ 0x5a) & 0xff

    rotated = (table[x] - constant) & 0xff

    A = ror8(rotated, shift)

    base = (x * 7 + 0x31) & 0xff

    flag[x] = chr(base ^ A)

print(''.join(flag))
```

Çalıştırdığımızda sonuç:

```text
CMO{orbit_folded_twice}
```

## Conclusion

Bu challenge'da temel yaklaşımımız brute force yapmak yerine validation algoritmasını tersine çevirmek oldu.

Özellikle üç nokta çözümün temelini oluşturdu:

1. `0x17` değerinden flag uzunluğunun 23 olduğunu çıkarmak.
2. `DAT_001020a0` tablosunun flag index'lerini belirlediğini fark etmek.
3. `bVar11 |= result` ve `bVar11 == 0` koşullarından her karakter için `result = 0` olması gerektiğini çıkararak dönüşümü tersine çevirmek.

Bu sayede flag'i tahmin etmek yerine binary'nin uyguladığı işlemlerden doğrudan geri çıkardık.
