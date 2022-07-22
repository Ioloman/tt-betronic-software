from init import init
from fastapi import FastAPI

from utils import DummyDB

LOGGER_NAME = init(__file__)

app = FastAPI(
    title='Line Provider'
)

line_db = DummyDB()