# Challenge Name

Internal Anomaly

---
The challenge involved analyzing a packet capture file (root.pcapng) to uncover what an attacker obtained through encrypted channels. The solution required multiple stages: identifying suspicious network traffic patterns, discovering TLS session keys hidden in plain sight, decrypting encrypted communications, and extracting the flag from the decrypted content.

**Provided Files:**
- `root.pcapng` – A network packet capture file containing traffic from an anomalous

#Approach
 analyzed `root.pcapng` and retrieved the flag.


## Steps Taken
1.  **Initial Analysis**: Inspecting the protocol hierarchy revealed a mix of standard traffic (local discovery, Ubuntu updates) and encrypted channels (TLS/SSL).

2.  **File Extraction**: I extracted HTTP objects from the pcap file. This revealed a suspicious file named `runtime_cache.dat`.
    -   Analysis of `runtime_cache.dat` showed it to be a TLS key log file (`SSLKEYLOGFILE` format).

3.  **Decryption**: Using the extracted key log file, I decrypted the TLS traffic in the pcap.
    -   Command: `tshark -r root.pcapng -o tls.keylog_file:extracted_files/runtime_cache.dat ...`

4.  **Identifying the Exploit**:
    -   In the decrypted traffic, I found a single HTTP GET request inside a TLS session.
    -   The request was: `GET /sys_health_report.log HTTP/1.1` to `10.31.42.158:8443`.
    -   User-Agent: `curl/8.5.0`

5.  **Flag Retrieval**:
    -   I followed the TCP stream (Index 3025) for this request.
    -   The response contained a system health report with the flag.



## Evidence
### Decrypted GET Request
```
GET /sys_health_report.log HTTP/1.1
Host: 10.31.42.158:8443
User-Agent: curl/8.5.0
Accept: */*
```
### Decrypted Response
```
HTTP/1.0 200 ok
Content-type: text/plain
===== System Health Summary =====
Node: srv-prod-02
Timestamp: 2026-02-06 02:11:43
CPU Status: Normal
Memory Utilization: 73%
Disk Integrity: Verified
I/O Latency: Within threshold
audit_maker= ROOT{P4cK3T_4n4L7515_55ucC355F0L}
Scheduler: Active
Auto-healing: Enabled


## The Flag
`ROOT{P4cK3T_4n4L7515_55ucC355F0L}`



#Tools Used
-- tshark:

This was the primary tool (the command-line version of Wireshark).
Usage:
Traffic Analysis: viewing protocol hierarchies (-z io,phs) and conversation statistics.
Filtering: isolating specific traffic like HTTP, TLS, and DNS (-Y ...).
File Extraction: extracting the key log file (

runtime_cache.dat
) from the packet capture (--export-objects).
Decryption: using the extracted SSLKEYLOGFILE to decrypt TLS traffic (-o tls.keylog_file:...).
Stream Reconstruction: following the specific TCP stream to read the sys_health_report.log content (-z follow...).

-- grep:

Used to search through the massive amount of decrypted text data for specific keywords like "flag", "root{", and "secret".
file:

Used to identify the type of the extracted 

runtime_cache.dat
 (identifying it as ASCII text).



-- Languages
Bash / Shell Scripting: All commands were executed in a Linux terminal (Zsh) to chain tools together and manage files.
Wireshark Display Filter Syntax: Technically a query language used within tshark to filter packets (e.g., http.request and tcp, tls.handshake.type == 1).


