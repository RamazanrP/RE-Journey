## The Stack

Bu odada, program başlangıcında stack üzerinde bulunan verilere erişmeyi ve bu verileri kullanarak program akışını kontrol etmeyi öğrendik.

## 1. Argüman Sayısını Okumak (mov ile)

**Soru:** Program başlangıcında `rsp` stack'in en üstünü gösterir. `[xxx]` adresinde argüman sayısı (argc) bulunur. Bu değeri okuyup exit kodu olarak kullan.

**Çözüm:**

```asm
.intel_syntax noprefix
mov xxx, [xxx]
mov rax, 60
syscall
```

**Açıklama:**

- `[xxx]` doğrudan stack'in ilk elemanını okur.
- Bu değer programın kaç argümanla çağrıldığını söyler (program adı dahil).
- `exit` syscall'ı bu değeri çıkış kodu olarak kullanır.

**Derleme:**

```bash
nano argc.s
as -o argc.o argc.s
ld -o argc argc.o
/challenge/check ./argc
```
> Diğer sorular için derleme kısmı aynı olduğu için aynı satırları yazmaya gerek duymadım.
## 2. Offset ile Stack'ten Veri Okumak

**Soru:** Stack üzerinde `rsp`'den 128 bayt ileride gizli bir değer saklanmıştır. Bu değeri okuyup exit kodu olarak kullan.

**Çözüm:**

```asm
.intel_syntax noprefix
mov xxx, [xxx+128]
mov rax, 60
syscall
```

**Açıklama:**

- `[xxx+128]` ifadesi, stack'in başlangıcından 128 bayt sağa gider.
- Stack üzerindeki değerler 8 bayt sınırlarına hizalanmış olsa da, offset doğrudan bayt cinsindendir.

## 3. Double Dereference

**Soru:** Program bir argümanla çağrılır. Stack'te `[rsp+xx]` adresinde, ilk argümanın metninin bulunduğu adres (pointer) saklanır. Bu pointer'ı kullanarak argümanın değerini oku ve exit kodu olarak kullan.

**Çözüm:**

```asm
.intel_syntax noprefix
mov rdi, [rsp+xx]
mov xxx, [xxx]
mov rax, 60
syscall
```

**Açıklama:**

- `[rsp+xx]` → stack'ten ilk argümanın pointer'ını alır
- `[rdi]` → bu pointer'ın gösterdiği adresteki veriyi okur
- Burada `[rdi]` ile 8 bayt okunur, dolayısıyla argüman metni sayısal olarak yorumlanır.

## 4. `pop` ile Stack'ten Veri Çekmek

**Soru:** `pop` komutu, `[rsp]`'deki değeri okur, hedef register'a yazar ve `rsp`'yi **8 artırır**. Bu mekanizmayı kullanarak argüman sayısını oku ve exit kodu olarak kullan.

**Çözüm:**

```asm
.intel_syntax noprefix
pop xxx
mov rax, 60
syscall
```

**Açıklama:**

- `pop xxx` → `[rsp]`'deki değeri alır (argüman sayısı), `rdi`'ye kopyalar, ardından `rsp`'yi 8 artırır.
- Bu işlem sonrası stack'in tepesi bir sonraki elemana geçmiş olur.
- `mov rax, 60` ve `syscall` ile program sonlanır.

## Genel Değerlendirme

Bu odada öğrendiğimiz en önemli ders: Stack sadece bir veri yığını değil, aynı zamanda program başlangıcında argümanların ve işaretçilerin saklandığı kritik bir bellek bölgesidir.
`rsp`'den offset veya `pop` ile bu verilere erişmek, ilerideki sömürü modüllerinde işimize yarayacak ve de şu anki repomda diğer bir klasör olan `crackmes.one` daki bazı dosyalarda yarayadı (gdb kullanımında)
