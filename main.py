from fastapi import FastAPI

from utils.init import init


init()

app = FastAPI(
    title='Bet Maker'
)
