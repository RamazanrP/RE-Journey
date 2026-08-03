# SecureVault Write-up (ENG & TR)

# 🇬🇧 English

## Overview

This challenge initially appears to be an authentication problem where the user must enter a correct access code. However, analysis reveals that there is no real validation logic. Instead, the binary contains a classic **stack-based buffer overflow vulnerability**.

The goal is not to find the correct input, but to redirect execution flow to the `win` function.

## Analysis

Entry point:

`main(void)`

Flow:

- prints banner  
- calls `vulnerable_function`  
- prints `"Access denied"`  

This implies:

→ there is **no legitimate success path**

## Vulnerability

Inside `vulnerable_function`:

- `auStack_50 [64]` → 64-byte buffer  
- `read(0, ..., 0x100)` → reads 256 bytes  

This creates a:

→ **stack buffer overflow**

## Stack Layout

Typical layout:

- buffer (64 bytes)  
- saved frame pointer  
- return address  

Overflow allows:

→ overwriting return address

## Target Function

Hidden function:

`win(void)`

This function:

- prints success message  
- prints flag  
- executes `system("/bin/sh")`  

## Exploit Strategy

Goal:

→ overwrite return address  
→ redirect execution to `win`

## Offset

- buffer: 64 bytes  
- saved pointer: 8 bytes  

Total:

→ **72 bytes to reach return address**

## Payload Structure

`padding + win_address`

## Important Details

### Architecture

Binary is:

→ RISC-V 64-bit

Must be executed with:

→ `qemu-riscv64`

### Endianness

Addresses must be written in:

→ little endian format

## Result

Successful exploitation leads to:

- control flow hijack  
- execution of `win`  
- flag disclosure  
- shell access  

## Takeaways

- Not every challenge requires finding correct input  
- Exploitation can bypass logic entirely  
- Buffer overflow enables control flow manipulation

## Final Note

This is a classic:

→ **ret2win** challenge

The objective is:
→ not to solve the program but to control it

# 🇹🇷 Türkçe

## Genel Bakış

Bu challenge ilk bakışta bir **authentication** problemi gibi görünüyor. Program kullanıcıdan bir **access code** ister. Ancak yapılan analiz sonucunda gerçek bir doğrulama mekanizması olmadığı, bunun yerine klasik bir **buffer overflow (stack-based)** zafiyeti bulunduğu görüldü.
Amaç doğru şifreyi bulmak değil, programın kontrol akışını değiştirerek `win` fonksiyonuna ulaşmak.

## Analiz

Programın giriş noktası:

`main(void)`

Akış:

- başlık yazdırılır  
- `vulnerable_function` çağrılır  
- ardından `"Access denied"` mesajı basılır  

Buradan şu çıkarım yapılır:

→ normal akışta **başarı durumu yoktur**

## Zafiyet

Zafiyet `vulnerable_function` içindedir:

- `auStack_50 [64]` → 64 byte buffer  
- `read(0, ..., 0x100)` → 256 byte okuma  

Bu durum **stack buffer overflow** oluşturur.

## Stack Davranışı

Fonksiyon çağrısı sırasında stack şu şekildedir:

- buffer (64 byte)  
- saved frame pointer  
- return address  

256 byte input verilirse:

→ buffer taşar  
→ return address overwrite edilir  

## Hedef Fonksiyon

Binary içinde gizli bir fonksiyon bulunur:

`win(void)`

Bu fonksiyon:

- `[ACCESS GRANTED]` mesajı basar  
- flag’i yazdırır  
- `system("/bin/sh")` ile shell açar  

## Exploit Mantığı

Amaç:

→ `vulnerable_function` dönüş adresini `win` adresi ile değiştirmek  

## Offset Hesabı

- buffer: 64 byte  
- saved pointer: 8 byte  

Toplam **72 byte sonra return address**

## Payload

Payload yapısı = `padding + win_address`

## Önemli Detaylar

### Architecture

Binary:

→ RISC-V 64-bit

Bu yüzden doğrudan çalıştırılamadım.

Çözüm:

→ `qemu-riscv64` ile emülasyon

### Endianness

Adresler:

→ little endian formatında yazılmalıydı.

## Sonuç

Exploit başarıyla çalıştırıldığında:

- kontrol akışı ele geçirilir  
- `win` fonksiyonu çağrılır  
- flag elde edilir  
- shell açılır  

## Çıkarımlar

- Her zaman doğru input aranmaz  
- Bazı durumlarda kontrol akışı manipüle edilir  
- Buffer overflow → control flow hijack  

## Son Not

Bu challenge bir **ret2win** örneğidir.

Amaç:

→ programı çözmek değil programı kontrol etmektir  
