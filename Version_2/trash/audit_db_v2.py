import os
import sqlite3

def check_db():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "data", "dataset_v2.db")
    
    if not os.path.exists(db_path):
        print(f"База данных не найдена по пути: {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM activities")
    act_count = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM properties")
    prop_count = c.fetchone()[0]
    
    print(f"--- Статистика базы dataset_v2 ---")
    print(f"Всего уникальных активити: {act_count}")
    print(f"Извлечено параметров RETURN: {prop_count}")
    
    print("\n--- Пример 3 случайных активити ---")
    c.execute("SELECT code, name, category FROM activities ORDER BY RANDOM() LIMIT 3")
    for row in c.fetchall():
        print(f"[{row[0]}] {row[1]} | Категория: {row[2]}")
        
    conn.close()

if __name__ == "__main__":
    check_db()