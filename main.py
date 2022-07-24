import os
from aioredis import Redis
from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.sql import Select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from connections.database import init_db
from connections.services import RedisHandler
from models import Bet, BetCreate, Event
from connections.database import get_session
from utils import get_events_cached

app = FastAPI(
    title='Bet Maker'
)


@app.on_event('startup')
async def startup():
    await init_db()
    RedisHandler().init(os.getenv('REDIS_URL'))


@app.get('/bets', response_model=list[Bet])
async def get_bets(session: AsyncSession = Depends(get_session)):
    expr: Select = select(Bet)
    result = (await session.exec(expr)).all()
    return result


@app.post('/bets', response_model=Bet)
async def create_bet(bet: BetCreate, session: AsyncSession = Depends(get_session)):
    bet_created = Bet(**bet.dict(), coefficient=1.5)
    session.add(bet_created)
    await session.commit()
    await session.refresh(bet_created)
    return bet_created


@app.get('/events', response_model=list[Event])
async def get_events(*, redis: Redis = Depends(RedisHandler().get_conn), tasks: BackgroundTasks):
    return await get_events_cached(redis, tasks)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, port=8001)