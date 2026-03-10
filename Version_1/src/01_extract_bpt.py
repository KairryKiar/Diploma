import zlib
import phpserialize
import os



base_path = r"C:\Users\Frich\Downloads\MLops\Diploma"


input_file_path = os.path.join(base_path, "Other.bpt")
output_file_path = os.path.join(base_path, "Other.txt")

def save_structure():
    
    try:
        if not os.path.exists(input_file_path):
            print(f"❌ Файл не найден по пути: {input_file_path}")
            return

        with open(input_file_path, "rb") as file:
            compressed_data = file.read()
        
        
        
        try:
            decompressed_data = zlib.decompress(compressed_data)
        except zlib.error:
            
            decompressed_data = compressed_data
            
        php_data = phpserialize.loads(decompressed_data)
        
    except Exception as e:
        print(f"❌ Ошибка при чтении или распаковке: {e}")
        return

    
    def decode_bytes(data):
        if isinstance(data, bytes):
            return data.decode('utf-8', errors='ignore')
        if isinstance(data, dict):
            return {decode_bytes(k): decode_bytes(v) for k, v in data.items()}
        if isinstance(data, list):
            return [decode_bytes(i) for i in data]
        return data

    process_data = decode_bytes(php_data)

    
    def write_full_dump(data, file_handle, level=0):
        
        indent = "    " * level

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    file_handle.write(f"{indent}{key}:\n")
                    write_full_dump(value, file_handle, level + 1)
                else:
                    
                    str_value = str(value) if value is not None else ""
                    if "\n" in str_value:
                        file_handle.write(f"{indent}{key}:\n")
                        for code_line in str_value.splitlines():
                            file_handle.write(f"{indent}    {code_line}\n")
                    else:
                        file_handle.write(f"{indent}{key}: {str_value}\n")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    file_handle.write(f"{indent}[{i}]:\n")
                    write_full_dump(item, file_handle, level + 1)
                else:
                    file_handle.write(f"{indent}[{i}]: {item}\n")
        else:
            file_handle.write(f"{indent}{data}\n")

    
    try:
        with open(output_file_path, "w", encoding="utf-8") as f:
            f.write(f"Файл исходник: {input_file_path}\n")
            f.write("=" * 60 + "\n\n")
            write_full_dump(process_data, f)

        print(f"✅ Готово! Полный код BPT записан в файл: {output_file_path}")

    except Exception as e:
        print(f"❌ Ошибка при записи файла: {e}")

if __name__ == "__main__":
    save_structure()