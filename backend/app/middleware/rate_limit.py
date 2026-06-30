from fastapi import Request, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings

limiter = Limiter(key_func=get_remote_address)


def get_rate_limit():
    """Get rate limit from settings."""
    return f"{settings.RATE_LIMIT_PER_MINUTE}/minute"
