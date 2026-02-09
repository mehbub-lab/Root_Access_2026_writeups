# Challenge Name  
A Game of Circles and Crosses

---

## Approach  

Analyze bugs.py
-- The computer checks for threats (imp list) and blocks them. If multiple threats exist, it blocks the first one it finds in its hardcoded checks.
-- Create a Fork: Play a sequence that creates two winning threats simultaneously. The computer will block one, leaving the other open for you to win.

Winning Moves:
-- 1, 1 (Center)
-- 2, 2 (Bottom Right)
-- 2, 0 (Top Right) -> Critical Move: This sets up two wins: vertical column 3 and diagonal.
-- 2, 1 (Right Middle) -> Win.


1. Analyze the Code (bugs.py)
   Observation: The computer's logic is deterministic. It evaluates the board and blocks the first immediate threat it finds in a fixed priority order (lines 332-386).
   Vulnerability: It does not look ahead more than one move. If you create two simultaneous threats (a "fork"), it will block the first one it checks based on its hardcoded if-elif chain, leaving the second one open for you to win.
2. Formulate a Strategy (The "Fork")
   You need a sequence of moves that forces the computer into a losing position.

Move 1: 

(1, 1)
 [Center] - Controls the board.
Move 2: 

(2, 2)
 [Bottom Right] - Forces a response.
Move 3: 

(2, 0)
 [Top Right] - The winning move.
This creates two threats at once:
Diagonal Win (needs 0, 2)
Right Column Win (needs 2, 1)
The computer will block one (likely 0, 2 due to code order), leaving 2, 1 open.
Move 4: 

(2, 1)
 [Right Middle] - Take the open spot and win.
3. Execution (The Script)
   Instead of playing manually (which can be error-prone or laggy), write a script to send this exact sequence to the /verify endpoint.

I created solve.py to do exactly this:

python
human_moves = [
    {"x": 1, "y": 1},
    {"x": 2, "y": 2},
    {"x": 2, "y": 0},
    {"x": 2, "y": 1},
]
Running this script retrieves the flag: 

#Flag
root{M@yb3_4he_r3@!_tr3@5ur3_w@$_th3_bug$_w3_m@d3_@l0ng_4h3_w@y}


#Tools Used

-- Code Analysis (Static Analysis): Reading bugs.py to understand the game logic and find the deterministic behavior. I identified the prioritized if-elif blocks the computer uses to decide its moves.
-- Strategy Formulation: Developing a specific sequence of moves (a "fork") that exploits the computer's logic to guarantee a win.
-- Python Scripting: Creating a custom script (solve.py) to automate the winning moves and interact directly with the game server's API.
-- Libraries used: urllib.request, json, base64, secrets.
-- API interaction: Sending a crafted JSON payload to the /verify endpoint to retrieve the flag.
