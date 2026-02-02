import subprocess
import win32process
import win32api
import win32gui
import win32con
import time

from PIL import ImageGrab

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

    if path.RECENT_STATE:
        img.save(path.RECENT_STATE)

    minimize()

    return img


if __name__ == '__main__':
    config.init()
    init()
    capture()