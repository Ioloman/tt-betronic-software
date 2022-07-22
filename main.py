from init import init
from fastapi import FastAPI

from utils import DummyDB

LOGGER_NAME = init(__file__)

app = FastAPI(
    title='Line Provider'
)

event_db = DummyDB()


@app.get('/events', response_model=list[Event])
async def get_events():
    """
    Get list of all events
    """
    return event_db.get_all()


@app.post('/events', response_model=Event, status_code=status.HTTP_201_CREATED)
async def create_event(event: Event):
    event_db.add(event)
    return event


@app.get('/events/{uid}', response_model=Event)
async def get_event(uid: UUID):
    """
    Get event by uuid
    """
    event = event_db.get(str(uid))
    if event is None:
        raise HTTPException(status_code=404, detail='Event Not Found')
    return event
