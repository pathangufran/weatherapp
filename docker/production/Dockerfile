FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY . .

RUN groupadd --system app && \
    useradd --system --gid app app

RUN chown -R app:app /app

USER app

CMD ["gunicorn", "-c","docker/production/gunicorn.conf.py","weather.wsgi:application"]

ENTRYPOINT ["docker/production/entrypoint.sh"]