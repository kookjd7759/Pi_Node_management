import json
import os
import tkinter as tk
from tkinter import filedialog

import path

_DATA = None

### user selet Pi Desktop execution program
def _find_file_exe():
    root = tk.Tk()
    root.withdraw() 

    path = filedialog.askopenfilename(
        title="Select Pi Desktop execute file",
        filetypes=[("Executable files", "*.exe")]
    )

    return path if path else None

def _load():
    global _DATA
    
    if not os.path.exists(path.CONFIG_PATH):
        ## Initial config data
        data = {
            'path' : None,
            'check_time' : 0
            }
        with open(path.CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    with open(path.CONFIG_PATH, "r", encoding="utf-8") as f:
        _DATA = json.load(f)

def _save():
    os.makedirs(os.path.dirname(path.CONFIG_PATH) or ".", exist_ok=True)
    with open(path.CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(_DATA, f, indent=2, ensure_ascii=False)

def init():
    global _DATA

    _load()
    isChange = False
    if _DATA['path'] == None:
        isChange = True
        _DATA['path'] = path.expect_program_path()
        if _DATA['path'] == None:
            _DATA['path'] = _find_file_exe()
    
    if isChange:
        _save()

def get_path():
    return _DATA['path']
def set_path(path):
    global _DATA
    _DATA['path'] = path
    _save()

def get_check_time():
    return _DATA['check_time']
def set_check_time(index):
    global _DATA
    _DATA['check_time'] = index
    _save()

if __name__ == '__main__':
    init()
    print(get_path())
    print(get_check_time())