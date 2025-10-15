from __future__ import annotations
import os

_BASE = f"{os.path.dirname(os.path.abspath(__file__))}/"
_IMG = _BASE + "btn_img/"

BTN_PI_APP              = _IMG + "Pi_App.png"
BTN_PI_NODE             = _IMG + "Pi_Node.png"
BTN_MINING_STATE        = _IMG + "Mining_state.png"
LABEL_SCROLL_SUPPORT    = _IMG + "scroll_support.png"
ICON                    = _IMG + "Pi coin.png"

DATA_JSON         = _BASE + "data.json"
PATH_OCR          = _BASE + "temp/ocr.png"
BASE_RECORD       = _BASE + "record"
SCHEDULER_STATE   = _BASE + "cache/scheduler_state.json"

def debug_print_paths() -> None:
    print("[path] IMG dir     :", _IMG)
    print("[path] DATA_JSON   :", DATA_JSON)
    print("[path] TEMP(OCR)   :", PATH_OCR)
    print("[path] RECORD DIR  :", BASE_RECORD)
    print("[path] SCHED STATE :", SCHEDULER_STATE)
    print("[path] BTN_PI_APP :", BTN_PI_APP)
    print("[path] BTN_PI_NODE :", BTN_PI_NODE)
    print("[path] BTN_MINING_STATE :", BTN_MINING_STATE)
    print("[path] SCHEDULER_STATE :", SCHEDULER_STATE)

debug_print_paths()