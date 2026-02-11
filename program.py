import subprocess
import win32process
import win32api
import win32gui
import win32con
import pyautogui
import ctypes
import time
import cv2
import numpy as np

from PIL import ImageGrab
from datetime import datetime

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
            time.sleep(1)
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
                    time.sleep(1)
                    return True
            else:
                stable = 0
                last_rect = rect

        time.sleep(0.05)
    time.sleep(1)
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

def _mouse_move(x, y):
    _USER32.SetCursorPos(x, y)
def _mouse_click():
    _USER32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.1)
    _USER32.mouse_event(0x0004, 0, 0, 0, 0)
def _mouse_scrollDown():
    pyautogui.scroll(-500)

def _capture():
    maximize()

    img = ImageGrab.grab(all_screens=False)

    if path.IMG_RECENT_STATE:
        today = datetime.now().strftime("%Y-%m-%d (%Hh %Mm %Ss)")
        save_path = path.RECORD_BASE + f'\\{today}.png'
        img.save(save_path)
        img.save(path.IMG_RECENT_STATE)

    minimize()

    return img

def _find_image(image: str, threshold: float = 0.8):
    # --- 0) 템플릿 로드(그레이)
    templ0 = cv2.imread(image, cv2.IMREAD_GRAYSCALE)
    if templ0 is None:
        raise FileNotFoundError(image)

    # --- 1) 캡처: 가능하면 Pi Desktop "창 영역(ROI)"만
    img = ImageGrab.grab(all_screens=True).convert("RGB")
    screen = np.array(img)
    screen0 = cv2.cvtColor(screen, cv2.COLOR_RGB2GRAY)

    # --- 2) 전처리 2개를 만들어서 "더 높은 점수"를 채택 (일반적으로 이게 제일 안정적)
    # A: 원본 + 약한 블러(노이즈만 살짝)
    scrA = cv2.GaussianBlur(screen0, (3, 3), 0)
    tmpA = cv2.GaussianBlur(templ0, (3, 3), 0)

    # B: CLAHE(조명/대비 차이 대응) + 약한 블러
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    scrB = cv2.GaussianBlur(clahe.apply(screen0), (3, 3), 0)
    tmpB = cv2.GaussianBlur(clahe.apply(templ0), (3, 3), 0)

    # --- 3) 멀티스케일 매칭 (DPI/해상도 차이 대응의 핵심)
    # 필요하면 범위를 조금 늘려도 됨.
    scales = [0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15, 1.20, 1.25]

    def run_match(screen_gray, templ_gray):
        best = (-1.0, (0, 0), (templ_gray.shape[1], templ_gray.shape[0]), 1.0)  # score, loc, (w,h), scale
        H, W = screen_gray.shape[:2]
        th0, tw0 = templ_gray.shape[:2]

        for s in scales:
            tw = int(tw0 * s)
            th = int(th0 * s)
            if tw < 12 or th < 12:
                continue
            if tw > W or th > H:
                continue

            t_resized = cv2.resize(templ_gray, (tw, th), interpolation=cv2.INTER_AREA)
            res = cv2.matchTemplate(screen_gray, t_resized, cv2.TM_CCOEFF_NORMED)
            _, maxv, _, maxloc = cv2.minMaxLoc(res)

            if maxv > best[0]:
                best = (float(maxv), maxloc, (tw, th), s)

        return best

    # A, B 두 가지 전처리 중 최선 선택
    scoreA, locA, whA, scA = run_match(scrA, tmpA)
    scoreB, locB, whB, scB = run_match(scrB, tmpB)

    if scoreB > scoreA:
        maxv, maxloc, (w, h), used_scale = scoreB, locB, whB, scB
        used = "CLAHE"
    else:
        maxv, maxloc, (w, h), used_scale = scoreA, locA, whA, scA
        used = "RAW"

    # --- 4) ROI 좌표 -> 실제 화면 좌표
    cx_img = maxloc[0] + w // 2
    cy_img = maxloc[1] + h // 2

    cx = cx_img
    cy = cy_img

    found = maxv >= threshold

    print(f"Find Image - {image}\nfound={found} score={maxv:.4f} used={used} scale={used_scale:.2f} x={cx} y={cy}")
    return found, (cx, cy)

def _go_to_status_page():
    restart()
    maximize()

    start = time.time()
    while time.time() - start < 120: # (120s)
        notWorking, (x, y) = _find_image(path.IMG_STARTMINING_TXT)
        if notWorking:
            return False
        
        status_btn, (x, y) = _find_image(path.IMG_STATUS_BTN)
        if status_btn:
            _mouse_move(x, y)
            _mouse_click()
        
        time.sleep(1)

        isSuccess, (x, y) = _find_image(path.IMG_MININGRATE_TXT)
        if isSuccess:
            _mouse_move(x, y)
            return True
        
    
    return False

def checking_status():
    isStatusPage = _go_to_status_page()
    minimize()
    return isStatusPage

def capture_status():
    isStatusPage = _go_to_status_page()
    if not isStatusPage:
        _capture()
        return False
    
    start = time.time()
    while time.time() - start < 60:
        _mouse_scrollDown()
        time.sleep(1)
        ok, (x, y) = _find_image(path.IMG_NODEBONUS_TXT)
        if ok:
            _capture()
            return True
    _capture()
    return False



if __name__ == '__main__':
    config.init()
    init()
    time.sleep(0.5)
    _capture()