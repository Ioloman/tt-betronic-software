import datetime
import os
import urllib.parse

import httpx
from aio_pika.connection import make_url
from aioredis import Redis
from fastapi import FastAPI, Depends, BackgroundTasks, status, HTTPException
from sqlalchemy.sql import Select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from connections.database import init_db
from connections.services import RedisHandler, RabbitHandler
from models import Bet, BetCreate, Event, EventStatus
from connections.database import get_session
from helpers import get_events_cached, update_bet

app = FastAPI(
    title='Bet Maker'
)


@app.on_event('startup')
async def startup():
    # init database connection and other services
    await init_db()
    RedisHandler().connect(os.getenv('REDIS_URL'))
    rabbit = RabbitHandler()
    await rabbit.connect(make_url(
        host=os.getenv('RABBIT_HOST'),
        port=int(os.getenv('RABBIT_PORT')),
        login=os.getenv('RABBIT_USER'),
        password=os.getenv('RABBIT_PASS'),
        timeout=int(os.getenv('RABBIT_TIMEOUT'))
    ))

    # register message handler to receive updates of events
    channel = await rabbit.get_conn()
    queue = await channel.declare_queue(os.getenv('RABBIT_QUEUE'), durable=True)
    await queue.consume(update_bet)


@app.on_event('shutdown')
async def shutdown():
    # close connections
    await RedisHandler().disconnect()
    await RabbitHandler().disconnect()


@app.get('/bets', response_model=list[Bet])
async def get_bets(session: AsyncSession = Depends(get_session)):
    """
    Get all placed bets
    """
    expr: Select = select(Bet)
    result = (await session.exec(expr)).all()
    return result


@app.post('/bets', response_model=Bet, status_code=status.HTTP_201_CREATED)
async def create_bet(bet: BetCreate, session: AsyncSession = Depends(get_session)):
    """
    Place a bet on event
    """
    # get an event from line-provider service
    # there is a way to get it from cache if it's in there
    # but http request for single event is quite lightweight and more safe
    async with httpx.AsyncClient() as client:  # type: httpx.AsyncClient
        response = await client.get(urllib.parse.urljoin(os.getenv('EVENTS_API_URL'), f'/events/{bet.event_uid}'))
    # handle Not Found
    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='event not found')
    # check if suitable to bet
    event = Event(**response.json())
    if event.deadline < datetime.datetime.now() or event.status != EventStatus.NOT_FINISHED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='event deadline passed')

    # if all checks passed - add to database
    bet_created = Bet(**bet.dict(), coefficient=event.coefficient, status=event.status)
    session.add(bet_created)
    await session.commit()
    await session.refresh(bet_created)
    return bet_created


@app.get('/events', response_model=list[Event])
async def get_events(*, redis: Redis = Depends(RedisHandler().get_conn), tasks: BackgroundTasks):
    """
    Get events eligible for bet
    """
    return await get_events_cached(redis, tasks)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, port=8001)