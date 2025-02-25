FROM python:3.9.16-slim-buster

COPY . /app
WORKDIR /app

ENV PYTHONPATH=/app

COPY pyproject.toml .

RUN pip install -U pip setuptools wheel
RUN pip install pdm
RUN pdm install

ENTRYPOINT ["pdm", "run", "src/utils/telegram_bot.py"]
ENTRYPOINT ["pdm", "run", "src/server.py"]
