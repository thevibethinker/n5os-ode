import shutil
from pathlib import Path
import logging

logging.basicConfig(filename='/home/workspace/Temp/temp_catcher.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')

TEMP_DIR = Path('/home/workspace/Temp')

# Function to add or move a file into Temp directory
def add_to_temp(file_path: str):
    file = Path(file_path)
    if not file.exists():
        logging.error(f'File {file_path} does not exist and cannot be moved to Temp.')
        return
    destination = TEMP_DIR / file.name
    shutil.move(str(file), str(destination))
    logging.info(f'Moved file {file_path} to Temp directory.')

# Example usage:
#if __name__ == '__main__':
#    add_to_temp('/some/loose/file.txt')
