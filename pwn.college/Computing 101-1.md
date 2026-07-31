# 🐧 Computer Memory 

Bu modül, assembly dilinde bellek adreslemenin (memory addressing) ve işaretçilerin nasıl çalıştığını uygulamalı olarak öğretti.
Artık sadece register'lar arasında veri taşımak yerine, doğrudan bellek üzerinde okuyarak (dereferencing) program davranışını kontrol edebiliyorum.

## 1. Temel Bellek Okuma

En temel seviyede, belirli bir adresteki değeri okuyup `rdi`'ye koyarak `exit` syscall'ı ile sonlandırdık.

- **Kullanım:** `mov rdi, [ADRES]`
- **Mantık:** Köşeli parantez `[]`, "bu adresteki değeri oku" anlamına gelir.

## 2. Register ile Adresleme (Pointer Kullanımı)

Bazen adres sabit olarak verilmez, bir register'da (örneğin `rax`) tutulur. Bu durumda register bir **pointer**  görevi görür.

- **Kullanım:** `mov rdi, [xxx]`
- **Mantık:** `xxx`'in içindeki değer bir adres olarak yorumlanır ve o adresteki veri `rdi`'ye kopyalanır.
- **Örnek:** Checker `xxx`'e `123400` koyar, `mov rdi, [xxx]` ile o adresteki gizli sayı okunur.

## 3. Offset (Adres Farkı) ile Adresleme

Bazen veri, pointer'ın gösterdiği adreste değil, o adresten belirli bir miktar (byte) ileride bulunur.

- **Kullanım:** `mov rdi, [rdi + *]`
- **Mantık:** `rdi`'deki adrese * eklenir ve o yeni adresteki değer okunur.
- **Kazanım:** Bu, diziler veya struct'lar içindeki elemanlara erişmenin temel yoludur.

## 4. Double Pointer

Adresler de tıpkı sayılar gibi bellek içinde saklanabilir. Yani bir adreste, başka bir adres tutulabilir.

- **Senaryo:** `rax` → `SECRET_LOCATION_2` → `SECRET_LOCATION_1` → `SECRET_VALUE`
- **Kod:**
  ```asm
  mov rdi, [blah]   ; blah'taki adresten SECRET_LOCATION_1'i oku
  mov rdi, [blah]   ; SECRET_LOCATION_1'deki gerçek değeri oku
  mov rax, 60
  syscall
  ```
- **Kazanım:** Bu sene bahar döneminde tanıştığım ve de acıyla öğrendiğim "pointer to pointer" (çift işaretçi) mantığını assembly seviyesinde deneyimledim :)

## 5. Derleme Süreci (Assemble & Link)

Her seferinde aynı adımları uyguladım:

1.  **Yaz:** `nano program.s`
2.  **Assemble:** `as -o program.o program.s`
3.  **Link:** `ld -o program program.o`
4.  **Çalıştır/Test Et:** `/challenge/check ./program`

## Genel Değerlendirme

Bu modül, assembly'de belleğe erişmenin temel yöntemlerini (doğrudan, dolaylı, offset'li ve çift seviyeli) deneyimletti.Bu beceri, ilerideki **Exploitation** ve **Binary Reverse Engineering** modüllerinde bana çok büyük avantaj sağlayacak.
