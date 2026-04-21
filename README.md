<div align="center">

# 📡 PULSE LLMOps

### Real-Time LLMOps Monitoring and Observability Platform

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.x-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![Groq](https://img.shields.io/badge/Groq-LLM_API-000000?style=for-the-badge)](https://groq.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<br/>

> **PULSE LLMOps** is a full-stack observability dashboard for production AI workloads. It captures and stores every LLM call, computes latency/token/cost/error metrics, pushes live updates over WebSockets, and helps teams quickly detect quality and reliability issues.

<br/>

![Live Metrics](https://img.shields.io/badge/Live-KPI%20Dashboard-blue?style=for-the-badge) ![Telemetry Ingestion](https://img.shields.io/badge/Track-External%20App%20Calls-orange?style=for-the-badge) ![Alerts](https://img.shields.io/badge/Threshold-Alert%20Engine-red?style=for-the-badge)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Application Preview](#-application-preview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [Security Notes](#-security-notes)

---

## 🧠 Overview

PULSE is built for teams running LLM-powered features in real products.

It answers core production questions in seconds:

- Are responses slowing down?
- Which model or endpoint is driving cost?
- How often are calls failing?
- Which sessions need deeper trace-level debugging?

Instead of treating AI calls as opaque events, PULSE turns every request into structured telemetry and live operational intelligence.

---

## 💻 Application Preview
<br/>
<br/>
<img width="1365" height="643" alt="{82DD1B1B-6CB3-492D-9A39-081EFE80EBE9}" src="https://github.com/user-attachments/assets/1a606b34-06b4-483f-b568-9190da410f67" />
<br/>
<br/>
<img width="1366" height="640" alt="{35E76ADA-0EA2-4D95-8B34-658FE56A2945}" src="https://github.com/user-attachments/assets/2237e21e-532f-4c22-add4-887f74867906" />
<br/>
<br/>
<img width="1366" height="642" alt="{576061B8-32EF-4D9E-8E34-FB7D7137E7AA}" src="https://github.com/user-attachments/assets/b6ed4243-e554-4b72-b62d-1d779d78f5d9" />
<br/>
<br/>
<img width="1366" height="639" alt="{21EFAE31-4DAE-490F-86FD-AE6DC1A60BC4}" src="https://github.com/user-attachments/assets/b2a68731-7052-45bf-acbb-aba4c757bb1c" />
<br/>
<br/>
<img width="1366" height="636" alt="{36D5E71C-D97B-4C8D-AE96-E63EB77B8FC4}" src="https://github.com/user-attachments/assets/d914c724-becb-4bbc-9906-f1aa541afcdd" />
<br/>
<br/>
<img width="1361" height="639" alt="{83F067E6-244D-4728-A7E3-3DB3B9C1F2BC}" src="https://github.com/user-attachments/assets/5fc26acc-ee0a-432c-a17e-067dafa1ba05" />
<br/>
<br/>

## ✨ Features

| Feature | Description |
|---|---|
| 📈 **Live KPI Dashboard** | Real-time total calls, avg latency, token usage, error rate, and estimated cost |
| 📊 **Time-Series Analytics** | Persisted trends for latency and token volume over time |
| 🧾 **Trace Log & Call Inspector** | View prompt, response, model, latency, tokens, status, and metadata per call |
| 🚨 **Alert Engine** | Trigger alerts on latency spikes, high error rates, and daily cost thresholds |
| ▶️ **Playground Calls** | Send direct prompts from the app and track them like first-class production calls |
| 🔌 **External App Tracking** | Ingest telemetry from any app through `POST /track` |
| 🔄 **WebSocket Streaming** | Pushes new call and alert updates to the dashboard live |
| 🔐 **Security Layer** | Optional API-key auth plus in-memory per-IP rate limiting |
| 🐳 **Deployment Ready** | Dockerfiles, docker-compose, and CI workflow included |

---

## 🏗️ Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                      React Dashboard                        │
│   KPI cards • charts • recent calls • alerts • demo run    │
└───────────────┬─────────────────────────────────────────────┘
                │ HTTP + WebSocket
┌───────────────▼─────────────────────────────────────────────┐
│                      FastAPI Backend                        │
│                                                             │
│  /track         ingest external app telemetry               │
│  /playground    run tracked Groq calls                      │
│  /demo/run-support  run realistic support demo tickets      │
│  /metrics/*     summary, timeseries, model breakdown        │
│  /calls, /alerts persisted observability records            │
│  /ws            live broadcast on new calls + alerts        │
└───────────────┬─────────────────────────────────────────────┘
                │
      ┌─────────▼─────────┐          ┌────────────────────────┐
      │ SQLite + aiosqlite│          │ Groq API (LLM provider)│
      │ calls + alerts    │          │ llama-3.1-8b-instant   │
      └───────────────────┘          └────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, Recharts, Axios |
| **Backend** | FastAPI, Uvicorn, Pydantic, aiosqlite |
| **LLM Provider** | Groq Python SDK (`groq`) |
| **Realtime** | FastAPI WebSockets |
| **Storage** | SQLite (`pulse.db`) |
| **Security** | API key middleware + in-memory rate limiter |
| **DevOps** | Docker, Docker Compose, GitHub Actions |
| **Testing** | Pytest |

---

## 📁 Project Structure

```text
pulse-llmops/
├── backend/
│   ├── main.py
│   ├── groq_service.py
│   ├── database.py
│   ├── alert_engine.py
│   ├── analyzer.py
│   ├── rate_limiter.py
│   ├── schemas.py
│   ├── settings.py
│   ├── tests/test_api.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/pages/DashboardPage.jsx
│   ├── src/services/api.js
│   ├── src/styles/globals.css
│   ├── Dockerfile
│   └── package.json
├── examples/
│   └── support_bot_demo.py
├── docs/screenshots/
├── .github/workflows/ci.yml
├── docker-compose.yml
├── render.yaml
└── README.md
```

---

## 🚀 Installation

### Prerequisites

- Python 3.12+
- Node.js 18+
- Groq API key

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm start
```

### Local URLs

- Dashboard: `http://localhost:3000`
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

---

## 💻 Usage

### 1) Track external app calls

Send your app telemetry to:

- `POST /track`

### 2) Run playground prompts

Use:

- `POST /playground`

### 3) Observe live dashboard

Watch KPI cards, charts, call logs, and alerts update automatically via polling + WebSocket events from `/ws`.

### 4) Run one-click demo

Use **Run Demo Tickets** from the dashboard to simulate a support workflow and generate tracked calls.

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health status |
| GET | `/metrics/summary` | Aggregate KPI summary |
| GET | `/metrics/timeseries?hours=24` | Time-bucket trend metrics |
| GET | `/metrics/models` | Per-model aggregate metrics |
| GET | `/calls?limit=50&offset=0` | Recent call records |
| GET | `/calls/{call_id}` | Single call detail |
| GET | `/alerts` | Active alerts |
| POST | `/track` | Ingest external call telemetry |
| POST | `/playground` | Run and track a Groq call |
| POST | `/demo/run-support` | Execute built-in support demo |
| WS | `/ws` | Live event stream |

---

## ⚙️ Configuration

Set values in `backend/.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
API_KEY=
APP_ENV=development
DB_PATH=./pulse.db
ALLOW_CORS_ORIGINS=http://localhost:3000
RATE_LIMIT_PER_MINUTE=120
COST_PER_1K_INPUT_TOKENS=0.00015
COST_PER_1K_OUTPUT_TOKENS=0.0006
LATENCY_ALERT_MS=5000
ERROR_RATE_ALERT_PCT=10
DAILY_COST_ALERT_USD=1.0
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
venv\Scripts\python -m pytest -q

# Frontend production build
cd ../frontend
npm run build
```

---

## 🔒 Security Notes

- Never commit real API keys.
- Restrict CORS origins before public deployment.
- Replace SQLite with Postgres for multi-user production workloads.
- Add secret rotation and managed secret storage for deployed environments.

---

## 📜 License

Licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

<div align="center">

Built with ❤️ by [Crasta Telvin](https://github.com/crastatelvin)

⭐ Star this repo if you find it useful!

</div>
