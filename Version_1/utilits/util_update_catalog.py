import sqlite3, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(os.path.join(BASE_DIR, "bitrix_ai_dataset.db"))
cursor = conn.cursor()







updates = [
    
    ("Поставить задачу",                    "Задания",            "Task2Activity"),
    ("Запрос дополнительной информации",    "Задания",            "RequestInformationActivity"),
    ("Ознакомление с документом",           "Задания",            "ReviewActivity"),
    ("Утверждение документа",               "Задания",            "ApproveActivity"),

    
    ("Условие",                             "Конструкции",        "IfElseActivity"),
    ("Ветка условия",                       "Конструкции",        "IfElseBranchActivity"),
    ("Цикл",                                "Конструкции",        "WhileActivity"),
    ("Последовательность действий",         "Конструкции",        "SequenceActivity"),
    ("Последовательный бизнес-процесс",     "Конструкции",        "SequentialWorkflowActivity"),
    ("Прерывание процесса",                 "Конструкции",        "TerminateActivity"),

    
    ("Изменение документа",                 "Обработка документа", "SetFieldActivity"),
    ("Установка прав",                      "Обработка документа", "SetPermissionsActivity"),
    ("Установить статус",                   "Обработка документа", "SetStateTitleActivity"),

    
    ("Изменение переменных",                "Прочее",             "SetVariableActivity"),
    ("Пауза в выполнении",                  "Прочее",             "DelayActivity"),
    ("Выбор сотрудника",                    "Прочее",             "GetUserActivity"),
    ("Запись в отчет",                      "Прочее",             "LogActivity"),
    ("Блок действий",                       "Прочее",             "EmptyBlockActivity"),

    
    ("Сообщение соц. сети",                 "Уведомления",        "IMNotifyActivity"),

    
    ("Создать папку в Диске",               "Диск",               "DiskAddFolderActivity"),
]

for display_name, category, bitrix_code in updates:
    cursor.execute(
        "UPDATE activities_catalog SET display_name = ?, category = ? WHERE bitrix_code = ?",
        (display_name, category, bitrix_code)
    )

conn.commit()


rows = conn.execute("""
    SELECT bitrix_code, display_name, category
    FROM activities_catalog
    ORDER BY category, display_name
""").fetchall()
conn.close()

col = [32, 38, 26]
sep = "| " + " | ".join("-"*w for w in col) + " |"
hdr = f"| {'bitrix_code':<{col[0]}} | {'display_name':<{col[1]}} | {'category':<{col[2]}} |"
print()
print(hdr)
print(sep)
for code, name, cat in rows:
    print(f"| {(code or ''):<{col[0]}} | {(name or 'NULL'):<{col[1]}} | {(cat or 'NULL'):<{col[2]}} |")
print(f"\n✅ Обновлено строк: {len(updates)}")
