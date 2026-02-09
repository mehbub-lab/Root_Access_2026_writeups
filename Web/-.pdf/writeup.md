# Approach
-- Inspect HTML Source: View the source code of the main page. You'll find a hidden comment pointing to a GitHub repository: https://github.com/Asif-Tanvir-2006/rootaccess_web_chal_pdf.
-- Check Commit History: The README hints at ignoring "history," which is a clue to check the git commit history.
-- Decode Secret Message: In the commits, there's a suspicious Base64 message.
-- Base64 Decode: dWdnY2Y6Ly9... becomes uggcf:Ly/enj....
-- ROT13 Decode: The result is still obfuscated. Applying ROT13 reveals a URL: https://raw.githubusercontent.com/Asif-Tanvir-2006/fonts/main/font.ttf.
-- Analyze the Font: Download font.ttf and run the strings command on it (or open it in a text editor and search).
-- Find Flag: You will find the flag root{easy_if_u_follow} at the end of the file.



# Steps to Solution

1. Exploration
Visited the challenge website: https://rootaccess-web-chal-pdf.vercel.app/
Analyzed the HTML source and found a hidden comment:


html comment
<!-- {
    "version": "1.0.3",
    "allow-cookies": "all",
    "github_url": "https://github.com/Asif-Tanvir-2006/rootaccess_web_chal_pdf/tree/main",
    "author": "Asif"
    a
} -->
This pointed to the GitHub repository: https://github.com/Asif-Tanvir-2006/rootaccess_web_chal_pdf

2. GitHub Investigation
Explored the GitHub repository.
The README.md contained a hint: "Ignore the history of these people and try getting the flag, just like you ignore commit histories in your github repos"
Checked the commit history and found a suspicious commit message 8622249 with Base64 encoded text: dWdnY2Y6Ly9lbmoudHZndWhvaGZyZXBiYWdyYWcucGJ6L05mdnMtR25haXZlLTIwMDYvc2JhZ2Yvem52YS9zYmFnLmdncw==

3. Decoding and Retrieval
Decoded the Base64 string to get a ROT13 string: uggcf:Ly/enj.tvguhbusercontent.pbz/Nfvs-Gnaive-2006/sbagf/znva/sbag.ggs
Applied ROT13 decoding to reveal a URL: https://raw.githubusercontent.com/Asif-Tanvir-2006/fonts/main/font.ttf
Downloaded the font.ttf file.

4. Flag Extraction
Ran strings font.ttf and searched for "flag" or "root".
Found the flag at the end of the file strings: root{easy_if_u_follow}



# Flag
root{easy_if_u_follow}

# Tools Used
- ROT13 Decoder
- Base64 Decoder
- Text Editor
