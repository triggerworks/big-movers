# Big Movers Dashboard

A self-hosted stock research tool for studying historical big movers in US equities, inspired by the Qullamaggie Breakout Methodology. Browse a curated list of high-momentum tickers on the left and study their historical price action with interactive charts on the right.

Reference: https://github.com/willhjw/big_movers

---

## Architecture

```
Big Movers/
├── CLAUDE.md                    # This file
├── Big_movers_server.py         # Flask backend server (port 5051)
├── Big_movers.html              # Frontend single-page app
├── big_movers_result.csv        # 1,495 real big mover entries (2000–2026)
├── SPY Historical Data.csv      # SPY benchmark reference data
├── Start Big Movers.bat         # Desktop shortcut — starts server + opens browser
├── collected_stocks/            # 929 per-ticker OHLCV CSV files (source: GitHub repo)
└── drawings/                    # Auto-created; per-symbol drawing annotations (JSON)
```

### Frontend ↔ Backend Communication
- Flask serves `Big_movers.html` at `/`
- Frontend calls REST endpoints to load ticker lists and chart data
- Drawing annotations are saved server-side as JSON in `drawings/`

---

## Tech Stack

| Layer     | Technology                                |
|-----------|-------------------------------------------|
| Backend   | Python 3.x + Flask                        |
| Frontend  | Vanilla HTML/CSS/JavaScript               |
| Charts    | TradingView Lightweight Charts v3.8 (CDN) |
| Data      | Local CSV files — no external APIs        |

---

## Quick Start

### Option A — Desktop shortcut (recommended)
Double-click `Start Big Movers.bat` on the Desktop. It starts the server and opens the browser automatically. Press any key in the terminal window to stop the server.

### Option B — Manual
```bash
pip install flask
python Big_movers_server.py
# then open http://127.0.0.1:5051
```

---

## Real Data Format

### collected_stocks/<TICKER>.csv
Sourced from https://github.com/willhjw/big_movers/tree/main/collected_stocks

```
Unnamed: 0,DateTime,Open,High,Low,Close,Volume
0.0,2000-01-04,0.9665,0.9877,0.9035,0.9152,512377600
```

Note: date column is `DateTime` (not `Date`). The server handles this automatically.

### big_movers_result.csv
```
year,symbol,gain_pct,low_date,high_date,low_price,high_price,avg_vol_b
2000,SCON,2472.64,2000-01-03,2000-02-29,...
```

---

## API Endpoints

| Route           | Method   | Query Params  | Description                             |
|-----------------|----------|---------------|-----------------------------------------|
| `/`             | GET      | —             | Serves `Big_movers.html`                |
| `/api/results`  | GET      | —             | Returns `big_movers_result.csv` as JSON |
| `/api/ohlcv`    | GET      | `symbol=AAPL` | Returns OHLCV candlestick data          |
| `/api/spy`      | GET      | —             | Returns SPY benchmark data              |
| `/api/drawings` | GET/POST | `symbol=AAPL` | Read/write per-symbol drawing JSON      |
| `/api/symbols`  | GET      | —             | Lists all tickers with CSV files        |

---

## Dashboard Features

### Left Panel — Ticker List
- **Search** by symbol name
- **Year filter** — dropdown auto-populated from data (2000–2026)
- **Gain range filter:**
  - All Gains
  - 100% – 200%
  - 200% – 500%
  - 500% – 1000%
  - Above 1000%
  - Boundary rule: exactly 200% falls in the 100–200% bucket (upper-inclusive)
- Click any row to load its chart; row shows symbol, year, date range, and gain%

### Right Panel — Chart
- **Candlestick** chart with volume histogram
- **Timeframes:** Daily (D), Weekly (W), Monthly (M)
- **Moving Averages:** EMA 20 (orange), EMA 50 (blue), SMA 200 (purple) — toggleable
- **Scale:** Logarithmic / Linear toggle
- **Fit** button — resets zoom to show all data

### Drawing Tools

| Key | Tool            | Behaviour                                              |
|-----|-----------------|--------------------------------------------------------|
| V   | Pan             | Default — drag to scroll the chart                     |
| H   | H-Line          | Single click → yellow dashed horizontal price line     |
| R   | Ray             | Two clicks → line from point 1, extending to the right |
| S   | Segment         | Two clicks → fixed line between two points             |
| Esc | Cancel          | Cancels a pending 2-point drawing mid-way              |

- After placing any drawing the tool reverts to **Pan**
- **Clear** button removes all drawings from the current chart
- Drawings are cleared automatically when switching to a different ticker

---

## Known Bugs Fixed This Session

| Bug | Fix |
|-----|-----|
| EMA 20 / EMA 50 not rendering | `calcEMA` used `result.length` as loop guard (deadlock). Fixed to use index counter `i >= period - 1` |
| Drawing tools did nothing | No click handler existed. Added `chart.subscribeClick()`, SVG overlay for segments/rays, and `candleSeries.createPriceLine()` for H-lines |

---

## Data Notes

- 929 tickers sourced from the reference GitHub repo (data back to 2000, includes delisted stocks)
- 1,495 big mover entries across 2000–2026
- `SPY Historical Data.csv` loaded for benchmark reference
- `drawings/` is created automatically on first save
- To add more tickers: drop `<TICKER>.csv` into `collected_stocks/` with columns `DateTime,Open,High,Low,Close,Volume`
