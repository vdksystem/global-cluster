import json

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime, timedelta, UTC
import uuid
from confluent_kafka import Producer
import socket

from models import *
from game_logic import generate_reels, calculate_win

app = FastAPI()
security = HTTPBearer()
SECRET_KEY = "secret"
ALGORITHM = "HS256"

# Mock "DB"
USERS = {"player": {"password": "test", "balance": 100.0, "history": []}}

# my-cluster-kafka-bootstrap.kafka.svc.cluster.local
conf = {'bootstrap.servers': 'localhost:9092',
        'client.id': socket.gethostname()}

producer = Producer(conf)


def create_token(username: str):
    data = {"sub": username, "exp": datetime.now(UTC) + timedelta(hours=1)}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def get_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username in USERS:
            return username
        raise HTTPException(status_code=401)
    except JWTError:
        raise HTTPException(status_code=401)


@app.post("/auth/login", response_model=TokenResponse)
def login(data: LoginRequest):
    user = USERS.get(data.username)
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(data.username)
    return {"token": token}


@app.post("/session/start")
def start_session(username: str = Depends(get_user_from_token)):
    return {
        "sessionId": str(uuid.uuid4()),
        "balance": USERS[username]["balance"]
    }


@app.post("/session/end")
def end_session(username: str = Depends(get_user_from_token)):
    return {"message": f"Session ended for user {username}"}


@app.get("/balance")
def get_balance(username: str = Depends(get_user_from_token)):
    return {"balance": USERS[username]["balance"]}


@app.post("/game/spin", response_model=ReelResult)
def spin(request: SpinRequest, username: str = Depends(get_user_from_token)):
    user = USERS[username]
    if request.betAmount > user["balance"]:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    reels = generate_reels()
    win = calculate_win(reels)
    user["balance"] -= request.betAmount
    user["balance"] += win

    spin_id = str(uuid.uuid4())
    spn = {
        "spinId": spin_id,
        "timestamp": str(datetime.now(UTC)),
        "betAmount": request.betAmount,
        "winAmount": win,
        "username":  username,
        "result": "WON" if win > 0 else "LOST"
    }
    user["history"].append(spn)

    producer.produce("spin.history.slot_game.spins_by_user", value=json.dumps(spn).encode('utf-8'))

    return {
        "reels": reels,
        "spinId": spin_id,
        "betAmount": request.betAmount,
        "winAmount": win,
        "balanceAfter": user["balance"],
        "bonusTriggered": False
    }


@app.get("/game/history", response_model=List[GameHistoryEntry])
def history(username: str = Depends(get_user_from_token)):
    return USERS[username]["history"]
