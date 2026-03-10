import os
import re
import sqlite3

def is_valid_key(key: str) -> bool:
    
    if not key or key.isdigit() or ' ' in key: return False
    if re.search(r'[а-яА-ЯёЁ]', key) or re.match(r'^\d+\.', key): return False
    if len(key) > 40 or not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', key): return False
    return True

def parse_user_dumps():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dumps_dir = os.path.join(script_dir, "..", "data", "user_bp_dumps")
    db_path = os.path.join(script_dir, "..", "data", "dataset_v2.db")

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    
    c.execute("SELECT code FROM activities")
    known_activities = {row[0].lower() for row in c.fetchall()}

    
    try:
        c.execute("ALTER TABLE properties ADD COLUMN source TEXT DEFAULT 'core'")
    except sqlite3.OperationalError:
        pass

    added_count = 0

    for filename in os.listdir(dumps_dir):
        if not filename.endswith('.txt'):
            continue

        filepath = os.path.join(dumps_dir, filename)
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        
        activities = re.findall(
            r'([A-Za-z0-9_]+Activity)\s*:\s*\n((?:\s+.*\n?)*)',
            content, 
            re.DOTALL | re.MULTILINE
        )

        for act_type, props_block in activities:
            act_code = act_type.lower()
            
            
            if act_code not in known_activities:
                continue

            
            for line in props_block.splitlines():
                if not line.strip() or ':' not in line:
                    continue
                
                key = line.strip().split(':')[0].strip()
                if not is_valid_key(key) or key.lower() in ['title', 'name']:
                    continue
                
                
                c.execute("SELECT 1 FROM properties WHERE activity_code = ? AND name = ? AND is_return = 0", (act_code, key))
                if not c.fetchone():
                    c.execute(
                        "INSERT INTO properties (activity_code, name, type, is_return, source) VALUES (?, ?, 'string', 0, 'user_dump')", 
                        (act_code, key)
                    )
                    added_count += 1

    conn.commit()
    conn.close()
    print(f"Готово! Из пользовательских txt-файлов извлечено и добавлено входящих свойств: {added_count}")

if __name__ == "__main__":
    parse_user_dumps()