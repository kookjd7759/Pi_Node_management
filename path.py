# path.py
from __future__ import annotations
import os, sys
from pathlib import Path

def app_dir() -> Path:
    if getattr(sys, "frozen", False) is True:
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

_APP = app_dir()
_IMG = _APP / "btn_img"

BTN_PI_APP        = str(_IMG / "Pi_App.png")
BTN_PI_NODE       = str(_IMG / "Pi_Node.png")
BTN_MINING_STATE  = str(_IMG / "Mining_state.png")
LABEL_SCROLL_SUPPORT = str(_IMG / "scroll_support.png") 
ICON              = str(_IMG / "Pi coin.png") 

DATA_JSON         = str(_APP / "data.json")
PATH_OCR          = str(_APP / "temp"   / "ocr.png")
BASE_RECORD       = str(_APP / "record")
CACHE_DIR         = _APP / "cache"
SCHEDULER_STATE   = str(CACHE_DIR / "scheduler_state.json")

os.makedirs(Path(PATH_OCR).parent, exist_ok=True)
os.makedirs(BASE_RECORD, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(SCHEDULER_STATE, exist_ok=True)

EXE_PATH = ''
def cache_PATH(path):
    global EXE_PATH
    EXE_PATH = path
    print(f'cache the exe path - {EXE_PATH}')

def debug_print_paths() -> None:
    print("[path] app_dir     :", app_dir())
    print("[path] IMG dir     :", _IMG)
    print("[path] DATA_JSON   :", DATA_JSON)
    print("[path] TEMP(OCR)   :", PATH_OCR)
    print("[path] RECORD DIR  :", BASE_RECORD)
    print("[path] CACHE DIR   :", str(CACHE_DIR))
    print("[path] SCHED STATE :", SCHEDULER_STATE)
    print("[path] BTN_PI_APP :", BTN_PI_APP)
    print("[path] BTN_PI_NODE :", BTN_PI_NODE)
    print("[path] BTN_MINING_STATE :", BTN_MINING_STATE)
    print("[path] SCHEDULER_STATE :", SCHEDULER_STATE)
    print("[path] EXE_PATH :", EXE_PATH)
