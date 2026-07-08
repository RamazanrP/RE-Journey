## [Write-up] DebugMe (ENG & TR)

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
