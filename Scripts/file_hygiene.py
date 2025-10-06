import os
import time
import shutil
from pathlib import Path
from typing import Dict, Callable
import logging
import hashlib

class FileHandlerStrategy:
    def __init__(self, log_file: str):
        self.log_file = log_file

    def handle(self, file_path: Path) -> None:
        raise NotImplementedError

    def log_action(self, action: str, file_path: Path, target: str = ""):
        with open(self.log_file, 'a') as f:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"{timestamp} - {action}: {file_path} -> {target}\n")

    def compute_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of the file content."""
        hash_sha256 = hashlib.sha256()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()

    def is_duplicate(self, source_path: Path, target_dir: Path) -> bool:
        """Check if source file is a duplicate of any file in target_dir."""
        source_hash = self.compute_hash(source_path)
        for existing_file in target_dir.iterdir():
            if existing_file.is_file():
                try:
                    if self.compute_hash(existing_file) == source_hash:
                        return True
                except:
                    pass
        return False

class TempFileStrategy(FileHandlerStrategy):
    def handle(self, file_path: Path) -> None:
        if time.time() - file_path.stat().st_mtime > 7 * 86400:
            os.remove(file_path)
            self.log_action("Deleted temp file", file_path)

class BackupStrategy(FileHandlerStrategy):
    def __init__(self, log_file: str, root: str):
        super().__init__(log_file)
        self.backup_dir = Path(root) / 'Backups'
        os.makedirs(self.backup_dir, exist_ok=True)

    def handle(self, file_path: Path) -> None:
        target = self.backup_dir / file_path.name
        shutil.move(str(file_path), target)
        self.log_action("Moved to backup", file_path, str(target))

class DocumentStrategy(FileHandlerStrategy):
    def __init__(self, log_file: str, root: str):
        super().__init__(log_file)
        self.doc_dir = Path(root) / 'Documents'
        os.makedirs(self.doc_dir, exist_ok=True)

    def handle(self, file_path: Path) -> None:
        if self.is_duplicate(file_path, self.doc_dir):
            os.remove(file_path)
            self.log_action("Deleted duplicate document", file_path)
        else:
            target = self.doc_dir / file_path.name
            counter = 1
            while target.exists():
                stem = file_path.stem
                suffix = file_path.suffix
                target = self.doc_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            shutil.move(str(file_path), target)
            self.log_action("Moved to documents", file_path, str(target))

class ImageStrategy(FileHandlerStrategy):
    def __init__(self, log_file: str, root: str):
        super().__init__(log_file)
        self.img_dir = Path(root) / 'Images'
        os.makedirs(self.img_dir, exist_ok=True)

    def handle(self, file_path: Path) -> None:
        if self.is_duplicate(file_path, self.img_dir):
            os.remove(file_path)
            self.log_action("Deleted duplicate image", file_path)
        else:
            target = self.img_dir / file_path.name
            counter = 1
            while target.exists():
                stem = file_path.stem
                suffix = file_path.suffix
                target = self.img_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            shutil.move(str(file_path), target)
            self.log_action("Moved to images", file_path, str(target))

class ScriptStrategy(FileHandlerStrategy):
    def __init__(self, log_file: str, root: str):
        super().__init__(log_file)
        self.script_dir = Path(root) / 'Scripts'
        os.makedirs(self.script_dir, exist_ok=True)

    def handle(self, file_path: Path) -> None:
        if self.is_duplicate(file_path, self.script_dir):
            os.remove(file_path)
            self.log_action("Deleted duplicate script", file_path)
        else:
            target = self.script_dir / file_path.name
            counter = 1
            while target.exists():
                stem = file_path.stem
                suffix = file_path.suffix
                target = self.script_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            shutil.move(str(file_path), target)
            self.log_action("Moved to scripts", file_path, str(target))

class LogStrategy(FileHandlerStrategy):
    def __init__(self, log_file: str, root: str):
        super().__init__(log_file)
        self.log_dir = Path(root) / 'Logs'
        os.makedirs(self.log_dir, exist_ok=True)

    def handle(self, file_path: Path) -> None:
        if self.is_duplicate(file_path, self.log_dir):
            os.remove(file_path)
            self.log_action("Deleted duplicate log", file_path)
        else:
            target = self.log_dir / file_path.name
            counter = 1
            while target.exists():
                stem = file_path.stem
                suffix = file_path.suffix
                target = self.log_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            shutil.move(str(file_path), target)
            self.log_action("Moved to logs", file_path, str(target))

class DataStrategy(FileHandlerStrategy):
    def __init__(self, log_file: str, root: str):
        super().__init__(log_file)
        self.data_dir = Path(root) / 'Data'
        os.makedirs(self.data_dir, exist_ok=True)

    def handle(self, file_path: Path) -> None:
        if self.is_duplicate(file_path, self.data_dir):
            os.remove(file_path)
            self.log_action("Deleted duplicate data", file_path)
        else:
            target = self.data_dir / file_path.name
            counter = 1
            while target.exists():
                stem = file_path.stem
                suffix = file_path.suffix
                target = self.data_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            shutil.move(str(file_path), target)
            self.log_action("Moved to data", file_path, str(target))

class OtherStrategy(FileHandlerStrategy):
    def __init__(self, log_file: str, root: str):
        super().__init__(log_file)
        self.other_dir = Path(root) / 'Misc'
        os.makedirs(self.other_dir, exist_ok=True)

    def handle(self, file_path: Path) -> None:
        if self.is_duplicate(file_path, self.other_dir):
            os.remove(file_path)
            self.log_action("Deleted duplicate misc", file_path)
        else:
            target = self.other_dir / file_path.name
            counter = 1
            while target.exists():
                stem = file_path.stem
                suffix = file_path.suffix
                target = self.other_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            shutil.move(str(file_path), target)
            self.log_action("Moved to misc", file_path, str(target))

# Add more strategies as needed

class FileHandlerFactory:
    @staticmethod
    def get_handler(category: str, log_file: str, root: str) -> FileHandlerStrategy:
        if category == 'temp':
            return TempFileStrategy(log_file)
        elif category == 'backup':
            return BackupStrategy(log_file, root)
        elif category == 'document':
            return DocumentStrategy(log_file, root)
        elif category == 'image':
            return ImageStrategy(log_file, root)
        elif category == 'script':
            return ScriptStrategy(log_file, root)
        elif category == 'log':
            return LogStrategy(log_file, root)
        elif category == 'data':
            return DataStrategy(log_file, root)
        elif category == 'other':
            return OtherStrategy(log_file, root)
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
                '.backup': 'backup',
                '.md': 'document',
                '.txt': 'document',
                '.pdf': 'document',
                '.docx': 'document',
                '.png': 'image',
                '.jpg': 'image',
                '.jpeg': 'image',
                '.gif': 'image',
                '.py': 'script',
                '.sh': 'script',
                '.log': 'log',
                '.csv': 'data',
                '.json': 'data',
                '.jsonl': 'data',
                # Add more extension-to-category mappings
            }
        return cls._instance

    def categorize_and_handle(self, roots: list = ['/home/workspace']):
        log_file = '/home/workspace/file_hygiene_log.txt'
        for root in roots:
            root_path = Path(root)
            if not root_path.exists():
                continue
            for file_path in root_path.iterdir():
                if file_path.is_file() and not file_path.name.startswith('.') and file_path.name != 'file_hygiene_log.txt':
                    # Exclude core N5 system files
                    if 'N5/commands.jsonl' in str(file_path) or 'N5/prefs.md' in str(file_path) or file_path.parent == Path('/home/workspace/N5'):
                        continue
                    ext = file_path.suffix.lower()
                    category = self.categories.get(ext, 'other')
                    if category != 'unknown':
                        handler = FileHandlerFactory.get_handler(category, log_file, root)
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