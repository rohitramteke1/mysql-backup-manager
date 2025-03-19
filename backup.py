import os
from dotenv import load_dotenv
import time
import subprocess
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
BACKUP_DIR = os.getenv("BACKUP_DIR", "backups") # default backups

os.makedirs(BACKUP_DIR, exist_ok=True)

timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
backup_file = os.path.join(BACKUP_DIR, f"{DB_NAME}_backup_{timestamp}.sql")

try:
    command = f"mysqldump -h {DB_HOST} -u {DB_USER} -p{DB_PASSWORD} {DB_NAME} > {backup_file}"
    subprocess.run(command, shell=True, check=True)
    print(f"✅ Backup successful: {backup_file}")
except subprocess.CalledProcessError as e:
    print(f"❌ Backup failed: {e}")