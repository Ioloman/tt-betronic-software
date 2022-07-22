from init import init
from fastapi import FastAPI


LOGGER_NAME = init(__file__)

app = FastAPI(
    title='Line Provider'
)