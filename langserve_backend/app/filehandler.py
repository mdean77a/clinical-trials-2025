import os
import json
from threading import Lock
from .config import Config

class FileHandler():
    def __init__(self):
        # Lock for thread-safe file access
        self.file_status_lock = Lock()
        self.DB_FILE = Config.DB_FILE

    def load_file_status(self):
        with self.file_status_lock:
            if os.path.exists(self.DB_FILE):
                with open(self.DB_FILE, 'r') as f:
                    file_status = json.load(f)
            else:
                file_status = {}
        return file_status

    def save_file_status(self, file_status):
        with self.file_status_lock:
            with open(self.DB_FILE, 'w') as f:
                json.dump(file_status, f)