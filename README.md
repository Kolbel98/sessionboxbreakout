# 📊 SessionBox — Trading Strategy Analyzer

> **Backtest intraday breakout strategies based on session boxes — built with Django & React.**

SessionBox is a full-stack web application designed for backtesting an **intraday breakout strategy** that relies on session-defined price ranges (session boxes). The app fetches historical 5-minute OHLCV data from TradingView, calculates session highs/lows, detects breakouts, and evaluates them against configurable Take Profit, Stop Loss, and Risk-to-Reward parameters — all presented through a clean, modern dashboard.

---

## 🎯 Strategy Overview

The core idea is simple:

1. **Define a session window** — e.g. the Asian session (00:00–09:00 CET) for DAX, or the European session (07:00–16:00 CET) for US indices.
2. **Calculate the session box** — the high and low of that session window.
3. **Wait for a breakout** — the first candle that breaks above or below the session box after the session ends.
4. **Enter the trade** with a user-defined TP (Take Profit) and SL (Stop Loss) derived from the chosen R:R ratio.
5. **Walk forward** through subsequent candles to determine win, loss, or no breakout.

Each instrument has its own session configuration:

| Instrument | Session Window | Breakout Window |
|------------|---------------|-----------------|
| DAX (FDAX) | 00:00 – 09:00 | 09:00 – 16:00 |
| NQ (E-mini Nasdaq) | 07:00 – 16:00 | 16:00 – 21:00 |
| SP500 (E-mini S&P) | 07:00 – 16:00 | 16:00 – 21:00 |
| DJ (E-mini Dow) | 07:00 – 16:00 | 16:00 – 21:00 |

---

## ✨ Features

- 📈 **Multi-instrument support** — DAX, Nasdaq (NQ), S&P 500, Dow Jones
- 📅 **Flexible date ranges** — Yesterday, This Week, Last Week, This Month, or Custom range (up to 30 days)
- 🎯 **Configurable TP/SL** — Set Take Profit in points, Stop Loss auto-calculated from R:R ratio (1:1, 1:2, 1:3, 2:1, or custom)
- 📊 **Visual summary** — SVG donut chart showing win/loss/no-breakout distribution
- 📋 **Detailed results table** — Day-by-day breakdown with direction, entry, TP/SL levels, points gained/lost
- 🗄️ **Smart data caching** — Fetched price data is stored in the database to avoid redundant API calls
- ⏱️ **5-minute resolution** — All analysis runs on 5-min OHLCV candles from TradingView
- 🔌 **REST API** — Clean Django REST Framework endpoints for easy extensibility

---

## 🛠️ Tech Stack

### Backend
- **Python 3.13+** with **[uv](https://docs.astral.sh/uv/)** package manager
- **Django 6.0** — web framework
- **Django REST Framework** — API serialization & views
- **tvDatafeed** — historical price data scraped from TradingView
- **pandas** — data manipulation & time series handling
- **PostgreSQL** + **psycopg2-binary** — production-ready relational database
- **python-dotenv** — environment variable management
- **django-cors-headers** — CORS support for frontend dev

### Frontend
- **React 19** with **TypeScript**
- **Vite 8** — blazing fast dev server & build tool
- **TailwindCSS v4** — utility-first styling
- **Outfit** — Google Font for clean UI typography

---

## 📁 Project Structure

```
SessionBox/
├── README.md
├── tv_data_fetch/                  # Backend (Django)
│   ├── pyproject.toml              # Python dependencies (uv)
│   ├── main.py
│   └── session_box/
│       ├── manage.py
│       └── api_tvData/
│           ├── models.py           # PriceRecord model
│           ├── views.py            # PriceDataView, BacktestView
│           ├── serializers.py
│           └── services/
│               ├── tv_data_service.py      # Data fetching & caching
│               ├── session_box_service.py  # Session box calculation
│               ├── breakout_service.py     # Breakout detection & evaluation
│               └── summary_service.py      # Aggregated statistics
└── react-interface/                # Frontend (React)
    └── session-box/
        ├── package.json
        ├── vite.config.ts
        └── src/
            ├── App.tsx
            ├── api.ts              # API types & fetch logic
            └── components/
                ├── BacktestForm.tsx
                ├── SummaryPanel.tsx
                └── ResultsTable.tsx
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.13+** & **[uv](https://docs.astral.sh/uv/)**
- **Node.js 20+** & **npm**
- **PostgreSQL** running locally (or remote)

### Environment Variables

Create a `.env` file in the project root:

```env
# PostgreSQL
DB_NAME=sessionbox
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Backend Setup

```bash
# Navigate to backend directory
cd tv_data_fetch

# Install dependencies with uv
uv sync

# Create the database in PostgreSQL
psql -U postgres -c "CREATE DATABASE sessionbox;"

# Run migrations
uv run python session_box/manage.py migrate

# Start the development server
uv run python session_box/manage.py runserver
```

The API will be available at `http://localhost:8000`.

### Frontend Setup

```bash
# Navigate to frontend directory
cd react-interface/session-box

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The frontend will be available at `http://localhost:5173`.

---

## 🔌 API Endpoints

### `GET /api/backtest/`

Run a backtest for a given instrument and time period.

**Query Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `instrument` | string | Trading instrument | `DAX`, `NQ`, `SP500`, `DJ` |
| `period` | string | Time period | `yesterday`, `this_week`, `last_week`, `this_month`, `custom` |
| `tp_points` | number | Take Profit in points | `60` |
| `offset_points` | number | Entry offset in points | `5` |
| `rr_mode` | string | Risk-to-Reward ratio | `1:1`, `1:2`, `1:3`, `2:1`, `custom` |
| `custom_sl` | number | Custom SL (if rr_mode=custom) | `30` |
| `start_date` | string | Start date (if period=custom) | `2026-03-01` |
| `end_date` | string | End date (if period=custom) | `2026-03-15` |

**Example Request:**

```
GET /api/backtest/?instrument=DAX&period=this_week&tp_points=60&offset_points=5&rr_mode=1:2
```

### `GET /api/price-data/`

Fetch raw OHLCV price data for an instrument and date range.

---



<p align="center">
  Built with ☕ and 📊 by <a href="https://github.com/Kolbel98">@Kolbel98</a>
</p>