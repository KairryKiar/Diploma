import sqlite3
import re
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bitrix_ai_dataset.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id, completion_json, source_file FROM training_dataset")
rows = cursor.fetchall()

suspects = []

for row_id, props, source_file in rows:
    props_str = str(props).strip()
    
    has_title = bool(re.search(r'^\s*Title:', props_str, re.MULTILINE))
    
    lines = props_str.splitlines()
    last_line = lines[-1] if lines else ""
    abrupt_end = bool(re.search(r'^\s*(Type|Name|Description|Default|Required|Multiple|Options|Settings):\s*([a-zA-Z0-9_]*)$', last_line))
    
    if not has_title or abrupt_end:
        suspects.append((row_id, source_file, props_str))

for row_id, source, props in suspects:
    print(f"ID: {row_id} | Источник: {source}")
    print(f"Содержимое:\n{props}")
    print("=" * 60)

print(f"Найдено потенциально обрезанных блоков: {len(suspects)}")

conn.close()