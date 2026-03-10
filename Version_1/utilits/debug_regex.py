import sqlite3, re, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
conn = sqlite3.connect(os.path.join(BASE_DIR, "bitrix_ai_dataset.db"))
row = conn.execute("SELECT completion_json FROM training_dataset WHERE id=3").fetchone()
conn.close()

props = row[0]


m = re.search(r'propertyvariablecondition:\s*\n((?:[ \t]+.+\n?)*)', props, re.MULTILINE)
if m:
    block = m.group(1)
    print("=== RAW BLOCK (каждый символ показан) ===")
    for i, line in enumerate(block.splitlines()):
        
        spaces = len(line) - len(line.lstrip())
        print(f"  [{i}] spaces={spaces:2d} | repr: {repr(line)}")
