import time
from contextlib import asynccontextmanager

import prometheus_client as prometheus
from fastapi import FastAPI, Request, Response
from sqlalchemy import create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker,
)

alloc_mem = []

engine = create_engine(
    "postgresql+psycopg2://prometheus:prometheus@postgres:5432/prometheus",
    pool_size=10,
    max_overflow=0,
)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


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
    prometheus.start_http_server(9100)
    yield


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def increase_endpoint_call_counter(request: Request, call_next):
    alloc_mem.append("X" * 100_000)

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
