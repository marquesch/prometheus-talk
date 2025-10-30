import asyncio
import random
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_client import Histogram, start_http_server


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_http_server(9101)
    yield


app = FastAPI(lifespan=lifespan)

workload_sim_histogram = Histogram(
    "workload_sim_histogram",
    "Histogram representing the time taken to simulate workload by success or failure",
    ["success", "tenant_id"],
)


@app.get("/")
async def root():
    return {"message": "Hello world!"}


@app.post("/simulate-workload-endpoint")
async def simulate_workload():
    tenant_id = random.randint(0, 5)
    start = time.perf_counter_ns()
    success = await workload()
    end = time.perf_counter_ns()

    time_taken_ms = (end - start) / 1000

    workload_sim_histogram.labels(success=success, tenant_id=tenant_id).observe(
        time_taken_ms
    )

    return {"success": success}


async def workload():
    time_to_sleep = random.randint(0, 10)
    await asyncio.sleep(time_to_sleep)
    return time_to_sleep % 2 == 0
