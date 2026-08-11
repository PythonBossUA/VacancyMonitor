# VacancyMonitor

![VacancyMonitor — Job Vacancy Scraping & Tracking Dashboard](https://image.qwenlm.ai/public_source/3e1e5889-d752-454f-9887-55df0e7d78f9/126f7ca03-ad23-4b55-a597-9d2ecc1bf54d.png)

> **A Django-powered web application that automatically scrapes IT job vacancies from [jobs.dou.ua](https://jobs.dou.ua), tracks their activity over time, and gives you a clean dashboard to search, filter, and manage them.**

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.1-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![BeautifulSoup](https://img.shields.io/badge/BeautifulSoup-4.15-E46C0A?style=for-the-badge&logo=python&logoColor=white)](https://www.crummy.com/software/BeautifulSoup/)
[![httpx](https://img.shields.io/badge/httpx-0.28-2C9FCB?style=for-the-badge&logo=python&logoColor=white)](https://www.python-httpx.org/)
[![Gunicorn](https://img.shields.io/badge/Gunicorn-26.0-499886?style=for-the-badge&logo=gunicorn&logoColor=white)](https://gunicorn.org/)
[![Status](https://img.shields.io/badge/status-active%20development-brightgreen?style=for-the-badge)](https://github.com/PythonBossUA/VacancyMonitor)

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [How It Works](#-how-it-works)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Data Models](#-data-models)
- [Getting Started](#-getting-started)
- [Usage Guide](#-usage-guide)
- [HTTP Endpoints](#-http-endpoints)
- [Deployment](#-deployment)
- [Logging & Error Handling](#-logging--error-handling)
- [Roadmap](#-roadmap)
- [Author](#-author)

---

## 🔭 Overview

**VacancyMonitor** is a personal job-market intelligence tool. It periodically crawls the Ukrainian IT job board **DOU (jobs.dou.ua)**, collects every fresh vacancy across all categories, stores them in a relational database, and presents them in a responsive, easy-to-use web dashboard.

Instead of manually browsing dozens of pages of job listings, you get:

- 🔄 **One-click scraping** — the whole market is collected in the background;
- 🔎 **Instant search & filtering** — by keyword, category, status, and activity;
- 🏷️ **Personal tracking** — mark vacancies as *"Applied"* or *"Not interested"*;
- 🧹 **Smart cleanup** — purge outdated (inactive) listings with a single action.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🕷️ **Automated Scraping** | Crawls *all* vacancy categories on jobs.dou.ua, following pagination until every listing is collected. |
| 🧵 **Background Processing** | Scraping runs in a daemon thread, so the UI responds instantly while data is being collected. |
| 🔁 **Smart Upserts** | Uses `bulk_create(..., update_conflicts=True)` — existing vacancies are re-activated, new ones inserted, all in a single atomic transaction. |
| 📉 **Activity Tracking** | Vacancies that disappeared from the source site are automatically flagged as `is_active=False`. |
| 🔎 **Search & Filters** | Full-text search by vacancy/company name + filters by category, personal status, and activity. |
| 📄 **Pagination** | Results are paginated (50 per page) for fast rendering. |
| 🏷️ **Status Management** | Tag any vacancy as `applied` / `not_interested` directly from the dashboard. |
| 🗑️ **Bulk Cleanup** | Delete all inactive vacancies with one POST request. |
| 🎨 **Beautiful UI** | Clean, responsive server-rendered templates with static assets. |
| 🌐 **Production Ready** | Ships with `gunicorn`, `whitenoise`, and `dj-database-url` for easy cloud deployment. |

---

## ⚙️ How It Works

The scraping pipeline (`app/tasks.py → scrap_data()`) follows these steps:

```text
┌─────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│  GET /scrap/│───▶│ Background thread│───▶│ GET jobs.dou.ua     │
└─────────────┘    │  scrap_data()    │    │ (grab CSRF cookie)  │
                   └──────────────────┘    └──────────┬──────────┘
                                                      ▼
┌─────────────────────────────────────────────────────────────────┐
│ Discover categories via <a class="cat-link"> → build XHR URLs   │
└──────────────────────────────┬──────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ POST to xhr-load endpoint (paginated via "count" offset)        │
│ until response["last"] == True                                  │
└──────────────────────────────┬──────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ Parse HTML fragments with BeautifulSoup:                        │
│  • title  → a.vt            • company → strong > a              │
│  • url    → a.vt[href]      • date    → div.date (UA months)    │
└──────────────────────────────┬──────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│ Atomic DB transaction:                                          │
│  1. Mark ALL vacancies inactive                                 │
│  2. Upsert scraped rows (unique by URL, re-activate on match)   │
└─────────────────────────────────────────────────────────────────┘
```

**Notable engineering details:**

- 🇺🇦 **Ukrainian date parsing** — month names like `січня`, `лютого` … are mapped to numeric months.
- 🔐 **CSRF-aware client** — the scraper extracts the `csrftoken` cookie and sends it with every paginated POST, mimicking the real browser XHR flow.
- 🛡️ **Defensive parsing** — every vacancy block is parsed inside its own `try/except`, so one malformed listing never kills the whole run.
- 💾 **Conflict-safe writes** — `bulk_create` with `unique_fields=["url"]` and `update_conflicts=True` keeps the dataset fresh without duplicates.

---

## 🧰 Tech Stack

| Layer | Technology | Version |
|---|---|---|
|  Language | Python | 3.12+ |
| 🌐 Framework | Django | 6.1 |
| 🕷️ HTML Parsing | BeautifulSoup4 | 4.15.0 |
| 🌍 HTTP Client | httpx | 0.28.1 |
| 🗄️ Database | PostgreSQL / SQLite (via `dj-database-url`) | — |
| 🚀 WSGI Server | Gunicorn | 26.0.0 |
| 📦 Static Files | WhiteNoise | 6.12.0 |
| 🎨 Frontend | HTML5 / CSS (server-rendered templates) | — |

---

## 🗂️ Project Structure

```text
VacancyMonitor/
├── app/                        # Core Django application
│   ├── migrations/             # Database schema migrations
│   ├── __init__.py
│   ├── models.py               # Company & Vacancy ORM models
│   ├── tasks.py                # Scraping engine (httpx + BeautifulSoup)
│   └── views.py                # Dashboard, filters, status & cleanup actions
├── server/                     # Django project configuration
│   ├── __init__.py
│   ├── settings.py             # Settings (WhiteNoise, DB URL, static)
│   ├── urls.py                 # URL routing
│   └── wsgi.py                 # WSGI entry point (Gunicorn)
├── static/                     # CSS / assets for the UI
├── templates/
│   ├── view_scraped_data.html  # Main dashboard (search, filters, pagination)
│   └── scraping_process_started.html
├── manage.py                   # Django CLI utility
├── requirements.txt            # Pinned production dependencies
└── build.sh                    # Deployment start-up script
```

---

## 🗃️ Data Models

### `Company`
| Field | Type | Notes |
|---|---|---|
| `name` | `CharField(255)` | `UNIQUE`, required |

### `Vacancy`
| Field | Type                  | Notes |
|---|-----------------------|---|
| `name` | `CharField(255)`      | Job title |
| `company` | `ForeignKey(Company)` | `on_delete=CASCADE` |
| `publication_date` | `DateField`           | Parsed from Ukrainian date strings |
| `url` | `URLField`            | `UNIQUE` — the deduplication key |
| `category` | `CharField(31)`       | DOU category (e.g. *backend*, *qa*) |
| `status` | `CharField(31)`       | `applied` / `not_interested` / `None` |
| `is_active` | `BooleanField`        | `False` if the vacancy vanished from dou.ua |

The model also exposes a handy `status_display` property that renders human-readable labels (`Відгукнувся`, `Не цікаво`, `Без статусу`).

---

## 🚀 Getting Started

### 1. Prerequisites
- Python **3.12+**
- `pip` and (optionally) `virtualenv`

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/PythonBossUA/VacancyMonitor.git
cd VacancyMonitor

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure the database *(optional)*

The project uses `dj-database-url`. Set `DATABASE_URL` for PostgreSQL, or leave the default SQLite:

```bash
export DATABASE_URL=postgres://user:password@localhost:5432/vacancy_monitor
```

### 4. Migrate & Run

```bash
python manage.py migrate
python manage.py runserver
```

Open **http://127.0.0.1:8000/** — your dashboard is live. 🎉

---

## 📚 Usage Guide

1. **Start scraping** — visit `/scrap/`. A background thread begins collecting vacancies; you'll see a confirmation page.
2. **Browse the dashboard** — the home page lists all vacancies, newest first.
3. **Search & filter** — combine a keyword search with category / status / activity filters.
4. **Track your progress** — use the per-vacancy status control to mark *Applied* or *Not interested*.
5. **Clean up** — press the *delete inactive* action to remove listings that are no longer published.

---

## 🔌 HTTP Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Dashboard: vacancy list with search, filters, pagination |
| `GET` | `/scrap/` | Launch the background scraping process |
| `POST` | `/vacancy/<int:vacancy_id>/status/` | Update a vacancy's personal status |
| `POST` | `/vacancy/delete/unactive/` | Bulk-delete all inactive vacancies |

---

## ☁️ Deployment

The project is configured for painless deployment to any WSGI-capable host (Render, Railway, VPS, …):

- **Gunicorn** serves the app via `server.wsgi`;
- **WhiteNoise** handles static file serving with no external CDN;
- **dj-database-url** reads the connection string from the `DATABASE_URL` environment variable;
- A shell start-up script is included for one-command boot.

```bash
gunicorn server.wsgi:application --bind 0.0.0.0:$PORT
```

---

## 🧾 Logging & Error Handling

The scraper logs every important event through Python's `logging` module:

- ❌ HTTP status errors and network failures (per category & per page);
- ⚠️ Empty HTML payloads and malformed vacancy blocks;
- 🛑 Critical failures with full stack traces (`logger.exception`);
- ✅ Successful batch saves with row counts.

All database writes happen inside `transaction.atomic()`, guaranteeing a consistent dataset even if the run fails midway.

---

## 🗺️ Roadmap

- [ ] Scheduled scraping (cron / management command)
- [ ] Salary extraction & analytics charts
- [ ] User accounts & per-user vacancy tracking
- [ ] REST API for external clients
- [ ] Email / Telegram notifications for new vacancies

---

## 👤 Author

**PythonBossUA** — [GitHub Profile](https://github.com/PythonBossUA)

---

<div align="center">

### ⭐ If you find this project useful, give it a star!

*Built with ❤️ and Django*

</div>
