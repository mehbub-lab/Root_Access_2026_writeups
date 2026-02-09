# Echoes of the Future

## Challenge Overview
**Objective**: Break into `vault.docx`, decipher the binary `lmao`, and retrieve the "Prophesied Texts" to find the flag.
**Files Provided**: 
- `lmao` (Binary data)
- `vault.docx` (Encrypted Word document with password "The Onion Field")
- `vaultkey.txt` (Riddle for the password)

## Approach & Solution

### Step 1: Unlocking the Vault
My initial reconnaissance identified `vault.docx` as an encrypted OLE Compound File. Inspecting the directory, I found `vaultkey.txt` containing a riddle:
> Two people I seek, whose names must be known... One of them made D Albert's tree... I want to know the name of the 3rd film of DOH, the Firefox

Identifying the subjects as **David Albert Huffman** (Huffman coding) and **David Oliver Huffman** (actor in *Firefox*), I determined the password was the title of David Oliver Huffman's third film: **The Onion Field**.

Using Python and `msoffcrypto-tool`, I decrypted the vault seamlessly.

**Decryption Command:**
```bash
# Setup virtual environment and install tool
python3 -m venv venv
./venv/bin/pip install msoffcrypto-tool olefile

# Run decryption script
python3 decrypt_vault.py
```

**Script `decrypt_vault.py`:**
```python
import msoffcrypto
file = msoffcrypto.OfficeFile(open("vault.docx", "rb"))
file.load_key(password="The Onion Field")
with open("decrypted.docx", "wb") as f:
    file.decrypt(f)
```

### Step 2: The Prefix-Free Code Riddle
Extracting `word/document.xml` from the decrypted file revealed a "Binary Prefix-Free Code Reconstruction Riddle". The riddle described a unique Huffman tree with precise constraints on subtree structures and terminal lengths.

I implemented a solver to reconstruct the tree based on these logical rules. The constraints (e.g., "Two terminals of length 6 are siblings", "Space has 111 encoding") deterministically assigned binary codes to the alphabet.

**Tree Construction Logic:**
- **00 Subtree**: Leaves `h`, `u`, `b`, `g`, `s`, `r` assigned to lengthy prefixes starting with `00`.
- **01 Subtree**: Right-recursive chain assigning `e`, `c`, `k`, `j`, `q`, `z`, `x`, `v`, `y`, `n`.
- **10 Subtree**: Balanced structure assigning `I`, `o`, `l`, `d`, `m`, `w`, `p`, `f`.
- **11 Subtree**: `a`, `t`, `[SPACE]` (111).

### Step 3: Bitstream Analysis & Decoding
Next, I analyzed the binary file `lmao`. Recognizing that Huffman codes are variable-length prefix codes, correct bit interpretation is critical. Through careful analysis of the riddle's bit-ordering hints, I determined the file used **Little Endian bit ordering** within each byte (i.e., bits must be read in reverse order: 76543210).

I wrote a decoding script that reversed the bits of each byte in `lmao` before traversing the reconstructed Huffman tree. This process converted the binary blob into a monoalphabetic substitution ciphertext.

**Decoding Snippet (Bit Reversal):**
```python
# Read binary and reverse bits for correct traversal
with open("lmao", "rb") as f:
    raw_data = f.read()
bitstring = "".join(f"{byte:08b}"[::-1] for byte in raw_data)

# Decode stream using the tree
decoded_text = ""
cur = ""
for b in bitstring:
    cur += b
    if cur in rev_codes:
        decoded_text += rev_codes[cur]
        cur = ""
```

### Step 4: Cryptanalysis
The resulting text was a monoalphabetic substitution cipher. The riddle provided explicit frequency rank hints:
- Rank 7 -> `r`
- Rank 8 -> `s`
- Rank 9 -> `h`
- ...and so on.

I performed frequency analysis on the decoded text, which aligned perfectly with the provided hints. Applying these fixed mappings and solving the remaining high-frequency letters (`e`, `t`, `a`, `o`, `i`, `n`) using standard English distribution patterns immediately revealed readable text.

**Solving Strategy:**
1. Map high-frequency cipher letters to `e, t, a, o, i, n`.
2. Apply the fixed mappings from the hints (`r`, `s`, `h`, `f`, `p`, `w`, `y`, `m`, `g`).
3. Refine the remaining letters based on context.

The resulting plaintext was a passage from a book.

### Step 5: The Flag
The deciphered text reads:
> "...The book was... The Theory and Practice of Oligarchical Collectivism..."

This is a passage from George Orwell's *1984*, reading from the frictional book titled **The Theory and Practice of Oligarchical Collectivism**. The challenge requested the Author's Name as the flag.

**Flag:**
`root{Emmanuel_Goldstein}`

## Tools Used
- **Python**: For bit manipulation, Huffman tree reconstruction, and substitution cipher solving.
- **msoffcrypto-tool**: To decrypt the password-protected OLE document.
- **Standard Linux Utils**: `unzip`, `grep` for initial file inspection.
