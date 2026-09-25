# LifeDrop — Blood Donor Management MVP

A demo-ready blood donor management app built with **Python Flask + SQLite + vanilla HTML/CSS/JS**. No authentication, no test suite — just register donors, search for them, submit blood requests, and view live dashboard stats.

## Project structure

```
app.py            # Flask app, routes, DB init
seed.py           # Populates 12 sample donors
templates/index.html
static/style.css
static/script.js
database.db        # auto-created on first run
```

## Setup & run

```bash
pip install flask
python seed.py      # optional: adds 12 sample donors
python app.py
```

Then open **http://localhost:5000** (or the Replit webview URL).

On Replit, the app automatically binds to `0.0.0.0` and uses the `PORT` environment variable if set, so it works out of the box.

## Features

- **Register** — add a donor (name, age 18–65, blood group, phone, location, last donation date, availability)
- **Search** — live filter donors by blood group and city, shown as responsive cards
- **Request** — submit a blood request (patient, blood group, hospital, location, contact)
- **Dashboard** — live stats (total donors, available donors, pending requests) plus a table of all requests, newest first

## API routes

| Method | Route | Description |
|---|---|---|
| GET | `/` | Serves the single-page app |
| GET | `/api/donors?blood_group=&location=` | List/search donors |
| POST | `/api/donors` | Register a donor |
| GET | `/api/requests` | List all blood requests |
| POST | `/api/requests` | Submit a blood request |
| GET | `/api/stats` | Donor/request counts |

## Notes

- `database.db` is created automatically the first time `app.py` or `seed.py` runs.
- `seed.py` skips seeding if donors already exist — delete `database.db` for a clean reseed.
- No external CDNs are used except Google Fonts (Poppins).
