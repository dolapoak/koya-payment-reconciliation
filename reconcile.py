#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

latest_by_txn = {}

with open("payments.jsonl", encoding="utf-8") as f:
    for line in f:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        txn_id = event.get("txn_id")
        if not txn_id:
            continue

        timestamp = datetime.fromisoformat(event["ts"].replace("Z", "+00:00"))
        previous = latest_by_txn.get(txn_id)
        # On equal timestamps, keep the later event in the export.
        if previous is None or timestamp >= previous[0]:
            latest_by_txn[txn_id] = (timestamp, event)

successful_events = [
    event for _, event in latest_by_txn.values()
    if event["status"] == "success"
]
count = len(successful_events)
total = sum(
    (Decimal(str(event["amount"]).replace(",", "")) for event in successful_events),
    Decimal(0),
)

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    rounded_total = total.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    print(f"Your code: KOYA-{rounded_total}")
