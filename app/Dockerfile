FROM python:3.13.9-trixie

COPY . /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD uvicorn main:app --host 0.0.0.0 --port 8000 --reload --workers 1
