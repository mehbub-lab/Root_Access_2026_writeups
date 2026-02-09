# Source Inspector

---

## Approach
Bypass PHP filter
-- Opened and got 3 sites 
-- Payload: Visit: https://daemon.lovestoblog.com/?page=PhP://FiLtEr/convert.base64-encode/resource=flag.php (Note the mixed case: PhP, FiLtEr)
-- Decode: Take the returned Base64 string and decode it entirely to see the PHP source code.
-- Result: root{php_wrappers_r3v3al_s3cr3ts}


Goal: Retrieve the flag from flag.php. Target: https://daemon.lovestoblog.com/ (also available on deity and evil subdomains). Vulnerability: Local File Inclusion (LFI) via the ?page= parameter.
----
# Methodology

1. Reconnaissance
We started by exploring the application's behavior.

Normal Usage: ?page=hello.txt displays the content of the text file.
Vulnerability Check: We identified that the application takes a file path in the page parameter and includes it.

2. Identifying the Problem
We verified that flag.php exists, but we couldn't read it directly.

Direct Inclusion (?page=flag.php): The page returned an empty result.
Reason: When a PHP file is "included" by the server, the server executes the code. If the code (like $flag = "...") doesn't print anything, the user sees nothing.
HTML Hint: A comment in the HTML source confirmed this: <!-- Hint: I tried including flag.php directly, but the screen was blank. Where did the text go? -->

3. The "Security Upgrade v2.0" Filter
To read the source code (and thus the variable), we needed to use a PHP wrapper like php://filter to encode the file content (e.g., base64) before it is executed. However, the application had a filter in place.
We fingerprinting the filter by testing various payloads:

php://filter/... -> Blocked/Empty. The filter detects the php:// protocol.
flag.php -> Blocked/Empty. The keyword flag is also likely filtered or monitored.

4. Bypass Attempts
We attempted several standard bypass techniques:

URL Encoding (%70hp://...): Failed. The server decodes the URL before filtering.
Double URL Encoding: Failed.
Path Traversal (....//): Failed.
Wrapper Variations (data://, expect://): Failed/Blocked.
Nested Keywords (pphphp://): Failed. This suggests the filter isn't just stripping keywords once (which would allow pphphp -> php).

5. The Solution: Mixed Case Bypass
PHP protocols and filter names are case-insensitive, but poorly written regex filters often look for exact lowercase matches (e.g., php:// or filter).

Attack Vector: We modified the casing of the protocol and keywords.
Payload: PhP://FiLtEr/convert.base64-encode/resource=flag.php
PhP: Bypasses a filter looking for php.
FiLtEr: Bypasses a filter looking for filter.
convert.base64-encode: Instructs PHP to encode the file content instead of executing it.
resource=flag.php: The target file.

6. Retrieval and Decoding
The successful payload returned a base64 string instead of executing the file:

"PD9waHAKJGZsYWcgPSAicm9vdHtwaHBfd3JhcHBlcnNfcjN2M2FsX3MzY3IzdHN9IjsKPz4K"
Decoding this string gives the original source code:

<?php
$flag = "root{php_wrappers_r3v3al_s3cr3ts}";
?>


# Flag
root{php_wrappers_r3v3al_s3cr3ts}

# Tools Used

-- Web Browser: This was the primary tool. Due to the site's anti-bot protection (an AES/JavaScript challenge page typical of InfinityFree hosting), standard command-line tools like curl or Python scripts failed to connect reliably. A real browser (or a browser automation tool) was necessary to execute the JavaScript and pass the challenge.
-- Developer Tools (Console): Used to execute JavaScript (e.g., to retrieve cookies or view page source) when the standard interface (right-click -> view source) might be blocked or cumbersome.
-- Base64 Decoder: Essential for decoding the retrieved string to get the final flag.

