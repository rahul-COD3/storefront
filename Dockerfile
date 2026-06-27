FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/venv \
    PATH="/venv/bin:$PATH"

RUN apt-get update \
  && apt-get install -y python3-dev default-libmysqlclient-dev gcc pkg-config \
  && rm -rf /var/lib/apt/lists/*

RUN pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --all-groups --no-install-project

COPY . /app/

EXPOSE 8000