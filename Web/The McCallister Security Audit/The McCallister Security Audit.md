# The McCallister Security Audit

## Overview
This report documents the systematic bypass and data recovery of a secured McCallister environment. The challenge required a multi-layered approach involving web reconnaissance, metadata analysis, and steganographic extraction to retrieve a fragmented flag.

---

## Methodology

### Phase 1: Perimeter Reconnaissance
The initial entry point returned a `403 Forbidden` status. However, a deep dive into the HTML comments revealed a vital clue: 
> *“Tip: Kevin always leaves a trail in the metadata of his photos.”*

This directed the focus towards forensic analysis of visual assets rather than standard web vulnerabilities.

### Phase 2: Metadata Harvesting
Analysis began with `kevin_hallway.jpeg`. Using `exiftool`, I scrutinized the image's internal metadata.

```bash
exiftool kevin_hallway.jpeg
```

**Discovery:** A hidden parameter `page_id=0h_n0_i_f0rg0t` was found nested within the tags. 

Navigating to the new endpoint:
`https://homealone.fwh.is/?page_id=0h_n0_i_f0rg0t`

The page revealed a Base64-encoded string: `Um9hZCBSdW5uZXIg`.
- **Decoded Value:** `Road Runner`

---

### Phase 3: Steganographic Extraction

#### Fragment 1: The Buzz Archive
Applying binary analysis to `buzz_final.jpeg` indicated embedded data structures.

```bash
binwalk -e buzz_final.jpeg
```

This extracted a password-protected ZIP archive. Using the discovered passphrase `KevinMcAllister`, I retrieved a hex-encoded fragment and a `key_hint.txt` file.
- **Fragment 1 (Hex):** `370d0303293e5d18541c0d5e123b662a235a`

#### Fragment 2: Secret Communications
The image `worried_siblings.jpeg` appeared to house hidden data via steganography. Using `steghide` with the previously recovered passphrase `Road Runner`:

```bash
steghide extract -sf worried_siblings.jpeg
```

**Result:** Extracted the ending of the flag: `st3r_Pl4nn3r_2025}`.

---

### Phase 4: Decryption & Final Assembly
The `key_hint.txt` pointed towards a classic **ROT13** cipher for the initial fragment.

1. **Initial Fragment (Decoded from ROT13):** `root{K3v1n_1s_4_M4`
2. **Second Fragment (From steghide):** `st3r_Pl4nn3r_2025}`

By merging these components, the full administrative flag was reconstructed.

---

## Tools Utilized
| Tool | Purpose |
| :--- | :--- |
| **Exiftool** | Metadata inspection and tag discovery |
| **Binwalk** | Binary carving and file extraction |
| **Steghide** | Extraction of password-protected steganographic data |
| **CyberChef** | Base64 decoding and cryptographic analysis |
| **ROT13** | Multi-stage character rotation for final decryption |

## Final Flag
**`root{K3v1n_1s_4_M4st3r_Pl4nn3r_2025}`**
