import os
import zlib

def php_serialize(obj):
    if isinstance(obj, str):
        encoded = obj.encode('utf-8')
        return f's:{len(encoded)}:"{obj}";'.encode('utf-8')
    elif isinstance(obj, bool):
        return f'b:{1 if obj else 0};'.encode('utf-8')
    elif isinstance(obj, int):
        return f'i:{obj};'.encode('utf-8')
    elif isinstance(obj, float):
        return f'd:{obj};'.encode('utf-8')
    elif obj is None:
        return b'N;'
    elif isinstance(obj, list):
        res = [f'a:{len(obj)}:{{'.encode('utf-8')]
        for i, val in enumerate(obj):
            res.append(php_serialize(i))
            res.append(php_serialize(val))
        res.append(b'}')
        return b''.join(res)
    elif isinstance(obj, dict):
        res = [f'a:{len(obj)}:{{'.encode('utf-8')]
        for key, val in obj.items():
            res.append(php_serialize(key))
            res.append(php_serialize(val))
        res.append(b'}')
        return b''.join(res)
    else:
        raise TypeError(f"Unsupported type: {type(obj)}")

def create_test_bpt():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(script_dir, "test_import.bpt")

    template_data = {
        "TEMPLATE": [
            {
                "Type": "SequentialWorkflowActivity",
                "Name": "Template",
                "Properties": {
                    "Title": "Последовательный бизнес-процесс"
                },
                "Children": [
                    {
                        "Type": "LogActivity",
                        "Name": "A1",
                        "Properties": {
                            "Title": "Первый лог",
                            "LogMessage": "Это первый блок",
                            "Parameters": {}
                        }
                    },
                    {
                        "Type": "LogActivity",
                        "Name": "A2",
                        "Properties": {
                            "Title": "Второй лог",
                            "LogMessage": "Палитра вернулась!",
                            "Parameters": {}
                        }
                    }
                ]
            }
        ],
        "VARIABLES": {},
        "CONSTANTS": {},
        "PARAMETERS": {}
    }

    serialized_data = php_serialize(template_data)
    compressed_data = zlib.compress(serialized_data)

    with open(out_path, 'wb') as f:
        f.write(compressed_data)
        
    print(f"Тестовый файл успешно создан: {os.path.abspath(out_path)}")

if __name__ == "__main__":
    create_test_bpt()