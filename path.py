import sys
import os

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))
BASE_PATH = get_base_path()

### generally program path
# = C:\\Users\\(user_name)\\AppData\\Local\\Programs\\pi-network-desktop\\Pi Network
def expect_program_path():
    expected_path = f'{os.environ.get("USERPROFILE")}\\AppData\\Local\\Programs\\Pi-network-desktop\\Pi Network.exe'
    if os.path.exists(expected_path):
        return expected_path
    else:
        return None

CONFIG_PATH = BASE_PATH + '\\config.json'
RECENT_STATE = BASE_PATH + '\\image\\recent.png'

if __name__ == '__main__':
    print(f'BASE_PATH - {BASE_PATH}')
    print(f'CONFIG_PATH - {CONFIG_PATH}')
    print(os.environ.get("USERPROFILE"))