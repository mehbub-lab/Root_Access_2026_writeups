# Rootium Browser Vault

This write-up details the process of reverse engineering the Rootium Browser to unlock its "Secret Vault" and retrieve the root flag.

## Challenge Overview
The objective was to recover a master password protecting a "Secret Vault" feature within a custom secure browser (`rootium-browser`) distributed as a Debian package. This required extracting the application, identifying the authentication mechanism, and reverse engineering the binary responsible for password verification.

## Tools Used
- `ar`: For extracting the `.deb` package.
- `tar`: For extracting the data archive within the `.deb`.
- `asar`: For unpacking the Electron application resources.
- `file`: For identifying file types.
- `objdump`: For disassembling the binary executable.
- `python3`: For writing the decryption script.

## Methodology

### 1. Extraction and Initial Analysis
The first step was to inspect the contents of the installer package `rootium-browser_1.0.0_amd64-1.deb`.

```bash
mkdir extracted
cd extracted
ar x ../rootium-browser_1.0.0_amd64-1.deb
tar -xf data.tar.xz
```

This revealed the installation directory structure. The browser was installed in `/opt/Rootium`. Listing the files, I identified it as an Electron-based application due to the presence of `resources/app.asar`.

### 2. Locating the Application Logic
Electron applications pack their source code into an ASAR archive. I used the `asar` tool (via `npx`) to extract `app.asar` and inspect the main process code.

```bash
cd opt/Rootium/resources
npx asar extract app.asar extracted_app
```

Analyzing `extracted_app/main.js`, I found the code responsible for spawning the vault process:

```javascript
const binaryName = process.platform === 'win32' ? 'rootium_vault.exe' : 'rootium_vault';
// ...
vaultProcess = spawn(binPath);
// ...
ipcMain.on('unlock-vault', (event, password) => {
    vaultProcess.stdin.write(`AUTH ${password}\n`);
});
```

This confirmed that the authentication logic resides in an external binary named `rootium_vault` located in the `bin/` directory.

### 3. Reverse Engineering the Binary
I located the binary at `extracted_app/bin/rootium_vault` and confirmed it was a 64-bit ELF executable.

```bash
file bin/rootium_vault
# bin/rootium_vault: ELF 64-bit LSB pie executable, x86-64 ...
```

I used `objdump` to disassemble the binary and analyze its control flow.

```bash
objdump -d -M intel bin/rootium_vault > vault.asm
```

The disassembly revealed a function at offset `0x125c` that performed complex bitwise operations. This function appeared to be a decryption routine for the stored password hash/encrypted string.

Key observations from the assembly:
- **XOR Operation**: The byte is XORed with `0x42`.
- **Rotate Right (ROR)**: The result is rotated right by 3 bits.
- **Rolling Key XOR**: The result is XORed with a key derived from stack values.

The key bytes were reconstructed from stack initialization:
- `0xd8, 0xc5, 0xc5, 0xde` (from `rbp-0x12`)
- `0xde, 0xc3, 0xdf, 0xc7` (from `rbp-0xf`, overlapping)

Resulting Key Stream: `[0xd8, 0xc5, 0xc5, 0xde, 0xc3, 0xdf, 0xc7]`

### 4. Decrypting the Master Password
I extracted the encrypted password bytes from the binary (offset `0x3080`) and wrote a Python script to reverse the process. Since the validation logic compares the *input* processed by this function to a stored value, or decrypts a stored value to compare with input, I simulated the decryption routine to reveal the expected password.

**Solver Script (`solve.py`):**

```python
data = [0x62, 0x98, 0x92, 0x82, 0xaa, 0x13, 0x42, 0x70, 0xa2, 0x9a, 0x78, 0x9a, 
        0x13, 0xaa, 0x70, 0xa2, 0xa2, 0x1b, 0x98, 0x68, 0xb8, 0x60]
key_bytes = [0xd8, 0xc5, 0xc5, 0xde, 0xc3, 0xdf, 0xc7]

def ror(val, r_bits, max_bits=8):
    return ((val & 255) >> r_bits) | ((val << (8 - r_bits)) & 255)

password = ""
for i, b in enumerate(data):
    b1 = b ^ 0x42           # Step 1: XOR 0x42
    b2 = ror(b1, 3)         # Step 2: ROR 3
    k = key_bytes[i % 7]
    k_xor = k ^ 0xaa        # Step 3: Key derivation
    res = b2 ^ k_xor        # Step 4: Final XOR
    password += chr(res)

print(f"Recovered Password: {password}")
```

**Output:**
```
Recovered Password: v4ult_m4st3r_p4ss_2026
```

### 5. Retrieving the Flag
With the master password recovered, I interacted with the `rootium_vault` binary directly to authenticate and retrieve the flag.

```bash
./bin/rootium_vault
AUTH v4ult_m4st3r_p4ss_2026
# Output: ACCESS_GRANTED

GET_FLAG
# Output: FLAG:root{n0_m0r3_34sy_v4ult_3xtr4ct10n_99}
```

## Conclusion
By dissecting the application structure and reverse engineering the custom encryption routine within the helper binary, I successfully bypassed the security mechanism.

**Final Flag:** `root{n0_m0r3_34sy_v4ult_3xtr4ct10n_99}`
