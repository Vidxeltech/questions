# Real-time Question Submission & Moderation (Django + Channels)

Production-grade **real-time Question Submission & Moderation** system:

- **/screen/**: Fullscreen projector page showing **approved questions** + a **QR code** to **/ask/**
- **/ask/**: Mobile form (name optional, question required) with **rate limiting** and **admin-configurable max length**
- **/admin/**: Secure admin moderation (approve/reject/delete) — approving updates **/screen/** instantly (no refresh)
- Real-time updates via **Django Channels (WebSockets)** (no polling)

---

## 0) Requirements

- Python 3.10+ recommended
- PostgreSQL (created & managed in **pgAdmin**)
- Redis (Channels layer) — local install or Docker **(OK; DB is NOT dockerized)**

---

## 1) Create PostgreSQL DB in pgAdmin (MANDATORY)

### 1.1 Create database
1. Open **pgAdmin**
2. Connect to your PostgreSQL server
3. Right-click **Databases → Create → Database**
4. **Database name:** `question_moderation`
5. Owner: your postgres user (e.g. `postgres`)
6. Save

### 1.2 Create an app user (recommended)
Run in pgAdmin Query Tool (adjust password):

```sql
CREATE USER question_app WITH PASSWORD 'change_me_strong_password';
GRANT ALL PRIVILEGES ON DATABASE question_moderation TO question_app;
```

If your Postgres version requires schema privileges after migrations, run:

```sql
\c question_moderation
GRANT ALL ON SCHEMA public TO question_app;
```

---

## 2) Setup locally (Baby Guide)

### 2.1 Unzip
Unzip to something like: `C:\projects\realtime_questions\`

### 2.2 Create & activate a virtualenv (Windows CMD)
```bat
cd C:\projects\realtime_questions
python -m venv venv
venv\Scripts\activate
```

### 2.3 Install dependencies
```bat
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3) Configure environment variables

Create **.env** beside `manage.py`:

```env
DJANGO_SECRET_KEY=change-me-to-a-long-random-secret
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=question_moderation
DB_USER=question_app
DB_PASSWORD=change_me_strong_password
DB_HOST=127.0.0.1
DB_PORT=5432

# Channels / Redis
REDIS_URL=redis://127.0.0.1:6379/0
```

If using **ngrok**, also add:

```env
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost,xxxx.ngrok-free.dev
DJANGO_CSRF_TRUSTED_ORIGINS=https://xxxx.ngrok-free.dev
```

---

## 4) Run migrations (creates tables in your existing DB)
```bat
python manage.py migrate
```

---

## 5) Create admin user
```bat
python manage.py createsuperuser
```

---

## 6) Start Redis (required for real-time)

### Option A: Redis via Docker (recommended)
```bat
docker run --name rq_redis -p 6379:6379 -d redis:7
```

### Option B: Redis on WSL / local
Ensure Redis is reachable at `127.0.0.1:6379`.

---

## 7) Start the server (Channels enabled)
```bat
python manage.py runserver 0.0.0.0:8000
```

Open:
- Screen: `http://127.0.0.1:8000/screen/`
- Ask: `http://127.0.0.1:8000/ask/`
- Admin: `http://127.0.0.1:8000/admin/`

---

## 8) Test (Step-by-step)

### 8.1 Set AppSetting (MANDATORY)
1. Go to admin → **QA → App settings**
2. Edit singleton row:
   - `max_question_length` (e.g. 200)
   - `submissions_enabled` (True)

### 8.2 Projector screen
1. Open `/screen/`
2. Press **F11** or kiosk mode
3. You should see QR code and approved questions list

### 8.3 Submit from phone
1. Scan QR
2. Submit question → you get confirmation

### 8.4 Approve in admin
1. Admin → **QA → Questions**
2. Filter **pending**
3. Select → **Approve selected questions**
4. The `/screen/` updates instantly

---

## 9) Kiosk / Fullscreen (No URL indicators)

Chrome kiosk shortcut target:

```text
"C:\Program Files\Google\Chrome\Application\chrome.exe" --kiosk http://127.0.0.1:8000/screen/
```

---

## 10) SQL Schema

Equivalent PostgreSQL schema: `sql/schema.sql`

> You still run Django migrations; this schema is provided to satisfy the “SQL schema” deliverable.

