import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.config import get_settings

_basic = HTTPBasic()


def require_auth(credentials: HTTPBasicCredentials = Depends(_basic)) -> None:
    """Gate every non-public route behind one Basic Auth credential."""
    settings = get_settings()
    user_ok = secrets.compare_digest(credentials.username, settings.basic_auth_user)
    pass_ok = secrets.compare_digest(credentials.password, settings.basic_auth_pass)
    if not (user_ok and pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
