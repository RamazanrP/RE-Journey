# Goth House Write-up — ENG & TR

## English Version

### Overview

This crackme is not a simple XOR check. It combines:

* Input length validation (17 bytes)
* A loop that runs **17 times**
* Inside it, another loop of **6 iterations**
* A **SHA256 hash per character**
* A **rolling XOR state**
* A comparison against a large static table (`DAT_00104060`, 544 bytes)

This creates a chained validation mechanism where each character affects future state.

### Step 1 — Input Handling

```c
fgets(local_c8 + 0x20, 0x80, stdin);
```

* Input is stored at offset `+0x20`
* Max length: 128 bytes
* Then newline is removed

```c
if (local_20 == 0x11)
```

* Required length: **17 characters**

### Step 2 — Main Loop (17 iterations)

```c
for (local_c = 0; local_c < 0x11; local_c++)
```

Each iteration processes **one character**.

### Step 3 — Per-character transformation

```c
local_21 = input[i];
```

Then:

```c
for (local_10 = 0; local_10 < 6; local_10++) {
    local_ef[local_10] = local_10 + local_21;
}
```

So we build a 6-byte array:

```
[char + 0, char + 1, char + 2, char + 3, char + 4, char + 5]
```

### Step 4 — SHA256

```c
SHA256(local_ef, 6, local_e8);
```

* Input: 6 bytes
* Output: 32 bytes (`local_e8`)

This is critical:

Each character produces a **unique 32-byte hash block**

### Step 5 — Rolling XOR State

```c
for (local_14 = 0; local_14 < 0x20; local_14++) {
    local_c8[local_14] ^= local_e8[local_14];
}
```

This is NOT simple XOR.

Important:

* `local_c8[0..31]` is reused every iteration
* It accumulates changes

So:

```
state = state ^ hash(char_i)
```

This is a **rolling state**

### Step 6 — Comparison

```c
memcmp(local_c8, DAT_00104060 + i * 0x20, 0x20)
```

* Compare current state (32 bytes)
* With expected block at:

```
DAT_00104060[i * 32]
```

Total size:

```
17 * 32 = 544 bytes
```

That matches your observation.

### Step 7 — Important Insight

This is NOT:

```
input[i] ^ key = data
```

This is:

```
state_0 = 0
state_1 = hash(c0)
state_2 = hash(c0) ^ hash(c1)
state_3 = hash(c0) ^ hash(c1) ^ hash(c2)
...
```

And each step must match:

```
state_i == DAT[i]
```

### Step 8 — How to Solve

We reverse step by step.

#### First character:

```
state_1 = hash(c0)
```

So:

```
hash(c0) == DAT[0]
```

→ brute-force c0

#### Second character:

```
state_2 = state_1 ^ hash(c1)
```

So:

```
hash(c1) = DAT[1] ^ DAT[0]
```

#### General case:

```
hash(ci) = DAT[i] ^ DAT[i-1]
```

### Step 9 — Attack Strategy

1. Extract all 17 blocks (32 bytes each)
2. Compute:

```python
hash_ci = DAT[i] ^ DAT[i-1]
```

3. For each `hash_ci`:

   * brute-force character
   * compute SHA256 of `[c, c+1, ..., c+5]`
   * match hash

## Key Finding

## 1. We first captured the critical line

```c
local_c8[local_14] = local_c8[local_14] ^ local_e8[local_14];
```

Here:

* `local_c8[0..31]` → state
* `local_e8[0..31]` → SHA256 result

So:

```
state ^= hash
```

At this point, we realize:
**There is no constant key. The key = the dynamically generated hash.**

---

## 2. Searching for a "key" is actually the wrong approach

Initially, the expectation is:

* There is a `key[]` array
* The input is XORed with it

But that is not the case here.

In Ghidra, we noticed this:

```c
SHA256(local_ef, 6, local_e8);
```

The data going into the XOR is **not hardcoded**; it is generated in every iteration.

## 3. How is the hash's input generated?

This loop:

```c
for (local_10 = 0; local_10 < 6; local_10++) {
    local_ef[local_10] = local_10 + local_21;
}
```

Here:

* `local_21 = input[i]`

So:

```
local_ef = [
  c,
  c+1,
  c+2,
  c+3,
  c+4,
  c+5
]
```

We now clearly know the SHA256 input.

## 4. How did we understand this in Ghidra?

### Step by step:

1. We went to the `memcmp` line
2. We traced it backwards (using XREF logic)

We saw this chain:

```
memcmp → local_c8 → XOR → local_e8 → SHA256 → local_ef → input
```

This chain tells you: the XOR key is not fixed; it is derived from the input.

---

## 5. Noticing how the state accumulates

The most critical insight:

```c
memset(local_c8, 0, 0x20);
```
Initially, state = 0

Then, in each round:

```c
state = state ^ hash(ci)
```

So:

```
state0 = 0
state1 = hash(c0)
state2 = hash(c0) ^ hash(c1)
state3 = hash(c0) ^ hash(c1) ^ hash(c2)
```

## 6. What does the comparison with DAT show?

```c
memcmp(local_c8, DAT_00104060 + i*0x20, 0x20)
```

This means:

```
state_i == DAT[i]
```

## 7. How is the "key" derived from this?

Here is the most critical breakthrough:

```
state_i = state_(i-1) ^ hash(ci)
```

Invert it:

```
hash(ci) = state_i ^ state_(i-1)
```

But:

```
state_i = DAT[i]
state_(i-1) = DAT[i-1]
```

RESULT:

```
hash(ci) = DAT[i] ^ DAT[i-1]
```
And we found the password to be **buttercupcosplays**. I wasn't expecting something so meaningful :)

## 8. How did we realize this in Ghidra?

By combining these 3 things:

1. `memset(..., 0x20)` → state initialization
2. XOR loop → state accumulation
3. DAT pointer incrementing (`+ i * 0x20`)

=> This is a "progressive state validation" system.

## 9. So "finding the key" is actually this:

There is no classic key to find here:

```
key_i = hash(ci)
```

and we derive it as:

```
key_i = DAT[i] ^ DAT[i-1]
```

## Short Summary

In Ghidra, we found the key like this:

* We saw the XOR line → deduced that there is a state
* We saw SHA256 → deduced that the key is dynamic
* We saw memset → understood the state initialization
* We saw memcmp + offset → solved that this is a state chain
* From this:

```
hash(ci) = DAT[i] ^ DAT[i-1]
```

## Türkçe Versiyon

### Genel Bakış

Bu crackme basit XOR değildir. İçinde:

* 17 karakter uzunluk kontrolü
* 17’lik ana döngü
* 6’lık iç döngü
* Her karakter için SHA256
* Biriken XOR state
* 544 byte’lık karşılaştırma tablosu vardır

### 1 — Input

* Input `+0x20` offsetine yazılıyor
* Uzunluk: **17 karakter**

### 2 — Ana Döngü

```c
for (i = 0; i < 17; i++)
```

Her turda 1 karakter işlenir.


### 3 — 6 byte oluşturma

```c
[c, c+1, c+2, c+3, c+4, c+5]
```

### 4 — SHA256

Her karakter -> 32 byte hash üretir.


### 5 — State mantığı

```c
state ^= hash
```

Yani:

```
state = state ^ hash(ci)
```

Üst üste biriken bşr yapı görüyoruz.

### 6 — Karşılaştırma

```c
memcmp(state, DAT[i])
```

Toplam:

```
17 * 32 = 544 byte
```

### 7 — Kritik Nokta

Bu:

```
input ^ key = data
```

DEĞİL

Bu:

```
state_i = state_(i-1) ^ hash(ci)
```

### 8 — Tersine Çözüm

```
hash(ci) = DAT[i] ^ DAT[i-1]
```

---

### 9 — Çözüm Yolu

1. DAT verisini çıkar
2. XOR ile hashleri bul
3. Her hash için brute-force karakter dene
4. SHA256 ile eşleşeni bul
```python
dat = [...]   # DAT_00104060 byte'ları
key = [...]   # state / key

result = []
for i in range(len(dat)):
    result.append(dat[i] ^ key[i % len(key)])

print(bytes(result))
```
Ve de şifreyi **buttercupcosplays** olarak buluyoruz. Böyle anlamlı bir şey çıkmasını ben de beklemiyordum :)

## Key Bulma

## 1. Önce kritik satırı yakaladık

```c
local_c8[local_14] = local_c8[local_14] ^ local_e8[local_14];
```

Burada:

* `local_c8[0..31]` → state
* `local_e8[0..31]` → SHA256 sonucu

Yani:

```
state ^= hash
```

Bu noktada şunu anlıyoruz:
**Key diye sabit bir şey yok. Key = dinamik olarak üretilen hash.**


## 2. “Key nerede?” diye aramak aslında yanlış yaklaşım

Başta beklenti şu oluyor:

* bir `key[]` dizisi vardır
* input onunla XOR’lanır

Ama burada öyle değil.

Ghidra’da şunu fark ettik:

```c
SHA256(local_ef, 6, local_e8);
```

XOR’a giren veri **hardcoded değil**, her iterasyonda üretiliyor.

## 3. Hash’in input’u nasıl oluşuyor?

Şu loop:

```c
for (local_10 = 0; local_10 < 6; local_10++) {
    local_ef[local_10] = local_10 + local_21;
}
```

Burada:

* `local_21 = input[i]`

Yani:

```
local_ef = [
  c,
  c+1,
  c+2,
  c+3,
  c+4,
  c+5
]
```
SHA256 input’unu artık net biliyoruz.

## 4. Ghidra’da bunu nasıl anladık?

### Adım adım:

1. `memcmp` satırına gittik
2. Geri doğru takip ettik (XREF mantığı)

Şu zincir çıktı:

```
memcmp → local_c8 → XOR → local_e8 → SHA256 → local_ef → input
```

Bu zincir bize şunu söyler: XOR key sabit değil, input’tan türetiliyor

## 5. State’in nasıl biriktiğini fark etmek

En kritik insight:

```c
memset(local_c8, 0, 0x20);
```
Başlangıçta state = 0

Sonra her turda:

```c
state = state ^ hash(ci)
```

Yani:

```
state0 = 0
state1 = hash(c0)
state2 = hash(c0) ^ hash(c1)
state3 = hash(c0) ^ hash(c1) ^ hash(c2)
```

## 6. DAT ile karşılaştırma neyi gösteriyor?

```c
memcmp(local_c8, DAT_00104060 + i*0x20, 0x20)
```

Bu şu demek:

```
state_i == DAT[i]
```

---

## 7. Buradan “key” nasıl çıkarılıyor?

İşte en kritik kırılma noktası:

```
state_i = state_(i-1) ^ hash(ci)
```

Bunu ters çevirdik:

```
hash(ci) = state_i ^ state_(i-1)
```

Ama:

```
state_i = DAT[i]
state_(i-1) = DAT[i-1]
```

SONUÇ:

```
hash(ci) = DAT[i] ^ DAT[i-1]
```

---

## 8. Ghidra’da bunu nasıl fark ettik?

Şu 3 şey birleşince:

1. `memset(..., 0x20)` → state başlangıcı
2. XOR loop → state birikiyor
3. DAT pointer artıyor (`+ i * 0x20`)

=> Bu bir “progressive state validation” sistemi

## 9. Yani “key bulma” aslında şu:

Klasik bir key bulma yok burda:

```
key_i = hash(ci)
```

ve onu da:

```
key_i = DAT[i] ^ DAT[i-1]
```

şeklinde çıkarıyoruz.

## Kısa Özet

Ghidra’da key’i şöyle bulduk:

* XOR satırını gördük → state var dedik
* SHA256 gördük → key dinamik dedik
* memset gördük → state başlangıcını anladık
* memcmp + offset gördük → state zinciri olduğunu çözdük
* buradan:

  ```
  hash(ci) = DAT[i] ^ DAT[i-1]
  ```
