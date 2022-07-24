from fastapi import FastAPI, Depends
from sqlalchemy.sql import Select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from connections.database import init_db
from models import Bet, BetCreate
from connections.database import get_session


app = FastAPI(
    title='Bet Maker'
)


@app.on_event('startup')
async def startup():
    await init_db()


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

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)