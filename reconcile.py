#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json
from datetime import datetime

total = 0.0
count = 0

# Pass 1: keep only the latest attempt for each txn_id + skip problematic lines (unreadable and missing id)
latest = {}

with open("payments.jsonl") as f:
    for line in f:
        try:
            # Check whether payment is unreadable 
            event = json.loads(line)
            # Check whether it doesn't have a txn_id
            if "txn_id" not in event:
                continue
        except json.JSONDecodeError:
            continue    
    
        # Track only latest attempts for each txn_id
        curr_txn_id = event["txn_id"]
        event.pop("txn_id")
        
        # Check if txn_id is new then add to latest dict
        if curr_txn_id not in latest:
            latest[curr_txn_id] = event
        # Check if txn_id exists then compare both records to track the latest one
        else:
            curr_ts = datetime.fromisoformat(event["ts"])
            prev_ts = datetime.fromisoformat(latest[curr_txn_id]["ts"])
            
            if (curr_ts > prev_ts):
                latest[curr_txn_id] = event

# Pass 2: calculate the total collected money from processed records
for event in latest.values():        
    if event["status"] == "success":
        # Safely convert amount from str/float to float
        amount = float(event["amount"].replace(",","")) if isinstance(event["amount"], str) else event["amount"]
        total += amount
        count += 1

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
