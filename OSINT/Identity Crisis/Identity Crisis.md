# The Identity Crisis

**Challenge Name:** The Identity Crisis  
**Category:** OSINT + Web  
**Objective:** Identify the real person behind a handle, locate their digital portfolio, and reverse a client-side JavaScript check to reveal the flag.

---

## 🚩 Challenge Overview
The challenge begins with a target handle, **"daemonized.u"**, and a few contextual clues:
- Their personal motto/bio is: *"I am who I am"*.
- The website associated with them treats all visitors as "guests," but a "true daemon" can unlock the secret.

This required a two-pronged approach: **OSINT** to find the target's identity and portfolio, followed by **Web Reverse Engineering** to bypass the client-side identity check.

---

## 🔍 Step 1: OSINT - Piercing the Veil
To find the "true daemon," I needed to locate the target's digital footprint. 

### Initial Information Gathering
Knowing the affiliation (ASCE IIEST Shibpur), I targeted platforms common for students and academic groups:
1.  **Username Variations:** I looked for variations of `daemonized.u` across social media platforms.

### The Breakthrough
A search for `daemonized_u` on Instagram yielded a profile with:
- **Bio:** "I am who I am." (An exact match for the challenge clue).
- **Link:** `https://uttamm.web.app/`

This link revealed the portfolio of **Uttam Mahata**, a student at IIEST Shibpur.

---

## 🛠️ Step 2: Technical Analysis - JavaScript Reversing
Visiting the portfolio site, I was greeted as a "guest." The goal was to find how the site distinguishes between a guest and the "true daemon."

### Inspecting the Source
I examined the source code and identified the main JavaScript bundle: `/assets/index-CtPivjS7.js`.

### Analyzing the Bundle
Searching for keywords like `daemon`, `guest`, and `flag` within the minified JS revealed a logic block handling "identity tokens":

```javascript
// Structurally represented logic
localStorage.getItem("identity_token") || localStorage.setItem("identity_token", "guest");

if (identityToken === "daemon") {
    const d = "cm9vdHsxXzRtX1doMF8xXzRtXzIwMjV9";
    displayFlag(atob(d));
}
```

The code checks `localStorage` for an `identity_token`. If it equals `"daemon"`, it base64-decodes a hardcoded string `d` and displays it.

---

## 🔓 Step 3: Flag Extraction
The flag was hiding in plain sight within the JavaScript variable `d`. I didn't even need to manipulate the `localStorage`; I simply needed to decode the base64 string.

### Decoding the Secret
Using the terminal, I decoded the payload:

```bash
echo "cm9vdHsxXzRtX1doMF8xXzRtXzIwMjV9" | base64 -d
```

**Output:** `root{1_4m_Wh0_1_4m_2025}`

The flag "1_4m_Wh0_1_4m" translates to "I am who I am", perfectly closing the loop on the OSINT clues.

---

## 🎯 Final Flag
**`root{1_4m_Wh0_1_4m_2025}`**

