import json
import os
from datetime import datetime

HISTORY_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'history.json')

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, 'r') as f:
        return json.load(f)

def save_to_history(question, sql, row_count):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    history = load_history()
    history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question": question,
        "sql": sql,
        "rows": row_count
    })
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history[-50:], f, indent=2)  # keep last 50