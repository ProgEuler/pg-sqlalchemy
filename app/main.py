import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User
from app.schemas import UserCreate, UserOut

load_dotenv()

app = FastAPI(
    title=os.getenv("APP_NAME", "FastAPI with pg"),
    description="A CRUD API for user management with PostgresSQL",
    version="1.0.0",
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/ping")
def ping():
    return {"status": "ok", "message": "pong"}


@app.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing_user = (
        db.query(User)
        .filter((User.email == payload.email) | (User.username == payload.username))
        .first()
    )


if existing_user:
    raise
