from sqlalchemy.orm import Session
from app.db.models.event import Event
from app.schemas.event import EventCreate, EventUpdate

def create_event(db: Session, event_data: EventCreate):
    new_event = Event(**event_data.dict())
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

def get_all_events(db: Session):
    return db.query(Event).all()

def get_event_by_id(db: Session, event_id: int):
    return db.query(Event).filter(Event.id == event_id).first()

def update_event(db: Session, event_id: int, event_data: EventUpdate):
    event = get_event_by_id(db, event_id)
    if event:
        for key, value in event_data.dict().items():
            setattr(event, key, value)
        db.commit()
        db.refresh(event)
    return event

def delete_event(db: Session, event_id: int):
    event = get_event_by_id(db, event_id)
    if event:
        db.delete(event)
        db.commit()
    return event
