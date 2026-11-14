# TryHackMe — Network Essentials Write-up

Bu yazımda, TryHackMe Cyber Security Path içindeki Module 5'te yer alan "Network Essentials" odasını nasıl tamamladığımı, odadaki temel ağ kavramlarını ve soruların cevaplarını kendi bakış açımla özetledim.
Oda biraz sözel ve teorik ağırlıklı olduğu için konuları kafamda daha iyi canlandırabilmek adına her birine günlük hayattan basit birer benzetme eklemek istedim.

---

## Task 1 — Introduction

Bu görevde odanın hedeflerini okudum. Bilgisayarımın ağa bağlandığında kendi kendine nasıl ayarlandığını, paketlerin hedefe giderken kaç ülkeden geçtiğini ve tek bir genel IP adresiyle evdeki tüm cihazların internete nasıl çıktığını öğreneceğimizi gördüm.
Bu oda, "Networking Concepts" odasının devamı niteliğindeydi ve DHCP, ARP, NAT, ICMP, Ping ve Traceroute gibi protokolleri kapsıyordu. Bu odaya başlamadan önce "Network Concepts" bitirilmeeli!

## Task 2 — DHCP: Give Me My Network Settings

Bu görevde, bir ağa bağlandığımızda cihazımızın otomatik olarak IP adresi, subnet mask, varsayılan ağ geçidi ve DNS sunucusu bilgilerini nasıl aldığını öğrendim. Bu işi **DHCP (Dynamic Host Configuration Protocol)** yapıyor.
Manuel ayarlamak sunucular için mantıklı olabilir ama telefonum veya dizüstü bilgisayarım için otomatik olması büyük kolaylık. Ayrıca iki cihaza aynı IP adresinin verilmesi gibi çakışmaları da DHCP engelliyor.
Protokol, UDP 67 ve 68 numaralı portları kullanıyor ve **DORA** (Discover, Offer, Request, Acknowledge) adı verilen 4 adımlı bir süreçle çalışıyor.

*Benzetme:* DHCP'yi, yeni bir şehre taşındığımda belediyeye gidip bana bir adres ve posta kodu tahsis etmeleri gibi düşünüyorum.
Ben "Buradayım ve bir adrese ihtiyacım var" diyorum (Discover).
Belediye bana uygun bir adres öneriyor (Offer).
Ben "Tamam, bu adresi istiyorum" diyorum (Request).
Belediye de "Adres artık senin" diyerek onaylıyor (Acknowledge).

**Soru 1:** DHCP, ağ yapılandırmasını sağlamak için kaç adım kullanır?
**Cevabım:** **4**. Süreç Discover, Offer, Request ve Acknowledge adımlarından oluşur.

**Soru 2:** Bir istemci, DHCP Discover paketi gönderdiğinde hangi hedef IP adresini kullanır?
**Cevabım:** **255.255.255.255**. Çünkü istemci henüz bir sunucu bulamadığı için ağdaki herkese yayın (broadcast) yapar.

**Soru 3:** Bir istemci, DHCP üzerinden IP ağ yapılandırması almaya çalışırken hangi kaynak IP adresini kullanır?
**Cevabım:** **0.0.0.0**. Çünkü istemcinin henüz atanmış bir IP adresi yoktur; bu adres "benim henüz bir kimliğim yok" anlamına gelir.

## Task 3 — ARP: Bridging Layer 3 Addressing to Layer 2 Addressing

Bu görevde, aynı yerel ağdaki cihazların birbirleriyle konuşabilmesi için **IP adresini (Layer 3)** **MAC adresine (Layer 2)** çeviren **ARP (Address Resolution Protocol)**'ü öğrendim. Ağdaki bir cihaz, "Bu IP adresi kimin?" diye sorduğunda, herkes duysun diye yayın yapar ve doğru cihaz kendi MAC adresini bildirir.

*Benzetme:* ARP'yi, bir apartmanda birine ulaşmak istemem ama sadece kapı numarasını (IP) bilmem, ismini (MAC) bilmemem gibi düşünüyorum. Apartmanın hoparlöründen "Daire 5'te oturan kim?" diye soruyorum (ARP Request). Daire 5'teki kişi "Benim, adım Ahmet" diye cevap veriyor (ARP Reply). Böylece hem kapı numarasını hem de ismi eşleştirmiş oluyorum.

**Soru 1:** Bir ARP İsteğinde (ARP Request) kullanılan hedef MAC adresi nedir?
**Cevabım:** **ff:ff:ff:ff:ff:ff**. Çünkü istek tüm ağa yayınlanır; bu MAC adresi "herkes duysun" anlamına gelen yayın adresidir.

**Soru 2:** Yukarıdaki örnekte 192.168.66.1'in MAC adresi nedir?
**Cevabım:** **44:df:65:d8:fe:6c**. Çünkü görseldeki "is-at" ifadesi, o IP adresine karşılık gelen MAC adresini gösteriyordu.

## Task 4 — ICMP: Troubleshooting Networks

Bu görevde, ağ bağlantısını test etmek ve sorunları teşhis etmek için kullanılan **ICMP (Internet Control Message Protocol)**'ü öğrendim. `ping` komutu bir hedefe "Echo Request" gönderir ve "Echo Reply" bekler. `traceroute` ise paketin hedefe giderken hangi yönlendiricilerden (router) geçtiğini adım adım gösterir. `traceroute`'un çalışabilmesi için IP başlığındaki **TTL (Time-to-Live)** alanının sıfıra ulaşması gerekir.

*Benzetme:* ICMP'yi, bir arkadaşıma mektup gönderip "Sana ulaştı mı?" diye sormam gibi düşünüyorum. `ping` ile "Orada mısın?" derim ve cevap beklerim. `traceroute` ise mektubun geçtiği her postaneyi tek tek kaydetmek gibi; her postane mektubu alınca üzerindeki "geçerlilik süresini" (TTL) bir azaltır, süre bitince mektup geri döner ve ben hangi postanede kaldığını anlarım.

**Soru 1:** Yukarıdaki örnek görsellere göre, yankı (ping) isteğinde kaç bayt gönderilmiştir?
**Cevabım:** **40**. Çünkü ping isteğinin veri kısmında 40 bayt veri taşınıyordu.

**Soru 2:** `traceroute` komutu hangi IP başlık alanının sıfıra ulaşmasını gerektirir?
**Cevabım:** **TTL**. Çünkü her yönlendirici TTL değerini bir azaltır; sıfıra ulaşınca paket düşürülür ve kaynak cihaza ICMP "Time Exceeded" mesajı gönderilir.

## Task 5 — Routing

Bu görevde, paketlerin farklı ağlar arasında hedefe nasıl yönlendirildiğini öğrendim. Yönlendiriciler (router), **yönlendirme tablolarını (routing table)** kullanarak hedef IP adresine göre karar verir. Yönlendirme statik (elle yapılandırılmış) veya dinamik (protokoller aracılığıyla otomatik öğrenilen) olabilir. Odada bahsedilen dinamik yönlendirme protokollerinden **EIGRP (Enhanced Interior Gateway Routing Protocol)**, Cisco'ya özgü (proprietary) bir protokoldür.

*Benzetme:* Routing'i, bir şehirdeki trafik polisi gibi düşünüyorum. Ben (bir paket) bir adrese gitmek istiyorum. Polis (router), elindeki trafik haritasına (routing table) bakarak bana "Şu yoldan git, sonra sağa dön" diyor. Eğer harita sürekli güncelleniyorsa (dinamik routing), o anki en hızlı güzergahı seçiyor; eğer harita sabit ve elle çizilmişse (statik routing), her zaman aynı yolu kullanıyorum.

**Soru 1:** Bu görevde tartışılan yönlendirme protokollerinden hangisi Cisco'ya özgü (proprietary) bir protokoldür?
**Cevabım:** **EIGRP**. Çünkü EIGRP, yalnızca Cisco cihazlarında çalışacak şekilde tasarlanmış bir protokoldür.

## Task 6 — NAT

Bu görevde, özel (private) IP adreslerinin genel (public) IP adreslerine nasıl çevrildiğini öğrendim. **NAT (Network Address Translation)**, evdeki birden çok cihazın tek bir genel IP adresini paylaşarak internete çıkmasını sağlar. Bu sayede iç ağdaki cihazlar dışarıdan doğrudan görünmez, bu da bir miktar güvenlik ve IP tasarrufu sağlar. NAT'ın statik, dinamik ve port tabanlı (PAT) türleri vardır.

*Benzetme:* NAT'yi, bir apartmanın tek bir sokak kapısı ve tek bir adresi olması gibi düşünüyorum. Dairelerin (iç cihazların) kendi iç kapı numaraları var ama dışarıdan bakıldığında herkes aynı binanın adresini görüyor. Postacı (dış dünya) mektubu binanın adresine getiriyor, görevli (router/NAT) da mektubu doğru daireye yönlendiriyor.

**Soru 1:** Yukarıdaki ağ diyagramında, telefonun internete erişirken kullanacağı genel IP adresi nedir?
**Cevabım:** **212.3.4.5**. Çünkü telefonun özel IP'si (192.168.0.137), NAT ile bu genel IP adresine çevriliyordu.

**Soru 2:** Yönlendiricinin sonsuz işlem gücüne sahip olduğunu varsayarsak, yaklaşık olarak kaç bin eşzamanlı TCP bağlantısı sürdürebilir?
**Cevabım:** **65**. Çünkü bir TCP bağlantısı, kaynak IP, kaynak port, hedef IP ve hedef port olmak üzere 4 parametre ile tanımlanır; bu da teorik olarak 65535 farklı bağlantıya (yaklaşık 65 bin) izin verir.

## Task 7 — Help the Computer

Bu görevde, öğrendiklerimi bir arada kullanarak etkileşimli bir siteye eriştim ve son bayrağı elde ettim.

**Soru:** Siteyi ziyaret ederek talimatları izleyin ve bayrağı elde edin.
**Cevabım:** **THM{computer_is_happy}**. Çünkü site, doğru yapılandırma adımlarını tamamladıktan sonra bu bayrağı gösteriyordu.

---

## Kafamda Canlandırmak İçin: Bir İsteğin Yolculuğu

Diyelim ki evimdeki bilgisayardan `www.tryhackme.com` adresine bir istek gönderiyorum. Bu isteğin yolculuğu kısaca şöyle:

1.  **DHCP (Evden Çıkış):** Bilgisayarım ağa ilk bağlandığında DHCP'den bir IP adresi, ağ geçidi ve DNS sunucusu alır. Böylece "kimlik kazandım" ve "dışarıya nasıl çıkacağımı" öğrendim.
2.  **DNS (Adres Sorgusu):** `www.tryhackme.com` yazdığımda, DNS sunucusuna "Bu ismin IP adresi ne?" diye sorarım. Bana sitenin genel IP adresini söyler.
3.  **ARP (Yerel Ağda Yön Bulma):** Bu IP adresine gitmek için önce kendi ağ geçidime (router'ıma) ulaşmam gerekir. Router'ımın IP'sini biliyorum ama MAC adresini bilmiyorum. ARP ile "Bu IP kimin?" diye sorar ve router'ımın MAC adresini öğrenirim.
4.  **NAT (Dışarıya Çıkış):** İsteğim router'ıma ulaştığında, router benim özel IP adresimi kendi genel IP adresiyle değiştirir (NAT). Artık dış dünya isteği router'ımın genel IP'sinden geliyormuş gibi görür.
5.  **Routing (İnternette Yolculuk):** İstek, internetteki bir dizi yönlendiriciden geçerek hedef sunucuya ulaşır. Her yönlendirici, yönlendirme tablosuna bakarak isteği bir sonraki durağa yönlendirir.
6.  **ICMP (Yolculuğu İzleme):** Eğer isteğin hangi yollardan geçtiğini merak edersem, `traceroute` komutuyla TTL mekanizmasını kullanarak her duraktan bilgi alabilirim.
7.  **Geri Dönüş:** Sunucudan gelen cevap, aynı yollardan geri döner ve router'ım NAT tablosunu kullanarak cevabı bana, yani doğru özel IP adresine iletir.

---

## Öğrendiklerimin Özeti

- Cihazların ağa otomatik katılmasını ve IP almasını sağlayan şey **DHCP**'dir (DORA süreci).
- Yerel ağda IP adreslerini MAC adreslerine çeviren şey **ARP**'dir.
- Ağ sorunlarını teşhis etmek ve yolu izlemek için **ICMP** (ping, traceroute) kullanılır.
- Paketlerin farklı ağlar arasında hedefe gitmesini sağlayan şey **Routing**'dir (yönlendirme tabloları, statik/dinamik).
- Birden çok özel IP'nin tek bir genel IP ile internete çıkmasını sağlayan şey **NAT**'tir.

Bu oda, ağ dünyasının görünmez kahramanlarını tanımamı sağladı. Artık bir web sitesine tıkladığımda arkada neler olup bittiğini çok daha net hayal edebiliyorum.
