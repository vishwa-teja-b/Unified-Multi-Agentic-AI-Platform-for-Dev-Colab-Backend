"""
Auth dependencies for extracting user info from JWT tokens.
Shared across all routers that require authentication.
"""

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.config.jwt_config import decode_token
import logging

logger = logging.getLogger(__name__)

# OAuth2 scheme - enables Swagger's "Authorize" button
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    """Extract user_id from JWT token"""
    logger.debug("Token received: %s...", token[:30] if token else 'NONE')
    try:
        payload = decode_token(token)
        logger.debug("User ID extracted: %s", payload['sub'])
        return int(payload["sub"])
    except Exception as e:
        logger.debug("Token error: %s", e)
        raise HTTPException(status_code=401, detail="Invalid or expired token")
