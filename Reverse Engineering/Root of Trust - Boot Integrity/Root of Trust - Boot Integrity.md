# Root of Trust - Boot Integrity


## Challenge Description

A custom bootable ISO was provided containing a minimal Linux kernel and initramfs. The system launches directly into a verification interface with no shell, no network, and no recovery tools. The goal is to bypass the authentication mechanism and retrieve the flag.

**Flag Format:** `root{...}`

---

## Tools Used

| Tool | Purpose |
|------|---------|
| `7z` | ISO extraction |
| `cpio` | Initramfs extraction |
| `gzip` | Decompressing initramfs |
| `file` | Identifying file types |
| `strings` | Extracting readable strings from binaries |
| `readelf` | Analyzing ELF section headers |
| `objdump` | Disassembling the binary |
| `grep` | Searching through disassembly |
| `python3` | Writing the decryption script |

---

## Methodology

### Phase 1: Reconnaissance

First, I examined the provided ISO file to understand its structure.

```bash
$ ls -la
total 23948
-rw-r--r-- 1 user user 24506368 Dec 27 11:39 custom_root_access.iso

$ 7z l custom_root_access.iso
```

**Key findings from ISO listing:**
- `boot/kernel` - Linux kernel (13.8 MB)
- `boot/initramfs.cpio.gz` - Compressed initramfs (~305 KB)
- Standard GRUB bootloader files

---

### Phase 2: Extraction

#### Step 1: Extract ISO Contents

```bash
$ mkdir -p extracted_iso
$ 7z x custom_root_access.iso -oextracted_iso boot/kernel boot/initramfs.cpio.gz -r
```

#### Step 2: Extract Initramfs

```bash
$ mkdir -p extracted_iso/initramfs
$ cd extracted_iso/initramfs
$ gzip -dc ../boot/initramfs.cpio.gz | cpio -idm
```

**Initramfs contents:**
```
extracted_iso/initramfs/
├── dev/
├── init        <-- Main binary (684 KB)
├── proc/
└── sys/
```

---

### Phase 3: Binary Analysis

#### Step 1: Identify the Binary Type

```bash
$ file extracted_iso/initramfs/init
extracted_iso/initramfs/init: ELF 64-bit LSB executable, x86-64, version 1 (GNU/Linux), 
statically linked, BuildID[sha1]=f430c41cfbd81d057325dbec398530d2fc594ce9, 
for GNU/Linux 3.2.0, stripped
```

**Key observations:**
- 64-bit ELF executable
- Statically linked (all libraries embedded)
- Stripped (no debug symbols)

#### Step 2: String Analysis

```bash
$ strings extracted_iso/initramfs/init | grep -iE "root|flag|password|verify"
```

**Output:**
```
Enter Authentication Credentials (Flag): 
root{
```

This confirms the binary prompts for a flag and expects the `root{` prefix.

#### Step 3: Locate String Offsets

```bash
$ strings -t x extracted_iso/initramfs/init | grep "Enter Authentication Credentials"
  79230 Enter Authentication Credentials (Flag):

$ strings -t x extracted_iso/initramfs/init | grep "root{"
  7925a root{
```

---

### Phase 4: Reverse Engineering

#### Step 1: Disassemble the Binary

```bash
$ objdump -d extracted_iso/initramfs/init > disassembly.txt
```

#### Step 2: Locate the Verification Logic

I searched for code referencing the prompt string at address `0x479230`:

```bash
$ grep -C 5 "479230" disassembly.txt
```

**Key code flow identified at `0x401bd2`:**
```asm
  401bd2:   lea    0x77657(%rip),%rax        # 0x479230 "Enter Authentication..."
  401bd9:   mov    %rax,%rdi
  401bdc:   call   0x401841                  ; print function
  ...
  401c0e:   call   0x41ed90                  ; read input
```

#### Step 3: Analyze Format Validation

```asm
  ; Check if input starts with "root{" (5 bytes)
  401c6a:   lea    0x775e9(%rip),%rcx        # 0x47925a "root{"
  401c78:   mov    $0x5,%edx                 ; compare 5 bytes
  401c83:   call   0x401068                  ; strncmp
  401c88:   test   %eax,%eax
  401c8a:   jne    0x401ca0                  ; fail if not matching
  
  ; Check if last character is '}'
  401c9c:   cmp    $0x7d,%al                 ; 0x7d = '}'
  401c9e:   je     0x401ca5                  ; continue if matches
```

#### Step 4: Analyze Transformation Function

At `0x401cf8`, the input content (inside braces) is passed to a transformation function:

```asm
  401cf8:   call   0x401725                  ; transform_string()
```

**Analyzing function at `0x401725`:**

```asm
  ; For lowercase letters (0x61-0x7a, 'a'-'z')
  401749:   cmp    $0x60,%al
  40174b:   jle    0x4017ae
  40175d:   cmp    $0x7a,%al
  40175f:   jg     0x4017ae
  401774:   sub    $0x54,%eax               ; subtract 0x54 (84)
  ; ... division by 26, modulo operation ...
  401798:   lea    0x61(%rax),%ecx          ; add back 'a'
  
  ; For uppercase letters (0x41-0x5a, 'A'-'Z')
  4017be:   cmp    $0x40,%al
  4017d2:   cmp    $0x5a,%al
  4017e9:   sub    $0x34,%eax               ; subtract 0x34 (52)
  ; ... same modulo 26 operation ...
  40180d:   lea    0x41(%rax),%ecx          ; add back 'A'
```

**This is ROT13!** The transformation shifts letters by 13 positions.

#### Step 5: Analyze XOR Comparison

After transformation, the result is XORed and compared:

```asm
  ; Load expected bytes (hardcoded on stack)
  401cfd:   movabs $0x269a0acb649e20fa,%rax
  401d07:   movabs $0x1af5329f3dcf12f5,%rdx
  401d1f:   movabs $0xcb66d265cf1af532,%rax
  
  ; XOR loop
  401d5e:   mov    -0xc(%rbp),%eax          ; loop counter
  401d61:   and    $0x1,%eax                ; check even/odd
  401d64:   test   %eax,%eax
  401d66:   jne    0x401d6e
  401d68:   movb   $0xaa,-0xd(%rbp)         ; even index: XOR with 0xaa
  401d6c:   jmp    0x401d72
  401d6e:   movb   $0x55,-0xd(%rbp)         ; odd index: XOR with 0x55
  
  ; Compare transformed byte with expected
  401d83:   xor    %edx,%eax                ; input[i] ^ mask
  401d94:   cmp    %al,%dl                  ; compare with expected[i]
  401d96:   je     0x401da1                 ; match: continue
  401d98:   movl   $0x0,-0x8(%rbp)          ; mismatch: fail
```

**Length check at `0x401d46`:**
```asm
  401d46:   cmp    $0x15,%rax               ; length must be 21 (0x15)
```

---

### Phase 5: Exploitation

With the complete understanding of the verification logic, I wrote a Python script to reverse the process:

**Algorithm:**
1. Extract the 21-byte expected array from the binary
2. XOR each byte with the alternating mask (0xaa for even, 0x55 for odd)
3. Apply ROT13 (which is its own inverse) to get the original flag content

```python
#!/usr/bin/env python3
# solve.py - Secure Boot Flag Decryptor

# Expected bytes extracted from binary (little-endian)
expected = [
    0xfa, 0x20, 0x9e, 0x64, 0xcb, 0x0a, 0x9a, 0x26, 
    0xf5, 0x12, 0xcf, 0x3d, 0x9f, 0x32, 0xf5, 0x1a, 
    0xcf, 0x65, 0xd2, 0x66, 0xcb
]

# Step 1: Reverse XOR
decrypted_rot13 = []
for i in range(len(expected)):
    mask = 0xaa if i % 2 == 0 else 0x55
    decrypted_rot13.append(expected[i] ^ mask)

s = "".join([chr(c) for c in decrypted_rot13])
print("After XOR:", s)

# Step 2: Reverse ROT13
def rot13(s):
    res = ""
    for c in s:
        if 'a' <= c <= 'z':
            res += chr((ord(c) - ord('a') + 13) % 26 + ord('a'))
        elif 'A' <= c <= 'Z':
            res += chr((ord(c) - ord('A') + 13) % 26 + ord('A'))
        else:
            res += c
    return res

# Generate final flag
final_flag = "root{" + rot13(s) + "}"
print("Flag:", final_flag)
```

**Execution:**
```bash
$ python3 solve.py
After XOR: Pu41a_0s_Geh5g_Oe0x3a
Flag: root{Ch41n_0f_Tru5t_Br0k3n}
```

---

## Verification Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Input                                  │
│                  root{Ch41n_0f_Tru5t_Br0k3n}                     │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│               Format Validation                                  │
│         • Starts with "root{" ✓                                  │
│         • Ends with "}" ✓                                        │
│         • Content length = 21 ✓                                  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│            ROT13 Transformation                                  │
│    Ch41n_0f_Tru5t_Br0k3n → Pu41a_0s_Geh5g_Oe0x3a               │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              XOR Operation                                       │
│    Even indices: XOR 0xaa                                        │
│    Odd indices:  XOR 0x55                                        │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│          Compare with Expected Bytes                             │
│    fa 20 9e 64 cb 0a 9a 26 f5 12 cf 3d 9f 32 f5 1a cf 65 d2... │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
                    ┌─────────────┐
                    │  SUCCESS!   │
                    └─────────────┘
```

---

## Key Insights

1. **Static Linking**: The binary was statically linked, making it self-contained but larger to analyze.

2. **Two-Stage Encoding**: The flag content is protected by:
   - ROT13 cipher (alphabetic characters only)
   - XOR with alternating mask (0xaa/0x55)

3. **Format Enforcement**: Strict validation of `root{...}` format with exact length requirement.

4. **No Anti-Debug**: The binary didn't employ anti-debugging techniques, making static analysis straightforward.

---

## Lessons Learned

- Always extract and analyze embedded filesystems (initramfs, squashfs, etc.)
- String analysis is often the first step to understanding binary behavior
- Understanding the encoding scheme allows complete reversal without dynamic analysis
- ROT13 is a weak cipher - when combined with XOR, the security is still trivial to break

---

## Flag

```
root{Ch41n_0f_Tru5t_Br0k3n}
```