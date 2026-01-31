import subprocess
import win32ui
import win32gui
import ctypes
import time

from PIL import Image

import config
import path

_PROGRAM_PATH = None
_PROGRAM_HWND = None

def _find_window():
    return win32gui.FindWindow(None, 'Pi Desktop')

def _wait_for_window():
    start = time.time()
    while time.time() - start < 60:
        hwnd = _find_window()
        if hwnd != 0:
            return hwnd
        time.sleep(0.5)
    return None

def _launch_program(path):
    print(f'program path : {path}')
    subprocess.Popen(
        [path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def init():
    global _PROGRAM_PATH, _PROGRAM_HWND

    _PROGRAM_PATH = config.get_path()

    hwnd = _find_window()
    if hwnd != 0:
        _PROGRAM_HWND = hwnd
        return

    _launch_program(_PROGRAM_PATH)

    hwnd = _wait_for_window()
    if hwnd is None:
        raise RuntimeError('I can not found program')

    _PROGRAM_HWND = hwnd

def capture():

    # 창 전체(테두리/제목줄 포함) 크기
    left, top, right, bottom = win32gui.GetWindowRect(_PROGRAM_HWND)
    w, h = right - left, bottom - top

    hwnd_dc = win32gui.GetWindowDC(_PROGRAM_HWND)
    src_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    mem_dc = src_dc.CreateCompatibleDC()

    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(src_dc, w, h)
    mem_dc.SelectObject(bmp)

    # 2 = PW_RENDERFULLCONTENT (지원되는 앱이면 더 잘 뜸)
    ok = ctypes.windll.user32.PrintWindow(_PROGRAM_HWND, mem_dc.GetSafeHdc(), 2)

    # Bitmap -> PIL
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

    # 정리
    win32gui.ReleaseDC(_PROGRAM_HWND, hwnd_dc)
    mem_dc.DeleteDC()
    win32gui.ReleaseDC(_PROGRAM_HWND, hwnd_dc)
    win32gui.DeleteObject(bmp.GetHandle())

    return bool(ok)


if __name__ == '__main__':
    config.init()
    init()
    time.sleep(2)
    capture()