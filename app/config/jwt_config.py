import os
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))

# Debug: Print to verify values are loaded
print(f"🔑 SECRET_KEY loaded: {SECRET_KEY[:10] if SECRET_KEY else 'None'}...")
print(f"🔐 ALGORITHM loaded: {ALGORITHM}")

def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),  # JWT spec requires sub to be string
        "type": "access",
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),  # JWT spec requires sub to be string
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    print(f"🔍 Decoding token: {token[:50]}...")
    print(f"🔍 Using SECRET_KEY: {SECRET_KEY[:10]}... ALGORITHM: {ALGORITHM}")
    try:
        result = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"✅ Token decoded successfully: {result}")
        return result
    except jwt.ExpiredSignatureError:
        print("❌ Token expired")
        raise Exception("Token expired")
    except jwt.InvalidTokenError as e:
        print(f"❌ Invalid token error: {type(e).__name__}: {e}")
        raise Exception("Invalid token")
