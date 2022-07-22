import logging
import os
import datetime
import random
from decimal import Decimal
from uuid import UUID

from init import init
from fastapi import FastAPI, status, HTTPException

from models import Event, EventPut, EventCreate
from utils import DummyDB

LOGGER_NAME = init(__file__)
logger = logging.getLogger(LOGGER_NAME)

app = FastAPI(
    title='Line Provider'
)

event_db = DummyDB()
if os.getenv('APP_ENV') == 'prod':
    for _ in range(10):
        event_db.add(Event(
            coefficient=Decimal(round(Decimal(random.randint(1, 3) + random.random() + 0.01), 2)),
            deadline=datetime.datetime.now() + datetime.timedelta(minutes=random.randint(5, 30))
        ))


@app.get('/events', response_model=list[Event])
async def get_events():
    """
    Get list of all events
    """
    logger.info('request to get events list')
    return event_db.get_all()


@app.post('/events', response_model=Event, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate):
    event_created = Event(**event.dict())
    event_db.add(event_created)
    logger.info(f'added event={event_created}')
    return event_created


@app.get('/events/{uid}', response_model=Event)
async def get_event(uid: UUID):
    """
    Get event by uuid
    """
    event = event_db.get(str(uid))
    logger.info(f'got {event=} from {uid=}')
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Event Not Found')
    return event


@app.put('/events/{uid}', response_model=Event)
async def update_event(uid: UUID, event: EventPut):
    """
    Update event
    """
    # get event from db
    event_stored = event_db.get(str(uid))
    logger.info(f'got {event_stored=} from {uid=}, update {event}')
    if event_stored is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Event Not Found')

    # update it
    event_updated = event_stored.copy(update=event.dict())
    result = event_db.update(str(uid), event_updated)

    # return result
    if result:
        logger.info('updated')
        return event_updated
    else:
        raise HTTPException(status_code=status.HTTP_507_INSUFFICIENT_STORAGE, detail='Update failed')