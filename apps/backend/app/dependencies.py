import socket
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status
from jose import jwt, JWTError
from confluent_kafka import Producer
from datetime import datetime, timedelta, UTC
from .settings import settings as config

conf = {'bootstrap.servers': config.kafka_bootstrap_servers,
        'client.id': socket.gethostname()}

security = HTTPBearer()
SECRET_KEY = config.secret_key
ALGORITHM = config.algorithm

USERS = {"player": {"password": "test", "balance": 100.0, "history": []}}


def get_kafka_producer():
    return Producer(conf)


def create_token(username: str):
    data = {"sub": username, "exp": datetime.now(UTC) + timedelta(hours=1)}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def get_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username in USERS:
            return username
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
