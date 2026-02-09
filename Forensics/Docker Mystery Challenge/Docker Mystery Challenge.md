# Docker Mystery Challenge

This document outlines the step-by-step methodology used to solve the "RootAccess" Docker challenge and reconstruct the hidden flag.

**Challenge Goal:** Recover a fragmented flag hidden inside a Docker image.
**Target Image:** `ghcr.io/uttam-mahata/rootaccess:latest`

---

## 🏗️ Methodology & Tools Used

The investigation followed a standard container forensics workflow:
1.  **Acquisition:** Pulling the target image.
2.  **Static Analysis:** Inspecting image metadata (Labels, Env Vars) and layer history without running the container.
3.  **Dynamic Analysis:** Running the container to extract artifacts from the filesystem.

### 🛠️ Tools
-   **Terminal:** Linux bash shell
-   **Docker CLI:** `docker pull`, `docker inspect`, `docker history`, `docker run`
-   **Text Processing:** `grep`, `cat`

---

## 🔍 Investigation Walkthrough

### Step 1: Image Acquisition and Static Analysis (Metadata)

First, I pulled the image and inspected its configuration to look for low-hanging fruit like environment variables or labels.

**Command:**
```bash
docker pull ghcr.io/uttam-mahata/rootaccess:latest
docker inspect ghcr.io/uttam-mahata/rootaccess:latest
```

**Terminal Output (Snippet):**
```json
"Config": {
    "Env": [
        "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        "FLAG_PART_2=D0ck3r_"  <-- FOUND PART 2
    ],
    "Labels": {
        "flag_part_3": "1m4g3s_",  <-- FOUND PART 3
        "org.opencontainers.image.ref.name": "ubuntu"
    }
}
```

> **Detailed Findings:**
> -   **Part 2:** Found in the `Env` section: `D0ck3r_`
> -   **Part 3:** Found in the `Labels` section: `1m4g3s_`

---

### Step 2: Deep Static Analysis (Layer History)

Docker images are built in layers. Secrets are often accidentally committed in intermediate layers and then deleted in later ones. I used `docker history --no-trunc` to see the full commands used to build each layer.

**Command:**
```bash
docker history --no-trunc ghcr.io/uttam-mahata/rootaccess:latest
```

**Terminal Output (Snippet):**
```text
IMAGE          CREATED BY                                                                                                                                  
...
<missing>      /bin/sh -c echo "Part of the flag is hidden in the layers..." > /tmp/hint.txt && echo "FLAG_PART_1: root{L4y3r3d_" > /tmp/.secret_layer.txt
<missing>      /bin/sh -c rm /tmp/.secret_layer.txt
...
<missing>      /bin/sh -c echo "N3v3r_F0rg3t}" > /app/.hidden_flag_part4.txt && chmod 600 /app/.hidden_flag_part4.txt
```

> **Detailed Findings:**
> -   **Part 1:** Found in a build command that created a temporary secret file: `root{L4y3r3d_`
> -   **Clue for Part 4:** I noticed a command creating a file named `/app/.hidden_flag_part4.txt` with content `N3v3r_F0rg3t}`. Although I can see the content in the history command itself here, usually one would need to run the container to cat the file if it wasn't obvious in the history (e.g., if it was a `COPY` command).

---

### Step 3: Dynamic Analysis (Container Execution)

To verify the file content seen in the history and ensure I had the correct final part, I spun up a container.

**Command:**
```bash
docker run --rm --entrypoint /bin/sh ghcr.io/uttam-mahata/rootaccess:latest -c 'cat /app/.hidden_flag_part4.txt'
```

**Terminal Output:**
```text
N3v3r_F0rg3t}
```

> **Detailed Findings:**
> -   **Part 4:** Validated as `N3v3r_F0rg3t}`

---

## 🚩 Final Flag Reconstruction

Combining the pieces in the logical order (Part 1 -> Part 2 -> Part 3 -> Part 4):

1.  `root{L4y3r3d_`
2.  `D0ck3r_`
3.  `1m4g3s_`
4.  `N3v3r_F0rg3t}`

**Final Flag:**
```text
root{L4y3r3d_D0ck3r_1m4g3s_N3v3r_F0rg3t}
```
