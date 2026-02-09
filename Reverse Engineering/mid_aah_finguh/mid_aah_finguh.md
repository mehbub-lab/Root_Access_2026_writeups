# mid_aah_finguh

## Methodology

This writeup documents the steps taken to solve the "reverse" challenge, focusing on file analysis, steganography, binary reverse engineering, and cryptography.

**Tools Used:**
- `file`
- `strings`
- `binwalk`
- `zsteg`
- `dd`
- `objdump`
- `pdftotext`
- `python3`

---

## 1. Initial Reconnaissance

The challenge provided a single file: `middle_fingu.png`. I started by verifying its file type and checking for hidden strings.

```console
user@machine:~$ file middle_fingu.png
middle_fingu.png: PNG image data, 100 x 159, 8-bit/color RGB, non-interlaced
```

Running `strings` revealed a suspicious Base64-encoded string within the file.

```console
user@machine:~$ strings middle_fingu.png | head -n 10
...
WU9VX0NBTl9PTkxZX1VOTE9DS19NRV9XSEVOX0lfQU1fQVRfTVlfRlVMTF9QT1dFUg==
...
```

I decoded this string:

```console
user@machine:~$ echo "WU9VX0NBTl9PTkxZX1VOTE9DS19NRV9XSEVOX0lfQU1fQVRfTVlfRlVMTF9QT1dFUg==" | base64 -d
YOU_CAN_ONLY_UNLOCK_ME_WHEN_I_AM_AT_MY_FULL_POWER
```

This phrase hinted at a unlocking mechanism or password.

---

## 2. Steganography & Extraction

Next, I checked for hidden data using `zsteg` and simple `grep` commands. `zsteg` detected extra data after the end of the image.

To pinpoint the exact locations of potential hidden files, I searched for file headers:

```console
user@machine:~$ grep -oba "ELF" middle_fingu.png
27917:ELF
user@machine:~$ grep -oba "%PDF" middle_fingu.png
51868:%PDF
```

Wait, `27917` starts with 'E', but ELF headers usually start with `\x7fELF`. Checking the offset 27916:

```console
user@machine:~$ xxd -s 27916 -l 10 middle_fingu.png
00006d0c: 7f45 4c46 0201 0100 0000                 .ELF......
```

Correct! The ELF binary starts at offset **27916**. The PDF starts at **51868**.

I extracted these files using `dd`:

```console
user@machine:~$ dd if=middle_fingu.png of=hidden_elf bs=1 skip=27916 count=23952
user@machine:~$ dd if=middle_fingu.png of=hidden.pdf bs=1 skip=51868
user@machine:~$ chmod +x hidden_elf
```

---

## 3. Binary Analysis (`hidden_elf`)

I focused on the extracted ELF binary. Running it prompted for input:

```console
user@machine:~$ ./hidden_elf
Enter the number of test cases: 1
1
 Objection! 
Everyone come back
 We are having a retrial
```

Analyzing the strings and disassembly revealed interesting functions and data:

```console
user@machine:~$ objdump -t hidden_elf | grep "kitne_fingers"
00000000000023c9 g     F .text  0000000000000024              _Z13kitne_fingersv
```

Disassembling `kitne_fingers` and checking `.rodata` showed the string: `THE MIDDLE ONE IS THE BEST`.

This string, combined with the "number of test cases" prompt, suggested a specific input logic.

---

## 4. Unlocking the PDF (`hidden.pdf`)

The extracted PDF was password protected.

```console
user@machine:~$ pdfinfo hidden.pdf
Command Line Error: Incorrect password
```

Based on the binary analysis (and a bit of guessing/brute-forcing related to "fingers" or small numbers), I tried the password **20** (fingers/toes?).

```console
user@machine:~$ pdftotext -upw 20 hidden.pdf -
how many eyes? how many ropes 
7**1>//.7v#v7v+&vpq7v#0+8
```

Success! The PDF contained a ciphertext string: `7**1>//.7v#v7v+&vpq7v#0+8`.

---

## 5. Decrypting the Flag

The string `7**1>//.7v#v7v+&vpq7v#0+8` looked like a simple XOR cipher. I wrote a Python script to brute-force the XOR key.

```python
ciphertext = "7**1>//.7v#v7v+&vpq7v#0+8"
for k in range(256):
    res = "".join(chr(ord(c) ^ k) for c in ciphertext)
    if "root" in res or "flag" in res:
        print(f"Key {k}: {res}")
```

Running the script:

```console
user@machine:~$ python3 decrypt.py
Key 69: root{jjkr3f3r3nc354r3fun}
```

The key was **69**.

## Final Flag

```
root{jjkr3f3r3nc354r3fun}
```
