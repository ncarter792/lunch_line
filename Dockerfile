FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /lunch_line_app

RUN python -m pip install --upgrade pip && pip install uv

COPY pyproject.toml /lunch_line_app/
COPY . /lunch_line/ 

RUN uv sync --all-extras

EXPOSE 8080
CMD ["python", "-m", "lunch_line.server"]
