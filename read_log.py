import os

log_file = 'scheduler_log_v3.txt'
if os.path.exists(log_file):
    with open(log_file, 'r', encoding='utf-16le', errors='replace') as f:
        lines = f.readlines()
        for line in lines:
            if "Supabase Response Text" in line or "BAD ROW" in line or "REASON" in line:
                print(line.strip())
else:
    print(f"{log_file} not found.")
