# Dancing Men - CTF Writeup

## Challenge Overview
**Challenge Name:** Dancing Men  
**Category:** Misc  
**Description:** A Sherlock Holmes-themed challenge requiring binary analysis of a polyglot file and decoding a "Dancing Men" stick figure cipher.

---

## Methodology

### Step 1: File Forensics & Polyglot Discovery
Initial analysis of the provided files revealed that `notSoImportant` was suspicious. While it appeared to be a JPEG image, hex analysis showed it was a **polyglot file** containing an encrypted ZIP archive.

1. **Locating the ZIP:** 
   I performed a hex dump analysis to find the ZIP file signature (`PK\x03\x04`).
   ```bash
   xxd notSoImportant | grep "504b 0304"
   ```
2. **Offset Calculation:** 
   The signature was located at offset `0xAA204`. However, there were 4 extra padding bytes (`89 1f ff d9`) between the JPEG data and the ZIP starting point.
3. **Extraction:**
   Knowing the actual ZIP data starts at `0xAA208`, I extracted it using `dd`:
   ```bash
   dd if=notSoImportant of=secrets.zip bs=1 skip=$((0xAA204 + 4))
   ```

### Step 2: Building the Cipher Dictionary
The challenge included a file called `shredder_of_truth.zip`. After unzipping it, I examined the `strip` folder which contained 50 PNG images.

- **The Discovery:** Each image featured a unique stick figure pose paired with a single letter (A-Z).
- **The Dictionary:** By mapping these figures to their letters, I created a visual translation key for the "Dancing Men" cipher.

### Step 3: Decoding the Secret Message
I turned my attention to `dancing_challenge.png`, which contained a sequence of 22 dancing figures.

- **Hand-Matching:** I manually matched each of the 22 figures against the dictionary I had just built from the `strip` folder.
- **The Result:** 
  The figures translated to: `T-H-A-T-S-_-S-O-M-E-_-N-E-R-D-Y-_-S-T-U-F-F`
- **Transformation:** Following standard CTF logic, I converted the string to uppercase and used underscores as indicated.
  **Password:** `THATS_SOME_NERDY_STUFF`

### Step 4: Final Extraction
Using the decoded password, I attempted to unlock `secrets.zip` (the extracted file from `notSoImportant`).

```bash
7z e -pTHATS_SOME_NERDY_STUFF secrets.zip
```
The extraction was successful, revealing `flag.txt`.

---

## Tools Used
- **Hexdump / xxd:** Binary analysis and signature identification.
- **dd:** Precise extraction of embedded data.
- **Manual Analysis:** Hand-matching cipher fragments to build a lookup table.
- **7-Zip:** Decrypting AES-protected archives.




## Final Flag
**Flag:** `root{3l3m3n74ry_my_d34r_w47s0n}`
