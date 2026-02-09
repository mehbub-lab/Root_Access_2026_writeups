import urllib.request
import json
import base64
import secrets

VERIFY_URL = "https://rootaccess.pythonanywhere.com/verify"


human_moves = [
    {"x": 1, "y": 1},  # Center
    {"x": 2, "y": 2},  # Bottom Right
    {"x": 2, "y": 0},  # Top Right (Sets up double threat)
    {"x": 2, "y": 1},  # Right Center (Winning move)
]

def send_proof_and_show_flag():
    payload = {
        "v": 1,
        "nonce": secrets.token_hex(8),
        "human": human_moves,
    }
    proof = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()

    req_body = json.dumps({"proof": proof}).encode("utf-8")
    req = urllib.request.Request(
        VERIFY_URL,
        data=req_body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    print("Sending winning moves to validaton server...")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("ok") and data.get("flag"):
                print("\nSUCCESS! FLAG FOUND:")
                print(data["flag"])
            else:
                print("\nFAILED.")
                print(f"Result: {data.get('result')}")
                print(f"Message: {data}")
    except Exception as e:
        print(f"Error contacting verifier: {e}")

if __name__ == "__main__":
    send_proof_and_show_flag()
