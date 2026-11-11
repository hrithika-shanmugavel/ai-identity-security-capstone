
import os
import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from jwt import PyJWKClient

load_dotenv()

app = FastAPI()

domain = os.getenv("AUTH0_DOMAIN")
audience = os.getenv("AUTH0_AUDIENCE")

issuer = f"https://{domain}/"

# Auth0's public keys are used to verify JWT signatures
jwks_client = PyJWKClient(
    f"https://{domain}/.well-known/jwks.json"
)

@app.post("/chat")
def chat(authorization: str | None = Header(default=None)):

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid token"
        )

    token = authorization.split(" ", 1)[1]

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=audience,
            issuer=issuer
        )

        print("Authenticated request!")
        print("Client:", payload.get("sub"))
        print("Chat API accessed successfully!")

        return {
            "message": "Success"
        }

    except jwt.ExpiredSignatureError:
        print("ERROR: Access token has expired!")

        raise HTTPException(
            status_code=401,
            detail="Access token expired"
        )

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid access token"
        )
