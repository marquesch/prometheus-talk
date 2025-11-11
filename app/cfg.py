import time
from contextlib import asynccontextmanager

import prometheus_client as prometheus
from fastapi import FastAPI, Request, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    scoped_session,
    sessionmaker,
)

engine = create_engine(
    "postgresql+psycopg2://prometheus:prometheus@postgres:5432/prometheus", echo=True
)
session = sessionmaker(bind=engine)

SessionLocal = scoped_session(session)


def get_db_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
        SessionLocal.remove()


class Base(DeclarativeBase):
    pass


Base.metadata.create_all(bind=engine)

endpoint_call_counter = prometheus.Counter(
    "endpoint_call_counter",
    "Counter representing the number of calls to each endpoint URL by return status code",
    ["url", "status_code"],
)

endpoint_time_histogram = prometheus.Histogram(
    "endpoint_time_histogram",
    "Histogram representing time taken to complete each request by URL and status code",
    ["url", "status_code"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    prometheus.start_http_server(9101)
    yield


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def increase_endpoint_call_counter(request: Request, call_next):
    start = time.perf_counter()
    response: Response = await call_next(request)
    endpoint_call_counter.labels(
        url=request.url, status_code=response.status_code
    ).inc()
    time_taken = (time.perf_counter() - start) / 1000

    endpoint_time_histogram.labels(
        url=request.url, status_code=response.status_code
    ).observe(time_taken)
    return response
