import pyautogui
import time
from pynput import keyboard
import threading
import math
import pyperclip  # 忘れずにインポート

BOOT_NOTIFY = True
BOT_NAME = "Chicken Bot"
VERSION = "0.0.2"

PRESS_DURATION = 1.0      # 矢印キーを押す時間 (秒) # 設定可能
WAIT_DURATION = 1.0       # 左右の移動の間の待ち時間 (秒) # 設定可能
RUNNING_CAMERA = False
PAUSED_CAMERA = False
Q_PRESSED_START_TIME = None
EXIT_LONG_PRESS_DELAY = 2      # qキー長押しで終了する秒数
SEQUENCE_THREAD = None    # シーケンス処理スレッドを保持する変数

AUTO_SAVE_CAMERA = True

TARGET_COLOR_RGB = (77, 17, 17)      # 監視したい色のRGB値 (例: 赤色)
TOLERANCE = 15            # 許容する色の誤差
MONITORING_INTERVAL = 1       # 色をチェックする間隔 (秒) # 設定可能
MONITORING_ENABLED = False      # 自動モニタリングの状態
DETECTION_FLAG = False        # 検知メッセージを一度だけ表示するためのフラグ
MONITORING_THREAD = None      # モニタリングスレッドを保持する変数

LEFT_CLICK_HOLD_ENABLED = False
LEFT_CLICK_HOLD_THREAD = None

W_HOLD_ENABLED = False
W_HOLD_THREAD = None
SPACE_HOLD_ENABLED = False
SPACE_HOLD_THREAD = None

time.sleep(5)
def chat(text):
    pyautogui.press('t')
    time.sleep(1)
    pyautogui.press("enter")
    time.sleep(0.2)
    pyperclip.copy(text)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.2)      # 貼り付け (Windows/Linux)
    pyautogui.press("enter")
    time.sleep(0.5)
    pyautogui.press("esc")

def command(text):
    pyautogui.press('t')
    time.sleep(1)
    pyautogui.press("enter")
    time.sleep(0.2)
    pyperclip.copy(text)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.2)      # 貼り付け (Windows/Linux)
    pyautogui.press("enter")


def color_distance(color1, color2):
    """2つのRGBカラーの距離を計算する"""
    return math.sqrt(
        (color1[0] - color2[0])**2 +
        (color1[1] - color2[1])**2 +
        (color1[2] - color2[2])**2
    )

def check_center_color():
    global DETECTION_FLAG
    try:
        screen_width, screen_height = pyautogui.size()
        center_x = screen_width // 2
        center_y = screen_height // 2 - 15
        center_color_rgb = pyautogui.pixel(center_x, center_y)
        print(f"現在の中心の色 (モニタリング中): {center_color_rgb}")
        distance = color_distance(center_color_rgb, TARGET_COLOR_RGB)

        if distance <= TOLERANCE and not DETECTION_FLAG:
            print("侵入検知を検知しました。")
            chat(f"§e[{BOT_NAME}] §a警告: 基地への侵入を検知しました！ 進入者である可能性があるプレイヤーは")
            time.sleep(1)
            command("/me §e>>§a @p[rm=1,r=15] です。")
            DETECTION_FLAG = True
        elif distance > TOLERANCE:
            # 色が許容範囲外になったらフラグをリセット
            print("問題はありませんでした。")
            DETECTION_FLAG = False

    except Exception as e:
        print(f"モニタリング中にエラーが発生しました: {e}")

def monitoring_loop():
    global MONITORING_ENABLED
    while MONITORING_ENABLED:
        check_center_color()
        time.sleep(MONITORING_INTERVAL)

def left_click_hold_loop():
    global LEFT_CLICK_HOLD_ENABLED
    while LEFT_CLICK_HOLD_ENABLED:
        pyautogui.mouseDown(button='left')
        # 長押しを続けるための短いスリープ
        time.sleep(0.1)
    pyautogui.mouseUp(button='left')

def w_hold_loop():
    global W_HOLD_ENABLED, SPACE_HOLD_ENABLED
    while W_HOLD_ENABLED:
        pyautogui.keyDown('w')
        if SPACE_HOLD_ENABLED:
            pyautogui.keyDown('space')
        time.sleep(0.1)
    pyautogui.keyUp('w')
    if SPACE_HOLD_ENABLED:
        pyautogui.keyUp('space')

if BOOT_NOTIFY:
    import pyperclip # pyperclip は必要な時のみインポート
    chat(f"§e{BOT_NAME} {VERSION} starting...")
    time.sleep(2)
    chat(f"§astarting complete.")

def camera_sequence_loop():
    global RUNNING_CAMERA, PAUSED_CAMERA
    while RUNNING_CAMERA and not PAUSED_CAMERA:
        pyautogui.keyDown('right')
        time.sleep(PRESS_DURATION)
        pyautogui.keyUp('right')
        time.sleep(WAIT_DURATION)
        if not RUNNING_CAMERA or PAUSED_CAMERA:
            break
        pyautogui.keyDown('left')
        time.sleep(PRESS_DURATION)
        pyautogui.keyUp('left')
        time.sleep(WAIT_DURATION)
        if not RUNNING_CAMERA or PAUSED_CAMERA:
            break

def on_press(key):
    global RUNNING_CAMERA, PAUSED_CAMERA, Q_PRESSED_START_TIME, SEQUENCE_THREAD, TARGET_COLOR_RGB, MONITORING_ENABLED, MONITORING_THREAD, DETECTION_FLAG, LEFT_CLICK_HOLD_ENABLED, LEFT_CLICK_HOLD_THREAD, W_HOLD_ENABLED, W_HOLD_THREAD, SPACE_HOLD_ENABLED, SPACE_HOLD_THREAD
    if hasattr(key, 'char'):
        if key.char == 'x' and not RUNNING_CAMERA:
            print("[Notification] カメラ移動シーケンスを開始します (右{}秒 => 待ち{}秒 => 左{}秒 => 待ち{}秒 の繰り返し)。".format(
                PRESS_DURATION, WAIT_DURATION, PRESS_DURATION, WAIT_DURATION
            ))
            RUNNING_CAMERA = True
            PAUSED_CAMERA = False
            SEQUENCE_THREAD = threading.Thread(target=camera_sequence_loop, daemon=True)
            SEQUENCE_THREAD.start()
        elif key.char == 'q':
            if Q_PRESSED_START_TIME is None:
                print("[Notification] qキーが押されました。短く押すと一時停止、長押しでプログラムを停止します。")
                Q_PRESSED_START_TIME = time.time()
            elif RUNNING_CAMERA and not PAUSED_CAMERA:
                print("[Notification] カメラ移動シーケンスを一時停止します。")
                PAUSED_CAMERA = True
        elif key.char == 'x' and RUNNING_CAMERA and PAUSED_CAMERA:
            print("[Notification] カメラ移動シーケンスを再開します。")
            PAUSED_CAMERA = False
            if SEQUENCE_THREAD is None or not SEQUENCE_THREAD.is_alive():
                SEQUENCE_THREAD = threading.Thread(target=camera_sequence_loop, daemon=True)
                SEQUENCE_THREAD.start()
        elif key.char == "m":
            MONITORING_ENABLED = not MONITORING_ENABLED
            DETECTION_FLAG = False # ON/OFF時にフラグをリセット
            if MONITORING_ENABLED:
                print(f"[Notification] 自動モニタリングを開始します (間隔: {MONITORING_INTERVAL}秒)。")
                MONITORING_THREAD = threading.Thread(target=monitoring_loop, daemon=True)
                MONITORING_THREAD.start()
            else:
                print("[Notification] 自動モニタリングを停止します。")
        elif key.char == 'o':
            LEFT_CLICK_HOLD_ENABLED = not LEFT_CLICK_HOLD_ENABLED
            if LEFT_CLICK_HOLD_ENABLED:
                print("[Notification] 左クリック長押しをONにします。")
                LEFT_CLICK_HOLD_THREAD = threading.Thread(target=left_click_hold_loop, daemon=True)
                LEFT_CLICK_HOLD_THREAD.start()
            else:
                print("[Notification] 左クリック長押しをOFFにします。")
        elif key.char == 'n':
            W_HOLD_ENABLED = not W_HOLD_ENABLED
            if W_HOLD_ENABLED:
                print("[Notification] Wキー長押しをONにします。")
                W_HOLD_THREAD = threading.Thread(target=w_hold_loop, daemon=True)
                W_HOLD_THREAD.start()
            else:
                print("[Notification] Wキー長押しをOFFにします。")
        elif key.char == ' ':
            SPACE_HOLD_ENABLED = not SPACE_HOLD_ENABLED
            if SPACE_HOLD_ENABLED and W_HOLD_ENABLED:
                print("[Notification] Wキー長押し中にスペースキー長押しをONにします。")
            elif SPACE_HOLD_ENABLED and not W_HOLD_ENABLED:
                print("[Notification] Wキー長押しがOFFのため、スペースキー長押しは有効になりません。")
            else:
                print("[Notification] スペースキー長押しをOFFにします。")


def on_release(key):
    global Q_PRESSED_START_TIME, RUNNING_CAMERA, SEQUENCE_THREAD, MONITORING_ENABLED, MONITORING_THREAD, LEFT_CLICK_HOLD_ENABLED, LEFT_CLICK_HOLD_THREAD, W_HOLD_ENABLED, W_HOLD_THREAD, SPACE_HOLD_ENABLED, SPACE_HOLD_THREAD
    if hasattr(key, 'char'):
        if key.char == 'q':
            if Q_PRESSED_START_TIME is not None:
                elapsed_time = time.time() - Q_PRESSED_START_TIME
                if elapsed_time >= EXIT_LONG_PRESS_DELAY:
                    print("[Notification] qキーが長押しされたため、プログラムを停止します。")
                    RUNNING_CAMERA = False
                    MONITORING_ENABLED = False # モニタリングも停止
                    LEFT_CLICK_HOLD_ENABLED = False # 左クリック長押しも停止
                    W_HOLD_ENABLED = False # Wキー長押しも停止
                    SPACE_HOLD_ENABLED = False # スペースキー長押しも停止
                    if SEQUENCE_THREAD and SEQUENCE_THREAD.is_alive():
                        RUNNING_CAMERA = False # スレッド内のループを抜けるように設定
                        SEQUENCE_THREAD.join(timeout=1) # スレッドの終了を待つ（タイムアウト付き）
                    if MONITORING_THREAD and MONITORING_THREAD.is_alive():
                        MONITORING_ENABLED = False
                        MONITORING_THREAD.join(timeout=1)
                    if LEFT_CLICK_HOLD_THREAD and LEFT_CLICK_HOLD_THREAD.is_alive():
                        LEFT_CLICK_HOLD_ENABLED = False
                        LEFT_CLICK_HOLD_THREAD.join(timeout=1)
                    if W_HOLD_THREAD and W_HOLD_THREAD.is_alive():
                        W_HOLD_ENABLED = False
                        W_HOLD_THREAD.join(timeout=1)
                    if SPACE_HOLD_THREAD and SPACE_HOLD_THREAD.is_alive():
                        SPACE_HOLD_ENABLED = False
                        SPACE_HOLD_THREAD.join(timeout=1)
                    return False    # Listener を停止
                Q_PRESSED_START_TIME = None

if __name__ == "__main__":
    print(f"\033[3m")
    print("「x」キーでカメラ移動シーケンスを開始/再開します。")
    print("右矢印キーと左矢印キーをそれぞれ {} 秒間押します。".format(PRESS_DURATION))
    print("左右の移動の間に {} 秒間待ちます。".format(WAIT_DURATION))
    print("「q」キーを短く押すと一時停止、長押しでプログラムを OFF にします。")
    print("「m」キーで自動モニタリングの ON / OFF を切り替えます (間隔: {}秒)。".format(MONITORING_INTERVAL))
    print("「o」キーで左クリック長押しの ON / OFF を切り替えます。")
    print("「n」キーでWキー長押しの ON / OFF を切り替えます。")
    print("スペースキーを押すと、Wキー長押しがONの場合にスペースキーも長押しします。")
    print("押す時間、待ち時間、監視間隔はコード内の変数を変更して調整できます。")

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    print("プログラムを終了します。")