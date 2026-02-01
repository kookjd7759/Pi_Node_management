import subprocess
import win32process
import win32api
import win32gui
import win32con
import win32ui
import ctypes
import time

from PIL import Image

import config
import path

_PROGRAM_PATH = None
_PROGRAM_HWND = None

def _find_window(wait=60):
    start = time.time()
    while time.time() - start < wait:
        hwnd = win32gui.FindWindow(None, 'Pi Desktop')
        if hwnd != 0:
            return hwnd
        time.sleep(0.5)
    return None

def _wait_window_ready(timeout=60, stable_count=8, stable_px=2):
    start = time.time()

    # 1️⃣ GUI 메시지 루프 초기화 대기 (가장 신뢰도 높음)
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
        pass  # 일부 앱에서는 실패 가능

    last_rect = None
    stable = 0

    # 2️⃣ 창 안정화 감시 루프
    while time.time() - start < timeout:
        if not win32gui.IsWindow(_PROGRAM_HWND):
            return False

        # 최소화 상태면 아직 안정화 아님
        if win32gui.IsIconic(_PROGRAM_HWND):
            stable = 0
            time.sleep(0.05)
            continue

        # 메시지 루프 응답 확인 (멈춘 창 필터링)
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

        l, t, r, b = win32gui.GetWindowRect(_PROGRAM_HWND)
        w, h = r - l, b - t

        # 너무 작은 크기는 초기 상태로 간주
        if w < 200 or h < 200:
            stable = 0
            time.sleep(0.05)
            continue

        rect = (l, t, r, b)

        if last_rect is None:
            last_rect = rect
            stable = 0
        else:
            dl = abs(rect[0] - last_rect[0])
            dt = abs(rect[1] - last_rect[1])
            dr = abs(rect[2] - last_rect[2])
            db = abs(rect[3] - last_rect[3])

            if dl <= stable_px and dt <= stable_px \
               and dr <= stable_px and db <= stable_px:
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
    # 1. 정상 종료 요청 (5s)
    win32gui.PostMessage(_PROGRAM_HWND, win32con.WM_CLOSE, 0, 0)

    start = time.time()
    while time.time() - start < 5:
        if not win32gui.IsWindow(_PROGRAM_HWND):
            return True
        time.sleep(0.5)

    # 2. 강제 종료
    try:
        _, pid = win32process.GetWindowThreadProcessId(_PROGRAM_HWND)
        hProc = win32api.OpenProcess(win32con.PROCESS_TERMINATE, False, pid)
        win32api.TerminateProcess(hProc, -1)
        win32api.CloseHandle(hProc)
        return True
    except:
        return False

def restart():
    terminate()
    global _PROGRAM_PATH, _PROGRAM_HWND
    _PROGRAM_PATH = None
    _PROGRAM_HWND = None
    init()

def minimize():
    if not win32gui.IsWindow(_PROGRAM_HWND):
        return False

    if win32gui.IsIconic(_PROGRAM_HWND):
        return True

    win32gui.ShowWindow(_PROGRAM_HWND, win32con.SW_MINIMIZE)
    return True

def maximize():
    if not win32gui.IsWindow(_PROGRAM_HWND):
        return False
    
    if win32gui.GetWindowPlacement(_PROGRAM_HWND)[1] == win32con.SW_MAXIMIZE:
        return True

    win32gui.ShowWindow(_PROGRAM_HWND, win32con.SW_MAXIMIZE)
    return True

def init():
    global _PROGRAM_PATH
    _PROGRAM_PATH = config.get_path()
    excute()
    minimize()

def capture():
    left, top, right, bottom = win32gui.GetWindowRect(_PROGRAM_HWND)
    w, h = right - left, bottom - top

    hwnd_dc = win32gui.GetWindowDC(_PROGRAM_HWND)
    src_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    mem_dc = src_dc.CreateCompatibleDC()

    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(src_dc, w, h)
    mem_dc.SelectObject(bmp)

    ok = ctypes.windll.user32.PrintWindow(_PROGRAM_HWND, mem_dc.GetSafeHdc(), 2)

    info = bmp.GetInfo()
    data = bmp.GetBitmapBits(True)
    img = Image.frombuffer(
        "RGB",
        (info["bmWidth"], info["bmHeight"]),
        data,
        "raw",
        "BGRX",
        0,
        1
    )
    img.save(path.RECENT_STATE)

    mem_dc.DeleteDC()
    src_dc.DeleteDC()
    win32gui.ReleaseDC(_PROGRAM_HWND, hwnd_dc)
    win32gui.DeleteObject(bmp.GetHandle())

    return bool(ok)


if __name__ == '__main__':
    config.init()
    init()