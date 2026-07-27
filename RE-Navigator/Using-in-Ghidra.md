# Ghidra ile Kullanım Rehberi

Bu tool, Ghidra ile birlikte çalışarak binary içindeki fonksiyonları analiz eder.  
Ghidra'dan alınan veriler `functions.json` dosyasına aktarılır ve analyzer bu dosya üzerinden çalışır.

---

## İlk Kurulum (Sadece 1 Kez Yapılacak)

### 1. Ghidra'yı Aç
- Binary dosyanı yükle
- Auto-analysis işleminin tamamlanmasını bekle

---

### 2. Script Manager Aç


Window → Script Manager

---

### 3. Yeni Script Oluştur

- **New Script** butonuna tıkla
- Python seç
- Script adı: export_functions.py


---

### 4. Aşağıdaki Script'i Yapıştırın

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
````

---

### 5. Script'i Kaydet

Artık bu işlemi tekrar yapmana gerek yok, kaydet, ilerde tek tuşla çalıştır.

---

## Günlük Kullanım

Her yeni binary için:

1. Binary’yi Ghidra’da aç
2. Script Manager’a gir
3. `export_functions.py` script’ini seç
4. **Run** tuşuna bas
5. Çıktıyı şu konuma kaydet: `data/functions.json`

---

## Analyzer'ı Çalıştır

Terminalde:

```bash
python main.py
```

---

## Opsiyonel Diğer Kullanım

Script’i üst menüye ekleyebilirsiniz:

* Script’e sağ tık
* **Add to Toolbar**

Artık tek tıkla JSON export alabilirsiniz.

---

## Bu Script Ne Yapar?

Şu bilgileri toplar:

* Fonksiyon isimleri
* Fonksiyon çağrıları (call graph)
* Stringler
* Instruction sayısı
* Loop ve koşul bilgisi

Ve bunları `functions.json` dosyasına çevirir.

Analyzer bu dosyayı kullanır.

---

## Gelecek Planları

* Ghidra headless otomasyon
* IDA desteği
* Daha güçlü string ve crypto tespiti
