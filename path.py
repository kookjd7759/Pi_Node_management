import sys
import os

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))
BASE_PATH = get_base_path()
IMG_BASE = BASE_PATH + '\\image'

### generally program path
# = C:\\Users\\(user_name)\\AppData\\Local\\Programs\\pi-network-desktop\\Pi Network
def expect_program_path():
    expected_path = f'{os.environ.get("USERPROFILE")}\\AppData\\Local\\Programs\\Pi-network-desktop\\Pi Network.exe'
    if os.path.exists(expected_path):
        return expected_path
    else:
        return None

CONFIG_PATH = BASE_PATH + '\\config.json'

ICON = IMG_BASE + '\\icon.png'

IMG_RECENT_STATE = IMG_BASE + '\\recent.png'
IMG_MININGRATE_TXT = IMG_BASE + '\\data\\basic_mining_rate_txt.png'
IMG_LOGIN_BTN = IMG_BASE + '\\data\\login_btn.png'
IMG_PIAPP_BTN = IMG_BASE + '\\data\\Pi_App_btn.png'
IMG_STATUS_BTN = IMG_BASE + '\\data\\status_btn.png'

if __name__ == '__main__':
    print(f'BASE_PATH - {BASE_PATH}')
    print(f'IMG_BASE - {IMG_BASE}')
    print(f'ICON - {ICON}')
    print(f'CONFIG_PATH - {CONFIG_PATH}')
    print(f'IMG_RECENT_STATE - {IMG_RECENT_STATE}')
    print(f'IMG_MININGRATE_TXT - {IMG_MININGRATE_TXT}')
    print(f'IMG_LOGIN_BTN - {IMG_LOGIN_BTN}')
    print(f'IMG_PIAPP_BTN - {IMG_PIAPP_BTN}')
    print(f'IMG_STATUS_BTN - {IMG_STATUS_BTN}')
    print(os.environ.get("USERPROFILE"))