# Ghidra ile Kullanım Rehberi

Bu tool, binary içindeki fonksiyonları analiz etmek için tasarlanmıştır.  
Varsayılan kullanım **tek komutluk (CLI)** akıştır.

Ghidra sadece **opsiyonel/advanced** kullanım içindir.

# Hızlı Başlangıç (Önerilen)

## 1. Workspace Hazırla

Analiz edeceğiniz dosyaları **tek klasörde** toplayın. Bu **ZORUNLULUKTUR**.

Örnek:

```

challenge_folder/
├── chall
├── readme.txt
├── flag.txt
```

Crackme indiriyorsanız:
- Arşivi açın (şifre: `crackmes.one`)
- İçindeki binary dosyayı bu klasöre koyun


## 2. Tek Komutla Çalıştır

```bash
python run.py ./challenge_folder
````

Tool otomatik olarak:

* Binary dosyayı bulur
* Analiz eder
* Gerekli çıktıyı üretir

---

# Ghidra ile Manuel Kullanım (Opsiyonel)

Eğer Ghidra üzerinden veri export etmek isterseniz:

## 1. Script Manager → New Script

Aşağıdaki script'i ekleyin:

```python
#@author you
#@category Export

import json

functions = []

fm = currentProgram.getFunctionManager()

for func in fm.getFunctions(True):
    name = func.getName()
    entry = func.getEntryPoint()

    calls = set()
    instr_count = 0
    has_loop = False
    has_conditional = False

    listing = currentProgram.getListing()
    instructions = listing.getInstructions(func.getBody(), True)

    for instr in instructions:
        instr_count += 1

        flow = instr.getFlowType()

        if flow.isCall():
            for ref in getReferencesFrom(instr.getAddress()):
                if ref.getReferenceType().isCall():
                    target = getFunctionAt(ref.getToAddress())
                    if target:
                        calls.add(target.getName())

        if flow.isConditional():
            has_conditional = True

        if flow.isJump():
            has_loop = True

    strings = []
    for ref in getReferencesFrom(entry):
        data = getDataAt(ref.getToAddress())
        if data and data.hasStringValue():
            strings.append(str(data.getValue()))

    functions.append({
        "name": name,
        "address": str(entry),
        "calls": list(calls),
        "call_count": len(calls),
        "strings": strings,
        "constants": [],
        "instruction_count": instr_count,
        "basic_block_count": func.getBody().getNumAddresses(),
        "has_loop": has_loop,
        "has_conditional": has_conditional,
        "imports": [],
        "suspicious_apis": [],
        "is_entry": name.lower() in ["main", "entry", "_start"]
    })

output_path = askFile("functions.json kaydet", "Save").getAbsolutePath()

with open(output_path, "w") as f:
    json.dump(functions, f, indent=2)

print("[+] Export tamamlandı!")
```


## 2. Script Ne Yapar?

Bu script:

* Fonksiyonları çıkarır
* Call graph oluşturur
* Stringleri toplar
* Basit kontrol akışı bilgisi üretir

Ve sonucu:

```
functions.json
```

olarak kaydeder.


## 3. Ne Zaman Gerekli?

* CLI otomasyonu yetmiyorsa
* Özel analiz yapmak istiyorsanız
* Ghidra içinden veri çekmek istiyorsanız


# Gelecek Planları

* Headless Ghidra entegrasyonu
* IDA desteği
* Otomatik string/crypto tespiti
