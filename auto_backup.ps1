Write-Host "Running MySQL Auto Backup Script..."

# Activate Python Virtual Environment
cd D:\Projects\Personal\mysql-backup-manager
D:\Projects\Personal\mysql-backup-manager\venv\Scripts\Activate

# Run the backup script
python backup.py

Write-Host "✅ Backup Completed!"
