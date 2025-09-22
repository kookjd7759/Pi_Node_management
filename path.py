# path.py
from __future__ import annotations
import os, sys
from pathlib import Path

def is_frozen() -> bool:
    # PyInstaller onefile/onedir 여부
    return getattr(sys, "frozen", False) is True

def app_dir() -> Path:
    """
    - 쓰기(writable)가 필요한 경로의 기준 폴더.
    - 개발: 이 파일이 있는 폴더
    - 배포: exe가 있는 폴더 (사용자 PC에서 항상 존재)
    """
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent

def resource_dir() -> Path:
    """
    - 읽기 전용 리소스(이미지/아이콘/정적파일)를 찾는 기준 폴더.
    - 개발: 소스 폴더
    - 배포: PyInstaller가 임시로 풀어 둔 _MEIPASS
    """
    if is_frozen():
        # PyInstaller가 리소스를 푸는 임시 폴더
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent

# ------------------------------
# 폴더/파일 경로 정의
# ------------------------------
# 정적 리소스(읽기 전용)
_APP = app_dir()
_IMG = _APP / "btn_img"

BTN_PI_APP        = str(_IMG / "Pi_App.png")
BTN_PI_NODE       = str(_IMG / "Pi_Node.png")
BTN_MINING_STATE  = str(_IMG / "Mining_state.png")
LABEL_SCROLL_SUPPORT = str(_IMG / "scroll_support.png") 
ICON              = str(_IMG / "Pi coin.png") 

# 가변 데이터(쓰기 필요)
DATA_JSON         = str(_APP / "data.json")
PATH_OCR          = str(_APP / "temp"   / "ocr.png")
BASE_RECORD       = str(_APP / "record")
CACHE_DIR         = _APP / "cache"
SCHEDULER_STATE   = str(CACHE_DIR / "scheduler_state.json")

# 최초 실행 시 필요한 폴더 생성
os.makedirs(Path(PATH_OCR).parent, exist_ok=True)
os.makedirs(BASE_RECORD, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# ------------------------------
# 디버그용: 현재 경로 상태 출력(원할 때 호출)
# ------------------------------
def debug_print_paths() -> None:
    print("[path] is_frozen:", is_frozen())
    print("[path] resource_dir:", resource_dir())
    print("[path] app_dir     :", app_dir())
    print("[path] IMG dir     :", _IMG)
    print("[path] DATA_JSON   :", DATA_JSON)
    print("[path] TEMP(OCR)   :", PATH_OCR)
    print("[path] RECORD DIR  :", BASE_RECORD)
    print("[path] CACHE DIR   :", str(CACHE_DIR))
    print("[path] SCHED STATE :", SCHEDULER_STATE)
