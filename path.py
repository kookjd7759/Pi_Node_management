# path.py
import os
import sys
from pathlib import Path

# ================================
# 1) 리소스(Base) 경로: exe 번들/개발모드 겸용
# ================================
def _is_frozen() -> bool:
    return getattr(sys, "frozen", False)

def _base_dir() -> Path:
    if _is_frozen():
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parent

_BASE = _base_dir()

_IMG_DIR = _BASE / "btn_img"
BTN_PI_APP          = str(_IMG_DIR / "Pi_App.png")
BTN_PI_NODE         = str(_IMG_DIR / "Pi_Node.png")
BTN_MINING_STATE    = str(_IMG_DIR / "Mining_state.png")
LABEL_SCROLL_SURPPORT = str(_IMG_DIR / "scroll_surpport.png")
ICON                = str(_BASE / "Pi coin.png")

# ==========================================
# 2) 실행 중 생성되는 데이터(설정/캐시/기록) 경로
#    - OS별 표준 사용자 디렉터리 사용
#    - platformdirs 미설치 시 홈 디렉터리 폴백
# ==========================================
_APPNAME  = "PiNodeManager"
_APPAUTH  = "KookJD"  # Windows에서만 의미(로밍 구분 등). 자유 변경 가능.

def _user_dirs():
    """
    (data_dir, cache_dir, log_dir)를 반환.
    platformdirs가 있으면 표준 경로, 없으면 홈 폴백.
    """
    try:
        from platformdirs import PlatformDirs
        d = PlatformDirs(appname=_APPNAME, appauthor=_APPAUTH, roaming=False)
        data_dir  = Path(d.user_data_dir)   # 설정/지속 데이터
        cache_dir = Path(d.user_cache_dir)  # 캐시/임시
        log_dir   = Path(d.user_log_dir)    # 로그
    except Exception:
        home = Path.home() / f".{_APPNAME}"
        data_dir  = home / "data"
        cache_dir = home / "cache"
        log_dir   = home / "logs"

    # 디렉터리 보장
    for p in (data_dir, cache_dir, log_dir):
        p.mkdir(parents=True, exist_ok=True)
    return data_dir, cache_dir, log_dir

_DATA_DIR, _CACHE_DIR, _LOG_DIR = _user_dirs()

# 하위 폴더(스크린샷 보관용)
_RECORD_DIR = _DATA_DIR / "record"
_RECORD_DIR.mkdir(parents=True, exist_ok=True)

# 파일 경로 노출 (다른 모듈들이 문자열로 사용하므로 str로 변환)
DATA_JSON           = str(_DATA_DIR / "data.json")
PATH_OCR            = str(_CACHE_DIR / "ocr.png")
BASE_RECORD         = str(_RECORD_DIR)
PATH_scheduler_state= str(_CACHE_DIR / "scheduler_state.json")

# ==========================================
# 3) 첫 실행 보조: 필수 파일 생성(없으면)
#    - cycle.py/tools.py가 바로 열람/쓰기 하므로 안전장치
# ==========================================
def _ensure_file(path: str, default_text: str = ""):
    p = Path(path)
    if not p.exists():
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(default_text, encoding="utf-8")
        except Exception:
            # 권한 등으로 실패해도 애플리케이션이 치명적으로 죽지 않도록 조용히 패스
            pass

# data.json이 없으면 기본 스켈레톤 생성
_ensure_file(DATA_JSON, default_text='{\n  "exe_path": ""\n}\n')
# 캐시/상태 파일은 필요 시 생성되므로 미리 만들 필요 없음

def print_all_paths():
    """현재 프로젝트에서 사용하는 주요 경로들을 전부 출력한다."""
    print("===== PATH SUMMARY =====")
    print(f"_BASE                = {_BASE}")
    print(f"IMG_DIR              = {_IMG_DIR}")
    print(f"BTN_PI_APP           = {BTN_PI_APP}")
    print(f"BTN_PI_NODE          = {BTN_PI_NODE}")
    print(f"BTN_MINING_STATE     = {BTN_MINING_STATE}")
    print(f"LABEL_SCROLL_SURPPORT= {LABEL_SCROLL_SURPPORT}")
    print(f"ICON                 = {ICON}")
    print(f"DATA_JSON            = {DATA_JSON}")
    print(f"PATH_OCR             = {PATH_OCR}")
    print(f"BASE_RECORD          = {BASE_RECORD}")
    print(f"PATH_scheduler_state = {PATH_scheduler_state}")
    print("========================")