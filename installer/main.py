import requests
import tkinter as tk
from tkinter import filedialog
from urllib.parse import urlparse
from pathlib import Path

BASE_PATH = ''
IMAGE_BASE = ''

def download_file(url: str, target: str):
    response = requests.get(url)
    
    with open(target + f'\\{Path(urlparse(url).path).name}', "wb") as f:
        f.write(response.content)

def _find_folder():
    root = tk.Tk()
    root.withdraw()

    folder_path = filedialog.askdirectory(title="Select Pi manager install folder")
    return folder_path if folder_path else None

if __name__ == '__main__':
    ### get base path from user
    BASE_PATH = _find_folder()
    print(f'selected target folder = {BASE_PATH}')
    IMAGE_BASE += BASE_PATH + '\\image'

    ### test
    download_file('https://raw.githubusercontent.com/kookjd7759/Pi_Node_management/refs/heads/main/image/data/Pi_App_btn.png', BASE_PATH)