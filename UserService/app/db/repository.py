from sqlalchemy.orm import Session
from app.db import models

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: models.User):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user