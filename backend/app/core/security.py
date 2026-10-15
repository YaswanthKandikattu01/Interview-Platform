import hashlib
import secrets
import hmac
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash
from jose import jwt, JWTError
from app.core.config import settings

# Initialize Argon2id password hasher with RFC 9106 recommended parameters
# memory_cost=65536 (64 MiB), time_cost=3 iterations, parallelism=4 threads
pwd_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    salt_len=16
)


def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2id."""
    return pwd_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against an Argon2id hash."""
    try:
        return pwd_hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHash):
        return False


def needs_rehash(hashed_password: str) -> bool:
    """Check if the hash needs upgrading to match newer parameters."""
    return pwd_hasher.check_needs_rehash(hashed_password)


def create_access_token(
    user_id: str,
    role: str,
    email: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a short-lived signed JWT access token (15 mins default)."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload: Dict[str, Any] = {
        "sub": user_id,
        "role": role,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": secrets.token_hex(16)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def generate_random_token(length_bytes: int = 32) -> str:
    """Generate a cryptographically secure random token string."""
    return secrets.token_urlsafe(length_bytes)


def hash_token(raw_token: str) -> str:
    """Calculate SHA-256 hash of a raw token for secure database storage."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def generate_csrf_token() -> str:
    """Generate a random CSRF token."""
    return secrets.token_hex(32)


def verify_csrf_token(header_token: str, cookie_token: str) -> bool:
    """Safely compare double-submit CSRF tokens in constant time."""
    if not header_token or not cookie_token:
        return False
    return hmac.compare_digest(header_token, cookie_token)
