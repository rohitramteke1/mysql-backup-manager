# MySQL Backup Manager

MySQL Backup Manager is a simple Python-based tool that automates the backup of MySQL databases and stores them securely in an AWS S3 bucket. It allows users to schedule backups and store them in a specified directory or S3 bucket for easy access and management.

---

## 📌 Features
- ✅ Automatic MySQL database backup using `mysqldump`
- ✅ Configurable backup directory and database credentials
- ✅ Timestamped backup files for easy tracking
- ✅ Supports Windows Task Scheduler for automation

---

## 🛠 Prerequisites
Before using this project, ensure you have the following installed:
- [Python 3.x](https://www.python.org/downloads/)
- [MySQL Server](https://dev.mysql.com/downloads/mysql/)
- `mysqldump` utility (included with MySQL)
- PowerShell (for automation)

---

## 🚀 Installation

### 1️⃣ Clone the repository
```sh
git clone https://github.com/rohitramteke1/mysql-backup-manager.git
cd mysql-backup-manager
```

### 2️⃣ Create and activate a virtual environment
```sh
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3️⃣ Install dependencies
```sh
pip install -r requirements.txt
```

### 4️⃣ Configure the `.env` file
Create a `.env` file in the project root and add:
```ini
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=yourdatabase
BACKUP_DIR=backups
```

---

## 📂 Project Structure
```bash
mysql-backup-manager/
│── backups/              # Directory to store backup files
│── .github/              # GitHub Actions/CI pipeline configuration
│── venv/                 # Virtual environment (ignored in Git)
│── .env                  # Environment variables (ignored in Git)
│── .gitignore            # Ignored files (venv, backups, etc.)
│── auto_backup.ps1       # PowerShell script for scheduled backups
│── backup.py             # Main script to perform MySQL backup
│── restore.py            # Script to restore backups
│── tests/                # Folder for test files
│   └── test_backup.py    # Test file for the backup functionality
│── requirements.txt      # Python dependencies
│── README.md             # Documentation
└── LICENSE               # License file

```

---

## 🔹 Usage

### ✅ Manual Backup
Run the following command to create a backup manually:
```sh
python backup.py
```
The backup will be stored in the `backups/` directory with a timestamped filename.

---

### ⏳ Automating Backups (Windows Task Scheduler)
To schedule a daily backup at 2:00 AM:
```sh
e.g. schtasks /create /tn "MySQL Auto Backup" /tr "powershell -ExecutionPolicy Bypass -File <your-project-path>\auto_backup.ps1" /sc daily /st 02:00


schtasks /create /tn "MySQL Auto Backup" /tr "powershell -ExecutionPolicy Bypass -File D:\Projects\Personal\mysql-backup-manager\auto_backup.ps1" /sc daily /st 02:00
```
📌 *This step is optional for the project but demonstrates automation.*

---

### 🔄 Restore a Backup
To restore a backup, use:
```sh
mysql -h localhost -u root -p yourdatabase < backups\db_backup_YYYY-MM-DD_HH-MM-SS.sql
```

---

## 💡 Contributing
Contributions are welcome! Feel free to submit issues or pull requests to improve this project.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
