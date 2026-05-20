import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User
from app.schemas import UserCreate, UserOut, UserUpdate

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
        raise HTTPException(
            status_code=400,
            detail="Email or username already exists"
        )

    user = User(email=payload.email, username=payload.username)
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@app.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).order_by(User.id.asc()).all()

@app.get(f"/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

@app.put(f"/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if payload.email and payload.email != user.email:
        
