# Howosec's crackme Write-up (ENG & TR)

## Overview

This challenge involves reversing a binary that asks for a password and prints a flag if the correct password is provided.

Instead of fully reversing the binary statically, we solved it dynamically using GDB by intercepting the password comparison.

## Binary Behavior

When running the binary:

```bash
./program
````

It prompts:

```
Insira sua senha:
```

If the password is incorrect:

```
Você errou hahahahah
```

If correct:

```
Aqui está sua flag: HOWO{REVERSING-A-COMPLEX-XOR}
```
Ofc if you found that :)

## Strategy

The binary likely compares user input with a hardcoded password using `strcmp`.

Instead of reverse engineering the entire binary, we:

* Set a breakpoint on `strcmp`
* Captured the arguments passed to it
* Extracted the correct password directly from memory

## Step-by-Step Solution

### 1. Open the binary in GDB

```bash
gdb ./program
```

### 2. Find `strcmp`

```gdb
info functions strcmp
```

Output:

```
0x0000555555555170  strcmp@plt
0x00007ffff7ca8b70  strcmp
```

We use `strcmp@plt` since it's the PLT entry used by the binary.

### 3. Set Breakpoint

```gdb
b strcmp@plt
```

### 4. Run the Program

```gdb
run
```

Enter any input when prompted:

```
Insira sua senha: hello
```

---

### 5. Breakpoint Hit

Execution stops at `strcmp`.

At this point:

* `$rdi` → user input
* `$rsi` → correct password

### 6. Inspect Registers

```gdb
x/s $rdi
```

Output:

```
"hello"
```

```gdb
x/s $rsi
```

Output:

```
"senhafoda1234567890"
```

We have successfully extracted the correct password.

### 7. Run Again with Correct Password

Exit GDB and run the binary:

```bash
./program
```

Enter:

```
senhafoda1234567890
```

```
Aqui está sua flag: HOWO{REVERSING-A-COMPLEX-XOR}
```

## Why This Works

`strcmp` compares two strings:

```c
strcmp(user_input, correct_password)
```

In x86_64 calling convention:

* First argument → `rdi`
* Second argument → `rsi`

By breaking at `strcmp`, we intercept the exact moment the comparison happens and read both values directly from registers.

## Notes

* Initially, registers were not accessible because the program had already exited.
* Breakpoints must be placed before the comparison occurs.
* Using `strcmp@plt` ensures we hook the correct call inside the binary.

## Conclusion

This challenge demonstrates a classic dynamic analysis technique:

* Instead of reversing logic, extract secrets at runtime.

Final flag:

```
HOWO{REVERSING-A-COMPLEX-XOR}
```

# Howosec's Crackme Write-up

## Genel Bakış

Bu challenge, kullanıcıdan bir şifre isteyen ve doğru girildiğinde flag veren bir binary üzerine kuruludur.

Statik analiz yerine, GDB kullanarak dinamik analiz ile çözüme ulaştık.


## Program Davranışı

Binary çalıştırıldığında:

```bash
./program
```

Şu mesaj gelir:

```
Insira sua senha:
```

Yanlış şifre girilirse:

```
Você errou hahahahah
```

Doğru şifre girilirse:

```
Aqui está sua flag: HOWO{REVERSING-A-COMPLEX-XOR}
```
Tabi bu mesajı hak etmemiz lazım :)

## Çözüm Stratejisi

Binary'nin `strcmp` ile şifre karşılaştırması bekleniyor.

Bu nedenle:

* `strcmp` fonksiyonuna breakpoint koyduk
* Argümanları register’lardan okuduk
* Doğru şifreyi direkt elde ettik


## Adım Adım Çözüm

### 1. GDB ile aç

```bash
gdb ./program
```

### 2. strcmp fonksiyonunu bul

```gdb
info functions strcmp
```

### 3. Breakpoint koy

```gdb
b strcmp@plt
```

### 4. Programı çalıştır

```gdb
run
```

Herhangi bir input gir:

```
hello
```

### 5. Breakpoint tetiklenir

Bu noktada:

* `$rdi` → kullanıcı inputu
* `$rsi` → gerçek şifre

---

### 6. Register’ları incele

```gdb
x/s $rdi
```

```
"hello"
```

```gdb
x/s $rsi
```

```
"senhafoda1234567890"
```

Doğru şifre elde edildi.

### 7. Programı tekrar çalıştır

```bash
./program
```

Şifreyi gir:

```
senhafoda1234567890
```

### 8. Flag'i al

```
Aqui está sua flag: HOWO{REVERSING-A-COMPLEX-XOR}
```

## Neden Çalışır?

`strcmp` fonksiyonu:

```c
strcmp(kullanici_input, dogru_sifre)
```

x86_64 mimarisinde:

* 1. argüman → `rdi`
* 2. argüman → `rsi`

Breakpoint ile bu değerleri doğrudan okuyabiliyoruz.

## Sonuç

Dinamik analiz ile:

* Binary’nin iç mantığını çözmeden
* Runtime sırasında kritik veriyi elde ettik

Final flag:

```
HOWO{REVERSING-A-COMPLEX-XOR}
```
