import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv
import logging

# Setup logging
logging.basicConfig(filename='backup.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class MySQLBackupManager:
    """
    Class for managing MySQL database backups including local backup creation
    and uploading backups to an S3 bucket.
    """

    def __init__(self):
        """
        Initialize MySQLBackupManager by loading environment variables 
        and setting up necessary configurations.
        """
        load_dotenv()
        self.db_host = os.getenv("DB_HOST")
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        self.db_name = os.getenv("DB_NAME")
        self.backup_dir = os.getenv("BACKUP_DIR", "backups")
        self.s3_bucket = os.getenv("S3_BUCKET_NAME")

        os.makedirs(self.backup_dir, exist_ok=True)

    def check_mysql_connection(self) -> bool:
        """
        Check if the MySQL server is reachable.

        @returns: True if MySQL server is running, False otherwise
        """
        try:
            command = f'mysqladmin -h {self.db_host} -u {self.db_user} -p"{self.db_password}" ping'
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if "mysqld is alive" in result.stdout:
                logging.info("MySQL server is up and running.")
                return True
            else:
                logging.error("MySQL server is not running.")
                return False
        except subprocess.CalledProcessError as e:
            logging.error(f"Error checking MySQL connection: {e}")
            return False

    def create_backup(self) -> str:
        """
        Creates a MySQL database backup and saves it to the backup directory.

        @returns: Path to the backup file if successful, None otherwise
        """
        if not self.check_mysql_connection():
            logging.error("Cannot proceed with backup. MySQL server is not running.")
            return None
        
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            backup_file = os.path.join(self.backup_dir, f"db_backup_{timestamp}.sql")
            dump_command = f"mysqldump -h {self.db_host} -u {self.db_user} -p{self.db_password} {self.db_name} > {backup_file}"

            subprocess.run(dump_command, shell=True, check=True)
            logging.info(f"Backup created: {backup_file}")
            return backup_file
        except subprocess.CalledProcessError as e:
            logging.error(f"Error creating backup: {e}")
            return None

    def upload_to_s3(self, backup_file: str) -> bool:
        """
        Uploads the created backup file to an AWS S3 bucket.

        @param backup_file: Path to the backup file to be uploaded
        @returns: True if upload is successful, False otherwise
        """
        if not backup_file:
            logging.error("No backup file to upload.")
            return False
        
        try:
            s3_upload_command = f"aws s3 cp {backup_file} s3://{self.s3_bucket}/"
            subprocess.run(s3_upload_command, shell=True, check=True)
            logging.info(f"Backup uploaded to S3: s3://{self.s3_bucket}/")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Error uploading to S3: {e}")
            return False


if __name__ == "__main__":
    # Initialize backup manager and create backup
    backup_manager = MySQLBackupManager()
    backup_file = backup_manager.create_backup()
    
    # Upload the backup to S3
    if backup_file:
        backup_manager.upload_to_s3(backup_file)
