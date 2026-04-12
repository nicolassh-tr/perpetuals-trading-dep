"""
Password-protect an HTML file using AES-256-GCM encryption.

The output is a self-contained HTML page with a login form.
Encrypted content is decrypted client-side using Web Crypto API (PBKDF2 + AES-GCM).
Even if someone has the link, the content is unreadable without the password.

Usage:
  python scripts/protect_html.py input.html output.html -p "mysecret"

  # Or import:
  from protect_html import protect_html_content
"""
import os
import base64
import json
import argparse
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def encrypt_content(plaintext: str, password: str) -> dict:
    """Encrypt HTML content with AES-256-GCM, compatible with Web Crypto API."""
    salt = os.urandom(16)
    iv = os.urandom(12)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=600000)
    key = kdf.derive(password.encode("utf-8"))
    ciphertext = AESGCM(key).encrypt(iv, plaintext.encode("utf-8"), None)
    return {
        "salt": base64.b64encode(salt).decode(),
        "iv": base64.b64encode(iv).decode(),
        "ct": base64.b64encode(ciphertext).decode(),
    }


def wrap_in_login_page(encrypted: dict, title: str = "Protected Report") -> str:
    """Wrap encrypted data in an HTML page with password form + Web Crypto decryption."""
    payload = json.dumps(encrypted)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
         background: #0f1923; color: #e0e0e0; display: flex; justify-content: center;
         align-items: center; min-height: 100vh; }}
  .login-box {{ background: #1a2633; border: 1px solid #2a3a4a; border-radius: 12px;
                padding: 40px; width: 400px; text-align: center;
                box-shadow: 0 8px 32px rgba(0,0,0,0.4); }}
  .login-box h1 {{ font-size: 1.3rem; margin-bottom: 8px; color: #fff; }}
  .login-box p {{ font-size: 0.85rem; color: #8899aa; margin-bottom: 24px; }}
  .lock {{ font-size: 2.5rem; margin-bottom: 16px; }}
  .field {{ margin-bottom: 14px; text-align: left; }}
  .field label {{ display: block; font-size: 0.8rem; color: #8899aa; margin-bottom: 4px; }}
  input {{ width: 100%; padding: 12px 16px; border: 1px solid #2a3a4a;
           border-radius: 8px; background: #0f1923; color: #fff; font-size: 1rem;
           outline: none; transition: border 0.2s; }}
  input:focus {{ border-color: #4a9eff; }}
  button {{ width: 100%; padding: 12px; border: none; border-radius: 8px;
           background: #4a9eff; color: #fff; font-size: 1rem; font-weight: 600;
           cursor: pointer; transition: background 0.2s; margin-top: 8px; }}
  button:hover {{ background: #3a8eef; }}
  .error {{ color: #ff6b6b; font-size: 0.85rem; margin-top: 12px; display: none; }}
  .spinner {{ display: none; margin: 12px auto; width: 24px; height: 24px;
             border: 3px solid #2a3a4a; border-top: 3px solid #4a9eff;
             border-radius: 50%; animation: spin 0.8s linear infinite; }}
  @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
</style>
</head>
<body>
<div class="login-box" id="loginBox">
  <div class="lock">&#128274;</div>
  <h1>{title}</h1>
  <p>Enter credentials to view this report.</p>
  <form id="form" onsubmit="return doDecrypt(event)">
    <div class="field">
      <label>Username</label>
      <input type="text" id="user" placeholder="Username" autofocus autocomplete="username" />
    </div>
    <div class="field">
      <label>Password</label>
      <input type="password" id="pw" placeholder="Password" autocomplete="current-password" />
    </div>
    <button type="submit">Unlock</button>
  </form>
  <div class="spinner" id="spinner"></div>
  <div class="error" id="error">Incorrect credentials. Try again.</div>
</div>
<script>
const PAYLOAD = {payload};

function b64decode(s) {{
  const bin = atob(s);
  const arr = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
  return arr;
}}

async function doDecrypt(e) {{
  e.preventDefault();
  const user = document.getElementById("user").value;
  const pw = document.getElementById("pw").value;
  if (!user || !pw) return false;

  document.getElementById("spinner").style.display = "block";
  document.getElementById("error").style.display = "none";
  document.querySelector("button").disabled = true;

  // Combine username + password as the decryption key
  const passphrase = user + ":" + pw;

  try {{
    const salt = b64decode(PAYLOAD.salt);
    const iv = b64decode(PAYLOAD.iv);
    const ct = b64decode(PAYLOAD.ct);

    const keyMaterial = await crypto.subtle.importKey(
      "raw", new TextEncoder().encode(passphrase), "PBKDF2", false, ["deriveKey"]
    );
    const key = await crypto.subtle.deriveKey(
      {{ name: "PBKDF2", salt: salt, iterations: 600000, hash: "SHA-256" }},
      keyMaterial,
      {{ name: "AES-GCM", length: 256 }},
      false,
      ["decrypt"]
    );
    const decrypted = await crypto.subtle.decrypt(
      {{ name: "AES-GCM", iv: iv }}, key, ct
    );
    const html = new TextDecoder().decode(decrypted);
    document.open();
    document.write(html);
    document.close();
  }} catch (err) {{
    document.getElementById("spinner").style.display = "none";
    document.getElementById("error").style.display = "block";
    document.querySelector("button").disabled = false;
    document.getElementById("pw").value = "";
    document.getElementById("pw").focus();
  }}
  return false;
}}
</script>
</body>
</html>'''


def protect_html_content(html_content: str, username: str, password: str,
                         title: str = "Protected Report") -> str:
    """Encrypt HTML string and return protected page. Passphrase = username:password."""
    encrypted = encrypt_content(html_content, f"{username}:{password}")
    return wrap_in_login_page(encrypted, title=title)


def protect_html_file(input_path: str, output_path: str, username: str,
                      password: str, title: str = "Protected Report"):
    """Read an HTML file, encrypt it, write the protected version."""
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()
    protected = protect_html_content(content, username, password, title=title)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(protected)
    print(f"  Protected: {len(content)//1024}KB -> {len(protected)//1024}KB ({title})")


def main():
    parser = argparse.ArgumentParser(description="Password-protect an HTML file with AES-256-GCM")
    parser.add_argument("input", help="Input HTML file")
    parser.add_argument("output", help="Output protected HTML file")
    parser.add_argument("--username", "-u", required=True)
    parser.add_argument("--password", "-p", required=True)
    parser.add_argument("--title", "-t", default="Protected Report")
    args = parser.parse_args()
    protect_html_file(args.input, args.output, args.username, args.password, args.title)


if __name__ == "__main__":
    main()
