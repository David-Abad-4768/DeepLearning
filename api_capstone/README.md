# Capstone Project – FastAPI API - Finnisimo Chat V2

> A multimodal platform that combines a domain‑tuned LLaMA 3.2‑3B recommender with Stable Diffusion 1.5 for smartphone advice and custom case design.

---

## 📑 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installing Python](#installing-python)
3. [Project Setup](#project-setup)
4. [Database & Migrations (Alembic)](#database--migrations-alembic)
5. [Running the API](#running-the-api)
6. [API Reference & Swagger](#api-reference--swagger)
7. [Running Tests](#running-tests)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

| Tool                    | Minimum version | Purpose                    |
| ----------------------- | --------------- | -------------------------- |
| **Python**              | 3.10+           | Core runtime               |
| **pip**                 | latest          | Python package manager     |
| **virtualenv / venv**   | built‑in        | Isolated env               |
| **Docker** _(optional)_ | 24.x            | DB container & prod deploy |
| **Alembic**             | 1.13+           | Schema migrations          |
| **pytest**              | 8.x             | Test runner                |

> ℹ️ _Docker is optional for local development. Alembic is already configured for **MySQL**._

---

## Installing Python

### Linux (Debian/Ubuntu)

```bash
sudo apt update && sudo apt install -y python3 python3-venv python3-pip
```

### Linux (Arch‑based)

```bash
sudo pacman -Syu python python-pip
```

### macOS (Homebrew)

```bash
brew install python@3.12
```

### Windows 10/11

1. Download the **Windows installer** from [https://www.python.org/downloads/](https://www.python.org/downloads/).
2. Run the installer _as Administrator_ and **check “Add Python to PATH.”**
3. Verify:

```powershell
python --version
pip --version
```

---

## Project Setup

1. **Clone the repo**

   ```bash
   git clone git@gitlab.com:jala-university1/cohort-1/oficial-es-aprendizaje-profundo-csai-353/secci-n-d/david_abad/capstone_api.git
   cd capstone_api
   ```

2. **Create a virtual environment**
   _Linux/macOS_

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

   _Windows PowerShell_

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Create/Update the `.env` file**
   Copy the template or paste the variables below:

   ````bash
   API_VERSION=1.0.0
   DEBUG_MODE=True

   # MySQL container connection
   DATABASE_URL="mysql+pymysql://root:root@localhost:3306/capstone"

   # Security & authentication
   SECRET_KEY=d1db137d1313d740f7cfcabde2446d744898b5c050b8126c27f1a0157e758fd1bd0e63cc83fddaa6f51ab990814b80b06449942126a07c61c39cc04ed019b9386ec76869711affb8499f221c52ca99cafc1c493fb88ede125f45f9962e0d363fde29e4f5a99158f73675d4c7cee0b22859914ec5c32df346b514ff0efb721a027909329bb4d3d2948fafba825848c7968f7a59a4f6dff602df0ef88ac6ef3407cfd6fc173af5cfd424e9e9a5977660e16f894fa158a0f4ed0ca661e8bd5e57a9bfffc6bb9cf56a4f23e76efe8acc396a5f902d4475fdfa0a0a5eed8753271e0b954cf5734f484a391fb8d8e7737e74cac01648acdda50944965f7e89f82ab704
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # Cloudinary
   CLOUDINARY_CLOUD_NAME=dd1ypjcgp
   CLOUDINARY_API_KEY=288288612763166
   CLOUDINARY_API_SECRET=rCUKWm6r1G0bwOWAjjTjWGTY6Sw
   ```bash
   cp .env.example .env
   # edit DB_URL, JWT_SECRET, CLOUDINARY_KEY, etc.
   ````

---

## Database & Migrations (Alembic)

The project uses **MySQL** and ships with a `docker-compose.yml` that spins up a single database container named **`db`** (port `3306`).

### 1. Start the database container

```bash
docker compose up -d db    # or docker-compose up -d db
```

> Your `.env` should contain `DB_URL=mysql+pymysql://user:pass@db:3306/capstone`.

### 2. Run migrations

```bash
alembic upgrade head         # inside the venv
```

_If you prefer to run Alembic from inside another container (e.g., `api`), change the command accordingly._

### 3. Create a new migration

```bash
alembic revision --autogenerate -m "Add new table"
alembic upgrade head
```

---

## Running the API

### Development server

```bash
python -m app.main                  # HTTPS on 0.0.0.0:8443 by default
```

The default host and port are configured in `Settings.py`. To override:

```bash
export API_HOST="127.0.0.1"
export API_PORT="8000"
python -m app.main
```

### Gunicorn (prod-like)

If you need a different process manager in production, you can still rely on `uvicorn` workers:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8443 --workers 4 --ssl-keyfile /path/key.pem --ssl-certfile /path/cert.pem
```

---

## API Reference & Swagger

| Documentation  | URL                           |
| -------------- | ----------------------------- |
| **Swagger UI** | `http://127.0.0.1:8000/docs`  |
| **ReDoc**      | `http://127.0.0.1:8000/redoc` |

Core base path: **`/api/v1`**

_Example protected flow_

1. `POST /api/v1/auth/login` → obtains and stores `access_token` cookie.
2. Authorize via Swagger’s **Authorize** button.
3. Interact with chats, messages, LLaMA endpoints, or Stable Diffusion tools.

---

## Running Tests

```bash
pytest                     # unit + integration
pytest --cov=app tests/    # with coverage (HTML report in htmlcov/)
```

Expected output sample:

```
101 passed in 3.47s, 3 warnings
----------- coverage: platform linux, Python 3.10 -----------
Name                               Stmts   Miss  Cover
------------------------------------------------------
app/...                               647     78    88%
```

---

## Troubleshooting

| Symptom                            | Fix                                                                               |
| ---------------------------------- | --------------------------------------------------------------------------------- |
| `ModuleNotFoundError: app`         | Ensure you run from repo root _and_ the venv is active.                           |
| Alembic `target_metadata` missing  | Import your `Base` into `alembic/env.py`.                                         |
| GPU OOM during LLaMA inference     | Use `POST /api/v1/llama/release` to free VRAM or set `CUDA_VISIBLE_DEVICES=""`.   |
| SSL error on `/docs` (self‑signed) | Launch with `--ssl-keyfile/--ssl-certfile` or switch to plain HTTP for local dev. |

---

### 💡 Tips

- Add a **Makefile** with common shortcuts (`make dev`, `make test`, `make migrate`).
- Use **pre‑commit** to auto‑format with _ruff + black_ before every commit.
- Set `PYTHONWARNINGS=ignore` to silence deprecation warnings during tests.
