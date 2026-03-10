
import sqlite3
import re
import os
import random

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
    return " ".join(lines[:2])







_MACRO_PATTERNS = {
    "document": re.compile(r'\{=Document:(\w+)\}'),
    "variable": re.compile(r'\{=Variable:(\w+)\}'),
    "constant": re.compile(r'\{=Constant:(\w+)\}'),
    "global_var": re.compile(r'\{=GlobalVar:(\w+)\}'),
    "activity": re.compile(r'\{=([A-Za-z0-9_]{8,}):(\w+)\}'),
}

def detect_macros(text: str) -> dict:
    
    found = {}
    for kind, pattern in _MACRO_PATTERNS.items():
        matches = pattern.findall(text)
        if matches:
            
            if kind == "activity":
                codes = [m[1] for m in matches]
            else:
                codes = list(matches)
            
            seen = []
            for c in codes:
                if c not in seen:
                    seen.append(c)
            found[kind] = seen
    return found

def macro_suffix(macros: dict) -> str:
    
    parts = []

    if "document" in macros:
        codes = macros["document"][:2]
        names = ", ".join(f"«{c}»" for c in codes)
        parts.append(f"используя поле документа {names}")

    if "variable" in macros:
        codes = macros["variable"][:2]
        names = ", ".join(f"«{c}»" for c in codes)
        parts.append(f"через переменную {names}")

    if "constant" in macros:
        codes = macros["constant"][:2]
        names = ", ".join(f"«{c}»" for c in codes)
        parts.append(f"из константы {names}")

    if "globalvar" in macros:
        codes = macros["globalvar"][:2]
        names = ", ".join(f"«{c}»" for c in codes)
        parts.append(f"на основе глобальной переменной {names}")

    if "activity" in macros and not any(k in macros for k in ("document","variable","constant","globalvar")):
        parts.append("используя результат предыдущего действия")

    return (", " + "; ".join(parts)) if parts else ""






def parse_condition(props: str) -> tuple:
    m = re.search(r'propertyvariablecondition:\s*\n((?:[ \t]+.+\n?)*)', props, re.MULTILINE)
    if not m:
        return ("", "", "")
    block = m.group(1)
    lines = block.splitlines()
    outer_indent = None
    for line in lines:
        if re.match(r'^\d+:$', line.strip()):
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
            data.setdefault(pair.group(1), pair.group(2).strip())
    return (data.get("0",""), data.get("1","="), data.get("2",""))


def infer_activity_type(props: str) -> str:
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






def generate_prompt(activity_type: str, props: str, macros: dict) -> str:
    
    op_map = {"=": "равно", "!=": "не равно", ">": "больше", "<": "меньше"}
    base = ""

    if activity_type == "Task2Activity":
        title  = get_value(props, "TITLE")
        hold   = get_value(props, "HoldToClose")
        block  = "не закрывать процесс до выполнения задачи" if hold == "Y" else ""
        base   = f"Поставь задачу «{title}»" if title else "Поставь задачу"
        if block:
            base += f" ({block})"

    elif activity_type == "RequestInformationActivity":
        name   = get_value(props, "Name")
        desc   = get_value(props, "Description")
        base   = "Запроси у пользователя дополнительную информацию"
        if name:
            base += f": «{name}»"
        if desc:
            base += f". {desc[:60]}"

    elif activity_type == "SetVariableActivity":
        pairs = re.findall(r'^\s{8,}(\w+):\s*(.+)', props, re.MULTILINE)
        if pairs:
            var_name, val = pairs[0]
            val_clean = val.strip()
            base = f"Установи переменную «{var_name}» в значение «{val_clean[:50]}»"
        else:
            base = "Измени значение переменной бизнес-процесса"

    elif activity_type == "IfElseBranchActivity":
        var, op, val = parse_condition(props)
        if var:
            base = f"Добавь ветку условия: если «{var}» {op_map.get(op, op)} «{val}»"
        else:
            title = get_value(props, "Title")
            base  = f"Добавь ветку «иначе» (else){': ' + title if title else ''}"

    elif activity_type == "WhileActivity":
        var, op, val = parse_condition(props)
        title = get_value(props, "Title")
        if var:
            base = f"Повторяй блок «{title}» в цикле, пока «{var}» {op_map.get(op, op)} «{val}»"
        else:
            base = "Добавь цикл While с условием на переменную"

    elif activity_type == "SequenceActivity":
        title = get_value(props, "Title")
        base  = f"Добавь блок последовательных действий{': «' + title + '»' if title else ''}"

    elif activity_type == "DiskAddFolderActivity":
        name = get_value(props, "FolderName")
        base = f"Создай папку на Диске{' «' + name + '»' if name else ''}"

    elif activity_type == "IMNotifyActivity":
        msg   = get_value(props, "Message")
        users = get_value(props, "Users")
        base  = "Отправь уведомление в чат"
        if users:
            base += f" пользователю {users}"
        if msg:
            base += f": «{msg[:60]}»"

    elif activity_type == "SetFieldActivity":
        field = get_value(props, "FieldId")
        val   = get_value(props, "Value")
        base  = f"Установи поле «{field}» документа в значение «{val}»"

    elif activity_type == "DelayActivity":
        delay = get_value(props, "Delay")
        base  = f"Добавь задержку на {delay}" if delay else "Добавь паузу в бизнес-процессе"

    elif activity_type == "ApproveActivity":
        title = get_value(props, "Title")
        base  = f"Добавь шаг согласования «{title}»" if title                else "Добавь шаг согласования документа"

    elif activity_type == "SetStateTitleActivity":
        title = get_value(props, "StatusTitle")
        base  = f"Установи статус процесса: «{title}»" if title                else "Измени статус бизнес-процесса"

    elif activity_type == "LogActivity":
        msg  = get_value(props, "LogMessage")
        base = f"Запиши в лог: «{msg[:60]}»" if msg               else "Добавь запись в журнал бизнес-процесса"

    elif activity_type == "SetPermissionsActivity":
        base = "Настрой права доступа к документу для участников процесса"

    else:
        title = get_value(props, "Title")
        base  = f"Выполни действие{': «' + title + '»' if title else ''}"

    
    return base + macro_suffix(macros)






def main():
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    rows = cursor.execute("""
        SELECT id, completion_json, source_file
        FROM training_dataset
        WHERE user_prompt IS NULL OR user_prompt = ''
    """).fetchall()

    if not rows:
        print("✅ Все записи уже размечены!")
        conn.close()
        return

    updated_with_macros = []   

    for row_id, props, source_file in rows:
        macros      = detect_macros(props)
        act_type    = infer_activity_type(props)
        prompt      = generate_prompt(act_type, props, macros)

        cursor.execute(
            "UPDATE training_dataset SET user_prompt = ? WHERE id = ?",
            (prompt, row_id)
        )

        has_macro_suffix = bool(macros)
        updated_with_macros.append((row_id, act_type, macros, prompt, has_macro_suffix))

    conn.commit()

    total        = len(rows)
    with_macros  = sum(1 for r in updated_with_macros if r[4])
    print(f"\n✅ Размечено записей      : {total}")
    print(f"   Из них с макросами     : {with_macros}  ({with_macros*100//total}%)")

    
    macro_rows = [r for r in updated_with_macros if r[4]]
    sample     = random.sample(macro_rows, min(5, len(macro_rows)))

    print()
    print("─" * 110)
    print("  5 случайных записей с применением синтаксических правил маппинга:")
    print("─" * 110)
    for rid, atype, macros, prompt, _ in sample:
        macro_types = ", ".join(
             f"{k}({len(v)})" for k, v in macros.items()
        )
        print(f"\n  ID         : {rid}")
        print(f"  Тип        : {atype}")
        print(f"  Макросы    : {macro_types}")
        print(f"  user_prompt: {prompt}")
    print("\n" + "─" * 110)

    conn.close()


if __name__ == "__main__":
    main()
