#!/bin/bash

/usr/bin/node_exporter &

exec uvicorn main:app --host 0.0.0.0 --port 8000
