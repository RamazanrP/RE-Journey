# TryHackMe — Linux Shells Write-up

Bu belgede, TryHackMe üzerindeki "Linux Shells" odasını nasıl tamamladığımı, odada anlatılan temel kavramları, soruların cevaplarını ve bu cevapların arkasındaki mantığı kendi bakış açımla özetledim. Oda, Linux komut satırına ve shell betiklerine (scripting) sağlam bir giriş yapmak isteyenler için oldukça faydalıydı. Özellikle ofansif güvenlik tarafında shell kavramının ne kadar kritik olduğunu bir kez daha gördüm.

## Task 1 — Introduction to Linux Shells

Bu görevde shell kavramının ne olduğunu ve neden önemli olduğunu öğrendim. Kullanıcı ile işletim sistemi arasındaki etkileşimi sağlayan arayüze **shell** denir. Grafik arayüz (GUI) de bir shell türü olabilir ancak komut satırı arayüzü (CLI) çok daha verimli ve kaynak dostudur. Özellikle sızma testlerinde ve sistem yönetiminde CLI kullanımı neredeyse bir zorunluluktur.

**Soru:** Kullanıcı ile işletim sistemi arasındaki arabulucu kimdir?
**Cevabım:** **Shell**. Çünkü shell, kullanıcıdan aldığı komutları yorumlayıp işletim sistemine ileten ve sonucu kullanıcıya döndüren katmandır.

## Task 2 — How To Interact With a Shell?

Bu görevde SSH ile makineye bağlanıp temel komutları hatırladım. `pwd` ile mevcut dizinimi gördüm, `cd` ile dizin değiştirdim, `ls` ile dosyaları listeledim ve `grep` ile dosya içinde arama yaptım. Bu komutlar günlük Linux kullanımının temel taşlarıdır.

**Soru 1:** Çoğu Linux dağıtımında varsayılan shell nedir?
**Cevabım:** **Bash**. Çünkü Bourne Again Shell (Bash), neredeyse tüm popüler Linux dağıtımlarında standart olarak gelir.

**Soru 2:** Bir dizinin içeriğini listelemek için hangi komut kullanılır?
**Cevabım:** **ls**. Bu komut, bulunduğum dizindeki dosya ve klasörleri görüntülememi sağlar.

**Soru 3:** Bir dosya içinde herhangi bir şeyi aramak için hangi komut yardımcı olur?
**Cevabım:** **grep**. Büyük dosyalar içinde belirli bir deseni veya kelimeyi hızlıca bulmamı sağlar.

## Task 3 — Types of Linux Shells

Bu görevde farklı shell türlerini ve özelliklerini karşılaştırdım. En yaygın olanları Bash, Fish ve Zsh olarak gördüm. Her birinin kendine has avantajları var:

- **Bash:** Geleneksel, geniş betik desteği ve yaygın kullanım.
- **Fish:** Kullanıcı dostu, otomatik yazım düzeltme ve yerleşik sözdizimi renklendirme.
- **Zsh:** Gelişmiş özelleştirme ve eklenti desteği (örneğin oh-my-zsh).

`echo $SHELL` komutu ile aktif shell'imi gördüm. `cat /etc/shells` ile sistemde yüklü tüm shell'leri listeleyebileceğimi öğrendim. Kalıcı olarak shell değiştirmek için `chsh -s /usr/bin/zsh` gibi bir komut kullanılabileceğini not ettim[.

**Soru 1:** Hangi shell, kutudan çıktığı gibi (out-of-the-box) sözdizimi renklendirme özelliği ile gelir?
**Cevabım:** **Fish**. Çünkü Fish, yerleşik olarak sözdizimi renklendirmesi sunar; diğerlerinde bu özellik ya yoktur ya da eklenti ile eklenir.

**Soru 2:** Hangi shell'de otomatik yazım düzeltme yoktur?
**Cevabım:** **Bash**. Bash'in ne yerleşik sözdizimi renklendirmesi ne de otomatik yazım düzeltmesi vardır; bu özellikler Fish ve Zsh'de bulunur.

**Soru 3:** Geçerli oturumda daha önce çalıştırılan tüm komutları hangi komut gösterir?
**Cevabım:** **history**. Bash, geçmiş komutları bir dosyada tutar ve `history` komutu ile bunları listeleyebilirim.

## Task 4 — Shell Scripting and Components

Bu görevde shell betiği yazmanın temellerini öğrendim. Bir betik, tekrar eden görevleri otomatikleştirmek için bir araya getirilmiş komutlar dizisidi. Betik dosyaları `.sh` uzantısıyla oluşturulur ve başında **shebang** (`#!/bin/bash`) bulunur.

Temel yapı taşları:
- **Değişkenler:** `read` ile kullanıcıdan girdi alıp `$değişken` ile kullanma].
- **Döngüler:** `for i in {1..10}; do ... done` gibi yapılarla tekrarlı işler.
- **Koşullu ifadeler:** `if [ "$name" = "Stewart" ]; then ... else ... fi` ile karar verme.
- **Yorumlar:** `#` ile kodun anlaşılırlığını artırma.

Betiği çalıştırmak için önce `chmod +x betik.sh` ile çalıştırma izni vermem gerektiğini, ardından `./betik.sh` şeklinde çalıştırmam gerektiğini öğrendim. `./` kullanmamın nedeni, shell'in betiği PATH ortam değişkeninde aramasını engellemek ve doğrudan geçerli dizindeki dosyayı çalıştırmaktır.

**Soru 1:** Bash betiğinde kullanılan shebang nedir?
**Cevabım:** **#!/bin/bash**. Bu satır, betiğin hangi yorumlayıcı ile çalıştırılacağını belirtir.

**Soru 2:** Bir betiğe çalıştırma izni veren komut hangisidir?
**Cevabım:** **chmod +x**. Bu komut, dosyaya çalıştırma (`execute`) izni ekler.

**Soru 3:** Hangi betikleme özelliği tekrarlı görevleri yapılandırmamıza yardımcı olur?
**Cevabım:** **loops** (döngüler). Döngüler, aynı kod bloğunu birden çok kez çalıştırarak tekrarı otomatikleştirir.

## Task 5 — The Locker Script

Bu görevde öğrendiklerimi birleştirerek bir kasa (locker) betiği yazdım. Betik, kullanıcıdan sırasıyla isim, şirket adı ve PIN girmesini istiyor; eğer bilgiler `John`, `Tryhackme` ve `7385` ile eşleşirse erişime izin veriyor, aksi halde reddediyordu.

**Soru:** Kasa betiğinde kimlik doğrulaması için doğru PIN nedir?
**Cevabım:** **7385**. Çünkü betikteki `if [ "$pin" = "7385" ]` koşulu, yalnızca bu değeri kabul ediyor.

## Task 6 — Practical Exercise

Bu görevde `/home/user` dizininde bir betik buldum. Betiğin amacı, `/var/log` dizinindeki `.log` uzantılı dosyalarda `thm-flag01-script` anahtar kelimesini aramaktı. Betikteki boş tırnak işaretlerini (`""`) doldurmam gerekiyordu. Betiği düzelttikten sonra `root` yetkisiyle çalıştırdım ve bayrağı buldum.

**Soru 1:** Anahtar kelimeyi içeren dosya hangisidir?
**Cevabım:** **authentication.log**. Çünkü betik, `/var/log` dizinindeki tüm `.log` dosyalarını taradı ve bayrağı bu dosyada buldu.

**Soru 2:** Kedi nerede uyuyor?
**Cevabım:** **under the table**. Bayrağın bulunduğu dosyayı `cat` ile açtığımda bu cümleyi gördüm.


## İleri Düzey Linux Komut Satırı Öğrenimi İçin Kaynaklar

Bu odadan sonra Linux komut satırı ve shell betikleme bilgimi derinleştirmek için aşağıdaki kaynakları kullanmayı planlıyorum:

- **"Linux Basics for Hackers" (No Starch Press):** Ağ yönetimi, metin işleme, süreç yönetimi ve Python betikleme gibi konuları güvenlik odaklı bir yaklaşımla ele alan kapsamlı bir kitap.
- **"Black Hat Bash" (No Starch Press):** Bash ile görev otomasyonu, araç geliştirme ve "living-off-the-land" saldırıları gibi ileri düzey konulara odaklanan pratik bir rehber.
- **SANS Linux Command Line Forensics:** Adli bilişim perspektifinden Linux komut satırı kullanımını öğreten ileri düzey bir eğitim.
- **Linux Foundations Labs (GitHub):** SOC analistleri ve siber güvenlik profesyonelleri için hazırlanmış, uygulamalı Linux CLI laboratuvarları.
- **TryHackMe — Linux CLI: Shells & Bells:** Temel komut satırı becerilerini pekiştirmek için eğlenceli ve uygulamalı bir oda.
