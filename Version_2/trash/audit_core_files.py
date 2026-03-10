import os

def audit_bitrix_files(base_dir):
    found_activities = 0
    print(f"Ищем в: {os.path.abspath(base_dir)}")
    for root, dirs, files in os.walk(base_dir):
        if '.description.php' in files:
            found_activities += 1
            activity_name = os.path.basename(root)
            print(f"[{found_activities}] {activity_name}")
    print(f"\nTotal: {found_activities}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(script_dir, "..", "data", "bitrix")
    audit_bitrix_files(target_dir)