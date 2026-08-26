<div align="center">

# 💸 GCash Spend Tracker

**Local macOS iMessage parser and spend dashboard**

[![Python](https://img.shields.io/badge/Python%203.9+-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![SQLite](https://img.shields.io/badge/SQLite3-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org)
[![macOS](https://img.shields.io/badge/macOS-000000?logo=apple&logoColor=white)](https://www.apple.com/macos)
[![HTML5](https://img.shields.io/badge/Dashboard-HTML5-E34F26?logo=html5&logoColor=white)](tracker.html)

</div>

GCash Spend Tracker automatically parses transaction SMS messages directly from your Mac's native iMessage database (`chat.db`) and presents expenditures, receipts, and category breakdowns on an offline, local-first web dashboard.

All parsing and data storage stay entirely on your Mac.

---

## Why it exists: payment alerts stay trapped in SMS

GCash sends real-time SMS receipts for payments, bank transfers, cash-ins, and cash-outs—but transaction histories in SMS are unorganized text messages. Calculating monthly totals or analyzing spending patterns manually requires line-by-line inspection. 

This pipeline reads your local iMessage SQLite database (`chat.db`), extracts financial transactions with regular expressions, writes structured ledger entries, and serves an interactive spending dashboard locally on port 8901.

| Problem | Solution | Result |
|---|---|---|
| GCash receipts are plain SMS prose | Deterministic Python regex engine extracts payment amounts, reference numbers, and merchant names | Structured JSON transaction ledger |
| Manual tracking exposes personal financial data to cloud tools | Local-first pipeline runs offline directly on macOS `chat.db` | 100% privacy-preserved transaction storage |
| Unstructured text makes spending analysis difficult | Local single-page web application visualizes transaction metrics | Real-time interactive spend dashboard |

## Architecture

```
┌───────────────────────────┐    ┌───────────────────────────┐    ┌──────────────────┐
│  macOS iMessage Storage   │───▶│  capture.py               │───▶│  ledger.json     │
│  (~/Library/Messages)     │    │  (SQLite3 + Regular Exp.) │    │  (Local Store)   │
└───────────────────────────┘    └───────────────────────────┘    └──────────────────┘
                                                                           │
                                                                           ▼
┌───────────────────────────┐    ┌───────────────────────────┐    ┌──────────────────┐
│  Browser Dashboard        │◀───│  Python http.server       │◀───│  tracker.html    │
│  (http://127.0.0.1:8901)  │    │  (tracker.sh daemon)      │    │  (Single Page)   │
└───────────────────────────┘    └───────────────────────────┘    └──────────────────┘
```

Pipeline stages:

1. **Capture** - `capture.py` connects to `~/Library/Messages/chat.db`, scans for incoming SMS messages from GCash handles, and parses transaction fields (amounts, recipients/merchants, reference numbers, dates).
2. **Persist** - Deduplicated transactions are appended to `ledger.json` next to the application code.
3. **Serve & Visualize** - `tracker.sh` manages background capture polling and runs a local `http.server` hosting `tracker.html` for real-time dashboard analytics.

## Features

- **Automated SMS Extraction**: Reads transaction texts directly from `chat.db` without export steps.
- **Pattern Matching Engine**: Tolerates changing GCash SMS structures across different years and transaction types (Payments, Bank Transfers, Received Funds, Express Send).
- **Background Daemon**: `tracker.sh` controls background capture loops and the web server via simple commands (`start`, `stop`).
- **Privacy First**: Zero network outbound requests. No external APIs or cloud services needed.

## Quick Start

### 1. Enable Full Disk Access
macOS protects `~/Library/Messages/chat.db`. Grant **Full Disk Access** to Terminal (or Python) under:
`System Settings > Privacy & Security > Full Disk Access`

### 2. Run the Tracker
Start the background capture loop and local web server:

```bash
./tracker.sh start
```

### 3. Open the Dashboard
Visit `http://127.0.0.1:8901/tracker.html` in your browser.

### 4. Stop the Daemon
To stop all background processes:

```bash
./tracker.sh stop
```

## Repository Structure

```
.
├── capture.py      # iMessage SQLite query & regex extraction engine
├── ledger.json     # Local store containing parsed transactions
├── tracker.html    # Web dashboard interface
└── tracker.sh      # Service daemon manager script
```

## License

MIT License.
