import sqlite3
import re
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "bitrix_ai_dataset.db")






def get_value(text: str, key: str) -> str:
    
    m = re.search(rf'^\s*{re.escape(key)}:\s*(.+)', text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def get_multiline_value(text: str, key: str) -> str:
    
    m = re.search(rf'^\s*{re.escape(key)}:\s*\n((?:[ \t]+.+\n?)*)', text, re.MULTILINE)
    if not m:
        return ""
    lines = [l.strip() for l in m.group(1).splitlines() if l.strip()]
    return " ".join(lines[:3])


def parse_condition(props: str) -> tuple:
    
    m = re.search(
        r'propertyvariablecondition:\s*\n((?:[ \t]+.+\n?)*)',
        props, re.MULTILINE
    )
    if not m:
        return ("", "", "")

    block = m.group(1)
    lines = block.splitlines()

    
    outer_indent = None
    for line in lines:
        stripped = line.strip()
        if re.match(r'^\d+:$', stripped):        
            outer_indent = len(line) - len(line.lstrip())
            break

    if outer_indent is None:
        return ("", "", "")

    
    data = {}
    for line in lines:
        indent = len(line) - len(line.lstrip())
        if indent <= outer_indent:
            continue
        pair = re.match(r'^[ \t]+(\d+):\s*(\S.*)', line)
        if pair:
            idx, val = pair.group(1), pair.group(2).strip()
            data.setdefault(idx, val)

    var = data.get("0", "")
    op  = data.get("1", "=")
    val = data.get("2", "")
    return (var, op, val)


def infer_activity_type(props: str, source_file: str) -> str:
    
    if re.search(r'^\s*Fields:', props, re.MULTILINE) and       re.search(r'^\s*HoldToClose:', props, re.MULTILINE):
        return "Task2Activity"

    if re.search(r'^\s*RequestedInformation:', props, re.MULTILINE):
        return "RequestInformationActivity"

    if re.search(r'^\s*VariableValue:', props, re.MULTILINE):
        return "SetVariableActivity"

    if re.search(r'^\s*propertyvariablecondition:', props, re.MULTILINE) and       re.search(r'^\s*Title:\s*Условие', props, re.MULTILINE):
        return "IfElseBranchActivity"

    if re.search(r'^\s*propertyvariablecondition:', props, re.MULTILINE):
        return "WhileActivity"

    if re.search(r'^\s*EntityId:', props, re.MULTILINE):
        return "DiskAddFolderActivity"

    if re.search(r'^\s*Message:', props, re.MULTILINE) and       re.search(r'^\s*Users:', props, re.MULTILINE):
        return "IMNotifyActivity"

    if re.search(r'^\s*Users:', props, re.MULTILINE) and       re.search(r'^\s*Name:', props, re.MULTILINE):
        return "RequestInformationActivity"

    if re.search(r'^\s*FieldId:', props, re.MULTILINE):
        return "SetFieldActivity"

    if re.search(r'^\s*Delay:', props, re.MULTILINE):
        return "DelayActivity"

    if re.search(r'^\s*WorkflowStatus:', props, re.MULTILINE):
        return "ApproveActivity"

    if re.search(r'^\s*StatusTitle:', props, re.MULTILINE):
        return "SetStateTitleActivity"

    if re.search(r'^\s*LogMessage:', props, re.MULTILINE):
        return "LogActivity"

    if re.search(r'^\s*Permission:', props, re.MULTILINE):
        return "SetPermissionsActivity"

    
    title_val = get_value(props, "Title")
    if title_val and not re.search(
        r'RequestedInformation|VariableValue|propertyvariablecondition|EntityId|Message|Users|FieldId|Delay|WorkflowStatus|StatusTitle|LogMessage|Permission',
        props, re.MULTILINE
    ):
        return "SequenceActivity"

    return "UnknownActivity"


def generate_prompt(activity_type: str, props: str) -> str:
    

    if activity_type == "Task2Activity":
        title   = get_value(props, "TITLE")
        resp    = get_value(props, "RESPONSIBLE_ID")
        desc    = get_multiline_value(props, "DESCRIPTION")
        hold    = get_value(props, "HoldToClose")
        blocker = "не закрывать процесс до выполнения задачи" if hold == "Y" else "задача без блокировки"

        
        parts = []
        if title:
            parts.append(f"Поставь задачу «{title}»")
        else:
            parts.append("Поставь задачу")
        if resp and resp not in ("user_1", "{=Document:CREATED_BY}"):
            parts.append(f"ответственному: {resp}")
        if desc:
            parts.append(f"с описанием: {desc[:80]}")
        parts.append(f"({blocker})")
        return " ".join(parts)

    if activity_type == "RequestInformationActivity":
        name = get_value(props, "Name")
        desc = get_value(props, "Description")
        
        options = re.findall(r'^\s{12,}(\w[^:]+):\s*\1', props, re.MULTILINE)
        opts_str = ", ".join(options[:3]) if options else ""
        prompt = f"Запроси у пользователя дополнительную информацию"
        if name:
            prompt += f": «{name}»"
        if desc:
            prompt += f". {desc}"
        if opts_str:
            prompt += f" Варианты: {opts_str}."
        return prompt

    if activity_type == "SetVariableActivity":
        
        pairs = re.findall(r'^\s{12,}(\w+):\s*(.+)', props, re.MULTILINE)
        if pairs:
            var_name, val = pairs[0]
            return f"Установи переменную «{var_name}» в значение «{val.strip()}»"
        return "Измени значение переменной бизнес-процесса"

    if activity_type == "IfElseBranchActivity":
        var, op, val = parse_condition(props)
        op_map = {"=": "равно", "!=": "не равно", ">": "больше", "<": "меньше"}
        if var:
            return f"Добавь ветку условия: если «{var}» {op_map.get(op, op)} «{val}»"
        
        title = get_value(props, "Title")
        return f"Добавь ветку «иначе» (else) в условие{': ' + title if title else ''}"

    if activity_type == "WhileActivity":
        var, op, val = parse_condition(props)
        op_map = {"=": "равно", "!=": "не равно", ">": "больше", "<": "меньше"}
        title = get_value(props, "Title")
        if var:
            return f"Повторяй блок «{title}» в цикле, пока «{var}» {op_map.get(op, op)} «{val}»"
        return "Добавь цикл While с условием на переменную"

    if activity_type == "SequenceActivity":
        title = get_value(props, "Title")
        return f"Добавь блок последовательных действий{': «' + title + '»' if title else ''}"

    if activity_type == "DiskAddFolderActivity":
        name   = get_value(props, "FolderName")
        entity = get_value(props, "EntityId")
        prompt = "Создай папку на Диске"
        if name:
            prompt += f" с именем «{name}»"
        if entity:
            prompt += f" (родительский ID: {entity})"
        return prompt

    if activity_type == "IMNotifyActivity":
        msg   = get_value(props, "Message")
        users = get_value(props, "Users")
        prompt = "Отправь уведомление в чат"
        if users:
            prompt += f" пользователю {users}"
        if msg:
            prompt += f": «{msg[:80]}»"
        return prompt

    if activity_type == "SetFieldActivity":
        field = get_value(props, "FieldId")
        val   = get_value(props, "Value")
        return f"Установи поле «{field}» документа в значение «{val}»"

    if activity_type == "DelayActivity":
        delay = get_value(props, "Delay")
        return f"Добавь задержку выполнения процесса на {delay}" if delay               else "Добавь паузу в бизнес-процессе"

    if activity_type == "ApproveActivity":
        title = get_value(props, "Title")
        return f"Добавь шаг согласования «{title}»" if title               else "Добавь шаг согласования документа"

    if activity_type == "SetStateTitleActivity":
        title = get_value(props, "StatusTitle")
        return f"Установи статус процесса: «{title}»" if title               else "Измени заголовок статуса бизнес-процесса"

    if activity_type == "LogActivity":
        msg = get_value(props, "LogMessage")
        return f"Запиши в лог сообщение: «{msg}»" if msg               else "Добавь запись в журнал бизнес-процесса"

    if activity_type == "SetPermissionsActivity":
        return "Настрой права доступа к документу для участников процесса"

    return f"Выполни действие типа {activity_type}"






def print_table(results: list):
    col_w = [4, 32, 70]
    sep    = "| " + " | ".join("-" * w for w in col_w) + " |"
    header = f"| {'ID':<{col_w[0]}} | {'Тип Activity':<{col_w[1]}} | {'Сгенерированный промпт':<{col_w[2]}} |"
    print()
    print(header)
    print(sep)
    for rid, atype, prompt in results:
        atype_s  = atype[:col_w[1]]
        prompt_s = prompt[:col_w[2]] + ("…" if len(prompt) > col_w[2] else "")
        print(f"| {rid:<{col_w[0]}} | {atype_s:<{col_w[1]}} | {prompt_s:<{col_w[2]}} |")
    print()


def main(redo_ids: list = None):
    
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if redo_ids:
        placeholders = ",".join("?" * len(redo_ids))
        rows = cursor.execute(
            f"SELECT id, completion_json, source_file FROM training_dataset WHERE id IN ({placeholders})",
            redo_ids
        ).fetchall()
    else:
        rows = cursor.execute("""
            SELECT id, completion_json, source_file
            FROM training_dataset
            WHERE user_prompt IS NULL OR user_prompt = ''
            LIMIT 10
        """).fetchall()

    if not rows:
        print("✅ Все записи уже размечены!")
        conn.close()
        return

    results = []
    for row_id, props, source_file in rows:
        act_type = infer_activity_type(props, source_file or "")
        prompt   = generate_prompt(act_type, props)

        cursor.execute(
            "UPDATE training_dataset SET user_prompt = ? WHERE id = ?",
            (prompt, row_id)
        )
        results.append((row_id, act_type, prompt))

    conn.commit()
    conn.close()

    print_table(results)
    print(f"✅ Обновлено {len(results)} записей в training_dataset")


if __name__ == "__main__":
    import sys
    
    if "--redo" in sys.argv:
        idx = sys.argv.index("--redo")
        ids = list(map(int, sys.argv[idx + 1:]))
        main(redo_ids=ids)
    else:
        main()
