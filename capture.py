#!/usr/bin/env python3
"""Capture GCash SMS from the local Messages database.

Reads ~/Library/Messages/chat.db (needs Full Disk Access for the running
process), extracts GCash payment, withdrawal, and received-money messages,
and appends them to ledger.json next to this script. Everything stays on
this Mac.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
LEDGER = BASE / "ledger.json"
MSGDB = Path(os.environ.get("GCASH_MSGDB", str(Path.home() / "Library/Messages" / "chat.db")))
APPLE_EPOCH_OFFSET = 978307200  # seconds from 1970-01-01 to 2001-01-01 (Apple epoch)

RE_OLD = re.compile(
    r"Your payment of P([\d,]+\.\d{2}) to (.+?) has been successfully processed on "
    r"\d{2}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2} [AP]M\. Ref\. No\. (\d+)",
    re.I,
)
RE_NEW = re.compile(
    r"You have paid P([\d,]+\.\d{2}) GCash to (.+?)\s+on "
    r"\d{2}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2} [AP]M[.,]?.*?Ref\. No\.? (\d+)",
    re.I,
)
RE_WITHDRAW = re.compile(
    r"You have successfully withdrawn P([\d,]+\.\d{2}) from your GCash wallet.*?on "
    r"\d{2}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2} [AP]M.*?Ref\. No\.? (\d+)",
    re.I,
)
RE_RECEIVED = re.compile(
    r"You have received P([\d,]+\.\d{2}) from (.+?) on "
    r"\d{2}-\d{2}-\d{4} \d{1,2}:\d{2}(?::\d{2})? [AP]M.*?GCash Ref\. No\.? (\d+)",
    re.I,
)


def load_ledger() -> list[dict]:
    if not LEDGER.exists():
        return []
    return json.loads(LEDGER.read_text())


def read_messages() -> list[tuple[str, int, str]]:
    """Return (text, unix seconds, sender id) for incoming messages.

    Recent messages may store their text in the attributedBody blob instead
    of the text column; decode it when needed.
    """
    if not MSGDB.exists():
        raise FileNotFoundError(
            f"{MSGDB} not found. Open the Messages app once, then make sure "
            "your iPhone forwards SMS to this Mac."
        )
    con = sqlite3.connect(f"file:{MSGDB}?mode=ro", uri=True)
    rows = con.execute(
        "SELECT m.text, m.attributedBody, m.date, h.id FROM message m "
        "LEFT JOIN handle h ON m.handle_id = h.ROWID "
        "WHERE m.is_from_me = 0"
    ).fetchall()
    con.close()
    out = []
    for text, blob, d, sender in rows:
        if not text and blob:
            text = blob.decode("utf-8", errors="ignore")
        if not text:
            continue
        # date is seconds, or nanoseconds on newer macOS, since 2001-01-01
        epoch = d / 1e9 if d > 1e12 else d
        out.append((text, int(epoch) + APPLE_EPOCH_OFFSET, sender or ""))
    return out


KINDS = (
    (RE_OLD, "payment", 1, 3, 2),
    (RE_NEW, "payment", 1, 3, 2),
    (RE_WITHDRAW, "withdraw", 1, 2, None),
    (RE_RECEIVED, "received", 1, 3, 2),
)


def parse_tx(text: str, ts: int, sender: str) -> dict | None:
    for regex, kind, amt_g, ref_g, merch_g in KINDS:
        m = regex.search(text)
        if m:
            return {
                "ref": int(m.group(ref_g)),
                "amt": float(m.group(amt_g).replace(",", "")),
                "merchant": m.group(merch_g).strip() if merch_g else "Cash Out",
                "ts": ts * 1000,
                "kind": kind,
                "source": "sms",
                "from": sender,
            }
    return None


def main() -> int:
    try:
        messages = read_messages()
    except Exception as e:
        print(f"capture failed: {e}", file=sys.stderr)
        return 1
    ledger = load_ledger()
    known = {t["ref"] for t in ledger}
    added = []
    unmatched = 0
    for text, ts, sender in messages:
        if "ref. no" not in text.lower():
            continue
        tx = parse_tx(text, ts, sender)
        if not tx:
            if "tiktok" in text.lower():
                print(f"  !! unmatched TikTok msg {datetime.fromtimestamp(ts)}: {text[:120]}", file=sys.stderr)
            unmatched += 1
            continue
        if tx["ref"] in known:
            continue
        ledger.append(tx)
        known.add(tx["ref"])
        added.append(tx)
    if added:
        ledger.sort(key=lambda t: t["ts"])
        tmp = LEDGER.with_suffix(".tmp")
        tmp.write_text(json.dumps(ledger, indent=2))
        tmp.replace(LEDGER)
    extra = f", {unmatched} skipped (not a supported GCash message)" if unmatched else ""
    print(f"added {len(added)} new, total {len(ledger)}{extra}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
