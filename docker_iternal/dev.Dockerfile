FROM python:3.12-slim
LABEL authors="exizman"

WORKDIR /app

ARG REQ_PATH=./requirements.txt
COPY ${REQ_PATH} ./requirements.txt
RUN pip install -r requirements.txt

# Если требуется, отдельный шаг для специфичных библиотек
RUN pip install passlib bcrypt

ENV PYTHONUNBUFFERED=1

# Универсальные переменные окружения
ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG POSTGRES_HOST
ARG POSTGRES_PORT
ARG POSTGRES_NAME

ENV POSTGRES_USER=$POSTGRES_USER
ENV POSTGRES_PASSWORD=$POSTGRES_PASSWORD
ENV POSTGRES_HOST=$POSTGRES_HOST
ENV POSTGRES_PORT=$POSTGRES_PORT
ENV POSTGRES_NAME=$POSTGRES_NAME

# Копируем всё приложение
COPY ./ /app

# Можно переопределить в docker-compose
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
