import uvicorn
from fastapi import FastAPI
from .db.database import engine, Base
from .core.config import settings
