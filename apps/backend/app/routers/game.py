import json
import random
import time
import uuid
from datetime import datetime, UTC
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import get_kafka_producer, get_user_from_token, USERS
from ..models import SpinRequest, ReelResult, GameHistoryEntry

router = APIRouter(prefix="/game", tags=["game"])

SYMBOLS = ["cherry", "lemon", "bell", "seven", "bar"]
ROWS, COLUMNS = 3, 3


def generate_reels():
    return [[random.choice(SYMBOLS) for _ in range(COLUMNS)] for _ in range(ROWS)]


def calculate_win(reels):
    # Simple: reward if middle row has all the same symbol
    middle_row = reels[1]
    if all(symbol == middle_row[0] for symbol in middle_row):
        return 10.0  # fixed win
    return 0.0


@router.post("/spin", response_model=ReelResult)
def spin(request: SpinRequest, username: str = Depends(get_user_from_token), producer=Depends(get_kafka_producer)):
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
        "username": username,
        "result": "WON" if win > 0 else "LOST"
    }
    user["history"].append(spn)

    producer.produce("spin.history.slot_game.spins_by_user", value=json.dumps(spn).encode('utf-8'))
    producer.flush()
    time.sleep(3)

    return {
        "reels": reels,
        "spinId": spin_id,
        "betAmount": request.betAmount,
        "winAmount": win,
        "balanceAfter": user["balance"],
        "bonusTriggered": False
    }


@router.get("/history", response_model=List[GameHistoryEntry])
def history(username: str = Depends(get_user_from_token)):
    return USERS[username]["history"]
