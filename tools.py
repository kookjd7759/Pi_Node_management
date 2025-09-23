import pyautogui
import psutil
import win32process
import win32gui
import win32con
import time
import json
import difflib
import easyocr
import numpy as np
from PIL import Image

from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from path import * 

KST = ZoneInfo("Asia/Seoul")

def now_kst() -> datetime:
    return datetime.now(tz=KST)

def fmt_kst(dt: datetime | None) -> str:
    if not dt:
        return "-"
    return dt.astimezone(KST).strftime("%Y-%m-%d %H:%M:%S %Z")

def plus_24h(base: datetime | None = None) -> datetime:
    base = base or now_kst()
    return base + timedelta(hours=24)

# ---------------
# Window Utility
# ---------------
def read_exe_path():
    with open(DATA_JSON, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def find_PI_window():
    data = read_exe_path()
    print(f'find a exe {data["exe_path"]}')
    if data['exe_path'] == '':
        print('Pi Network.exe의 실행 경로가 제대로 명시되지 않았습니다.')
        return None
    
    os.startfile(data['exe_path'])
    time.sleep(1)

    proc_name = 'Pi Network.exe'
    target_pids = {p.info['pid'] for p in psutil.process_iter(['pid','name'])
                   if (p.info['name'] or '').lower() == proc_name.lower()}
    if not target_pids:
        print(f"[ERR] '{proc_name}' 프로세스를 찾지 못했습니다.")
        return None

    hwnds = []
    def enum_handler(hwnd, _):
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid in target_pids:
                title = win32gui.GetWindowText(hwnd)
                if title.strip():
                    hwnds.append(hwnd)
        except:
            pass

    win32gui.EnumWindows(enum_handler, None)
    if not hwnds:
        print(f"[ERR] '{proc_name}'의 윈도우를 찾지 못했습니다.")
        return None
    
    return hwnds[0]
    
def capture_screen(path: str):
    img = pyautogui.screenshot()
    try:
        img.save(path)
    except:
        print(f'이미지 저장에 실패하였습니다.\n{path}')
    return path

def maximize_window(hwnd):
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    time.sleep(0.3)
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
    time.sleep(0.3)

    print(f"[OK] 최대화 완료 (hWnd={hwnd})")

def minimize_window(hwnd):
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    time.sleep(0.3)

    print(f"[OK] 최소화 완료 (hWnd={hwnd})")

# ---------------
# Mouse Utility
# ---------------
click_max = 20
def click_mouse_to(image_path: str):
    loc = None
    for attempt in range(click_max):
        try:
            loc = pyautogui.locateCenterOnScreen(image_path, confidence=0.95)
        except:
            print(f'버튼 찾기 {attempt + 1}/{click_max}회 실패')
            time.sleep(0.5)
            continue
        print(f'버튼 찾기 {attempt + 1}/{click_max}회차에 성공 !')
        break
    
    if loc:
        pyautogui.moveTo(loc.x, loc.y, duration=0.1)
        pyautogui.click()
        print(f"[OK] '{image_path}' 클릭 완료 → ({loc.x}, {loc.y})")
        return (loc.x, loc.y, 0.95)
    else:
        print(f"[ERR] '{image_path}' 화면에서 찾지 못함")
        return None

def scroll_down():
    for _ in range(5):
        pyautogui.scroll(-100)
        time.sleep(0.1)

# ---------------
# Capture Utility
# ---------------
reader = easyocr.Reader(['en'], gpu=False)

def ocr_text(img_path: Path):
    img = Image.open(img_path).convert("RGB")
    arr = np.array(img)
    result = reader.readtext(arr, detail=0, paragraph=False)
    return result

def get_OCR():
    capture_screen(PATH_OCR)
    lines = ocr_text(PATH_OCR)
    line = ''
    for text in lines:
        line += f'{text} '
    return line

# --------
# Cycle
# --------
def loop_chapture(hwnd):
    maximize_window(hwnd)
    click_mouse_to(BTN_PI_NODE)
    click_mouse_to(BTN_PI_APP)
    click_mouse_to(BTN_MINING_STATE)

    # for save scroll down
    click_mouse_to(LABEL_SCROLL_SUPPORT)
    scroll_down()

    file_name = datetime.now().strftime('%Y-%m-%d_%H시%M분')
    url = f'{BASE_RECORD}/{file_name}.png'
    capture_screen(url)

    minimize_window(hwnd)

def check_state(text: str):
    max_errors = 3
    target = 'Your computer is not running the blockchain'
    text = text.lower()
    target = target.lower()

    n, m = len(text), len(target)
    for i in range(0, n - m + 1):
        window = text[i:i+m]
        ratio = difflib.SequenceMatcher(None, window, target).ratio()
        errors = int((1 - ratio) * m)
        if errors <= max_errors:
            return False
    return True

def loop_get_state(hwnd):
    maximize_window(hwnd)
    click_mouse_to(BTN_PI_NODE)
    line = get_OCR()
    isRunning = check_state(line)
    minimize_window(hwnd)
    return isRunning

def cycle(hwnd):
    loop_chapture(hwnd)
    check = loop_get_state(hwnd)
    return check
