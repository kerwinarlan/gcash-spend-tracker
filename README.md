# GCash Spend Tracker

A privacy-focused, local-first macOS tool that automatically parses GCash transaction SMS messages from the native iMessage database (`chat.db`) and visualizes spending trends on a local dashboard.

All data remains local to your Mac.

## Features

- **Automated SMS Parsing**: Reads transaction texts directly from macOS iMessage storage (`~/Library/Messages/chat.db`).
- **Support for GCash Formats**: Extracts payments, transfer records, withdrawals, and received funds using regex pattern matching.
- **Local Dashboard**: Single-page visualization served over `127.0.0.1` showing total expenditures, categorized breakdowns, and transaction history.
- **Background Daemon**: Includes a shell daemon service (`tracker.sh`) for periodic background scanning and local serving.

## Requirements

- **macOS** with iMessage / Messages app synced.
- **Full Disk Access** enabled for Terminal (or Python) in `System Settings > Privacy & Security > Full Disk Access` to read `chat.db`.
- **Python 3**.

## Getting Started

### 1. Enable Full Disk Access
Grant **Full Disk Access** to Terminal or the application executing Python.

### 2. Start the Service
To start background capture and the local dashboard server:

```bash
./tracker.sh start
```

### 3. Open the Dashboard
Navigate to the local URL in your browser:
`http://127.0.0.1:8901/tracker.html`

### 4. Stop the Service
To stop the capture daemon and local server:

```bash
./tracker.sh stop
```

## Structure

```
.
├── capture.py      # SQLite iMessage reader & GCash SMS parser
├── tracker.html    # Local frontend web dashboard
├── tracker.sh      # Background process manager
├── ledger.json     # Local store for parsed transaction data
```
