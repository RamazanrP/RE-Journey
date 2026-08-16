# Dead Terminal Crackme Write-up (English)

This document describes step-by-step how the **Dead Terminal** crackme was solved.  
The goal was to find the secret key required by the `reap` command. (We saw the "reap <key>" request in the static analysis)
All analysis was performed using **Ghidra**.

## 1. Program Behavior

When executed, the program presents a shell prompt:

```
soulreaper shell >
```

The shell accepts several commands:

- `exit` – terminates the program
- `reap <key>` – validates the provided key
- Any other command (e.g., `ls`, `whoami`) is executed via `fork` + `execvp`

The interesting part is the `reap` command. The key passed to it is sent to the validation function `FUN_00101560`.

## 2. Inspection of the Validation Function

The decompiled code of `FUN_00101560` in Ghidra is shown below:

```c
undefined8 FUN_00101560(byte *param_1)
{
  (some variables)
  sVar1 = strlen((char *)param_1);
  uVar2 = 0;
  if (sVar1 == 8) {
    cVar4 = '\a';   // 7
    do {
      if (*pcVar3 != (byte)((*param_1 ^ 0x2a) + cVar4)) {
        uVar2 = 0;
        goto LAB_001015e1;
      }
      cVar4 = cVar4 + '\x03';  // increases by 3 each iteration
      param_1 = param_1 + 1;
      pcVar3 = pcVar3 + 1;
    } while (cVar4 != '\x1f');  // 31
    uVar2 = 1;
  }
LAB_001015e1:
  if (local_10 == *(long *)(in_FS_OFFSET + 0x28)) {
    return uVar2;
  }
  __stack_chk_fail();
}
```

## What the Function Does

1. **Length check:** The input (`param_1`) must be exactly **8 bytes** long.
2. **Constant array:** `local_18` holds 8 fixed bytes:
   ```
   0x7F, 0x79, 0x78, 0x8A, 0x82, 0x8E, 0x37, 0x34
   ```
3. **Loop:** It iterates 8 times. At each step:
   - `cVar4` starts at 7 and increases by 3 each round (7 → 10 → 13 → … → 28).
   - The expected byte is calculated as `(input_byte ^ 0x2A) + cVar4`.
   - This expected value is compared to the corresponding byte in the constant array.
   - If any mismatch occurs, the function returns `0` (failure).
4. **Success:** If all 8 bytes match, it returns `1`.

## 3. Deriving the Correct Key

The equality can be reversed to find the correct input byte:

```
constant_byte = (input_byte ^ 0x2A) + cVar4
```

Therefore:

```
input_byte = (constant_byte - cVar4) ^ 0x2A
```

Now compute each byte step by step:

| Step | cVar4 | Constant (hex) | Calculation | Result (hex) | Character |
|------|-------|----------------|-------------|--------------|-----------|
| 1    | 7     | 0x7F           | (0x7F - 7) ^ 0x2A = 0x78 ^ 0x2A | 0x52 | 'R' |
| 2    | 10    | 0x79           | (0x79 - 10) ^ 0x2A = 0x6F ^ 0x2A | 0x45 | 'E' |
| 3    | 13    | 0x78           | (0x78 - 13) ^ 0x2A = 0x6B ^ 0x2A | 0x41 | 'A' |
| 4    | 16    | 0x8A           | (0x8A - 16) ^ 0x2A = 0x7A ^ 0x2A | 0x50 | 'P' |
| 5    | 19    | 0x82           | (0x82 - 19) ^ 0x2A = 0x6F ^ 0x2A | 0x45 | 'E' |
| 6    | 22    | 0x8E           | (0x8E - 22) ^ 0x2A = 0x78 ^ 0x2A | 0x52 | 'R' |
| 7    | 25    | 0x37           | (0x37 - 25) ^ 0x2A = 0x1E ^ 0x2A | 0x34 | '4' |
| 8    | 28    | 0x34           | (0x34 - 28) ^ 0x2A = 0x18 ^ 0x2A | 0x32 | '2' |

The resulting key is: **REAPER42**


## 4. Testing

Run the program and, when the prompt appears, enter:

```
reap REAPER42
```

The output is:

```
Access granted
join us : https://t.me/+blTRfHi8oKJiN2E0
```

The crackme is successfully solved.

## 5. Conclusion

- The program validates the key by checking its length and applying a transformation (XOR and addition) to each byte, comparing the results against a fixed array.
- Through reverse engineering, the correct key (`REAPER42`) was recovered from the constant data and the transformation logic.
- This approach can be applied to similar validation mechanisms in other crackmes.

## Türkçe

Bu yazıda, **Dead Terminal** isimli crackme’nin nasıl çözüldüğünü adım adım anlatıyoruz.  
Hedef, programın `reap` komutu ile istediği gizli anahtarı bulmak, reap isteğini Statik Analiz kısmında gördük.  

## 1. Programın Çalışma Mantığı

Program çalıştırıldığında bir kabuk sunuyordu:

```
soulreaper shell >
```

Bu kabuk üzerinden komutlar girilebilir.  
Bize verilen komutlar:

- `exit` – programdan çıkar
- `reap <key>` – verilen anahtarı doğrular
- Diğer komutlar (`ls`, `whoami` vb.) `fork` + `execvp` ile çalıştırılır

Bizim ilgilendiğimiz kısım `reap` komutu. Komutun ardına yazılan `key` değeri, doğrulama fonksiyonu olan `FUN_00101560`’ya iletilir.

## 2. Doğrulama Fonksiyonunun İncelenmesi

Ghidra’da `FUN_00101560` fonksiyonunun decompile edilmiş kodu aşağıdaki gibidir:

```c
undefined8 FUN_00101560(byte *param_1)
{
  (bazı değişken atamaları)
  sVar1 = strlen((char *)param_1);
  uVar2 = 0;
  if (sVar1 == 8) {
    cVar4 = '\a';   // 7
    do {
      if (*pcVar3 != (byte)((*param_1 ^ 0x2a) + cVar4)) {
        uVar2 = 0;
        goto LAB_001015e1;
      }
      cVar4 = cVar4 + '\x03';  // her adımda 3 artar
      param_1 = param_1 + 1;
      pcVar3 = pcVar3 + 1;
    } while (cVar4 != '\x1f');  // 31
    uVar2 = 1;
  }
LAB_001015e1:
  if (local_10 == *(long *)(in_FS_OFFSET + 0x28)) {
    return uVar2;
  }
  __stack_chk_fail();
}
```

### Fonksiyonun Yaptığı

1. **Uzunluk kontrolü:** Girdi (`param_1`) tam olarak **8 bayt** uzunluğunda olmalıdır.
2. **Sabit dizi:** `local_18` dizisinde 8 adet sabit bayt saklıdır:
   ```
   0x7F, 0x79, 0x78, 0x8A, 0x82, 0x8E, 0x37, 0x34
   ```
3. **Döngü:** 8 kez tekrarlanır. Her adımda:
   - `cVar4` başlangıçta 7’dir ve her döngüde 3 artar (7 → 10 → 13 → … → 28).
   - Beklenen bayt = `(girilen_bayt ^ 0x2A) + cVar4`
   - Bu beklenen bayt, sabit dizideki karşılık gelen bayt ile karşılaştırılır.
   - Eşleşme olmazsa fonksiyon `0` (başarısız) döner.
4. **Başarılı durum:** Tüm 8 bayt eşleşirse `1` döner.

## 3. Doğru Anahtarın Hesaplanması

Her bir bayt için doğru değeri bulmak için eşitliği tersine çeviririz:

```
sabit_bayt = (girilen_bayt ^ 0x2A) + cVar4
```

Buradan:

```
girilen_bayt = (sabit_bayt - cVar4) ^ 0x2A
```

Şimdi her bir adım için hesaplayalım:

| Adım | cVar4 | Sabit Bayt (hex) | Hesaplama | Sonuç (hex) | Karakter |
|------|-------|------------------|-----------|-------------|----------|
| 1    | 7     | 0x7F             | (0x7F - 7) ^ 0x2A = 0x78 ^ 0x2A | 0x52 | 'R' |
| 2    | 10    | 0x79             | (0x79 - 10) ^ 0x2A = 0x6F ^ 0x2A | 0x45 | 'E' |
| 3    | 13    | 0x78             | (0x78 - 13) ^ 0x2A = 0x6B ^ 0x2A | 0x41 | 'A' |
| 4    | 16    | 0x8A             | (0x8A - 16) ^ 0x2A = 0x7A ^ 0x2A | 0x50 | 'P' |
| 5    | 19    | 0x82             | (0x82 - 19) ^ 0x2A = 0x6F ^ 0x2A | 0x45 | 'E' |
| 6    | 22    | 0x8E             | (0x8E - 22) ^ 0x2A = 0x78 ^ 0x2A | 0x52 | 'R' |
| 7    | 25    | 0x37             | (0x37 - 25) ^ 0x2A = 0x1E ^ 0x2A | 0x34 | '4' |
| 8    | 28    | 0x34             | (0x34 - 28) ^ 0x2A = 0x18 ^ 0x2A | 0x32 | '2' |

Elde edilen anahtar: **REAPER42**

## 4. Test

Programı çalıştırıp prompt geldiğinde aşağıdaki komutu gireriz:

```
reap REAPER42
```

Çıktı:

```
Access granted
join us : https://t.me/+blTRfHi8oKJiN2E0
```

Böylece crackme başarıyla çözülmüştür.

---

## 5. Sonuç

- Program, girdiğimiz anahtarın uzunluğunu ve her bir baytını belirli bir işlemden geçirerek sabit bir diziyle karşılaştırmaktadır.
- Tersine mühendislik ile bu sabit diziden ve işlem adımlarından doğru anahtarı (`REAPER42`) elde ettik.
