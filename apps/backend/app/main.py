import uvicorn
from fastapi import FastAPI
from .routers import game, auth
from .settings import settings as config

app = FastAPI()
app.include_router(game.router)
app.include_router(auth.router)


if __name__ == "__main__":
    # Uvicorn properly handles signals
    uvicorn.run(app, host=config.host, port=config.port, log_level="debug")
