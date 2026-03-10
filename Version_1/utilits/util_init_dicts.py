import sqlite3, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(os.path.join(BASE_DIR, "..", "src", "bitrix_ai_dataset.db"))
cursor = conn.cursor()

# Создаем таблицу, если ее еще нет
cursor.execute("""
CREATE TABLE IF NOT EXISTS syntax_dictionary (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    human_concept  TEXT,
    bitrix_syntax  TEXT,
    description    TEXT
)
""")

# Инициализируем базовыми правилами, если таблица пуста
if cursor.execute("SELECT COUNT(*) FROM syntax_dictionary").fetchone()[0] == 0:
    cursor.executemany("""
        INSERT INTO syntax_dictionary (human_concept, bitrix_syntax, description)
        VALUES (?, ?, ?)
    """, [
        (
            "Поле документа",
            "{=Document:FIELD_CODE}",
            "Используется для обращения к стандартным или пользовательским полям текущего документа."
        ),
        (
            "Переменная процесса",
            "{=Variable:VAR_CODE}",
            "Обращение к локальным переменным, созданным внутри конкретного шаблона бизнес-процесса."
        ),
        (
            "Константа процесса",
            "{=Constant:CONST_CODE}",
            "Используется для доступа к неизменяемым параметрам шаблона (константам)."
        ),
        (
            "Глобальная переменная",
            "{=GlobalVar:GVAR_CODE}",
            "Доступ к переменным, общим для всех бизнес-процессов в системе."
        ),
        (
            "Результат действия",
            "{=A12345_67890:PROPERTY_CODE}",
            "Получение выходного параметра (return property) от другого действия в этом же процессе."
        ),
    ])
    print(f"✅ Вставлено {cursor.rowcount} базовых концептов в словарь.")

conn.commit()

# Отображаем содержимое
rows = conn.execute("SELECT id, human_concept, bitrix_syntax, description FROM syntax_dictionary").fetchall()
conn.close()

col = [3, 25, 30, 60]
sep = "| " + " | ".join("-" * w for w in col) + " |"
hdr = f"| {'id':<{col[0]}} | {'human_concept':<{col[1]}} | {'bitrix_syntax':<{col[2]}} | {'description':<{col[3]}} |"

print()
print(hdr)
print(sep)
for rid, concept, syntax, desc in rows:
    desc_s = desc[:col[3]] + ("…" if len(desc) > col[3] else "")
    print(f"| {rid:<{col[0]}} | {concept:<{col[1]}} | {syntax:<{col[2]}} | {desc_s:<{col[3]}} |")

print(f"\n✅ Таблица syntax_dictionary: {len(rows)} записей")
