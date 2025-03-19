import unittest
from unittest.mock import patch, MagicMock
from backup import MySQLBackupManager
import subprocess 

class TestBackup(unittest.TestCase):
    
    @patch('subprocess.run')
    def test_backup_creation_failure(self, mock_subprocess):
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, 'mysqldump')

        backup_manager = MySQLBackupManager()
        result = backup_manager.create_backup()
        
        self.assertIsNone(result)

    @patch('subprocess.run')
    def test_upload_to_s3_failure(self, mock_subprocess):
        mock_subprocess.side_effect = subprocess.CalledProcessError(1, 'aws s3 cp')

        backup_manager = MySQLBackupManager()
        result = backup_manager.upload_to_s3('path/to/backup.sql')
        
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
