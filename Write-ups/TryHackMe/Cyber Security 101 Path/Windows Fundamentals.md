# TryHackMe — Windows Fundamentals (Module 3)

Bu belgede, Cyber Security Path içindeki Module 3: Windows Fundamentals altında yer alan üç odanın soru ve cevaplarını kendi çözümlerim olarak listeledim.

---

## Oda 1: Windows Fundamentals 1

### Task 1 — Windows Editions
- Pro sürümünde etkinleştirebildiğim ancak Home sürümünde etkinleştiremediğim şifreleme özelliğini **BitLocker** olarak yanıtladım.

### Task 2 — The Desktop (GUI)
- Search kutusunu gizleyen/ devre dışı bırakan seçeneği **Hidden** olarak işaretledim.
- Task View düğmesini gizleyen seçeneği **Show Task View button** olarak buldum.
- Bildirim alanında Clock ve Network dışında görünen simgeyi **Action Center** olarak belirledim.

### Task 3 — Introduction to Windows
- Bu görevde herhangi bir cevap gerekmedi; sanal makineyi başlattım.

### Task 4 — The File System
- NTFS'in anlamını **New Technology File System** olarak yanıtladım.

### Task 5 — The Windows\System32 Folders
- Windows klasörü için sistem değişkenini **%windir%** olarak tespit ettim.

### Task 6 — User Accounts, Profiles, and Permissions
- Diğer kullanıcı hesabının adını **tryhackmebilly** olarak buldum.
- Bu kullanıcının üye olduğu grupları **Remote Desktop Users, Users** olarak listeledim.
- Misafir erişimi için yerleşik hesabı **Guest** olarak belirledim.
- Hesap açıklamasını **window$Fun1!** olarak gördüm.

### Task 7 — User Account Control
- UAC'nin açılımını **User Account Control** olarak yanıtladım.

### Task 8 — Settings and the Control Panel
- Control Panel görünümünü Small icons yaptığımda listedeki son ayarın **Windows Defender Firewall** olduğunu gördüm.
### Task 9 — Task Manager
- Task Manager'ı açmak için kullandığım klavye kısayolunu **Ctrl+Shift+Esc** olarak kaydettim.

### Task 10 — Conclusion
- Son görevde ek bir cevap bulunmuyordu; sanal makineyi kapattım.

---

## Oda 2: Windows Fundamentals 2

### Task 1 — Introduction
- Bu görevde cevap gerekmedi; `freerdp` ile sanal makineye bağlandım.

### Task 2 — System Configuration
- Services sekmesinde üreticisi Systems Internals olan servisin adını **PsShutdown** olarak buldum.
- Windows lisansının kayıtlı olduğu kişiyi **Windows User** olarak gördüm.
- Windows Sorun Giderme komutunu **C:\Windows\System32\control.exe /name Microsoft.Troubleshooting** olarak tespit ettim.
- Control Panel'i açan komutu (sadece .exe adı) **control.exe** olarak yanıtladım.

### Task 3 — Change UAC Settings
- Kullanıcı Hesabı Denetimi Ayarları'nı açan komutu **UserAccountControlSettings.exe** olarak buldum.

### Task 4 — Computer Management
- Computer Management'i açan komutu **compmgmt.msc** olarak belirledim.
- GoogleUpdateTaskMachineUA görevinin her gün çalıştığı saati **6:15 AM** olarak gördüm.
- Gizli paylaşılan klasörün adını **sh4r3dF0Ld3r** olarak buldum.

### Task 5 — System Information
- System Information'ı açan komutu **msinfo32.exe** olarak yanıtladım.
- System Name altında listelenen adı **THM-WINFUN2** olarak gördüm.
- Environment Variables altında ComSpec değerini **%SystemRoot%\system32\cmd.exe** olarak tespit ettim.

### Task 6 — Resource Monitor
- Resource Monitor'ü açan komutu **resmon.exe** olarak buldum.

### Task 7 — Command Prompt
- System Configuration içinde Internet Protocol Configuration için tam komutu **C:\Windows\System32\cmd.exe /k %windir%\system32\ipconfig.exe** olarak gördüm.
- `ipconfig` komutunda ayrıntılı bilgi göstermek için **ipconfig /all** kullandım.

### Task 8 — Settings and the Control Panel
- Registry Editor'ü açan komutu **regedt32.exe** olarak yanıtladım.

---

## Oda 3: Windows Fundamentals 3

### Task 1 — Introduction
- Bu görevde cevap gerekmedi; sanal makineye `freerdp` ile bağlandım.

### Task 2 — Windows Updates
- VM'de yüklü iki tanım güncellemesinin yüklenme tarihini **5/3/2021** olarak gördüm.

### Task 3 — Windows Security
- Security bölümünde acil ilgi gerektiren alanı **Virus & threat protection** olarak belirledim.

### Task 4 — Virus & threat protection
- Windows'un açmam için bildirimde bulunduğu kapalı özelliği **Real-time protection** olarak tespit ettim.

### Task 5 — Firewall & network protection
- Havaalanı Wi-Fi'ına bağlıysam etkin güvenlik duvarı profilinin **Public network** olacağını yanıtladım.

### Task 6 — App & browser control
- Bu görevde ek bir soru yer almıyordu; SmartScreen ayarlarını inceledim.

### Task 7 — Device security
- TPM'in açılımını **Trusted Platform Module** olarak yanıtladım.

### Task 8 — BitLocker
- TPM 1.2 veya üzeri olmayan sistemlerde kullanılan çıkarılabilir sürücünün içerdiği şeyi **startup key** olarak buldum.

### Task 9 — Volume Shadow Copy Service
- VSS'in açılımını **Volume Shadow Copy Service** olarak yanıtladım.
