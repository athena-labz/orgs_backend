FROM python:3.11.5-slim

# One of: dev, prod
ARG CURRENT_ENVIRONMENT
ARG PORT

RUN apt-get update && \
    apt-get install -y curl

ENV CURRENT_ENVIRONMENT=${CURRENT_ENVIRONMENT} \
  PORT=${PORT} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local' \
  POETRY_VERSION=1.7.1

# System deps:
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /code
COPY poetry.lock pyproject.toml /code/

# Project initialization:
RUN poetry install $(test "$CURRENT_ENVIRONMENT" == prod && echo "--only=main") --no-interaction --no-ansi

COPY . /code

EXPOSE 8080

CMD uvicorn main:app --host 0.0.0.0 --port ${PORT} --root-path /api