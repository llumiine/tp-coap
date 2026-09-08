FROM python:3.12-slim

RUN pip install --no-cache-dir aiocoap

WORKDIR /app
COPY server.py client.py ./

CMD ["python", "server.py"]
