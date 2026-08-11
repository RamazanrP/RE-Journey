# IForgotMyPassword Crackme Write up (ENG & TR)

## English

### Introduction

This crackme initially looks more complicated than it actually is. The program presents an activation-number check surrounded by several suspiciously named functions such as `fake_transform_1`, `fake_hash`, `fake_transform_2`, `useless_math`, and `suspicious_function_that_does_nothing`.

The interesting part was not simply finding a hardcoded password. The goal was to understand how the program generates its internal reference value and how our input is transformed before being compared with it.

The final activation number was:

`6968271`

Which led to the flag:

`FLAG{Yeah_You_Should_Start_Forgetting_Your_Password_But_St1ll_3nj0y_t0uching_t1ings_that_@re_nice_to_touch}`

## 1. Starting from `main`

The first function we examined was `main()`.

The important part was:

```c
std::operator<<((ostream *)std::cout,"Enter activation number: ");
plVar2 = std::istream::operator>>((istream *)std::cin,(longlong *)&local_18);

if (cVar1 != '\0') {
    ...
}
else {
    dispatch_validation(local_18);
}
````

This immediately told us that the user input is stored as an integer and then passed to:

```text
dispatch_validation()
```

So instead of randomly searching for strings or passwords, we followed the validation path.

## 2. `dispatch_validation()`

The next function was:

```c
void dispatch_validation(ulong param_1)
{
    suspicious_function_that_does_nothing((uint)param_1 & 0xffff);

    uVar2 = fake_security_check();

    if ((char)uVar2 == '\0') {
        std::cout << "Internal error.";
        return;
    }

    bVar1 = verify_number(param_1);

    if (bVar1) {
        std::cout << "Yes correct number...";
        process_target();
        return;
    }

    std::cout << "haha u so dumb...";
}
```

This gave us the important condition:

```text
verify_number(input) == true
```

The suspicious functions before it turned out not to be important for finding the number.

Therefore, the next target was `verify_number()`.

---

## 3. Understanding `verify_number()`

The decompiled function was:

```c
bool verify_number(ulong param_1)
{
    ulong uVar1;
    undefined1 auVar2[16];

    uVar1 = generate_reference();

    indirect_mix(uVar1);
    auVar2 = indirect_mix(param_1);

    return auVar2._8_8_ == auVar2._0_8_;
}
```

The decompiler made this look confusing, so we checked the assembly.

The important instructions were:

```asm
CALL generate_reference
MOV  param_1,RAX
CALL indirect_mix

MOV  param_1,RBX
MOV  RDX,RAX
CALL indirect_mix

CMP  RDX,RAX
SETZ AL
```

This revealed the real logic:

```text
reference_result = mix_number(generate_reference())
input_result     = mix_number(input)

reference_result == input_result
```

So the actual equation was:

```text
mix_number(input) = mix_number(reference)
```

This was the central equation of the crackme.

---

## 4. `mix_number()`

The function responsible for the transformation was:

```c
ulong mix_number(ulong param_1)
{
    ulong uVar1;

    uVar1 = (param_1 ^ 0x193a74) * 0x7a69 + 0x817263;

    return uVar1 >> 0xb ^ uVar1;
}
```

We rewrote it as:

```text
x = (n XOR 0x193A74) * 0x7A69 + 0x817263

mix(n) = x XOR (x >> 11)
```

At this point we knew that finding the activation number required understanding `generate_reference()` first.

---

# 5. Following `generate_reference()`

The reference-generation function looked intimidating:

```c
string local_88 = "Awp2AmL3";

fake_transform_1(local_48, local_68);
adjust_text(local_48, local_68);

fake_hash(pbVar1);

fake_transform_2(local_48, local_68);

rebuild_block(local_48, local_88);

uVar2 = std::__cxx11::stoll(local_88, 0, 10);

lVar3 = useless_math(uVar2);
```

We investigated each function instead of assuming that every function performed an important transformation.

---

## 6. `fake_transform_1()`

The first function was:

```c
string * fake_transform_1(string *param_1,string *param_2)
{
    ...
    string::string(param_1,param_2);
    return param_1;
}
```

Although it contained a loop that accessed every character, it never modified them.

Therefore:

```text
"Awp2AmL3"
    |
    v
fake_transform_1()
    |
    v
"Awp2AmL3"
```

The function was effectively just a copy.

## 7. `adjust_text()`

This was the first real transformation.

The function processed every character and applied different operations to uppercase and lowercase letters.

The original string was:

```text
Awp2AmL3
```

The characters were processed individually.

The resulting string was:

```text
Njc2NzY3
```

So:

```text
Awp2AmL3
    |
    v
adjust_text()
    |
    v
Njc2NzY3
```

Digits were preserved while letters were transformed using arithmetic involving modulo 26.

This was an important observation because the resulting string looked suspiciously like an encoded value rather than a normal password.

## 8. `fake_hash()`

Next, we encountered:

```c
uint fake_hash(byte *param_1)
{
    byte bVar1;
    uint uVar2;
    uint uVar3;

    bVar1 = *param_1;
    uVar2 = 0x811f9dc5;

    if (bVar1 != 0) {
        do {
            uVar3 = (uint)bVar1;
            param_1++;
            bVar1 = *param_1;
            uVar2 = (uVar2 ^ uVar3) * 0x1000193;
        } while (bVar1 != 0);

        return uVar2;
    }

    return 0x811f9dc5;
}
```

The constants:

```text
0x811C9DC5
0x01000193
```

are associated with the FNV-1a 32-bit hashing algorithm.

However, the important thing was not identifying the algorithm.

The important observation was that `generate_reference()` called:

```c
fake_hash(pbVar1);
```

but did not store or use the returned value.

Therefore, the hash result did not affect the reference value.

This was another piece of intentional noise.

## 9. `fake_transform_2()`

The next function contained:

```c
std::reverse(begin, end);
std::reverse(begin, end);
```

So it reversed the string twice.

Mathematically:

```text
reverse(reverse(x)) = x
```

Therefore:

```text
Njc2NzY3
    |
    v
reverse
    |
    v
3YzNzc2j
    |
    v
reverse
    |
    v
Njc2NzY3
```

Again, the data entering the next stage remained:

```text
Njc2NzY3
```

At this point we had removed several layers of fake complexity.

# 10. `rebuild_block()` and Base64

The next function contained the following lookup table:

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/
```

This immediately suggested Base64.

The function looked up each character's position in this alphabet and accumulated six-bit values:

```c
uVar8 = uVar8 << 6 | (uint)lVar5;
```

This is the standard structure of Base64 decoding.

Therefore:

```text
Njc2NzY3
```

was treated as Base64.

Decoding it produced:

```text
676767
```

This was a major turning point because immediately afterwards the program called:

```c
stoll(local_88, 0, 10);
```

The `10` tells us that the string is interpreted as a decimal number.

Therefore:

```text
"676767"
    |
    v
stoll(..., 10)
    |
    v
676767
```
:)

## 11. `mix_number()` Validation

When analyzing `verify_number()`, we saw that both the reference value generated by the program and the user input are passed through the `mix_number()` function.

Therefore, the program does not perform a direct string comparison:

```text
reference
   ↓
mix_number()

input
   ↓
mix_number()

   ↓
comparison
```

By following the `generate_reference()` chain, we had already obtained the required reference value:

```text
676767
   ↓
useless_math()
   ↓
6968271
```

Therefore, the required activation number was:

```text
6968271
```

When this value is entered, both sides go through the same `mix_number()` operation, so the comparison succeeds and the program proceeds to `process_target()`, which reveals the flag.

# 12. Returning to `verify_number()`

Now the original equation became:

```text
mix_number(input) = mix_number(6968271)
```

The important detail is that the program does not compare the input directly against the reference.

Both values go through:

```text
mix_number()
```

before the comparison.

Therefore we calculated the target produced by:

```text
mix_number(6968271)
```

and mathematically reversed the transformation.

The transformation was:

```text
x = (n XOR 0x193A74) * 0x7A69 + 0x817263

result = x XOR (x >> 11)
```

The XOR-with-right-shift operation can be reversed because the shifted value only depends on bits that are already available.

After reversing that transformation and then reversing the multiplication using the modular inverse of `0x7A69`, we recovered the required input.

The resulting activation number was:

```text
6968271
```

In this particular crackme, the final activation number matches the generated reference value.

# 13. Final Verification

We ran:

```bash
./iForgotMyPassword
```

and entered:

```text
6968271
```

The program responded:

```text
Yes correct number...
But surely it cannot be THAT easy.
None of you are as pro as me at hmmmmmm ukuk??
Processing...
```

The program then revealed:

```text
FLAG{Yeah_You_Should_Start_Forgetting_Your_Password_But_St1ll_3nj0y_t0uching_t1ings_that_@re_nice_to_touch}
```

The crackme was successfully solved.

# 14. Final Chain

The entire solution can be summarized as:

```text
main()
  |
  v
dispatch_validation(input)
  |
  v
verify_number(input)
  |
  +-----------------------------+
  |                             |
  v                             v
generate_reference()        input
  |                             |
  v                             |
"Awp2AmL3"                       |
  |                             |
fake_transform_1                |
  |                             |
  v                             |
"Awp2AmL3"                       |
  |                             |
adjust_text                     |
  |                             |
  v                             |
"Njc2NzY3"                       |
  |                             |
fake_hash                       |
  |                             |
(result unused)                  |
  |                             |
fake_transform_2                |
  |                             |
(reverse twice)                 |
  |                             |
  v                             |
"Njc2NzY3"                       |
  |                             |
rebuild_block                   |
  |                             |
  v                             |
"676767"                         |
  |                             |
stoll(..., 10)                  |
  |                             |
  v                             |
676767                           |
  |                             |
useless_math                    |
  |                             |
  v                             |
6968271                          |
  |                             |
mix_number() <------------------+
  |
  v
CMP
  |
  v
TRUE
  |
  v
process_target()
  |
  v
FLAG
```

## Conclusion

The main lesson from this crackme was not the final number itself.

Several functions were deliberately made to look important:

* `suspicious_function_that_does_nothing()`
* `fake_transform_1()`
* `fake_hash()`
* `fake_transform_2()`
* `useless_math()`

Instead of trusting function names, we followed the data.

The important transformations were:

```text
Awp2AmL3
    ↓
adjust_text
    ↓
Njc2NzY3
    ↓
Base64 decode
    ↓
676767
    ↓
decimal 676767
    ↓
useless_math
    ↓
6968271
```

Then we followed `verify_number()` and understood that both the generated reference and our input were passed through `mix_number()` before comparison.

The crackme was finally defeated with:

```text
6968271
```

and the program rewarded us with the flag.

---

# IForgotMyPassword

## Türkçe

### Giriş

Bu crackme ilk bakışta olduğundan çok daha karmaşık görünüyor. Program kullanıcıdan bir activation number istiyor ve bu sayı birkaç farklı fonksiyondan geçirilerek kontrol ediliyor.

Özellikle şu fonksiyon isimleri dikkat çekiyor:

```text
suspicious_function_that_does_nothing
fake_transform_1
fake_hash
fake_transform_2
useless_math
```

İlk bakışta bunların hepsinin password üretiminde önemli olduğu düşünülebilir fakat çözüm sırasında en önemli yaklaşım, fonksiyon isimlerine güvenmek yerine **verinin fonksiyonlar arasında nasıl değiştiğini takip etmek** oldu.
Zira isimlerin bizi aldattığı yerler oldu :)
Sonunda bulduğumuz activation number:

```text
6968271
```

ve programın verdiği flag:

```text
FLAG{Yeah_You_Should_Start_Forgetting_Your_Password_But_St1ll_3nj0y_t0uching_t1ings_that_@re_nice_to_touch}
```
Şimdi bu mesajı almanın yolunu görelim:

## 1. main Fonksiyonu

İlk olarak `main()` fonksiyonuna gittik.

Burada program:

```text
Enter activation number:
```

diyerek kullanıcıdan bir integer alıyor.

Sonrasında `dispatch_validation(local_18)` çağrılıyor.

Dolayısıyla çözüm yolunu:

```text
main
  ↓
dispatch_validation
  ↓
verify_number
```

şeklinde takip etmeye karar verdik.


## 2. `dispatch_validation()`

Bu fonksiyon bize çok önemli bir bilgi verdi.

Önce bazı **şüpheli** fonksiyonlar çalışıyor:

```c
suspicious_function_that_does_nothing(...);
fake_security_check();
```

Ardından asıl kontrol:

```c
bVar1 = verify_number(param_1);
```

ile yapılıyor.

Eğer `verify_number()` true döndürürse:

```text
Yes correct number...
```

mesajı gösteriliyor ve `process_target()` çalışıyor.

Dolayısıyla asıl hedefimiz artık: `verify_number()` oldu.

## 3. `verify_number()` ve assembly kontrolü

Decompile edilmiş kod kafa karıştırıcıydı:

```c
uVar1 = generate_reference();
indirect_mix(uVar1);
auVar2 = indirect_mix(param_1);

return auVar2._8_8_ == auVar2._0_8_;
```

Bu yüzden assembly'ye baktık.

Kritik kısım:

```asm
CALL generate_reference
MOV  param_1,RAX
CALL indirect_mix

MOV  param_1,RBX
MOV  RDX,RAX
CALL indirect_mix

CMP  RDX,RAX
SETZ AL
```

Buradan gerçek mantığı çıkardık:

```text
mix_number(reference)
        ==
mix_number(input)
```

Yani doğrudan `input == reference` kontrolü yapılmıyordu.

İki değer de önce **aynı** matematiksel dönüşümden geçiriliyordu.

# 4. `generate_reference()`

`generate_reference()` başlangıçta **Awp2AmL3** string'ini oluşturuyordu.

Buradan sonra string pek çok fonksiyona uğradı. Bazıları ismindeki gibi gereksiz bazıları ise aldatmacaydı, işimize yarıoyrdu. Görelim:

## 5. `fake_transform_1()`

İlk fonksiyon ismine bakınca bir dönüşüm bekliyorduk.

Fakat fonksiyonu incelediğimizde karakterleri sadece okuduğunu ve sonunda string'i kopyaladığını gördük.

Hiçbir karakter değiştirilmiyordu.

Dolayısıyla:

```text
Awp2AmL3
   ↓
fake_transform_1()
   ↓
Awp2AmL3
```

## 6. `adjust_text()`

İlk gerçek dönüşüm burada gerçekleşiyordu.

Fonksiyon karakterleri tek tek ele alıyor ve **uppercase/lowercase** karakterlere farklı işlemler uyguluyordu.

İşlem sonucunda `Njc2NzY3` elde edildi.

Dolayısıyla:

```text
Awp2AmL3
    ↓
adjust_text()
    ↓
Njc2NzY3
```
Upper/lower kontolü var fakat **rakamlar** için bir değişim yok!

## 7. `fake_hash()`

Daha sonra `fake_hash()` fonksiyonuna geldik.

Fonksiyondaki:

```text
0x811C9DC5
0x01000193
```

sabitleri bunun **FNV-1a 32-bit** tarzında bir hash hesapladığını gösteriyordu.

Fakat daha önemli bir şey fark ettik:

`generate_reference()` içerisinde `fake_hash()` çağrılıyor ama dönüş değeri hiçbir yerde kullanılmıyordu.

Yani:

```text
Njc2NzY3
   ↓
fake_hash()
   ↓
hash sonucu
   ↓
kullanılmıyor
```

Bu nedenle hash'i hesaplayıp password üretmeye çalışmak gereksizdi. Bu, crackme'nin bizi yanlış yöne gönderen kısımlarından biriydi.

## 8. `fake_transform_2()`

Bu fonksiyonda art arda iki adet `reverse()` gördük.

İki reverse işlemi birbirini götürdüğü için `Njc2NzY3` string'i fonksiyondan çıktıktan sonra yine `Njc2NzY3` halinde kalıyordu.


# 9. `rebuild_block()` ve Base64

İçerisinde:

```text
ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/
```

vardı.

Bu Base64 alphabet'iydi.

Fonksiyon karakterleri bu tablo içerisindeki index'lerine çeviriyor ve 6-bit değerleri biriktiriyordu.

Dolayısıyla `rebuild_block()` fonksiyonunu:

```text
Base64 decode
```

olarak tanımladık.

Input:

```text
Njc2NzY3
```

Base64 decode edildiğinde:

```text
676767
```

elde edildi :)

Sonrasında:

```c
stoll(local_88, 0, 10);
```

çağrılıyordu.

Buradaki `10`, decimal tabanı gösteriyordu.

Böylece:

```text
"676767"
   ↓
stoll(..., 10)
   ↓
676767
```

oldu.

# 10. `useless_math()`

Şimdi elimizde:

```text
676767
```

vardı.

Bu değer `useless_math()` fonksiyonuna gönderiliyordu:

```c
((param_1 ^ 0x12345678) + 0x98765 ^ 0x12345678) - 0x98765
```

Adım adım hesapladık.

Önce:

```text
676767 = 0xA539F
```

Sonra:

```text
0x000A539F XOR 0x12345678
=   0x123E05E7
```

Toplama:

```text
0x123E05E7 + 0x00098765
= 0x12478D4C
```

İkinci XOR:

```text
0x12478D4C XOR 0x12345678
= 0x0073DB34
```

Son çıkarma:

```text
0x0073DB34 - 0x00098765
= 0x006A53CF
```

Dolayısıyla:

```text
reference = 0x6A53CF
```

Decimal karşılığı:

```text
6968271
```

Böylece `generate_reference()` fonksiyonunu tamamen çözmüş olduk.

Evet, burada `mix_number()` fonksiyonunun tersine çevrilmesi kısmı gereksiz. Çünkü `generate_reference()` zincirinden zaten **doğrudan gerekli activation number'ı** elde ettik. Daha temiz ve resmi hali şöyle:

## 11. `mix_number()` Validation

`verify_number()` fonksiyonunu incelediğimizde, hem programın ürettiği reference değerinin hem de kullanıcı girişinin `mix_number()` fonksiyonundan geçirildiğini gördük.

Bu nedenle doğrudan bir string karşılaştırması yapılmıyordu:

```text
reference
   ↓
mix_number()

input
   ↓
mix_number()

   ↓
karşılaştırma
```
Ve de biliyoruz ki:

```text
676767
   ↓
useless_math()
   ↓
6968271
```

Dolayısıyla programa verilmesi gereken activation number `6968271` oldu. mix_number()da ne olduğu şu an önemsiz.

Bu değer girildiğinde iki taraf da aynı `mix_number()` işleminden geçtiği için karşılaştırma başarılı oldu ve program `process_target()` fonksiyonuna ilerleyerek flag'i gösterdi.

# 12. Son test

Sonunda programı çalıştırdık:

```bash
./iForgotMyPassword
Enter activation number: 6968271
```

girdik.

Program:

```text
Yes correct number...
But surely it cannot be THAT easy.
None of you are as pro as me at hmmmmmm ukuk??
Processing...
```

dedi.

Ve ardından flag'i verdi:

```text
FLAG{Yeah_You_Should_Start_Forgetting_Your_Password_But_St1ll_3nj0y_t0uching_t1ings_that_@re_nice_to_touch}
```

---

# 13. Tam Çözüm Zinciri

Crackme'nin tamamını en kısa şekilde şöyle özetleyebiliriz:

```text
main
  ↓
dispatch_validation
  ↓
verify_number
  ↓
generate_reference
  ↓
"Awp2AmL3"
  ↓
fake_transform_1
  ↓
"Awp2AmL3"
  ↓
adjust_text
  ↓
"Njc2NzY3"
  ↓
fake_hash
  ↓
sonuç kullanılmıyor
  ↓
fake_transform_2
  ↓
reverse + reverse
  ↓
"Njc2NzY3"
  ↓
rebuild_block
  ↓
Base64 decode
  ↓
"676767"
  ↓
stoll
  ↓
676767
  ↓
useless_math
  ↓
6968271
  ↓
mix_number
  ↓
input ile karşılaştır
  ↓
TRUE
  ↓
process_target
  ↓
FLAG
```

## Nihai Sonuç

```text
Activation Number:
6968271

Flag:
FLAG{Yeah_You_Should_Start_Forgetting_Your_Password_But_St1ll_3nj0y_t0uching_t1ings_that_@re_nice_to_touch}
```

## Çıkarılan Dersler

Bu crackme'de en önemli ders, fonksiyon isimlerine güvenmemekti.

`fake_hash()` gerçekten hash hesaplıyor olabilir ama sonucu kullanılmıyorsa password açısından önemsizdir.

`fake_transform_2()` gerçekten iki kez reverse yapıyorsa sonuç yine aynıdır.

`suspicious_function_that_does_nothing()` gibi isimler ise doğrudan dikkat dağıtabilir.

En güvenilir yöntem:

```text
Fonksiyona gir
    ↓
Input ne?
    ↓
Hangi değişken değişiyor?
    ↓
Return değeri kullanılıyor mu?
    ↓
Sonraki fonksiyona ne aktarılıyor?
```

sorusunu her adımda sormaktır.

Bu yaklaşım sayesinde başlangıçta karmaşık görünen program:

```text
String transformation
→ Base64
→ Decimal
→ Arithmetic
→ Numeric mixing
→ Comparison
```

şeklinde bir zincire indirgenebildi.
