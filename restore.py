import os
from dotenv import load_dotenv
import subprocess

# Load environment variables
load_dotenv()

# Read from .env file
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
BACKUP_DIR = os.getenv("BACKUP_DIR", "backups")

# Function to restore from backup
def restore_backup(backup_file):
    if not os.path.exists(backup_file):
        print("❌ Error: Backup file does not exist!")
        return

    try:
        command = f'mysql -h {DB_HOST} -u {DB_USER} -p{DB_PASSWORD} {DB_NAME} < "{backup_file}"'
        subprocess.run(command, shell=True, check=True)
        print(f"✅ Restore successful from: {backup_file}")
    except subprocess.CalledProcessError:
        print("❌ Restore failed!")

# List all backup files
backup_files = sorted(os.listdir(BACKUP_DIR), reverse=True)

if not backup_files:
    print("❌ No backup files found!")
else:
    print("\nAvailable Backups:")
    for idx, file in enumerate(backup_files):
        print(f"{idx + 1}. {file}")

    # User input for restore
    choice = input("\nEnter the backup number to restore (or press Enter for latest): ").strip()

    if choice.isdigit() and 1 <= int(choice) <= len(backup_files):
        selected_backup = os.path.join(BACKUP_DIR, backup_files[int(choice) - 1])
    else:
        selected_backup = os.path.join(BACKUP_DIR, backup_files[0])  # Default to latest

    print(f"ℹ️ Restoring from: {selected_backup}")
    restore_backup(selected_backup)
