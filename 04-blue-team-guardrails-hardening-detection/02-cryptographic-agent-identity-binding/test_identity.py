
from pathlib import Path
from cryptography.exceptions import InvalidSignature

from identity_binding import (
    load_or_create_keys,
    sign_message,
    verify_message
)

# STEP 1: Generate or load Ed25519 keys
private_key, public_key = load_or_create_keys()

print("\n[KEY GENERATION] Ed25519 key pair ready.")

# Show that both key files exist
private_file = Path("keys/private_key.pem")
public_file = Path("keys/public_key.pem")

if private_file.exists() and public_file.exists():
    print("[SUCCESS] Private key file created:", private_file)
    print("[SUCCESS] Public key file created:", public_file)
else:
    print("[ERROR] Key files are missing!")
    raise SystemExit(1)


# STEP 2: Sign the original message
message = "Nova AI: Your leave balance is 10 days."

print("\n[AGENT] Original outgoing message:")
print(message)

signed_data = sign_message(message, private_key)

print("\n[SIGNING] Message signed using Ed25519 private key.")
print("[SIGNING] Digital signature generated successfully.")


# STEP 3: Verify original message
print("\n[RECEIVER] Verifying original message...")

try:
    verified_message = verify_message(signed_data, public_key)

    print("[SUCCESS] Signature verified!")
    print("[ACCEPTED]", verified_message)

except InvalidSignature:
    print("[SECURITY ALERT] Signature verification failed!")
    print("[REJECTED] Invalid signature.")


# STEP 4: Tamper with one character
tampered_data = signed_data.copy()

tampered_data["message"] = tampered_data["message"].replace(
    "10 days",
    "11 days",
    1
)

print("\n[ATTACK] One part of the message has been modified.")
print("[ORIGINAL]", message)
print("[TAMPERED]", tampered_data["message"])


# STEP 5: Verify tampered message
print("\n[RECEIVER] Verifying tampered message...")

try:
    verify_message(tampered_data, public_key)

    print("[ACCEPTED] Message verification successful.")

except InvalidSignature:
    print("[SECURITY ALERT] Signature verification failed!")
    print("[REJECTED] Message was modified or tampered with.")