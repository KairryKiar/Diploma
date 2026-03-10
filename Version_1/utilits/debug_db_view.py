import sqlite3

conn = sqlite3.connect('Diploma/bitrix_ai_dataset.db')

print("=== ПАРАМЕТРЫ Task2Activity ===")
for r in conn.execute("""
    SELECT param_key FROM activity_params 
    WHERE activity_id = (SELECT id FROM activities_catalog WHERE bitrix_code='Task2Activity') 
    ORDER BY param_key
""").fetchall():
    print(f"  {r[0]}")

print("\n=== ПАРАМЕТРЫ RequestInformationActivity ===")
for r in conn.execute("""
    SELECT param_key FROM activity_params 
    WHERE activity_id = (SELECT id FROM activities_catalog WHERE bitrix_code='RequestInformationActivity') 
    ORDER BY param_key
""").fetchall():
    print(f"  {r[0]}")

print("\n=== ВСЕ АКТИВНОСТИ В КАТАЛОГЕ ===")
for r in conn.execute('SELECT bitrix_code FROM activities_catalog ORDER BY bitrix_code').fetchall():
    print(f"  {r[0]}")

print(f"\nВсего записей в training_dataset: {conn.execute('SELECT count(*) FROM training_dataset').fetchone()[0]}")
print(f"Всего параметров в activity_params: {conn.execute('SELECT count(*) FROM activity_params').fetchone()[0]}")

conn.close()
