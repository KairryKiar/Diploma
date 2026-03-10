import sqlite3, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(os.path.join(BASE_DIR, "bitrix_ai_dataset.db"))

row = conn.execute("SELECT id, completion_json, source_file FROM training_dataset WHERE id=4").fetchone()
conn.close()

print(f"=== ID={row[0]} | source: {row[2]} ===\n")
print(row[1])
