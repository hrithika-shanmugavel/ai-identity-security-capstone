"""
Generated and saved the Ed25519 Key pair
Sign outgoing message using private key
Verify incoming message (receiving end) using public key.
"""

from pathlib import Path
import base64

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey
)
from cryptography.hazmat.primitives import serialization


KEY_DIR = Path("keys")
PRIVATE_KEY_FILE = KEY_DIR / "private_key.pem"
PUBLIC_KEY_FILE = KEY_DIR / "public_key.pem"


# STEP 1: Generate or load Ed25519 keys
def load_or_create_keys():

    KEY_DIR.mkdir(exist_ok=True)

    if PRIVATE_KEY_FILE.exists() and PUBLIC_KEY_FILE.exists():

        with open(PRIVATE_KEY_FILE, "rb") as file:
            private_key = serialization.load_pem_private_key(
                file.read(),
                password=None
            )

        with open(PUBLIC_KEY_FILE, "rb") as file:
            public_key = serialization.load_pem_public_key(
                file.read()
            )

        print("[IDENTITY] Existing Ed25519 keys loaded.")

    else:

        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()

        # Save private key
        with open(PRIVATE_KEY_FILE, "wb") as file:
            file.write(
                private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )
            )

        # Save public key
        with open(PUBLIC_KEY_FILE, "wb") as file:
            file.write(
                public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            )

        print("[IDENTITY] New Ed25519 key pair generated.")

    return private_key, public_key


# STEP 2: Sign outgoing messages
def sign_message(message, private_key):

    message_bytes = message.encode("utf-8")

    signature = private_key.sign(message_bytes)

    signed_data = {
        "message": message,
        "signature": base64.b64encode(signature).decode("utf-8")
    }

    return signed_data


# STEP 3: Verify incoming messages
def verify_message(signed_data, public_key):

    message = signed_data["message"]

    signature = base64.b64decode(
        signed_data["signature"],
        validate=True
    )

    message_bytes = message.encode("utf-8")

    # Raises InvalidSignature if the message was changed
    public_key.verify(signature, message_bytes)

    return message
