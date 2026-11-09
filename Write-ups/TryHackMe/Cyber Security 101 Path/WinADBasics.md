# TryHackMe — Windows Active Directory Basics (winadbasics) Write-up

Bu belgede, TryHackMe Cyber Security 101  Path içindeki Windows Fundamentals modülünün son odası olan "Windows Active Directory Basics" (winadbasics) odasını nasıl çözdüğümü adım adım anlatıyorum. Odayı tamamlarken Active Directory'nin temel yapısını, kullanıcı yönetimini ve yetkilendirme süreçlerini uygulamalı olarak deneyimledim.
Sorulara geçmeden önce Tasklarda bize verilen değerli bilgileri sırasıyla yazayım. Odayı sadece soruları çözüp puan kasmak amacıyla çözmemelşyiz.

# Windows Active Directory Basics — Siber Güvenlik Notlarım

Bu belgede, `winadbasics` odasındaki her Task içerisinde yer alan ve sınav sorusu olmayan ancak bir siber güvenlik profesyoneli olarak bilmem gereken kritik teorik bilgileri kendim için özetledim.

## Task 2 — Windows Domains (Windows Domainleri)
Küçük bir ağda her bilgisayarı tek tek yönetmek mümkünken, ağ büyüdükçe (yüzlerce kullanıcı ve cihaz) bu yöntem sürdürülemez hale gelir.
İşte bu noktada **Windows Domain** devreye girer; temel amaç, kullanıcı ve bilgisayar yönetimini **Active Directory (AD)** adı verilen merkezi bir depoda toplamaktır.
Bu sayede kimlik bilgileri her cihazda ayrı ayrı tutulmak zorunda kalmaz, kullanıcı ağdaki herhangi bir bilgisayarda aynı hesapla oturum açabilir.
Yönetimsel açıdan bu, kimlik yönetimini ve güvenlik politikalarının (örneğin kontrol paneli erişiminin kısıtlanması) tüm ağa tek noktadan uygulanmasını sağlar.
Siber güvenlik açısından bu merkezileşme, saldırganlar için tek bir “kilit taşı” (Domain Controller) yaratır; bu nedenle DC’ler en kritik varlıklar olarak korunmalı ve izlenmelidir.

## Task 3 — Active Directory (AD Bileşenleri ve Yapısı)
Bir Windows domaininin kalbi **Active Directory Domain Services (AD DS)**'tir. Bu servis, ağdaki tüm nesneleri (kullanıcılar, gruplar, makineler, yazıcılar, paylaşımlar) barındıran bir dizindir.
AD’deki kullanıcı hesapları “güvenlik sorumlusu” (security principal) olarak adlandırılır; yani kimlik doğrulaması yapabilir ve kaynaklar üzerinde yetki alabilirler.
Kullanıcılar gerçek kişileri temsil edebileceği gibi, IIS veya MSSQL gibi servislerin çalışması için ayrılmış servis hesaplarını da temsil edebilir. Bu servis hesapları genellikle sadece ilgili servisi çalıştıracak minimum yetkiye sahip olmalıdır; aksi halde saldırganların yatay hareketi için bir basamak olurlar.
Ayrıca her bilgisayar AD’ye katıldığında bir **makine hesabı** oluşturulur; bu hesapların isimleri genellikle `$` ile biter (örneğin `TOM-PC$`). Bu yapıyı anlamak, AD ortamlarındaki yetki yükseltme ve kalıcılık mekanizmalarını analiz ederken bana temel oluşturur.

## Task 4 — Managing Users in AD (Kullanıcı Yönetimi ve Delegasyon)
AD’de kullanıcı yönetimi sadece hesap açmakla sınırlı değildir; asıl güvenlik etkisi **delegasyon** ile ortaya çıkar.
Delegasyon, belirli bir OU (Organizational Unit) veya nesne üzerinde başka bir kullanıcıya yetki verme işlemidir.
Örneğin, satış departmanındaki kullanıcıların şifrelerini sıfırlama yetkisini bir yönetici asistanına devredebilirim.
Bu, en az yetki ilkesinin (least privilege) bir uygulamasıdır ve gereksiz Domain Admin yetkisi vermekten daha güvenlidir.
Ancak yanlış yapılandırılmış bir delegasyon, saldırganların düşük yetkili bir hesapla kritik hesapların şifresini değiştirmesine veya erişim elde etmesine yol açabilir.
Bu nedenle delegasyon izinlerini düzenli olarak denetlemem ve özellikle şifre sıfırlama gibi hassas işlemleri izlemem gerekir.
PowerShelldeki `Set-ADAccountPassword` gibi komutlar bu tür işlemleri otomatize eder; saldırganlar da bu komutları kendi amaçları için kullanabileceğinden, komut satırı denetimleri (logging) kritik önem taşır.

## Task 5 — Managing Computers in AD (Bilgisayar Nesneleri ve OU Tasarımı)
AD’deki bilgisayarlar da birer nesnedir ve bu nesneler **OU (Organizational Unit)** adı verilen mantıksal konteynerler içinde gruplanır.
OU’lar, yalnızca düzen sağlamakla kalmaz; aynı zamanda GPO’ların (Grup İlkeleri) uygulanacağı hedef kitleyi belirler.
Sunucular ile iş istasyonlarını (workstation) ayrı OU’lara ayırmak, güvenlik açısından kritik bir tasarım kararıdır. Çünkü sunuculara uygulanacak bir GPO (örneğin daha sıkı güvenlik duvarı kuralları veya farklı denetim ilkeleri) ile kullanıcı bilgisayarlarına uygulanacak GPO’lar farklı olmalıdır.
Ayrım yapmazsam, bir kullanıcı iş istasyonu için hazırladığım esnek bir politika yanlışlıkla kritik bir sunucuya uygulanabilir ve bu da savunma katmanlarımı zayıflatır. Bu nedenle OU yapısını kurarken “neyin nereye ait olduğunu” ve “hangi politikanın kimi etkileyeceğini” net bir şekilde planlamam gerekir.

## Task 6 — Group Policies (Grup İlkeleri ve Dağıtımı)
**Group Policy Objects (GPO)**'lar, kullanıcı ve bilgisayar ayarlarını merkezi olarak dayatmak için kullanılan yapılandırma koleksiyonlarıdır.
GPO’lar domaindeki makinelere **SYSVOL** adı verilen ağ paylaşımı üzerinden dağıtılır; bu paylaşımın güvenliği ve bütünlüğü, tüm domainin yapılandırma bütünlüğü için hayati önem taşır.
Bir GPO hem kullanıcı hem de bilgisayar ayarlarını aynı anda uygulayabilir; bu esneklik yönetimi kolaylaştırırken, yanlış yapılandırılmış bir GPO tüm domaini etkileyebilecek bir güvenlik açığına dönüşebilir.
Saldırganlar, kalıcılık sağlamak veya savunmayı zayıflatmak için GPO’ları kötüye kullanabilir (örneğin, tüm makinelerde güvenlik duvarını kapatmak veya zararlı bir betiği çalıştırmak için).
Bu nedenle GPO değişikliklerini izlemem, yalnızca yetkili yöneticilerin GPO oluşturup değiştirebildiğinden emin olmam ve SYSVOL erişimini sıkı denetlemem gerekir.

## Task 7 — Authentication Methods (Kerberos vs NetNTLM)
AD ortamlarında kimlik doğrulama için iki ana protokol kullanılır: **Kerberos** ve **NetNTLM**. Güncel Windows sürümlerinde tercih edilen varsayılan protokol Kerberos’tur.
Kerberos’ta kullanıcı önce **Ticket Granting Ticket (TGT)** alır; bu bilet ile daha sonra istediği servisler için **TGS (Ticket Granting Service)** bileti talep eder.
Bu bilet tabanlı yapı, kullanıcının parolasının ağ üzerinden hiçbir zaman doğrudan gönderilmemesini sağlar. Öte yandan NetNTLM, eski bir challenge-response protokolüdür ve güncel Windows sürümlerinde varsayılan olarak tercih edilmez.
NetNTLM kullanılsa bile kullanıcının parolası (veya hash’i) ağ üzerinden asla açıkça iletilmez; ancak yine de ele geçirilen bir NetNTLM hash’i “pass-the-hash” saldırılarında kullanılabildiği için ciddi bir risk oluşturur.
Bu nedenle bir savunmacı olarak ağda NetNTLM kullanımını mümkün olduğunca kısıtlamalı, Kerberos’a zorlamalı ve özellikle 4771, 4776 gibi Kerberos hata olaylarını ve anormal bilet taleplerini izlemeliyim.

## Task 8 — Trees, Forests and Trusts (Ağaçlar, Ormanlar ve Güven İlişkileri)
AD yapısı sadece tek bir domainden ibaret değildir; ölçek büyüdükçe **Tree (Ağaç)** ve **Forest (Orman)** yapıları devreye girer. Aynı kök domaini paylaşan birden çok domain bir **ağaç** oluşturur; farklı ağaçların bir araya gelmesiyle de **orman** meydana gelir.
Bu yapılar arasında kaynak paylaşımını ve kimlik doğrulamayı mümkün kılan şey **güven ilişkileridir (trusts)**. Güven ilişkileri, bir domaindeki kullanıcıların başka bir domaindeki kaynaklara erişmesine izin verir.
Ancak bu güvenler, saldırganlar için de yatay hareket ve yetki yükseltme fırsatları yaratır. Özellikle eski ve zayıf yapılandırılmış güven ilişkileri (örneğin, tek yönlü ve filtrelenmemiş güvenler) bir domaindeki ele geçirilmiş bir hesabın tüm ormana yayılmasına neden olabilir.
Bu nedenle orman ve güven yapılandırmalarını anlamam, saldırı yollarını (attack paths) analiz ederken ve savunma stratejimi belirlerken bana büyük avantaj sağlar.

## Task 9 — Conclusion (Genel Değerlendirme)
Bu oda boyunca Active Directory’nin sadece bir “kullanıcı yönetim aracı” olmadığını, aynı zamanda bir kurumsal ağın tüm güvenlik duruşunu belirleyen merkezi bir kimlik ve politika katmanı olduğunu gördüm.
Domain yapısı, OU tasarımı, delegasyon, GPO’lar ve kimlik doğrulama protokolleri bir bütün olarak hem saldırganların hedef aldığı hem de savunmacıların sıkı denetlemesi gereken alanlardır.
Bu odadaki bilgiler, ileride yapacağım AD saldırıları (Kerberoasting, pass-the-hash, GPO abuse vb.) ve savunma (log izleme, yetki denetimi, OU sertleştirme) çalışmalarım için sağlam bir temel oluşturdu.
---

## Task 1 — Introduction
- Bu görevde herhangi bir soru yer almıyordu; odanın genel hedeflerini okuyarak başladım.

## Task 2 — Windows Domains
- Windows domain yapısında kimlik bilgilerinin merkezi olarak saklandığı yapıyı **Active Directory** olarak yanıtladım.
- Active Directory servislerini çalıştıran sunucuyu **Domain Controller** olarak belirledim.
- Bu görevde ayrıca RDP ile makineye bağlanmak için gerekli bilgileri not aldım.

## Task 3 — Active Directory
- Bir domaindeki tüm bilgisayarları ve kaynakları normalde yöneten grubu **Domain Admins** olarak buldum.
- `TOM-PC` adlı bir makinenin makine hesabı adının **TOM-PC$** olacağını tespit ettim.
- Yeni bir Quality Assurance departmanı için politikaların tutarlı uygulanabilmesi amacıyla kullanılacak konteyner türünü **Organizational Units** olarak yanıtladım.

## Task 4 — Managing Users in AD
- Bu görevde, Phillip kullanıcısına Sales OU'su üzerinde delegasyon yetkisi verdim ve onun hesabıyla Sophie'nin şifresini sıfırladım.
- RDP bağlantısı için `THM\phillip` kullanıcı adını ve `Claire2008` şifresini kullandım.
- Sophie'nin şifresini PowerShell üzerinden `Set-ADAccountPassword sophie -Reset -NewPassword (Read-Host -AsSecureString -Prompt 'New Password') -Verbose` komutuyla değiştirdim.
- Sophie'nin masaüstünde bulduğum bayrağı **THM{thanks_for_contacting_support}** olarak not ettim.
- Bir kullanıcıya bir OU veya AD nesnesi üzerinde yetki verme sürecini **Delegation** olarak tanımladım.

## Task 5 — Managing Computers in AD
- Bilgisayarları organize ettikten sonra Workstations OU'sunda toplam **7** bilgisayar kaldığını gördüm.
- Sunucular ve iş istasyonları için ayrı OU'lar oluşturmanın önerilip önerilmediğini **yay** olarak yanıtladım.

## Task 6 — Group Policies
- GPO'ları domain makinelerine dağıtmak için kullanılan ağ paylaşımının adını **SYSVOL** olarak buldum.
- Bir GPO'nun hem kullanıcılara hem de bilgisayarlara ayar uygulamak için kullanılıp kullanılamayacağını **yay** olarak yanıtladım.

## Task 7 — Authentication Methods
- Güncel bir Windows sürümünün varsayılan olarak NetNTLM'i tercih edilen kimlik doğrulama protokolü olarak kullanıp kullanmadığını **nay** olarak yanıtladım.
- Kerberos'ta, TGS bileti talep etmeyi sağlayan bilet türünü **Ticket Granting Ticket** olarak belirledim.
- NetNTLM kullanılırken kullanıcının şifresinin ağ üzerinden herhangi bir noktada iletilip iletilmediğini **nay** olarak yanıtladım.

## Task 8 — Trees, Forests and Trusts
- Bu görevde herhangi bir soru yer almıyordu; orman ve güven ilişkileri konularını okudum.

## Task 9 — Conclusion
- Son görevde ek bir soru bulunmuyordu; odayı tamamladım.
