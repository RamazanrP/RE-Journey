# YAP Crackme Write-up

## Türkçe

### 1. Crackme'nin amacı

Programın açıklamasındaki kritik cümle şuydu:

> The flag itself is trivial to find, but the core challenge is to get
> the binary to say the flag out aloud.

Bu bize iki önemli ipucu veriyordu. Flag'in binary içerisinde bulunması
bekleniyordu; asıl amaç ise flag'i sadece bulmak değil, programın
çalışma akışı içerisinde kendisinin ekrana yazmasını sağlamaktı.

Bu nedenle ilk işimiz flag'i bulmak olsa da, onu doğrudan çözüm olarak
kabul etmedik.

### 2. Flag'i hemen bulduk

Ghidra'da ana fonksiyonu incelerken şu karşılaştırma dikkat çekti:

``` c
strcmp("flag{shaney_would_have_liked_this}", local_148)
```

Dolayısıyla flag zaten açık şekilde binary içerisinde bulunuyordu:

``` text
flag{shaney_would_have_liked_this}
```

İlk bakışta bunu input olarak vermek mantıklı görünebilirdi. Ancak hemen
üstündeki kontrolü takip ettiğimizde bunun özellikle bir tuzak olduğunu
gördük.

``` c
if (strcmp("flag{shaney_would_have_liked_this}", local_148) == 0) {
    puts(...);
    return 1;
}
```

Yani flag'i doğrudan girersek program başarı yoluna değil, erken çıkış
yapan branch'e giriyordu.

Buradan şu sonuca vardık:

**Flag'i bulmak yeterli değildi. Programın kendi kelime üretme
mekanizmasını çözmemiz gerekiyordu.**

### 3. Program hangi dosyaları kullanıyor?

Ana fonksiyonda iki dosyanın açıldığını gördük:

``` c
fopen("words.dat", "r");
fopen("data.dat", "r");
```

`words.dat` içerisindeki veriler bellekte kelimelere ayrılıyor ve her
kelimeye bir index veriliyordu.

Daha sonra `data.dat` okunuyor ve bu verinin `FUN_00101240()` tarafından
kullanıldığını gördük.

Bu noktada çözümün merkezinin `FUN_00101240()` olduğunu düşündük.

### 4. `FUN_00101240()` ne yapıyor?

Fonksiyon iki mevcut kelimeyi alıyor:

``` c
param_5
param_6
```

ve `words.dat` içerisinde bunların index'lerini buluyor.

Önemli bölüm:

``` c
iVar2 = strcmp(__s1, param_5);

if (iVar2 == 0) {
    local_40 = uVar4;
}

iVar2 = strcmp(__s1, param_6);

if (iVar2 == 0) {
    local_3a = uVar4;
}
```

Sonrasında bu iki index birleştiriliyor:

``` c
CONCAT22(local_40, local_3a)
```

ve `data.dat` içerisindeki kayıtlarla karşılaştırılıyor.

Eşleşen kayıt bulunduğunda `rand()` kullanılarak o transition
içerisindeki sonraki kelimelerden biri seçiliyor:

``` c
return *(ushort *)(param_1 + (ulong)(uVar3 % uVar1) * 2 + (long)(iVar2 + 8));
```

Böylece mekanizmanın aslında bir tür kelime geçiş sistemi olduğunu
anladık:

``` text
iki mevcut kelime
       ↓
words.dat → index'ler
       ↓
data.dat → transition
       ↓
sonraki kelime
       ↓
tekrar
```

### 5. Başlangıç kelimelerini bulmak

Ana fonksiyonda kullanıcı input'unun iki parçaya ayrıldığını gördük:

``` c
local_c8[0] = &local_78;
local_c8[1] = &local_b8;
```

ve boşluk karakterine göre ilk ve ikinci kelime bu iki alana
yazılıyordu.

Daha sonra:

``` c
FUN_00101240(..., (char *)&local_78, (char *)&local_b8);
```

çağrılıyordu.

Dolayısıyla kullanıcıdan iki kelimelik bir başlangıç çifti bekleniyordu.

### 6. Nerede tıkandık?

İlk analizimizde `words.dat` index'lerini yanlış yönde yorumladık ve:

``` text
prize: Your
```

input'unu denedik.

Program:

``` text
the words have gone missing...
```

veya çalıştırma bağlamına bağlı olarak herhangi bir transition sonucu
vermeden sonlanınca dosyaların gerçekten doğru dizinde olduğunu kontrol
ettik.

Ardından transition yönünü tekrar inceledik.

Bu kez `data.dat` içindeki kayıt ile `words.dat` index'lerini birlikte
değerlendirdik.

Doğru sıra:

``` text
344  = Your
1126 = prize:
744  = flag{shaney_would_have_liked_this}.
```

Transition ise:

``` text
344 → 1126 → 744
```

şeklindeydi.

Dolayısıyla doğru başlangıç çifti:

``` text
Your prize:
```

oldu.

### 7. Flag'in binary tarafından söylenmesini sağlamak

`Your prize:` input'u verildiğinde `FUN_00101240()` doğru transition'ı
buluyor ve `744` index'ini döndürüyor.

Ana döngü daha sonra bu index'teki kelimeyi alıyor:

``` c
pcVar2 = (char *)puVar7[(int)uVar10];
printf("%s ", pcVar2);
```

744 numaralı kelime:

``` text
flag{shaney_would_have_liked_this}.
```

olduğu için program flag'i kendisi stdout'a yazıyor.

Sonuç olarak çözüm:

``` text
Input:
Your prize:

        ↓

words.dat
Your      → 344
prize:    → 1126

        ↓

data.dat

344 → 1126 → 744

        ↓

words.dat

744 → flag{shaney_would_have_liked_this}.

        ↓

printf()

        ↓

FLAG
```

### 8. Sonuç

Bu crackme'nin ana fikri flag'i gizlemek değildi. Flag zaten `strcmp()`
içerisinde açıkça bulunuyordu.

Asıl challenge, programın açıklamasında belirtildiği gibi binary'nin
flag'i kendisinin söylemesini sağlamaktı.

Çözüm yolu:

1.  `strcmp()` ile flag'i keşfettik.
2.  Flag'i doğrudan input olarak vermenin yanlış branch'e götürdüğünü
    gördük.
3.  `words.dat` ve `data.dat` kullanımını takip ettik.
4.  `FUN_00101240()` fonksiyonunun iki kelimelik transition sistemi
    olduğunu çözdük.
5.  `words.dat` index'lerini çıkardık.
6.  `data.dat` içerisindeki transition yönünü doğruladık.
7.  İlk denemede kelime sırasını ters yorumlayarak takıldık.
8.  Doğru başlangıç çiftinin `Your prize:` olduğunu bulduk.
9.  Programın transition zinciri üzerinden flag'i kendisinin yazmasını
    sağladık.

Final input:

``` text
Your prize:
```

Flag:

``` text
flag{shaney_would_have_liked_this}
```

------------------------------------------------------------------------

# YAP Crackme Write-up

## English

### 1. The goal of the crackme

The most important sentence in the challenge description was:

> The flag itself is trivial to find, but the core challenge is to get
> the binary to say the flag out aloud.

This immediately gave us two clues. The flag was expected to be easy to
find inside the binary, while the actual challenge was making the
program itself print the flag during execution.

So finding the flag was only the beginning.

### 2. Finding the flag

While inspecting the main function in Ghidra, we found:

``` c
strcmp("flag{shaney_would_have_liked_this}", local_148)
```

The flag was therefore directly visible:

``` text
flag{shaney_would_have_liked_this}
```

However, this was not the solution.

The surrounding logic showed that entering the flag directly would
trigger an early-exit branch:

``` c
if (strcmp("flag{shaney_would_have_liked_this}", local_148) == 0) {
    puts(...);
    return 1;
}
```

So the obvious solution was intentionally a dead end.

The real goal was to understand how the binary generated and printed
words.

### 3. The external data files

The main function opened two files:

``` c
fopen("words.dat", "r");
fopen("data.dat", "r");
```

`words.dat` was loaded and split into individual words. Each word
received an index.

`data.dat` was then loaded as another data structure used by
`FUN_00101240()`.

This made `FUN_00101240()` the key function to reverse.

### 4. Understanding `FUN_00101240()`

The function receives two words:

``` c
param_5
param_6
```

It searches for both words inside the word table and records their
indexes:

``` c
iVar2 = strcmp(__s1, param_5);

if (iVar2 == 0) {
    local_40 = uVar4;
}

iVar2 = strcmp(__s1, param_6);

if (iVar2 == 0) {
    local_3a = uVar4;
}
```

The two indexes are then combined:

``` c
CONCAT22(local_40, local_3a)
```

and compared against records stored in `data.dat`.

Once a matching transition is found, `rand()` selects one of the
possible next words:

``` c
return *(ushort *)(param_1 + (ulong)(uVar3 % uVar1) * 2 + (long)(iVar2 + 8));
```

At this point the structure became clear:

``` text
two current words
       ↓
words.dat → word indexes
       ↓
data.dat → transition
       ↓
next word
       ↓
repeat
```

### 5. Finding the starting pair

The main function splits the user's input into two words and stores them
in:

``` c
local_78
local_b8
```

These are then passed to:

``` c
FUN_00101240(..., (char *)&local_78, (char *)&local_b8);
```

Therefore, the required input is a two-word starting pair.

### 6. Where we got stuck

Our first interpretation of the transition indexes was backwards, so we
tried:

``` text
prize: Your
```

This did not produce the expected transition.

After checking the actual index relationships in `words.dat` and
`data.dat`, we found the correct ordering:

``` text
344  = Your
1126 = prize:
744  = flag{shaney_would_have_liked_this}.
```

The transition was:

``` text
344 → 1126 → 744
```

Therefore, the correct starting input was:

``` text
Your prize:
```

### 7. Making the binary print the flag

With:

``` text
Your prize:
```

as the input, `FUN_00101240()` finds the matching transition and returns
index `744`.

The main loop then retrieves that word:

``` c
pcVar2 = (char *)puVar7[(int)uVar10];
printf("%s ", pcVar2);
```

Index `744` corresponds to:

``` text
flag{shaney_would_have_liked_this}.
```

The binary therefore prints the flag itself.

The complete chain is:

``` text
Your prize:
      ↓
words.dat
Your      → 344
prize:    → 1126
      ↓
data.dat
344 → 1126 → 744
      ↓
words.dat
744 → flag{shaney_would_have_liked_this}.
      ↓
printf()
      ↓
FLAG
```

### 8. Conclusion

The challenge was not about hiding the flag. The flag was intentionally
exposed through the `strcmp()` call.

The real challenge was understanding the program's word-transition
mechanism and making the binary reach the code that prints the flag.

The solution path was:

1.  Find the obvious flag in `strcmp()`.
2.  Notice that entering it triggers the wrong branch.
3.  Follow the use of `words.dat` and `data.dat`.
4.  Reverse `FUN_00101240()`.
5.  Map words to their indexes.
6.  Decode the transition stored in `data.dat`.
7.  Correct the initial reversed word order.
8.  Use `Your prize:` as the starting input.
9.  Let the binary traverse the transition and print the flag itself.

Final input:

``` text
Your prize:
```

Flag:

``` text
flag{shaney_would_have_liked_this}
```
