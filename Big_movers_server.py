import os
import csv
import json
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STOCKS_DIR = os.path.join(BASE_DIR, "collected_stocks")
RESULTS_CSV = os.path.join(BASE_DIR, "big_movers_result.csv")
SPY_CSV = os.path.join(BASE_DIR, "SPY Historical Data.csv")

# Vercel's filesystem is read-only except /tmp; use /tmp for drawings there
ON_VERCEL = bool(os.environ.get("VERCEL"))
DRAWINGS_DIR = "/tmp/drawings" if ON_VERCEL else os.path.join(BASE_DIR, "drawings")

app = Flask(__name__, static_folder=BASE_DIR)

# ── Ensure writable directories exist ────────────────────────────────────────

os.makedirs(DRAWINGS_DIR, exist_ok=True)
if not ON_VERCEL:
    os.makedirs(STOCKS_DIR, exist_ok=True)


# ── Helper: parse a CSV into a list of dicts ──────────────────────────────────

def parse_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({k.strip(): v.strip() for k, v in row.items()})
    return rows


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "Big_movers.html")


@app.route("/api/results")
def api_results():
    """Return the big movers result list as JSON."""
    if not os.path.exists(RESULTS_CSV):
        return jsonify([])
    try:
        rows = parse_csv(RESULTS_CSV)
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/ohlcv")
def api_ohlcv():
    """Return OHLCV candlestick data for a symbol."""
    symbol = request.args.get("symbol", "").upper().strip()
    if not symbol:
        return jsonify({"error": "symbol parameter required"}), 400

    csv_path = os.path.join(STOCKS_DIR, f"{symbol}.csv")
    if not os.path.exists(csv_path):
        return jsonify({"error": f"No data found for {symbol}"}), 404

    try:
        rows = parse_csv(csv_path)
        candles = []
        for row in rows:
            # Real data uses 'DateTime'; also support 'Date'/'date' fallbacks
            date = row.get("DateTime") or row.get("Date") or row.get("date") or ""
            try:
                candles.append({
                    "time": date,
                    "open": float(row.get("Open") or row.get("open") or 0),
                    "high": float(row.get("High") or row.get("high") or 0),
                    "low": float(row.get("Low") or row.get("low") or 0),
                    "close": float(row.get("Close") or row.get("close") or 0),
                    "volume": float(row.get("Volume") or row.get("volume") or 0),
                })
            except (ValueError, TypeError):
                continue
        # Sort ascending by date
        candles.sort(key=lambda x: x["time"])
        return jsonify(candles)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/spy")
def api_spy():
    """Return SPY OHLCV data for benchmark overlay."""
    if not os.path.exists(SPY_CSV):
        return jsonify([])
    try:
        rows = parse_csv(SPY_CSV)
        candles = []
        for row in rows:
            date = row.get("DateTime") or row.get("Date") or row.get("date") or ""
            try:
                candles.append({
                    "time": date,
                    "open": float(row.get("Open") or row.get("open") or 0),
                    "high": float(row.get("High") or row.get("high") or 0),
                    "low": float(row.get("Low") or row.get("low") or 0),
                    "close": float(row.get("Close") or row.get("close") or 0),
                    "volume": float(row.get("Volume") or row.get("volume") or 0),
                })
            except (ValueError, TypeError):
                continue
        candles.sort(key=lambda x: x["time"])
        return jsonify(candles)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/drawings", methods=["GET", "POST"])
def api_drawings():
    """Get or save drawing annotations for a symbol."""
    symbol = request.args.get("symbol", "").upper().strip()
    if not symbol:
        return jsonify({"error": "symbol parameter required"}), 400

    drawing_path = os.path.join(DRAWINGS_DIR, f"{symbol}.json")

    if request.method == "GET":
        if not os.path.exists(drawing_path):
            return jsonify([])
        with open(drawing_path, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))

    # POST — save drawings
    try:
        data = request.get_json(force=True)
        with open(drawing_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/symbols")
def api_symbols():
    """Return list of all available ticker symbols (CSV files present)."""
    symbols = []
    if os.path.exists(STOCKS_DIR):
        for fname in sorted(os.listdir(STOCKS_DIR)):
            if fname.endswith(".csv"):
                symbols.append(fname[:-4].upper())
    return jsonify(symbols)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Big Movers server starting at http://127.0.0.1:5051")
    print(f"  Stock data dir : {STOCKS_DIR}")
    print(f"  Results CSV    : {RESULTS_CSV}")
    app.run(host="127.0.0.1", port=5051, debug=True)
