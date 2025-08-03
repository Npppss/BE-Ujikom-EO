# app/crud/crud_event.py
from sqlalchemy.orm import Session
from app.db import models
from app.schemas.schema_event import EventCreate, EventUpdate

def get_all_events(db: Session):
    return db.query(models.Event).all()

def get_event(db: Session, event_id: int):
    return db.query(models.Event).filter(models.Event.id == event_id).first()

def create_event(db: Session, event: EventCreate):
    db_event = models.Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def update_event(db: Session, event_id: int, updated_event: EventUpdate):
    event = get_event(db, event_id)
    if not event:
        return None
    for key, value in updated_event.dict().items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)
    return event

def delete_event(db: Session, event_id: int):
    event = get_event(db, event_id)
    if not event:
        return None
    db.delete(event)
    db.commit()
    return event
