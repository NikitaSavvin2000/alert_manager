FROM python:3.9-slim-buster

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pdm install

CMD ["sh"]
