import pyautogui
import time
from pynput import keyboard
import threading

w_hold_enabled = False
w_hold_thread = None
lock = threading.Lock()

def w_hold_loop():
    global w_hold_enabled
    while w_hold_enabled:
        pyautogui.keyDown('w')
        pyautogui.keyDown("space")
        time.sleep(0.1)# キーを押し続ける間隔 (調整可能)
    pyautogui.keyUp('w')
    pyautogui.keyUp("space")

def on_press(key):
    global w_hold_enabled, w_hold_thread

    if hasattr(key, 'char'):
        if key.char == '\\':
            with lock:
                w_hold_enabled = not w_hold_enabled
                print(f"[Notfication] \\ キーが押されました。Wキーとスペースキーを長押し状態は {'ON' if w_hold_enabled else 'OFF'} です。")

                if w_hold_enabled and (w_hold_thread is None or not w_hold_thread.is_alive()):
                    w_hold_thread = threading.Thread(target=w_hold_loop, daemon=True)
                    w_hold_thread.start()
                elif not w_hold_enabled and w_hold_thread is not None and w_hold_thread.is_alive():
                    pass

def on_release(key):
    if hasattr(key, 'char') and key.char == ']':
        # ]キーでプログラムを終了
        return False

if __name__ == "__main__":
    print("[Notfication]")
    print(" - \\キーを押すとWキー長押しのON/OFFが切り替わります。")
    print(" - ]キーでプログラムを終了します。")

    with keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()

    print("[Notfication] プログラムを終了しました。")
