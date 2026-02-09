#Challenge Name

[REDACTED]

#Approach

This challenge focused on uncovering information hidden behind visual redactions in a PDF. Rather than involving cryptography or encoding, the flag was concealed using simple graphical overlays. By loading the file into an image editor and removing these overlays, the original content could be recovered.

#Methodology
Step 1: Reconnaissance
A PDF file was provided with several portions covered by solid black blocks.
At first glance, it appeared the sensitive data was properly censored.
The file was imported into Pixlr (AI Editor) to inspect whether these black regions were permanent or just layered objects.
Upon closer inspection, it became clear that the “redactions” were merely placed on top of existing text, not baked into the document itself.

Step 2: Key Insight
The black bars were separate visual elements rather than part of the actual document content. This meant they could be manually removed.
Since Pixlr allows layer-based editing, it was possible to isolate and delete these covering shapes, exposing whatever was underneath.

Step 3: Execution
Opened [REDACTED].pdf in Pixlr AI Editor.
Switched to edit mode and selected the black overlay regions using Pixlr’s selection tools.
Deleted each covering block individually.
Repeated the process until all masked areas were cleared.
As each rectangle was removed, the hidden text gradually became visible.

Step 4: Flag Recovery
Once all obstructing elements were eliminated, the full flag appeared clearly on the document:
 root{EASY_2_UNREDACT}

This challenge serves as a reminder that cosmetic redaction offers no real protection—data must be properly removed, not simply hidden.

#Flag
root{EASY_2_UNREDACT}


#Tools Used

Pixlr (AI Editor) – Used for opening the PDF, selecting graphical overlays, and revealing the concealed text.
