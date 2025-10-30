import asyncio
import random
import time
from contextlib import asynccontextmanager

import prometheus_client as prometheus
from fastapi import FastAPI, HTTPException, Request, Response


@asynccontextmanager
async def lifespan(app: FastAPI):
    prometheus.start_http_server(9101)
    yield


app = FastAPI(lifespan=lifespan)

send_email_http_request_timing_histogram = prometheus.Histogram(
    "send_email_http_request_timing_histogram",
    "Histogram representing time taken to send emails via http request in miliseconds",
)

endpoint_call_counter = prometheus.Counter(
    "endpoint_call_counter",
    "Counter representing the number of calls to each endpoint URL by return status code",
    ["url", "status_code"],
)


@app.middleware("http")
async def increase_prometheus_counter(request: Request, call_next):
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
    await send_email_via_http_request()


def _calculate_time_for_each_request():
    chance = random.randint(0, 100)

    if chance >= 99:
        time_range = (20, 30)
    elif chance >= 80:
        time_range = (8, 10)
    else:
        time_range = (0, 1)

    return random.uniform(*time_range)


async def send_email_via_http_request():
    start = time.perf_counter_ns()
    await asyncio.sleep(_calculate_time_for_each_request())

    end = time.perf_counter_ns()
    time_taken_ms = (end - start) / 1_000_000
    send_email_http_request_timing_histogram.observe(time_taken_ms)

    if random.randint(0, 100) > 90:
        raise HTTPException(500)
