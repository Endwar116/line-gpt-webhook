import os
import json

DATA_DIR = "user_memory"
os.makedirs(DATA_DIR, exist_ok=True)

def get_user_filepath(user_id):
    return os.path.join(DATA_DIR, f"{user_id}.json")

def save_user_message(user_id, message):
    filepath = get_user_filepath(user_id)
    history = []

    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            history = json.load(f)

    history.append(message)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def get_user_history(user_id):
    filepath = get_user_filepath(user_id)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []