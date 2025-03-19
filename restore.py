import os
from dotenv import load_dotenv
import subprocess
import boto3
import logging

# Setup logging
logging.basicConfig(filename='restore.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class RestoreManager:
    """
    Manages database backup restoration from local files or an S3 bucket.
    """

    def __init__(self, backup_source="local"):
        load_dotenv()
        self.db_host = os.getenv("DB_HOST")
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        self.db_name = os.getenv("DB_NAME")
        self.backup_dir = os.getenv("BACKUP_DIR", "backups")
        self.s3_bucket = os.getenv("S3_BUCKET_NAME")
        self.s3_client = boto3.client("s3")
        self.backup_source = backup_source  # "local" or "s3"

    def list_local_backups(self):
        """
        List available local backup files in the backup directory.

        Returns:
            list: List of local backup files or an empty list if no backups are found.
        """
        try:
            backup_files = sorted(os.listdir(self.backup_dir), reverse=True)
            if not backup_files:
                logging.error("No local backup files found.")
                return []
            
            print("\nAvailable Local Backups:")
            for idx, file in enumerate(backup_files):
                print(f"{idx + 1}. {file}")
            return backup_files
        except Exception as e:
            logging.error(f"Error listing local backups: {e}")
            return []

    def check_s3_bucket(self):
        """
        Check if the S3 bucket exists and is accessible.

        Returns:
            bool: True if the bucket exists, False otherwise.
        """
        try:
            self.s3_client.head_bucket(Bucket=self.s3_bucket)
            return True
        except boto3.exceptions.S3UploadFailedError:
            logging.error(f"Bucket '{self.s3_bucket}' does not exist or is inaccessible.")
            return False
        except Exception as e:
            logging.error(f"Error accessing S3 bucket: {e}")
            return False

    def list_s3_backups(self):
        """
        List available backup files in the S3 bucket.

        Returns:
            list: List of S3 backup files or an empty list if no backups are found.
        """
        if not self.check_s3_bucket():
            return []
        
        try:
            objects = self.s3_client.list_objects_v2(Bucket=self.s3_bucket).get("Contents", [])
            if not objects:
                logging.error("No S3 backup files found.")
                return []
            
            print("\nAvailable S3 Backups:")
            backup_files = sorted([obj["Key"] for obj in objects], reverse=True)
            for idx, file in enumerate(backup_files):
                print(f"S3-{idx + 1}. {file}")
            return backup_files
        except Exception as e:
            logging.error(f"Error listing S3 backups: {e}")
            return []

    def download_s3_backup(self, backup_key):
        """
        Download the selected S3 backup to the local directory.

        Args:
            backup_key (str): The S3 backup file key.

        Returns:
            str: Path to the downloaded backup file.
        """
        local_path = os.path.join(self.backup_dir, os.path.basename(backup_key))
        try:
            self.s3_client.download_file(self.s3_bucket, backup_key, local_path)
            logging.info(f"Downloaded S3 backup: {backup_key} to {local_path}")
            return local_path
        except Exception as e:
            logging.error(f"Error downloading S3 backup: {e}")
            return None

    def restore_backup(self, backup_file):
        """
        Restore from the selected backup file.

        Args:
            backup_file (str): Path to the backup file.
        """
        if not os.path.exists(backup_file):
            logging.error("Backup file does not exist!")
            return
        
        # Check MySQL connection before restoring
        if not self.check_mysql_connection():
            logging.error("Cannot proceed with restore. MySQL server is not running.")
            return
        
        try:
            # Use environment variables for credentials to restore
            command = f'mysql -h {self.db_host} -u {self.db_user} -p"{self.db_password}" {self.db_name} < "{backup_file}"'
            subprocess.run(command, shell=True, check=True)
            logging.info(f"Successfully restored from: {backup_file}")
            print(f"Restore successful from: {backup_file}")
            
            # Verify restore success
            self.verify_restore()
        except subprocess.CalledProcessError:
            logging.error("Restore failed!")
            print("Restore failed!")
    
    def verify_restore(self):
        """
        Verify the success of the restore operation by checking database tables.
        """
        try:
            # Verify restore by checking tables in the database
            command = f'mysql -h {self.db_host} -u {self.db_user} -p"{self.db_password}" -e "SHOW TABLES;" {self.db_name}'
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            tables = result.stdout.strip().split("\n")[1:]
            if tables:
                logging.info("Restore verification successful: Tables found in DB")
                print("✅ Restore verification successful: Tables found in DB")
            else:
                logging.warning("Restore verification failed: No tables found!")
                print("❌ Restore verification failed: No tables found!")
        except subprocess.CalledProcessError:
            logging.error("Error during restore verification!")
            print("❌ Error verifying restore!")

    def check_mysql_connection(self):
        """
        Check if the MySQL server is reachable.

        Returns:
            bool: True if MySQL server is running, False otherwise.
        """
        try:
            command = f'mysqladmin -h {self.db_host} -u {self.db_user} -p"{self.db_password}" ping'
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if "mysqld is alive" in result.stdout:
                return True
            else:
                logging.error("MySQL server is not running.")
                return False
        except subprocess.CalledProcessError as e:
            logging.error(f"Error checking MySQL connection: {e}")
            return False

    def choose_restore_source(self):
        """
        Ask the user to choose whether to restore from local or S3 backups.
        """
        print("Choose backup source:")
        print("1. Local backups")
        print("2. S3 backups")
        choice = input("Enter 1 or 2: ").strip()

        if choice == "1":
            self.backup_source = "local"
            local_backups = self.list_local_backups()
            if local_backups:
                choice = input("\nEnter the backup number to restore (1-N for local): ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(local_backups):
                    selected_backup = os.path.join(self.backup_dir, local_backups[int(choice) - 1])
                    print(f"Restoring from local backup: {selected_backup}")
                    self.restore_backup(selected_backup)
                else:
                    print("Invalid local backup selection!")
        elif choice == "2":
            self.backup_source = "s3"
            s3_backups = self.list_s3_backups()
            if s3_backups:
                choice = input("\nEnter the backup number to restore (prefix S3- for cloud backup): ").strip()
                if choice.lower().startswith("s3-"):
                    s3_index = int(choice.split("-")[1]) - 1
                    if 0 <= s3_index < len(s3_backups):
                        selected_backup = self.download_s3_backup(s3_backups[s3_index])
                        if selected_backup:
                            print(f"Restoring from S3 backup: {selected_backup}")
                            self.restore_backup(selected_backup)
                    else:
                        print("Invalid S3 backup selection!")
                else:
                    print("Invalid input format for S3 backup!")
        else:
            print("Invalid selection. Please choose either 1 or 2.")

if __name__ == "__main__":
    restore_manager = RestoreManager()
    restore_manager.choose_restore_source()
