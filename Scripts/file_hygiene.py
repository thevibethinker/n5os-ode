import os
import time
import shutil
from pathlib import Path
from typing import Dict, Callable

class FileHandlerStrategy:
    def handle(self, file_path: Path) -> None:
        raise NotImplementedError

class TempFileStrategy(FileHandlerStrategy):
    def handle(self, file_path: Path) -> None:
        if time.time() - file_path.stat().st_mtime > 7 * 86400:
            os.remove(file_path)

class BackupStrategy(FileHandlerStrategy):
    def handle(self, file_path: Path) -> None:
        backup_dir = Path('/home/workspace/Backups')
        os.makedirs(backup_dir, exist_ok=True)
        shutil.move(str(file_path), backup_dir / file_path.name)

# Add more strategies as needed

class FileHandlerFactory:
    @staticmethod
    def get_handler(category: str) -> FileHandlerStrategy:
        if category == 'temp':
            return TempFileStrategy()
        elif category == 'backup':
            return BackupStrategy()
        raise ValueError(f"Unknown category: {category}")

class FileManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FileManager, cls).__new__(cls)
            cls._instance.observers = []
            cls._instance.categories = {
                '.tmp': 'temp',
                '.bak': 'backup',
                # Add extension-to-category mappings
            }
        return cls._instance

    def categorize_and_handle(self, root: str = '/home/workspace'):
        for file_path in Path(root).iterdir():
            if file_path.is_file() and not file_path.name.startswith('.'):
                ext = file_path.suffix
                category = self.categories.get(ext, 'unknown')
                if category != 'unknown':
                    handler = FileHandlerFactory.get_handler(category)
                    handler.handle(file_path)
                # Notify observers if needed

    def add_observer(self, observer: Callable):
        self.observers.append(observer)

    def notify_observers(self, event):
        for observer in self.observers:
            observer(event)

# Usage example (run periodically)
if __name__ == "__main__":
    manager = FileManager()
    # Add observer example: def log_event(event): print(f"Event: {event}")
    # manager.add_observer(log_event)
    manager.categorize_and_handle()