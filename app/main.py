import random
import time
from contextlib import asynccontextmanager

import mock
import prometheus_client as prometheus
from fastapi import FastAPI, HTTPException, Request, Response


@asynccontextmanager
async def lifespan(app: FastAPI):
    prometheus.start_http_server(9101)
    yield


app = FastAPI(lifespan=lifespan)
buckets = (250, 500, 750, 1000, 2500, 5000, 10000, 20000, 30000, 60000, float("inf"))

send_email_http_request_timing_histogram = prometheus.Histogram(
    "send_email_http_request_timing_histogram",
    "Histogram representing time taken to send emails via http request in miliseconds",
    buckets=buckets,
)

endpoint_call_counter = prometheus.Counter(
    "endpoint_call_counter",
    "Counter representing the number of calls to each endpoint URL by return status code",
    ["url", "status_code"],
)


@app.middleware("http")
async def increase_endpoint_call_counter(request: Request, call_next):
    response: Response = await call_next(request)
    endpoint_call_counter.labels(
        url=request.url, status_code=response.status_code
    ).inc()
    return response


@app.get("/")
async def root():
    return {"message": "Hello world!"}


@app.post("/send-email")
async def send_email():
    start = time.perf_counter_ns()
    await mock.send_email_via_http_request()
    if random.randint(0, 100) > 99:
        raise HTTPException(500)

    end = time.perf_counter_ns()
    time_taken_ms = (end - start) / 1_000_000
    send_email_http_request_timing_histogram.observe(time_taken_ms)
    return {"status_code": 200, "message": "OK"}
