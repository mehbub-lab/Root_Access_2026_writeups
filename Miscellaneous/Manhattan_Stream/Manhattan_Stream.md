# Manhattan_Stream


## 1. Initial Reconnaissance & Discovery
I started by analyzing the partition layout of the provided `secret_disk.vhd` file using `mmls`.

**Command:** `mmls secret_disk.vhd`

**Result:** The NTFS partition started at sector 2048.

Next, I listed the files in the partition using `fls` to see if anything was hidden.

**Command:** `fls -o 2048 secret_disk.vhd`

**Critical Finding:** I noticed a file named `Newsur:important` (Inode 52-128-6).

The colon (`:`) syntax indicates an NTFS Alternate Data Stream (ADS). This meant the data was hidden in the metadata of the `Newsur` directory, not in a visible file.

## 2. Investigating Decoys (The Troll Flag)
Before diving into the ADS, I checked other suspicious files. I found `oppenheimer.png:hidden` (another ADS) and extracted its strings.

**Command:** `icat -o 2048 secret_disk.vhd 50-128-4 | strings`

**Result:** `root{get_the_correct_flag_lol}`

This was a decoy/troll flag, confirming I was on the right track but looking in the wrong place.

## 3. Analyzing the "Important" Stream
I returned to the suspicious `.:important` stream (Inode 52-128-6) and extracted it.

**Command:** `icat -o 2048 secret_disk.vhd 52-128-6 | head`

**Analysis:** The file header `%PDF-1.7` confirmed it was a PDF document.

I decompressed the PDF content to analyze its structure. I found that the document contained raw binary image streams. Using `grep`, I located the exact byte offsets for these streams.

**Command:** `icat -o 2048 secret_disk.vhd 52-128-6 | grep -a -b -o "stream"`

**Offsets Found:** 937 (Image 9) and 1617 (Image 10).

## 4. The Solution: Raw Image Reconstruction
The PDF contained raw RGB pixel data (FlateDecoded) without valid image headers, so standard tools couldn't open them.

To solve this, I manually constructed a PPM (Portable Pixel Map) header (P6) based on the PDF object dimensions (397x165) and injected it before the raw data. This forced `tesseract` (OCR) to interpret the raw bytes as a valid image.

### Recovering Flag Part 1 (Image 9)
I skipped to offset 945 (start of data) and piped the reconstructed image to `tesseract`.

**Command:**
```bash
{ printf "P6\n397 165\n255\n"; icat -o 2048 secret_disk.vhd 52-128-6 | dd bs=1 skip=945 | zlib-flate -uncompress; } | tesseract stdin stdout
```
**Output:** `root{nOw_1_4m_`

### Recovering Flag Part 2 (Image 10)
I repeated the process for the second image at offset 1625.

**Command:**
```bash
{ printf "P6\n397 165\n255\n"; icat -o 2048 secret_disk.vhd 52-128-6 | dd bs=1 skip=1625 | zlib-flate -uncompress; } | tesseract stdin stdout
```
**Output:** `b3cOm3_d347h}`

## 5. Final Flag
Combining the two parts from the hidden PDF images gave the complete flag:

`root{nOw_1_4m_b3cOm3_d347h}`

## Tools Used
*   `mmls`: Partition layout analysis
*   `fls`: Filesystem listing (ADS discovery)
*   `icat`: Inode data extraction
*   `grep`: Locating binary stream offsets
*   `dd`: Data carving
*   `zlib-flate`: Raw stream decompression
*   `printf`: File header injection
*   `tesseract`: Optical Character Recognition (OCR)
