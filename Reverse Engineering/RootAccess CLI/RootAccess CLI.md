# RootAccess CLI Write-up

**Category:** Reverse Engineering 
---

## Executive Summary

I successfully reverse-engineered the `root-access` CLI tool (v1.3.37, Codename: SHADOWGATE), uncovering a complex 10-layer security system. By de-obfuscating the source code and analyzing the runtime logic, I bypassed environment checks, access controls, hidden arguments, and time-based cryptographic challenges to forge a Master Key and retrieve the final flag.

**Final Flag:**
```
root{N0d3_Cl1_R3v3rs3_3ng1n33r1ng_M4st3r_0f_Sh4d0ws}
```

---

## Phase 1: Reconnaissance & De-obfuscation

### The Problem
The primary entry point, `dist/bin/cli.js`, was heavily obfuscated. It employed a string array rotation technique and a proxy decoder function to hide all string literals, making static analysis impossible.

**Obfuscated Snippet (Simulation):**
```javascript
const _0x1234 = ['\x68\x65\x6c\x6c\x6f', ...]; // "hello" hidden in hex/array
(function(_0xabc, _0xdef) { ... })(_0x1234, 0x1a2); // Array rotation
function _0xdecoder(_0xa, _0xb) { ... } // Decoder proxy
console.log(_0xdecoder('0x1')); // Prints obfuscated string
```

### The Solution: Static De-obfuscation
Instead of trying to read the obfuscated code, I wrote a script (`deobfuscate.js`) to:
1.  **Extract** the string array and rotation logic.
2.  **Evaluate** the rotation in a sandbox to get the final array state.
3.  **Regex Replace** every call to the decoder function (e.g., `_0xcba37(0x1a)`) with its actual string value (e.g., `'password'`).

This produced `cli.clean.js`, a readable file where I could trace the logic.

---

## Phase 2: Breaking the Security Layers

### Layer 1: Environment Logic (`ROOTACCESS_DEBUG`)

**Code Analysis:**
At the very top of `cli.clean.js`, I found a proxy on `process.env`. It was spying on environment variable access. Crucially, a variable `DEBUG_KEY` was being assigned.

```javascript
// Revealed Code
const DEBUG_KEY = process.env.ROOTACCESS_DEBUG;
if (DEBUG_KEY === "LAYER_ONE") {
    console.log("[DEBUG] Layer 1 unlocked!");
    // ... prints Fragment 1
}
```

**Exploit:**
Run the CLI with the expected environment variable.

```bash
user@ctf:~$ ROOTACCESS_DEBUG=LAYER_ONE ./cli.js
```

**Terminal Output:**
```
[DEBUG] Layer 1 unlocked!
[DEBUG] Fragment 1: root{N0
```

### Layer 2: Access Control (`ROOTACCESS_ADMIN`)

**Code Analysis:**
Further down, the logic checked for an "Admin Mode".
```javascript
const ADMIN_MODE = process.env.ROOTACCESS_ADMIN === "shadowgate";
// ...
if (ADMIN_MODE) {
    console.log("[ADMIN] Fragment 2: " + ...);
}
```

**Exploit:**
Set the admin variable to the hardcoded string found in the code.

```bash
user@ctf:~$ ROOTACCESS_ADMIN=shadowgate ./cli.js status
```

**Terminal Output:**
```
[ADMIN] Elevated access detected!
[ADMIN] Fragment 2: d3_Cl1_
```

### Layer 3: Hidden Arguments (`scan --ultra`)

**Code Analysis:**
The `commands` object mapped inputs to functions. I noticed logic inside `scan` that checked for undocumented flags.
```javascript
if (args.includes("--ultra")) {
    console.log("[ULTRA] Fragment 3: ...");
}
```

**Exploit:**
```bash
user@ctf:~$ ./cli.js scan --ultra
```

**Terminal Output:**
```
[*] Initiating security scan...
[ULTRA] Fragment 3: R3v3rs3
```

### Layer 4: Hidden Servers (`omega-7`)

**Code Analysis:**
The `connect` command had a whitelist of servers.
```javascript
if (server === "omega-7") {
    // Hidden connection logic
    console.log("[CLASSIFIED] Fragment 4: ...");
}
```

**Exploit:**
```bash
user@ctf:~$ ./cli.js connect --server=omega-7
```

**Terminal Output:**
```
[*] Connecting to server: omega-7
[+] Connection established to classified server!
[CLASSIFIED] Fragment 4: _3ng1n3
```

### Layer 5: Chain Encryption (`decrypt`)

**Code Analysis:**
The `decrypt` command required a `--chain` key. The code revealed this key was an MD5 hash of the first two fragments combined.
*   Fragment 1: `root{N0`
*   Fragment 2: `d3_Cl1_`
*   Target: `MD5("root{N0d3_Cl1_")[0:8]`

**Exploit:**
I calculated the hash (`aac9fbe6`) and passed it to the CLI.

```bash
user@ctf:~$ ./cli.js decrypt --msg=UNLOCK_CHAIN --chain=aac9fbe6
```

**Terminal Output:**
```
[+] Chain decryption successful!
[CHAIN] Fragment 5: 3r1ng_
```

### Layer 6: Internal Commands (`__internal__`)

**Code Analysis:**
The `commands` object contained a key `__internal__`. This command was not listed in the `help` output but was fully functional.

**Exploit:**
```bash
user@ctf:~$ ./cli.js __internal__
```

**Terminal Output:**
```
[INTERNAL] Access granted to internal API
[INTERNAL] Fragment 6: M4st3r
```

### Layer 7: Time Shadows (`shadow`)

**Code Analysis:**
The `shadow` command enforced a strict time window check:
```javascript
function isInShadowWindow() {
    const m = new Date().getUTCMinutes();
    return (m >= 0 && m <= 10) || (m >= 30 && m <= 40);
}
```
It also verified a "token" generated from the current time.

**Exploit:**
Instead of waiting for the right time, I **patched** the javascript file to force `isInShadowWindow` to return `true`. I then manually calculated the valid hex token (`D00A1A`) for the current timestamp.

```bash
user@ctf:~$ ./cli.patched.js shadow --token=D00A1A
```

**Terminal Output:**
```
[+] Shadow access granted!
[SHADOW] Fragment 7: _0f_
```

### Layer 8: Physical File Keys (`unlock`)

**Code Analysis:**
The `unlock` command checked for the *existence* and *content* of a specific file.
*   Path: `/tmp/.rootaccess_shadow`
*   Content: `SHA256(CODENAME + "_UNLOCK_" + VERSION)[0:16]`

**Exploit:**
I calculated the hash (`d3f8591aefdb7158`) and created the file.

```bash
user@ctf:~$ echo -n "d3f8591aefdb7158" > /tmp/.rootaccess_shadow
user@ctf:~$ ./cli.js unlock
```

**Terminal Output:**
```
[+] Unlock file verified!
[UNLOCK] Fragment 8: Sh4d
```

### Layer 9: Protocol Handshake

**Code Analysis:**
This simulated a TCP 3-way handshake.
1.  Client sends `--syn`.
2.  Server returns `TOKEN` + `TIMESTAMP`.
3.  Client must respond with `--ack` = `SHA256(TIMESTAMP + "SHADOWGATE" + "ACK")`.

**Exploit:**
I ran the SYN step, got the timestamp, calculated the SHA256 hash in Node.js, and sent the ACK.

```bash
user@ctf:~$ ./cli.js handshake --ack=A88FF421 --ts=1770387030084
```

**Terminal Output:**
```
[ACK] Handshake complete!
[ESTABLISHED] Fragment 9: 0ws
```

---

## Phase 3: The Master Key (Layer 10)

### Key Forge Logic
The final `assemble` command required a `MASTER_KEY`. The `forge` command revealed it was composed of 5 parts:
1.  **VERSION**: `1.3.37` -> `1337`
2.  **CODENAME**: Hash of "SHADOWGATE" -> `3987`
3.  **TIMESTAMP**: Hex encoded -> `1B`
4.  **XOR_PAIR**: `1403`
5.  **PRIMES**: `29`

Hint 6 revealed the pattern: `SHADOW_{v}_{codename}{xor}_{time}{primes}_GATE`.

**Master Key:** `SHADOW_1337_39871403_1B29_GATE`

### Final Assembly

```bash
user@ctf:~$ ./cli.js assemble --key=SHADOW_1337_39871403_1B29_GATE
```

**Terminal Output:**
```
[✓] MASTER KEY ACCEPTED

[FINAL] Fragment 10: }

[*] Assembling fragments...
  Fragment 01: root{N0
  Fragment 02: d3_Cl1_
  Fragment 03: R3v3rs3
  Fragment 04: _3ng1n3
  Fragment 05: 3r1ng_
  Fragment 06: M4st3r
  Fragment 07: _0f_
  Fragment 08: Sh4d
  Fragment 09: 0ws
  Fragment 10: }

════════════════════════════════════════════════════════════
[✓] FLAG: root{N0d3_Cl1_R3v3rs3_3ng1n33r1ng_M4st3r_0f_Sh4d0ws}
════════════════════════════════════════════════════════════
```

The challenge was successfully completed by systematically analyzing the de-obfuscated code logic and manipulating the runtime environment to satisfy each condition.
