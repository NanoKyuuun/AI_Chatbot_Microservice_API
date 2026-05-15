from passlib.context import CryptContext
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """Verify a plain API key against its hash."""
    return pwd_context.verify(plain_key, hashed_key)

def get_api_key_hash(api_key: str) -> str:
    """Generate a hash for an API key."""
    return pwd_context.hash(api_key)

def generate_api_key(prefix: str = "sk_live") -> str:
    """Generate a secure random API key with a prefix."""
    random_str = secrets.token_urlsafe(32)
    return f"{prefix}_{random_str}"
