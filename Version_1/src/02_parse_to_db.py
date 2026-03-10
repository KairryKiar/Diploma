import sqlite3
import re
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "bitrix_ai_dataset.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "arch.sql")


def setup_db():
    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    
    
    cursor = conn.cursor()
    cursor.execute("DELETE FROM training_dataset")
    
    
    
    
    conn.commit()
    return conn


def is_valid_key(key: str) -> bool:
    
    if not key:
        return False
    
    if key.isdigit():
        return False
    
    if ' ' in key:
        return False
    
    if re.search(r'[а-яА-ЯёЁ]', key):
        return False
    
    if re.match(r'^\d+\.', key):
        return False
    
    if len(key) > 40:
        return False
    
    if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', key):
        return False
    return True


def extract_param_paths(props_text: str) -> list:
    
    paths = []
    stack = []  

    for line in props_text.splitlines():
        
        if not line.strip():
            continue
        
        if ':' not in line:
            continue

        indent = len(line) - len(line.lstrip())
        key = line.strip().split(':')[0].strip()

        if not is_valid_key(key):
            continue

        
        while stack and stack[-1][0] >= indent:
            stack.pop()

        stack.append((indent, key))

        
        full_path = '.'.join(item[1] for item in stack)
        paths.append(full_path)

    return list(set(paths))


def parse_bp_files(file_list):
    conn = setup_db()
    cursor = conn.cursor()

    for file_path in file_list:
        full_path = os.path.join(BASE_DIR, file_path)
        if not os.path.exists(full_path):
            print(f"⚠️ Файл не найден: {full_path}")
            continue

        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()

        
        
        
        activities = re.findall(
            r'([A-Za-z0-9_]+Activity)\s*:\s*\n((?:\s+.*\n?)*)',
            content, 
            re.DOTALL | re.MULTILINE
        )

        added = 0

        for act_type, props_block in activities:
            added += 1

            cursor.execute(
                "INSERT OR IGNORE INTO activities_catalog (bitrix_code) VALUES (?)",
                (act_type,)
            )
            cursor.execute(
                "SELECT id FROM activities_catalog WHERE bitrix_code = ?",
                (act_type,)
            )
            act_id = cursor.fetchone()[0]

            param_paths = extract_param_paths(props_block)
            for path in param_paths:
                cursor.execute(
                    "INSERT OR IGNORE INTO activity_params (activity_id, param_key) VALUES (?, ?)",
                    (act_id, path)
                )

            cursor.execute(
                "INSERT INTO training_dataset (completion_json, source_file) VALUES (?, ?)",
                (props_block.strip(), file_path)
            )

        print(f"  ✅ {file_path}: добавлено {added} полных активностей (мусорные типы больше не мешают)")

    conn.commit()
    conn.close()
    print(f"\n✅ База данных очищена и наполнена! → {DB_PATH}")


if __name__ == "__main__":
    files = [
        "../data/Выдача наличных.txt",
        "../data/Заявление на командировку.txt",
        "../data/Заявление на отпуск.txt",
        "../data/Исходящие документы.txt",
        "../data/Счет на оплату.txt",
        "../data/activities.txt",
        "../data/bp-25.txt",
        "../data/Other.txt",
    ]
    parse_bp_files(files)