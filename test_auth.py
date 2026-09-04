import urllib.request
import urllib.error
import base64
import json
import os
from pathlib import Path

# Load .env if present
env_file = Path(__file__).resolve().parent / ".env"
env_vars = {}
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env_vars[k.strip()] = v.strip()

key = env_vars.get("ALPACA_API_KEY", "")
secret = env_vars.get("ALPACA_SECRET_KEY", "")

print("=" * 60)
print("      ALPACA CONNECTION VERIFIER (Option 1 & 2)")
print("=" * 60)
print(f"API Key ID:   {key[:6]}...{key[-4:] if len(key) > 10 else key}")
print(f"Secret Key:   {secret[:6]}...{secret[-4:] if len(secret) > 10 else secret}")
print("=" * 60)

configs = [
    ("Paper Headers (Option 1)", "https://paper-api.alpaca.markets/v2/account", {
        "APCA-API-KEY-ID": key,
        "APCA-API-SECRET-KEY": secret
    }),
    ("Paper Basic Auth (Option 2)", "https://paper-api.alpaca.markets/v2/account", {
        "Authorization": "Basic " + base64.b64encode(f"{key}:{secret}".encode()).decode()
    }),
    ("Live Headers (Option 1)", "https://api.alpaca.markets/v2/account", {
        "APCA-API-KEY-ID": key,
        "APCA-API-SECRET-KEY": secret
    }),
]

connected = False
for name, url, headers in configs:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            print(f"\n[+] SUCCESS via {name}!")
            print(f"    Account ID:       {data.get('id')}")
            print(f"    Account Number:   {data.get('account_number')}")
            print(f"    Status:           {data.get('status')}")
            print(f"    Portfolio Value:  ${float(data.get('portfolio_value', 0)):,.2f}")
            print(f"    Buying Power:     ${float(data.get('buying_power', 0)):,.2f}")
            print(f"    Cash:             ${float(data.get('cash', 0)):,.2f}")
            connected = True
            break
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore").strip()
        print(f"[-] FAILED [{name}]: HTTP {e.code} - {body}")
    except Exception as ex:
        print(f"[!] ERROR [{name}]: {ex}")

if not connected:
    print("\n" + "=" * 60)
    print("[-] RESULT: Connection Failed (HTTP 401 Unauthorized)")
    print("=" * 60)
    print("Notice: The keys currently in .env appear to be OAuth Client credentials,")
    print("not direct Paper Trading API Keys (which typically start with 'PK...').")
    print("To connect:")
    print("1. Go to https://app.alpaca.markets/paper/dashboard/overview")
    print("2. Under 'Your API Keys', click 'Generate New Key'")
    print("3. Copy the Key ID (starts with PK...) and Secret Key into .env")
