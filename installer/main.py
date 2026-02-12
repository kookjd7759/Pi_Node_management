import requests
import os

import tkinter as tk
from tkinter import filedialog
from urllib.parse import urlparse
from pathlib import Path

SORUCE_BASE = 'https://raw.githubusercontent.com/kookjd7759/Pi_Node_management/refs/heads/main/image/data'
EXEFILE_PATH = 'https://raw.githubusercontent.com/kookjd7759/Pi_Node_management/main/dist/UI.exe'

TARGET_BASE = ''
IMAGE_BASE = ''
DATA_BASE = ''

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
    TARGET_BASE = _find_folder()
    print(f'selected target folder = {TARGET_BASE}')

    ### create folder
    TARGET_BASE += '\\Pi Manager'
    IMAGE_BASE += TARGET_BASE + '\\image'
    DATA_BASE = IMAGE_BASE + '\\data'
    os.makedirs(TARGET_BASE, exist_ok=True)
    os.makedirs(IMAGE_BASE, exist_ok=True)
    os.makedirs(DATA_BASE, exist_ok=True)

    ### download image
    image_list = ['Pi_App_btn.png',
                  'basic_mining_rate_txt.png',
                  'close_btn.png',
                  'node_bonus_txt.png',
                  'start_mining_txt.png',
                  'status_btn.png']
    for image in image_list:
        download_file(SORUCE_BASE + f'/{image}', DATA_BASE)
    download_file(EXEFILE_PATH, TARGET_BASE)