import os
import sqlite3
import json

def generate_prompts():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "data", "dataset_v2.db")
    out_path = os.path.join(script_dir, "..", "data", "bitrix_llm_dataset.jsonl")

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("SELECT code, name, category FROM activities")
    activities = c.fetchall()

    with open(out_path, 'w', encoding='utf-8') as f:
        for act in activities:
            code, name, category = act
            
            c.execute("SELECT name, type FROM properties WHERE activity_code = ? AND is_return = 0", (code,))
            inputs = c.fetchall()
            
            c.execute("SELECT name, type FROM properties WHERE activity_code = ? AND is_return = 1", (code,))
            outputs = c.fetchall()

            prompt_text = f"Сгенерируй структуру элемента бизнес-процесса '{name}' (код: {code})."
            
            input_dict = {row[0]: row[1] for row in inputs} if inputs else {}
            output_dict = {row[0]: row[1] for row in outputs} if outputs else {}

            completion_obj = {
                "code": code,
                "name": name,
                "category": category,
                "inputs": input_dict,
                "outputs": output_dict
            }

            dataset_line = {
                "messages": [
                    {"role": "user", "content": prompt_text},
                    {"role": "assistant", "content": json.dumps(completion_obj, ensure_ascii=False)}
                ]
            }
            
            f.write(json.dumps(dataset_line, ensure_ascii=False) + "\n")

    conn.close()
    print(f"Датасет успешно сгенерирован: {os.path.abspath(out_path)}")

if __name__ == "__main__":
    generate_prompts()