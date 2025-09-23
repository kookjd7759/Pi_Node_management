import os
import json
import tkinter as tk
from tkinter import filedialog

from tools import *

def pick_exe():
    root = tk.Tk()
    root.withdraw() 

    path = filedialog.askopenfilename(
        title="Pi 실행파일을 선택하세요",
        filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
        initialdir=os.path.expanduser("~")
    )

    if not path:
        print("선택 취소됨")
        return None

    if os.path.isfile(path) and os.access(path, os.X_OK):
        print("선택된 파일:", path)
        return path
    else:
        print("선택된 항목이 유효한 실행 파일이 아닙니다.")
        return None

FIND_MAX = 10
def start():
    print('Pi window를 찾는 중 ...')
    hwnd = None
    for attempt in range(FIND_MAX):
        hwnd = find_PI_window()
        if hwnd != None:
            print(f'{attempt + 1}/{FIND_MAX}회차에 성공 !')
            break

        print(f'{attempt + 1}/{FIND_MAX}회 실패')
        time.sleep(3)
    return hwnd

def check_exe_path():
    print('Pi Network.exe 실행 파일 경로를 확인합니다.')
    
    data = read_exe_path()
    if os.path.isfile(data['exe_path']):
        print(f'[OK] {data["exe_path"]}')
    else:
        print('[Fail] 유효한 경로가 존재하지 않습니다.')
        path = None
        print(' - 경로를 추정합니다 ...')
        expect_path = f'C:/Users/{Path.home().name}/AppData/Local/Programs/pi-network-desktop/Pi Network.exe'
        print(f' - 추정 경로: {expect_path}')
        if os.path.isfile(expect_path):
            print(' - 추정된 경로를 활용합니다')
            path = expect_path
        else:
            print(' - 추정된 경로가 유효하지 않습니다. 직접 경로를 입력해주세요.')
            path = pick_exe()
        
        data['exe_path'] = path
        with open(DATA_JSON, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

def check():
    hwnd = start()
    if hwnd == None:
        print('Pi window를 찾지 못했습니다.')
        exit(0)
    return cycle(hwnd)

if __name__ == '__main__':
    check_exe_path()
    check()