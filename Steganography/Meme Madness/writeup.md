# Meme Madness
## Approach
1. Artifact Analysis

Krish_ka_gana_sunega.webm
: strings revealed KEY=Krish42.

nahi.jpeg
: contained a hidden byte sequence starting at offset 0x66a2, which included the "pieces" IMy81ZK, LaGh, 7rUiY visible in strings.

challenge_video.mp4
: contained a 38-byte encrypted trailer appended to the end of the file (after valid MP4 data).
2. Encryption Logic
The encryption was a multi-part XOR: Plaintext = Ciphertext XOR Cover_Bytes XOR Key

Ciphertext: 38 bytes found at the end of 

challenge_video.mp4
.
Cover_Bytes: 38 bytes found in 

nahi.jpeg
 starting at offset 0x66a2.
Key: Krish42 (repeating).
3. Decryption
 
# Check Screenshot for script
-------

# Step-by-Step Methodology
1. Identify the Key in the Webm File
We examine 

Krish_ka_gana_sunega.webm
 for hidden strings. The challenge description mentions "the key is hidden somewhere else".

Command:


strings Krish_ka_gana_sunega.webm | grep KEY
Output:

KEY=Krish42


2. Locate the Hidden "Pieces" in Nahi.jpeg
The challenge mentions "Munna Bhai... hid the secret... in pieces". We inspect the files for anomalous data. Using strings or a hex editor on 

nahi.jpeg
 reveals three unusual strings near the end of the file: IMy81ZK, LaGh, 7rUiY.

#Commands


strings nahi.jpeg | tail -n 10
These strings are part of a larger binary blob within the JPEG file structure. Checking the hex dump around these strings reveals a 38-byte block starting at offset 0x66a2 (26274).

Command (to view hex):

bash
xxd -s 26274 -l 38 nahi.jpeg
Extracted Bytes (Pad): b8 d4 b5 fc df 0d e3 5b f3 34 a6 d2 56 0c af 6f 3c 6b 8c 15 28 c4 a1 70 b9 20 7d 53 17 34 23 97 9b 37 72 55 69 59

3. Extract the Encrypted Trailer from the Video
We check 

challenge_video.mp4 (or 

mad.mp4, which is identical in this context). The file structure shows data appended after the valid MP4 atoms. Using binwalk or exiftool indicates the file ends earlier than its total size. We find 38 bytes appended at the end.

Command (to check trailer):

tail -c 38 challenge_video.mp4 | xxd
Extracted Bytes (Ciphertext): 81 c9 b3 fb cc 5a b9 65 f5 29 b4 d7 03 52 88 78 0a 6b 94 48 7e ea aa 46 a3 3b 16 17 35 24 23 8a ac 6b 21 6c 7f 4d

4. Decrypt the Flag
We have three components of length 38 (or repeating key):

Ciphertext: 38 bytes from 

challenge_video.mp4

Pad/Salt: 38 bytes from 

nahi.jpeg

Key: Krish42 (7 bytes).
The decryption logic is a simple XOR sum of all three components: Flag = Ciphertext XOR Pad XOR Key

Python Script:

python
import itertools
 1. Copied manually from 'tail -c 38 challenge_video.mp4 | xxd'
cipher = bytes.fromhex('81c9b3fbcc5ab965f529b4d7035288780a6b94487eeaaa46a33b16173524238aac6b216c7f4d')

 2. Copied manually from 'xxd -s 26274 -l 38 nahi.jpeg'
    (Found by searching for the "pieces" strings in hex editor)
pad = bytes.fromhex('b8d4b5fcdf0de35bf334a6d2560caf6f3c6b8c1528c4a170b9207d53173423979b3772556959')
 
 3. Found in webm file
key = b'Krish42' 
 Repeat key to match length
key_repeated = (key * 10)[:38]
 XOR Decryption
flag = []
for c, p, k in zip(cipher, pad, key_repeated):
    flag.append(c ^ p ^ k)
print(bytes(flag).decode())



# FLAG

root{chuttamalle_spidey_is_vibin_hard}


# Tools Used:

strings: Used to extract readable text (KEY=Krish42 and pieces IMy...) from binary files.
grep: Used to filter the output of strings.
xxd: Used to inspect binary data and extract specific hex sequences (the pad in nahi.jpeg and ciphertext in challenge_video.mp4).
tail: Used to easily extract the appended data at the end of the video file.
python: Used to perform the custom XOR decryption logic using the extracted components.
