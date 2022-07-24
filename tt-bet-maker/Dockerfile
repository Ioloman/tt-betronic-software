FROM python:3.10

WORKDIR /usr/src/tt-bet-maker

COPY . .

RUN pip install pipenv
RUN pipenv install

EXPOSE ${APP_PORT}

CMD pipenv run uvicorn main:app --host 0.0.0.0 --port ${APP_PORT}