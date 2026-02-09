# Challenge Name 
The Library Code

---
To access the treasure of past questions, one must know the path. The IIEST Library Question Bank holds the answer—its digital address (10.11.1.6) reveals the key. Sum all the essence within.
with a file encrypted.txt having strings:
Dro pvkq sc ss3cd5_vslbkbi



# Step 1: Initial Analysis

Input provided: a short encrypted string.

Hint references an IP address: 10.11.1.6.

The phrase “Sum all the essence within” suggests summing the digits of the IP.

# Calculate:

1 + 0 + 1 + 1 + 1 + 6 = 10

This strongly indicates a Caesar cipher with shift = 10.

No files were provided, so no file or strings checks were needed.

# Step 2: Core Technique

Technique used: Caesar Cipher Decryption

Reason:

Simple alphabetic substitution.

Explicit numeric hint gives the shift value.

Ciphertext format matches classic Caesar output.

Key observation:
The IP address directly gives the shift after summing its digits.

# Step 3: Implementation

Used standard Linux tools to decrypt with a rotation of 10.

#Method 1 – Using tr in terminal:
echo "Dro pvkq sc ss3cd5_vslbkbi" | tr 'A-Za-z' 'K-ZA-Jk-za-j'

Explanation:

tr rotates letters backward by 10.

Numbers and underscores remain unchanged.

# Output:

The flag is ii3st5_library
Alternative (optional) – CyberChef / online Caesar decoder

Set rotation to 10.

# Step 4: Extraction

Decrypted message:

The flag is ii3st5_library

Placed into required format:


# Flag

root{ii3st5_library}


# Tools Used

-echo – Provide ciphertext input
-tr – Perform Caesar rotation in terminal
-CyberChef – Manual Caesar verification
-Linux Terminal
-Bash
