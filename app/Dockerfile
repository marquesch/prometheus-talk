FROM python:3.13.9-trixie

COPY . /app

RUN wget -O - https://github.com/prometheus/node_exporter/releases/download/v1.10.2/node_exporter-1.10.2.linux-amd64.tar.gz | tar xvfz - --strip-components=1 -C /tmp
RUN mv /tmp/node_exporter /usr/bin/node_exporter

WORKDIR /app

RUN pip install -r requirements.txt

CMD ["./entrypoint.sh"]
