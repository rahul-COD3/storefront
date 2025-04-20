# Storefront

A Django-based web application for e-commerce and related services.

## Features

- Django 5.2+ with REST API (DRF)
- Celery for background tasks
- Redis and MySQL support (via Docker)
- JWT authentication (djoser, simplejwt)
- Modern dev tools: Debug Toolbar, Silk, pytest, Locust
- Dockerized for easy local development
- Managed with [`uv`](https://docs.astral.sh/uv/) (fast Python package/project manager)
- Python 3.13

---

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (recommended install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Python 3.13 (managed by uv)
- [Docker](https://www.docker.com/) and Docker Compose

---

## Getting Started

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd storefront
```

### 2. Install Python 3.13 (if not already)

```bash
uv python install 3.13
uv python pin 3.13
```

### 3. Install dependencies

```bash
uv sync
```

This will create a `.venv` and install all dependencies as defined in `pyproject.toml`.

### 4. Set up environment variables

Copy or edit the provided `docker.env` for local development. For local (non-Docker) runs, you can use a `.env` file with the same variables.

Example (`.env`):

```env
SECRET_KEY=your-secret-key
DATABASE_URL=mysql://root:MyPassword@localhost:3306/storefront_prod
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
INTERNAL_IPS=127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
DEFAULT_FROM_EMAIL=your@email.com
EMAIL_HOST=smtp4dev
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_PORT=2525
REDIS_URL=redis://localhost:6379/1
```

---

## Running Locally (without Docker)

1. **Activate the virtual environment:**
   ```bash
   source .venv/bin/activate
   ```
2. **Apply migrations:**
   ```bash
   uv run python manage.py migrate
   ```
3. **Run the development server:**
   ```bash
   uv run python manage.py runserver
   ```
4. **Run Celery worker (in a separate terminal):**
   ```bash
   uv run celery -A storefront worker --loglevel=info
   ```
5. **Run Celery beat (in a separate terminal):**
   ```bash
   uv run celery -A storefront beat --loglevel=info
   ```

---

## Running with Docker

1. **Build and start all services:**
   ```bash
   docker compose --env-file docker.env up --build
   ```
   This will start:
   - Django app (web)
   - MySQL
   - Redis
   - Celery worker & beat
   - Flower (Celery monitoring)
   - smtp4dev (for email testing)

2. **Access the app:**
   - Django: [http://localhost:8000](http://localhost:8000)
   - Flower: [http://localhost:5555](http://localhost:5555)
   - smtp4dev: [http://localhost:5000](http://localhost:5000)

---

## Running Tests

```bash
uv run pytest
```

Or with Docker:

```bash
docker compose run --rm tests
```

---

## Useful Commands

- **Add a new dependency:**
  ```bash
  uv add <package-name>
  ```
- **Add a dev dependency:**
  ```bash
  uv add --group dev <package-name>
  ```
- **Sync dependencies:**
  ```bash
  uv sync
  ```
- **Run management commands:**
  ```bash
  uv run python manage.py <command>
  ```

---

## References

- [uv documentation](https://docs.astral.sh/uv/)
- [Django documentation](https://docs.djangoproject.com/)
- [Celery documentation](https://docs.celeryq.dev/)

---

## Notes

- The project uses a `.python-version` file to pin Python 3.13 for uv.
- All dependencies are managed via `pyproject.toml` and `uv.lock`.
- For advanced usage, see the [uv documentation](https://docs.astral.sh/uv/).
