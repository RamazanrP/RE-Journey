Crackmes.one: "Access me please" - Static Analysis 


#  Crackmes.one: "Access me please" - Static Analysis & Reverse Engineering

##  Overview
This repository contains the reverse engineering process and static analysis of the "Access me please" binary from crackmes.one. The objective was to analyze an x86-64 Linux ELF executable, bypass its authentication mechanism, and retrieve the hidden flag (password). 

##  Phase 1: Initial Assessment
Upon extracting the binary, the first step was to identify the file architecture and set the correct execution environment.
Initially, the file lacked execution privileges (it was in read-only mode for execution). In Linux environments, security mechanisms prevent downloaded binaries from running directly. 
I modified the file permissions using the terminal to grant executable rights:
`chmod +x Accessme`

##  Phase 2: Static Analysis
Instead of guessing the password, I utilized **Ghidra** to perform static analysis and disassemble the machine code. 
1. Imported the binary into Ghidra and ran Auto-Analysis to map the memory and decompile the assembly instructions into readable C code.
2. Navigated to the `Symbol Tree` and located the `main` function to inspect the core logic of the program.

##  Phase 3: Vulnerability Discovery & Exploitation
Within the decompiled `main` function, I identified the password validation logic. The program uses `scanf` to take user input and stores it in a local variable (`local_14`).

The critical vulnerability was a hardcoded comparison:
c
if (local_14 == 0xb7b5) {
    printaccess();
}

## 🇹🇷 Türkçe Sürüm

###  Özet
Bu rapor, crackmes.one platformundaki "Access me please" dosyasının tersine mühendislik sürecini içermektedir...

###  Adım 1: İlk İnceleme ve Yetkilendirme
Dosyayı indirdikten sonra ilk olarak mimarisini inceledim ve Linux ortamında çalıştırılabilmesi için yetkilerini düzenledim. İndirilen dosyalar varsayılan olarak okuma modunda gelir, bu yüzden terminal üzerinden `chmod +x Accessme` komutu ile executable (çalıştırılabilir) yetkisi verdim.

###  Adım 2: Statik Analiz (via Ghidra)
Makine kodunu okunabilir C formatına çevirmek için programı Ghidra'ya import edip Auto-Analysis başlattım. Decompiler penceresinden `main` fonksiyonuna girip kontrol bloklarını inceledim.

###  Adım 3: Şifre Çözümü
Kodda, kullanıcı girdisinin onaltılık (hex) tabanda `0xb7b5` değeri ile kıyaslandığını (`CMP`) fark ettim. Terminale bu şifreyi girebilmek için değeri onluk (decimal) tabana çevirdim:
* **Hex:** `0xb7b5` -> **Decimal:** `47029`
Bu dönüşümü hızlıca doğrulamak için aşağıdaki tek satırlık Python  scriptini de kullanabilirsiniz:

```python
# Hexadecimal değeri onluk (decimal) tabana çeviren Python kodu
hex_value = "0xb7b5"
decimal_value = int(hex_value, 16)

print(f"Hex: {hex_value} -> Decimal: {decimal_value}")
# Çıktı: Hex: 0xb7b5 -> Decimal: 47029
```
Dosyayı `./Accessme` ile çalıştırıp `47029` girdiğimde "Access Granted" mesajına ulaştım.

###  Bana Ne Kattı?
* **Yetki Yönetimi:** `chmod +x` mantığıyla tanışmış oldum.
* **Hex/Dec Dönüşümü:** İşlemcilerin hex formatındaki kıyaslamalarını, bizim anlayacağımız decimal formata çevirdim.
* **Ghidra Kullanımı:** Karmaşık assembly satırları yerine Decompiler ile C seviyesinde ilk okumamı yaptım.
