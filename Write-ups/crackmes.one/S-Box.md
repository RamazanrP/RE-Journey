# SBoxCrypt v3.0 Crackme Write-up (TR & ENG)

# 🇬🇧 English Write-up

## 1. Initial Observations

When executed, the program prompts:

```text
enter license key>
```

Error messages:

```text
wrong length.
invalid key.
```

Success message:

```text
license accepted. congratulations!
```

This indicates:

* Fixed-length key (12 character)
* Validation logic present
* Success string embedded in binary

## 2. String Analysis

The following string is found:

```text
license accepted. congratulations!
```

Cross-references lead to:

```text
fcn.140002a80
```

This function performs the validation.

## 3. Input Length Check

Assembly:

```asm
cmp rax, 0xc
```

Meaning:

```text
Key length = 12 bytes
```

## 4. Transformation Logic

The program does not compare input directly. It applies a transformation.

### 4.1 S-Box Generation

Observed pattern:

```asm
div
swap
xorshift
```

Equivalent to:

```text
Fisher-Yates shuffle with XORSHIFT RNG
```

Python equivalent:

```python
sbox = list(range(256))
state = 0x12345678
```

### 4.2 Byte Transformation

Assembly:

```asm
xor al, byte [rcx]
movzx eax, byte [rsp + rax + 0xa0]
```

Mathematically:

```text
output[i] = sbox[input[i] XOR index]
```

Where:

```text
index = (i - 0x5b) mod 256
```

## 5. Final Comparison

The transformed input is compared to:

```text
ff 68 31 7c 90 57 29 97 d9 83 be 68
```

So:

```text
transform(input) == target
```

## 6. Solution Strategy

We observed:

* Deterministic algorithm
* Fixed RNG seed
* Reversible transformation

Thus, no brute force needed.

## 7. Inversion

Given:

```text
output = sbox[input XOR index]
```

We invert:

```text
input = inverse_sbox[output] XOR index
```

## 8. Python Solution
```py
sbox = list(range(256))

# XORSHIFT RNG
def xorshift(state):
    state ^= (state << 13) & 0xffffffff
    state ^= (state >> 17) & 0xffffffff
    state ^= (state << 5) & 0xffffffff
    return state & 0xffffffff

# Shuffle
state = 0x12345678

for i in range(255, -1, -1):
    j = state % (i + 1)
    sbox[i], sbox[j] = sbox[j], sbox[i]
    state = xorshift(state)

# inverse S-box
inv_sbox = [0] * 256
for i in range(256):
    inv_sbox[sbox[i]] = i

target = [
    0xff, 0x68, 0x31, 0x7c,
    0x90, 0x57, 0x29, 0x97,
    0xd9, 0x83, 0xbe, 0x68
]

key = []

for i in range(12):
    # index calculation (in binary: (-0x5b - base + i))
    index = (i - 0x5b) & 0xff

    # inverse
    val = inv_sbox[target[i]]

    # input byte
    inp = val ^ index
    key.append(inp)

key_str = ''.join(chr(x) for x in key)

print("License key:", key_str)
print("Raw bytes:", key)
```
## 9. Result

Recovered key:

```text
NOKTOSLABKEY
```

Program output:

```text
license accepted. congratulations!
```

## 10. Conclusion

This crackme uses:

* Custom encoding (not encryption)
* XOR + S-box transformation
* Deterministic reversible logic

Final solving principle:

```text
input = inverse(transform(target))
```

# 🇹🇷 Türkçe Write-up

## 1. İlk Gözlemler

Program çalıştırıldığında kullanıcıdan bir lisans anahtarı isteniyor:

```text
enter license key>
```

Yanlış girişlerde:

```text
wrong length.
invalid key.
```

Doğru girişte:

```text
license accepted. congratulations!
```

Buradan şunları anlıyoruz:

* Sabit uzunlukta bir key bekleniyor
* Doğrulama mekanizması mevcut
* Başarı mesajı string olarak binary içinde bulunuyor

## 2. String Analizi

Binary içinde şu string bulunur:

```text
license accepted. congratulations!
```

Bu string referanslanarak ilgili fonksiyon bulunur:

```text
fcn.140002a80
```

Bu fonksiyon lisans doğrulamasını içerir.

## 3. Input Kontrolü

Fonksiyon içinde şu kontrol vardır:

```asm
cmp rax, 0xc
je ...
```

Bu şu anlama gelir:

```text
Key uzunluğu = 12 byte
```

## 4. Transform Mekanizması

Program input üzerinde doğrudan karşılaştırma yapmaz. Önce bir dönüşüm uygular.

Bu dönüşüm şu adımlardan oluşur:

### 4.1 S-Box Oluşturma

Program içinde bir shuffle işlemi vardır:

```asm
div
swap
xorshift
```

Bu yapı:

```text
Fisher-Yates shuffle + XORSHIFT RNG
```

olarak tanımlanabilir.

Python karşılığı:

```python
sbox = list(range(256))
state = 0x12345678

for i in range(255, -1, -1):
    j = state % (i + 1)
    sbox[i], sbox[j] = sbox[j], sbox[i]
    state = xorshift(state)
```

### 4.2 Byte Transform

Her input byte şu şekilde işlenir:

```asm
xor al, byte [rcx]
movzx eax, byte [rsp + rax + 0xa0]
```

Bu şu matematiksel ifadeye karşılık gelir:

```text
output[i] = sbox[input[i] XOR index]
```

Burada:

```text
index = (i - 0x5b) mod 256
```

## 5. Final Karşılaştırma

Transform sonrası sonuç şu sabit değerle karşılaştırılır:

```text
ff 68 31 7c 90 57 29 97 d9 83 be 68
```

Yani:

```text
transform(input) == target
```

## 6. Çözüm Yaklaşımı

Bu noktada şu çıkarımı yaptık:

* Sistem deterministik
* RNG sabit seed kullanıyor
* Transform terslenebilir

Bu yüzden brute force gerekmez.

## 7. Tersine Çözüm

Verilen denklem:

```text
output = sbox[input XOR index]
```

Tersine çevrilirse:

```text
input = inverse_sbox[output] XOR index
```

## 8. Python ile Çözüm
```py
sbox = list(range(256))

# XORSHIFT RNG
def xorshift(state):
    state ^= (state << 13) & 0xffffffff
    state ^= (state >> 17) & 0xffffffff
    state ^= (state << 5) & 0xffffffff
    return state & 0xffffffff

# Shuffle
state = 0x12345678

for i in range(255, -1, -1):
    j = state % (i + 1)
    sbox[i], sbox[j] = sbox[j], sbox[i]
    state = xorshift(state)

# inverse S-box
inv_sbox = [0] * 256
for i in range(256):
    inv_sbox[sbox[i]] = i

target = [
    0xff, 0x68, 0x31, 0x7c,
    0x90, 0x57, 0x29, 0x97,
    0xd9, 0x83, 0xbe, 0x68
]

key = []

for i in range(12):
    # index calculation (in binary: (-0x5b - base + i))
    index = (i - 0x5b) & 0xff

    # inverse
    val = inv_sbox[target[i]]

    # input byte
    inp = val ^ index
    key.append(inp)

key_str = ''.join(chr(x) for x in key)

print("License key:", key_str)
print("Raw bytes:", key)
```
## 9. Sonuç

Elde edilen key:

```text
NOKTOSLABKEY
```

Programda doğrulandığında:

```text
license accepted. congratulations!
```

çıktısı alınır.

## 10. Genel Sonuç

Bu crackme’de:

* Direkt string karşılaştırma yok
* Custom transform (S-box + XOR) kullanılıyor
* Algoritma terslenebilir

Bu nedenle çözüm:

```text
input = inverse(transform(target))
```

şeklinde elde edilmiştir.
