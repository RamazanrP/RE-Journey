## [Write-up] DebugMe (ENG & TR)

# 1. Introduction and Objective Analysis

In this study, a multi-stage Linux ELF binary was analyzed, which exploits low-level C capabilities, the Linux /proc filesystem, and signal handling mechanisms (Signal Handlers) to mislead reverse engineers.

Unlike traditional anti-debugging techniques that aim to detect and prevent reverse engineering, the program is built on a fascinating paradox: it requires an active debugger (Tracer) to execute successfully.

# 2. In-Depth Function Analysis

A. The Secret Weapon: TracerPid Detector (FUN_00101259)

This function checks for the presence of a debugger (Tracer) by reading the /proc/self/status file of the operating system. However, it does so using an unconventional, clever buffer overflow illusion:
```
char local_129 [10];
char local_11f [255];
...
__stream = fopen("/proc/self/status","r");
...
pcVar2 = fgets(local_129, 0x109, __stream); // Reads exactly 0x109 = 265 bytes!
```

Buffer Overflow Exploit (Stack Layout Magic):

The `local_129` array is only $10\text{ bytes}$ in size. Right after it on the stack, the `local_11f` array ($255\text{ bytes}$) begins.

The fgets function reads exactly $265\text{ bytes}$ of data into the address of `local_129`. This is a controlled buffer overflow by design.

The program reads each line of `/proc/self/status` one by one and stops when it finds the "TracerPid:" line:

The string "TracerPid:" is exactly $10\text{ characters}$ long, perfectly filling the `local_129` array.

The rest of the line automatically overflows and spills directly into the adjacent `local_11f` variable!

Then, `atoi(local_11f)` is called, converting the overflowed Tracer PID value into an integer and returning it.

If no debugger is present: TracerPid is $0$. The function returns $0$.

If a debugger (GDB/Strace, etc.) is present: It returns the $\text{PID}$ of the tracing process.

# 3. Multi-Stage Section Controls

Stage 1: Signal Triggering (SIGFPE)

The setup in the main function is as follows:
```
signal(8, FUN_00101319); // 8 = SIGFPE (Floating Point Exception)
...
iVar2 = thunk_FUN_00101259(); // Returns the TracerPid value
if ((int)(0x43 / (long)iVar2) != 0x43) { puts("Fail"); }
```

Solution: To bypass Stage 1 and jump to the `FUN_00101319` signal handler function, we must trigger an arithmetic exception (Division by Zero).

For this, `iVar2` must be $0$.

Thus, we must run the program without a debugger (directly from the terminal) so that TracerPid returns $0$.

When it returns $0$, the $67 / 0$ operation throws a SIGFPE (Signal 8). Instead of crashing, the program jumps to the `FUN_00101319` handler. The terminal prints Pass!

Stage 2: The Paradox (Debugger Requirement)

After the signal is triggered, control transfers to the `FUN_00101319` function which contains a historical trap:
```
signal(8, (__sighandler_t)0x0); // Reset signal handler to DEFAULT (crash) mode!
...
iVar1 = thunk_FUN_00101259(); // Read TracerPid
iVar2 = thunk_FUN_00101259(); // Read TracerPid
if (iVar1 / iVar2 != 0) { ... }
```

The Dreadful Reality: Since the signal handler is reset to default, any subsequent division by zero will instantly crash the program (Core Dump).

If no debugger is attached to the program yet, both `iVar1` and `iVar2` will be $0$.

In this case, a $0 / 0$ operation occurs, and the program terminates in Stage 2 with a division-by-zero crash!

Bypass Condition: To pass Stage 2, `iVar1` and `iVar2` must be non-zero (i.e., the PID of an active debugger). For example, $4056 / 4056 = 1 \neq 0$ succeeds and avoids a crash.

Stage 3: Exact Identity Matching

The reverse engineer who successfully passes Stage 2 is met with one final lock:
```
if (DAT_00104074 == iVar1) {
  puts("Pass");
  __s = "Well done :)";
}
```

`DAT_00104074` is the integer we initially passed as an argument (atoi(argv[1])).

`iVar1` is the actual PID of the tracing debugger process.

Bypass Condition: The argument we pass to the program must match the exact PID of our background GDB or debugger process!

# 4. Definitive & Verified Solution Guide (Live GDB Kılavuzu / Guide)

The following steps describe the sequential and verified terminal protocol required to bypass the binary's protective mechanisms and capture the final victory message.

Step 1: Determine the Tracer Process PID

In a new terminal tab, run the following command to find the PID (Process ID) of the active GDB process:
```
$ pidof gdb
421661
```

(For this example, let's assume the returned PID value is 421661. This number is our key.)

Step 2: Launch the Program under GDB

Start the program under GDB, passing the discovered PID value as an argument:
```
$ gdb ./DebugMe
```

Step 3: PIE-Based Breakpoint Configuration and Turning Pagination Off

In order, execute the following commands to disable pagination, pause the program at the entry point to map memory, find the base address, and place a breakpoint at the thunk function wrapper:
```
(gdb) set args 421661
(gdb) set pagination off
(gdb) starti
(gdb) info proc mappings
```

At the very top of the output table, you will see the base address where the program is loaded. For example: $0x0000555555554000$.

Add the $0x1314$ offset retrieved from Ghidra to this base address and set the breakpoint:
```
(gdb) break *(0x555555554000 + 0x1314)
Breakpoint 1 at 0x555555555314
(gdb) continue
```

Step 4: Bypassing Stage 1 (Triggering Division by Zero)

The program will hit the breakpoint and pause:
```
Breakpoint 1, 0x0000555555555314 in ?? ()
```

Now, run the function until exit, then force the `RAX` register (which holds the TracerPid return value) to 0 to trigger the arithmetic exception:
```
(gdb) finish
Run till exit from #0  0x0000555555555314 in ?? ()
0x0000555555555131 in ?? ()
(gdb) set $rax = 0
(gdb) continue
```

You will see the confirmation message indicating that the arithmetic exception occurred successfully:
```
Program received signal SIGFPE, Arithmetic exception.
0x0000555555555139 in ?? ()
```

Step 5: Passing the Signal to the Program and the Grand Finale

To deliver the division-by-zero exception caught by GDB back to the program's own signal handler, run the following command:
```
(gdb) signal SIGFPE
Continuing with signal SIGFPE.
Pass
DebugMe stage 2: 
Breakpoint 1, 0x0000555555555314 in ?? ()
```

The terminal will print Pass and transition to Stage 2. In Stage 2, the program will call the thunk wrapper twice more to verify the true debugger PID and hit the breakpoint again.

From this point onward, do not reset any register values. Simply issue continue commands to let the program successfully read the actual PID:
```
(gdb) continue
Continuing.
Breakpoint 1, 0x0000555555555314 in ?? ()
(gdb) continue
Continuing.
Pass
DebugMe stage 3: Pass
Well done :)
[Inferior 1 (process 422057) exited normally]
```
# 1. Giriş ve Hedef Analizi

Bu çalışmada, C dilinin (low-level) yeteneklerini, Linux /proc dosya sistemini ve sinyal yakalama mekanizmalarını kullanarak ters köşe yapmayı hedefleyen çok aşamalı bir Linux ELF dosyası incelenmiştir.

Program, geleneksel anti-debugging yöntemlerinin aksine, çalışabilmek için aktif bir debugger talep eden bir paradoks üzerine kurulmuştur.

# 2. Fonksiyon Analizleri

A. TracerPid Dedektörü (FUN_00101259)

Bu fonksiyon, Linux işletim sisteminin `/proc/self/status` dosyasını okuyarak süreci izleyen bir debugger (Tracer) olup olmadığını kontrol eder. Ancak bunu yaparken standart yöntemlerden farklı  bir bellek taşma durumu kullanır:
```
char local_129 [10];
char local_11f [255];
...
__stream = fopen("/proc/self/status","r");
...
pcVar2 = fgets(local_129, 0x109, __stream); // 0x109 = 265 byte okur!
```

 Bellek Taşma Hilesi:

`local_129` dizisi sadece 10 byte boyutundadır. Hemen ardından stack üzerinde `local_11f` dizisi (255 byte) başlar.

fgets fonksiyonu `local_129` adresine tam 265 byte veri okur. Bu durum bilerek tasarlanmış kontrollü bir bellek taşmasıdır.

`/proc/self/status` dosyasındaki her satır tek tek okunur. Program "TracerPid:" satırını bulduğunda durur:

"TracerPid:" kelimesi tam olarak 10 karakterdir ve `local_129` dizisini milimetrik olarak doldurur.

Satırın geri kalan kısmı otomatik olarak taşarak hemen arkasındaki `local_11f` değişkeninin içine dökülür!

Ardından `atoi(local_11f)` çağrısı yapılarak, taşan kısımdaki Tracer PID değeri tam sayıya çevrilir ve geri döndürülür.

Debugger yoksa: TracerPid değeri 0'dır. Fonksiyon 0 döner.

Debugger (GDB/Strace vb.) varsa: İzleyen sürecin PID değerini döner.

# 3. Çok Aşamalı Bölüm Kontrolleri

 Stage 1: Sinyal Tetikleme (SIGFPE)

Ana fonksiyonda kurulan düzenek şöyledir:
```
signal(8, FUN_00101319); // 8 = SIGFPE (Floating Point Exception)
...
iVar2 = thunk_FUN_00101259(); // TracerPid değerini döner
if ((int)(0x43 / (long)iVar2) != 0x43) { puts("Fail"); }
```

Çözüm: Stage 1'i geçip `FUN_00101319` sinyal handler fonksiyonuna zıplayabilmek için bölme işleminin hata vermesini (Sıfıra Bölme) sağlamalıyız.

Bunun için `iVar2` değeri 0 olmalıdır.

Yani programı hata ayıklayıcı olmadan (doğrudan terminalden) çalıştırmalıyız ki TracerPid değeri 0 dönsün.

0 dönünce 67 / 0 işlemi SIGFPE (Signal 8) fırlatır ve program çökmek yerine `FUN_00101319` fonksiyonuna ışınlanır. Ekrana Pass basılır!

 Stage 2: Paradoks (Debugger Gereksinimi)

Sinyal tetiklendikten sonra kontrolün geçtiği `FUN_00101319` fonksiyonu şöyledir:
```
signal(8, (__sighandler_t)0x0); // Sinyal yakalayıcı DEFAULT (çökme) moduna çekilir!
...
iVar1 = thunk_FUN_00101259(); // TracerPid oku
iVar2 = thunk_FUN_00101259(); // TracerPid oku
if (iVar1 / iVar2 != 0) { ... }
```

Sinyal yakalayıcı sıfırlandığı için bu aşamadan sonra yaşanacak en ufak bir sıfıra bölme hatası programı anında çökertecektir.

Eğer programa hala bir debugger bağlı değilse, hem iVar1 hem de `iVar2` değeri 0 olacaktır.

Bu durumda 0 / 0 işlemi gerçekleşecek, program sıfıra bölme hatasıyla Stage 2'de sonlanacaktır!

Geçiş Şartı: Stage 2'yi geçebilmek için `iVar1` ve `iVar2` değerlerinin sıfırdan farklı (yani bir debugger PID'si) olması gerekir.

Stage 3: Doğru Kimlik Eşleşmesi

Stage 2'yi geçen kişi için son bir if bloğu daha vardır:
```
if (DAT_00104074 == iVar1) {
  puts("Pass");
  __s = "Well done :)";
}
```

`DAT_00104074` bizim ilk başta parametre olarak girdiğimiz sayıdır (atoi(argv[1])).

`iVar1` ise bizi izleyen debugger sürecinin gerçek PID değeridir.

Geçiş Şartı: Programa argüman olarak verdiğimiz sayı, o an arkada çalışan GDB veya hata ayıklayıcımızın PID değeriyle eşleşmelidir!

# 4. Kesin ve Doğrulanmış Çözüm Rehberi (GDB Kılavuzu)

Aşağıdaki adımlar, programın kendi koruma mekanizmalarını alt ederek zafer mesajına ulaşmak için gerekli olan sıralı ve doğrulanmış terminal protokolünü içerir.

Adım 1: İzleyici Sürecin PID Değerini Öğrenin

Yeni bir terminal sekmesinde aşağıdaki komut ile arka planda çalışan GDB sürecinin PID (Process ID) numarasını bulun:
```
pidof gdb(Örneğin ekrana 421661 değeri dönmüş olsun. Bu bizim anahtarımızdır.)
```
Adım 2: Programı GDB ile başlatın

Bulduğunuz PID değerini argüman olarak vererek programı GDB altında başlatın:
```
gdb ./DebugMe
```

Adım 3: PIE Tabanlı Breakpoint Ayarlaması ve Sayfalama Kapatma

Sırasıyla aşağıdaki komutları girerek sayfalamayı devre dışı bırakın, taban adresi bulun ve thunk fonksiyonunun çağrıldığı yere breakpoint yerleştirin:
```
(gdb) set args 421661
(gdb) set pagination off
(gdb) starti
(gdb) info proc mappings
```

Çıkan tablonun en üstünde programın yüklendiği taban adresini göreceksiniz. Örneğin: 0x0000555555554000.

Ghidra üzerinden aldığımız 0x1314 offsetini bu adrese ekleyerek breakpoint koyuyoruz:
```
(gdb) break *(0x555555554000 + 0x1314)
(gdb) continue
```

Adım 4: Stage 1'i Geçmek (Sıfıra Bölme Tetikleme)

Program breakpoint'e çarptığında donacaktır:
```
Breakpoint 1, 0x0000555555555314 in ?? ()
```

Şimdi fonksiyonun bitmesini sağlayın ve TracerPid değerini tutan `RAX` register'ını zorla 0 yaparak sıfıra bölme hatasını tetikleyin:
```
(gdb) finish
(gdb) set $rax = 0
(gdb) continue
```

Ekranda aritmetik istisnanın oluştuğuna dair onay mesajını göreceksiniz:
```
Program received signal SIGFPE, Arithmetic exception.
0x0000555555555139 in ?? ()
```

Adım 5: Sinyali Programa İletmek ve Final

GDB'nin kabul ettiği bu sıfıra bölme istisnasını programın kendisine döndürün:
```
(gdb) signal SIGFPE
```

Ekrana Pass basılacak ve program Stage 2'ye geçecektir. Stage 2'de program thunk fonksiyonunu iki kez daha çağırıp gerçek debugger PID değerini doğrulamaya çalışacak ve yine breakpoint'e takılacaktır.

Bu andan itibaren başka hiçbir değeri sıfırlamadan programın gerçek PID değerini başarıyla okumasına izin vermek için sadece continue komutlarını verin:
```
(gdb) continue
# (Program aynı breakpoint'e ikinci kez takılır)
(gdb) continue
```

Saniyeler içinde tüm aşamalar doğrulanacak ve nihai çıktı ekrana dökülecektir:
```
Continuing.
Pass
DebugMe stage 3: Pass
Well done :)
[Inferior 1 (process 422057) exited normally]
```
