import os
import re
import sqlite3

def get_array_content(text, start_idx):
    idx = start_idx
    while idx < len(text) and text[idx] not in "([":
        idx += 1
    if idx >= len(text): return ""
    
    open_char = text[idx]
    close_char = ')' if open_char == '(' else ']'
    stack = 0
    for i in range(idx, len(text)):
        if text[i] == open_char:
            stack += 1
        elif text[i] == close_char:
            stack -= 1
            if stack == 0:
                return text[idx+1:i]
    return ""

def read_file(path):
    with open(path, 'rb') as f:
        raw = f.read()
        try:
            return raw.decode('utf-8')
        except UnicodeDecodeError:
            return raw.decode('windows-1251', errors='ignore')

def extract_metadata():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(script_dir, "..", "data", "bitrix")
    db_path = os.path.join(script_dir, "..", "data", "dataset_v2.db")
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS activities (code TEXT UNIQUE, name TEXT, category TEXT)")
    # Учитываем, что мы добавили id и source ранее
    c.execute("""
    CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        activity_code TEXT, 
        name TEXT, 
        type TEXT, 
        is_return INTEGER,
        source TEXT DEFAULT 'core'
    )
    """)
    c.execute("DELETE FROM activities")
    c.execute("DELETE FROM properties")
    
    for root, dirs, files in os.walk(base_dir):
        if '.description.php' in files:
            act_code = os.path.basename(root)
            if act_code in ['ru', 'en', 'de', 'kz', 'lang', 'la', 'br', 'fr', 'pl', 'ua', 'activities']:
                continue
                
            main_php = os.path.join(root, '.description.php')
            content = read_file(main_php)
            
            ru_path = os.path.join(root, 'lang', 'ru', '.description.php')
            if not os.path.exists(ru_path):
                ru_path = os.path.join(root, 'ru', '.description.php')
                
            ru_dict = {}
            if os.path.exists(ru_path):
                ru_content = read_file(ru_path)
                for match in re.finditer(r"\$MESS\s*\[\s*['\"](.*?)['\"]\s*\]\s*=\s*(['\"])(.*?)\2", ru_content):
                    ru_dict[match.group(1)] = match.group(3)
            
            cat_match = re.search(r"['\"]CATEGORY['\"]\s*=>", content, re.I)
            category = ""
            if cat_match:
                cat_content = get_array_content(content, cat_match.end())
                id_match = re.search(r"['\"]ID['\"]\s*=>\s*['\"](.*?)['\"]", cat_content, re.I)
                if id_match:
                    category = id_match.group(1)
            
            name_match = re.search(r"['\"]NAME['\"]\s*=>\s*(?:.*?getMessage\(['\"](.*?)['\"]|GetMessage\(['\"](.*?)['\"]\)|['\"](.*?)['\"])", content, re.I | re.DOTALL)
            name_key = ""
            if name_match:
                name_key = next((g for g in name_match.groups() if g), "")
            
            name = ru_dict.get(name_key, name_key)
            if not name:
                name = act_code
            
            c.execute("INSERT INTO activities (code, name, category) VALUES (?, ?, ?)", (act_code, name, category))
            
            # --- ИСХОДЯЩИЕ ПАРАМЕТРЫ (is_return = 1) ---
            ret_match = re.search(r"['\"]RETURN['\"]\s*=>", content, re.I)
            if ret_match:
                ret_content = get_array_content(content, ret_match.end())
                for prop_match in re.finditer(r"['\"]([a-zA-Z0-9_]+)['\"]\s*=>", ret_content):
                    prop_name = prop_match.group(1)
                    prop_body = get_array_content(ret_content, prop_match.end())
                    type_match = re.search(r"['\"]TYPE['\"]\s*=>\s*['\"](.*?)['\"]", prop_body, re.I)
                    prop_type = type_match.group(1) if type_match else "string"
                    
                    if prop_body.strip():
                        c.execute("INSERT INTO properties (activity_code, name, type, is_return, source) VALUES (?, ?, ?, 1, 'core')", (act_code, prop_name, prop_type))
            
            # --- ВХОДЯЩИЕ ПАРАМЕТРЫ (is_return = 0) ИЗ ЯДРА ---
            # Пытаемся найти класс самого активити:
            activity_php = os.path.join(root, f"{act_code}.php")
            if os.path.exists(activity_php):
                act_content = read_file(activity_php)
                prop_keys = []
                
                # Способ 1: Ищем определение $this->arProperties
                match = re.search(r"\$this->arProperties\s*=", act_content)
                if match:
                    arr_content = get_array_content(act_content, match.end())
                    prop_keys = re.findall(r"['\"]([a-zA-Z0-9_]+)['\"]\s*=>", arr_content)
                else:
                    # Способ 2: Ищем функцию getPropertiesMap
                    match2 = re.search(r"function\s+getPropertiesMap\s*\(", act_content, re.I)
                    if match2:
                        ret_match = re.search(r"return\s+", act_content[match2.end():])
                        if ret_match:
                            arr_content = get_array_content(act_content, match2.end() + ret_match.end())
                            # Ищем ключи первого уровня
                            prop_keys = re.findall(r"^\s*['\"]([a-zA-Z0-9_]+)['\"]\s*=>", arr_content, re.MULTILINE)
                
                # Добавляем найденные входящие настройки
                for k in prop_keys:
                    k_clean = k.strip()
                    if k_clean and k_clean.lower() not in ('title', 'name'):
                        c.execute("SELECT 1 FROM properties WHERE activity_code=? AND name=? AND is_return=0", (act_code, k_clean))
                        if not c.fetchone():
                            c.execute("INSERT INTO properties (activity_code, name, type, is_return, source) VALUES (?, ?, 'string', 0, 'core')", (act_code, k_clean))

    conn.commit()
    conn.close()
    print(f"Extraction complete. DB saved to: {os.path.abspath(db_path)}")

if __name__ == "__main__":
    extract_metadata()