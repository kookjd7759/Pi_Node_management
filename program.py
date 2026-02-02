import subprocess
import win32process
import win32api
import win32gui
import win32con
import ctypes
import time
import cv2
import numpy as np

from PIL import ImageGrab

import config
import path

_USER32 = ctypes.windll.user32
_PROGRAM_PATH = None
_PROGRAM_HWND = None

def _find_window(timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        hwnd = win32gui.FindWindow(None, 'Pi Desktop')
        if hwnd != 0:
            return hwnd
        time.sleep(0.5)
    return None

def _wait_window_ready(timeout=60, stable_count=10):
    start = time.time()

    # GUI 메시지 루프 초기화 대기
    try:
        _, pid = win32process.GetWindowThreadProcessId(_PROGRAM_HWND)
        hProc = win32api.OpenProcess(
            win32con.SYNCHRONIZE | win32con.PROCESS_QUERY_INFORMATION,
            False,
            pid
        )
        win32process.WaitForInputIdle(hProc, 10000)
        win32api.CloseHandle(hProc)
    except:
        pass

    last_rect = None
    stable = 0

    # 창 안정화 감시
    while time.time() - start < timeout:
        if not win32gui.IsWindow(_PROGRAM_HWND):
            return False

        # hung 여부 체크 (WM_NULL 응답 확인)
        try:
            win32gui.SendMessageTimeout(
                _PROGRAM_HWND,
                win32con.WM_NULL,
                0,
                0,
                win32con.SMTO_ABORTIFHUNG,
                100
            )
        except:
            stable = 0
            time.sleep(0.05)
            continue

        rect = win32gui.GetWindowRect(_PROGRAM_HWND)

        if last_rect is None:
            last_rect = rect
            stable = 0
        else:
            # rect가 완전히 동일해야 stable 카운트 증가
            if rect == last_rect:
                stable += 1
                if stable >= stable_count:
                    return True
            else:
                stable = 0
                last_rect = rect

        time.sleep(0.05)

    return False

def _launch_program():
    subprocess.Popen(
        [_PROGRAM_PATH],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def excute():
    global _PROGRAM_HWND

    _launch_program()
    hwnd = _find_window()
    if hwnd is None:
        raise RuntimeError('I can not found program')

    _PROGRAM_HWND = hwnd
    _wait_window_ready()

def terminate():
    global _PROGRAM_PATH, _PROGRAM_HWND
    hwnd = _PROGRAM_HWND
    _PROGRAM_PATH = None
    _PROGRAM_HWND = None

    # 0. 이미 종료 된 경우 (핸들이 유효한지 확인)
    try:
        if hwnd is None or hwnd == 0:
            return True
        if not win32gui.IsWindow(hwnd):
            return True
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid == 0:
            return True
    except:
        return True
    
    # 1. 정상 종료 요청 (5s)
    try:
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    except Exception:
        return True

    start = time.time()
    while time.time() - start < 5:
        if not win32gui.IsWindow(hwnd):
            return True
        time.sleep(0.5)

    # 2. 강제 종료
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        hProc = win32api.OpenProcess(win32con.PROCESS_TERMINATE, False, pid)
        win32api.TerminateProcess(hProc, -1)
        win32api.CloseHandle(hProc)
        return True
    except:
        return False

def restart():
    terminate()
    init()

def minimize():
    if not win32gui.IsWindow(_PROGRAM_HWND):
        return False

    if win32gui.IsIconic(_PROGRAM_HWND):
        return True

    win32gui.ShowWindow(_PROGRAM_HWND, win32con.SW_MINIMIZE)
    _wait_window_ready()
    return True

def maximize():
    if not win32gui.IsWindow(_PROGRAM_HWND):
        return False
    
    if win32gui.GetWindowPlacement(_PROGRAM_HWND)[1] == win32con.SW_MAXIMIZE:
        return True

    win32gui.ShowWindow(_PROGRAM_HWND, win32con.SW_MAXIMIZE)
    _wait_window_ready()
    return True

def init():
    global _PROGRAM_PATH
    _PROGRAM_PATH = config.get_path()
    excute()
    minimize()

def capture():
    maximize()

    img = ImageGrab.grab(all_screens=False)

    if path.IMG_RECENT_STATE:
        img.save(path.IMG_RECENT_STATE)

    minimize()

    return img

def _move_mouse(x, y):
    _USER32.SetCursorPos(x, y)

def _click_mouse():
    _USER32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.1)
    _USER32.mouse_event(0x0004, 0, 0, 0, 0)

def _find_image(image: str, threshold: float = 0.8):
    _SM_XVIRTUALSCREEN = 76
    _SM_YVIRTUALSCREEN = 77
    _SM_CXVIRTUALSCREEN = 78
    _SM_CYVIRTUALSCREEN = 79

    # 1) 전체 화면 캡쳐 (모든 모니터 포함)
    img = ImageGrab.grab(all_screens=True).convert("RGB")
    screen = np.array(img)
    screen_gray = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)

    # 2) 템플릿 로드
    templ = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
    if templ is None:
        raise FileNotFoundError(image)

    # 3) 템플릿 매칭
    res = cv2.matchTemplate(screen_gray, templ, cv2.TM_CCOEFF_NORMED)
    _, maxv, _, maxloc = cv2.minMaxLoc(res)

    h, w = templ.shape[:2]
    cx_img = maxloc[0] + w // 2
    cy_img = maxloc[1] + h // 2

    # 4) "이미지 좌표" -> "실제 화면 좌표"로 스케일/오프셋 보정
    vx = _USER32.GetSystemMetrics(_SM_XVIRTUALSCREEN)
    vy = _USER32.GetSystemMetrics(_SM_YVIRTUALSCREEN)
    vw = _USER32.GetSystemMetrics(_SM_CXVIRTUALSCREEN)
    vh = _USER32.GetSystemMetrics(_SM_CYVIRTUALSCREEN)

    img_w, img_h = img.size
    cx = int(vx + cx_img * (vw / img_w))
    cy = int(vy + cy_img * (vh / img_h))

    found = maxv >= threshold

    print(f"found={found} score={maxv:.4f} x={cx} y={cy}")
    return found, (cx, cy)

def checking_status():
    restart()
    maximize()

    start = time.time()
    while time.time() - start < 120: # (120s)
        status_btn, (x, y) = _find_image(path.IMG_STATUS_BTN)
        if status_btn:
            _move_mouse(x, y)
            _click_mouse()
        
        time.sleep(1)

        isSuccess, (x, y) = _find_image(path.IMG_MININGRATE_TXT)
        if isSuccess:
            minimize()
            return True
    
    minimize()
    return False



if __name__ == '__main__':
    config.init()
    init()
    time.sleep(0.5)
    checking_status()