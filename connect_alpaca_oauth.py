#!/usr/bin/env python3
"""
connect_alpaca_oauth.py
=======================
OptionAlpha Agent — Alpaca OAuth 2.0 Authorization & Token Exchanger

Connects your Alpaca Paper Trading account using OAuth Client ID & Secret.
Flow:
1. Constructs the Alpaca OAuth consent URL with your Client ID.
2. Starts a local HTTP callback listener OR accepts a pasted callback URL/code.
3. Exchanges the authorization code for an OAuth access token.
4. Saves the access token into your local .env file.
5. Verifies live connection to your Alpaca paper account.
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent / ".env"

DEFAULT_CLIENT_ID = "ce946808ae14f57dabac4fe01aeb6d5a"
DEFAULT_CLIENT_SECRET = "87cb268720752c3d9f756a9ba85e9ad0d6bd0c54"
DEFAULT_REDIRECT_URI = "http://localhost:8000/callback"


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    auth_code = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            OAuthCallbackHandler.auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"""
            <html>
            <body style="font-family:sans-serif; background:#0a0b0f; color:#10b981; text-align:center; padding:50px;">
                <h1>&#10004; Authorization Successful!</h1>
                <p style="color:#94a3b8;">You can close this tab and return to the terminal.</p>
            </body>
            </html>
            """)
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No code parameter found.")

    def log_message(self, format, *args):
        pass  # Suppress default server logs


def exchange_code_for_token(code: str, client_id: str, client_secret: str, redirect_uri: str) -> str:
    """POST to Alpaca token endpoint to get Bearer access_token."""
    token_url = "https://api.alpaca.markets/oauth/token"
    payload = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri
    }).encode("utf-8")

    req = urllib.request.Request(
        token_url,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["access_token"]
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"\n[!] Token exchange failed: {e.code} - {err_msg}")
        sys.exit(1)


def verify_account(token: str) -> dict:
    """Test connection to Paper API using Bearer token."""
    account_url = "https://paper-api.alpaca.markets/v2/account"
    req = urllib.request.Request(
        account_url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def update_env_file(token: str, client_id: str, client_secret: str):
    """Write or update ALPACA_OAUTH_TOKEN in .env."""
    lines = []
    if ENV_PATH.exists():
        lines = ENV_PATH.read_text().splitlines()

    updated = False
    new_lines = []
    for line in lines:
        if line.startswith("ALPACA_OAUTH_TOKEN="):
            new_lines.append(f"ALPACA_OAUTH_TOKEN={token}")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        new_lines.append(f"ALPACA_OAUTH_TOKEN={token}")

    ENV_PATH.write_text("\n".join(new_lines) + "\n")
    print(f"[+] Saved ALPACA_OAUTH_TOKEN securely into: {ENV_PATH}")


def main():
    parser = argparse.ArgumentParser(description="Alpaca OAuth 2.0 Paper Account Connector")
    parser.add_argument("--client-id", default=DEFAULT_CLIENT_ID, help="Alpaca OAuth Client ID")
    parser.add_argument("--client-secret", default=DEFAULT_CLIENT_SECRET, help="Alpaca OAuth Client Secret")
    parser.add_argument("--redirect-uri", default=DEFAULT_REDIRECT_URI, help="Redirect URI registered in Alpaca app")
    parser.add_argument("--code", default=None, help="Directly exchange an authorization code if already obtained")
    args = parser.parse_args()

    client_id = args.client_id
    client_secret = args.client_secret
    redirect_uri = args.redirect_uri

    print("=" * 65)
    print("      ALPACA OAUTH 2.0 PAPER ACCOUNT CONNECTOR")
    print("=" * 65)
    print(f"Client ID:      {client_id}")
    print(f"Redirect URI:   {redirect_uri}")
    print("Environment:    Paper Trading (Safe)")
    print("=" * 65)

    code = args.code
    if not code:
        auth_url = (
            f"https://app.alpaca.markets/oauth/authorize?"
            f"response_type=code&client_id={client_id}&"
            f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
            f"scope=account:write%20trading%20data&env=paper"
        )

        print("\nStep 1: Open the following URL in your browser to authorize your paper account:\n")
        print(f"👉 {auth_url}\n")

        parsed_uri = urllib.parse.urlparse(redirect_uri)
        if parsed_uri.hostname in ("localhost", "127.0.0.1"):
            port = parsed_uri.port or 8000
            print(f"[*] Starting local callback server on port {port}...")
            print("[*] Waiting for Alpaca to redirect back...")
            try:
                server = HTTPServer(("localhost", port), OAuthCallbackHandler)
                server.timeout = 180  # 3 minutes timeout
                try:
                    webbrowser.open(auth_url)
                except Exception:
                    pass
                while not OAuthCallbackHandler.auth_code:
                    server.handle_request()
                code = OAuthCallbackHandler.auth_code
            except Exception as e:
                print(f"[!] Could not start local server ({e}).")

        if not code:
            print("\nPaste either the full redirected URL or the code parameter here:")
            user_input = input("Callback URL or Code: ").strip()
            if "code=" in user_input:
                parsed = urllib.parse.urlparse(user_input)
                params = urllib.parse.parse_qs(parsed.query)
                code = params.get("code", [user_input])[0]
            else:
                code = user_input

    print(f"\n[*] Exchanging authorization code for OAuth access token...")
    token = exchange_code_for_token(code, client_id, client_secret, redirect_uri)
    print(f"[+] Successfully received OAuth Bearer Token: {token[:8]}...{token[-6:]}")

    update_env_file(token, client_id, client_secret)

    print("\n[*] Verifying connection to Paper Trading account...")
    try:
        account = verify_account(token)
        print("\n" + "=" * 65)
        print("          &#10004; ALPACA PAPER ACCOUNT CONNECTED SUCCESSFULLY!")
        print("=" * 65)
        print(f"Account ID:        {account.get('id')}")
        print(f"Account Number:    {account.get('account_number')}")
        print(f"Status:            {account.get('status')}")
        print(f"Currency:          {account.get('currency')}")
        print(f"Portfolio Value:   ${float(account.get('portfolio_value', 0)):,.2f}")
        print(f"Buying Power:      ${float(account.get('buying_power', 0)):,.2f}")
        print(f"Cash:              ${float(account.get('cash', 0)):,.2f}")
        print("=" * 65)
    except Exception as e:
        print(f"[!] Warning: Token obtained, but account check failed: {e}")


if __name__ == "__main__":
    main()
