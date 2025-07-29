from pydantic import BaseModel
from typing import List
from datetime import datetime


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    token: str


class SpinRequest(BaseModel):
    betAmount: float


class ReelResult(BaseModel):
    reels: List[List[str]]
    spinId: str
    betAmount: float
    winAmount: float
    balanceAfter: float
    bonusTriggered: bool


class GameHistoryEntry(BaseModel):
    spinId: str
    timestamp: datetime
    betAmount: float
    winAmount: float
    result: str
