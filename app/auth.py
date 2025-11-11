from datetime import datetime, timedelta

import jwt
import prometheus_client as prometheus
from cfg import app, get_db_session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from model import User
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

logged_users_gauge = prometheus.Gauge(
    "logged_users_gauge", "Currently logged users gauge."
)

security = HTTPBearer()

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DELTA = timedelta(minutes=120)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    token: str


def create_jwt_token(user: User) -> str:
    data = user.to_dict()
    expire = datetime.now() + ACCESS_TOKEN_EXPIRE_DELTA
    data.update({"exp": expire})

    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def decode_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db_session: Session = Depends(get_db_session),
) -> User:
    token = credentials.credentials
    payload = decode_jwt_token(token)
    print(payload)

    username = payload.get("username")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user = db_session.query(User).where(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    return user


@app.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, session: Session = Depends(get_db_session)):
    stmt = select(User).where(
        User.username == request.username,
        User.password_plaintext == request.password,
    )
    user = session.execute(stmt).scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    logged_users_gauge.inc()

    return {"token": create_jwt_token(user)}


@app.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    # do nothing as we're using jwt
    logged_users_gauge.dec()
    return
