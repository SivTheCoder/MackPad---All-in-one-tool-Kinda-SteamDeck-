import json
import threading
import time
import subprocess
import ctypes
from pathlib import Path

from flask import Flask, jsonify, request, render_template

try:
    import keyboard
except ImportError:
    keyboard = None

try:
    import pyautogui
except ImportError:
    pyautogui = None


app = Flask(__name__)
MACROS_FILE = Path("macros.json")


def load_macros():
    if MACROS_FILE.exists():
        return json.loads(MACROS_FILE.read_text())
    return []


def save_macros(macros):
    MACROS_FILE.write_text(json.dumps(macros, indent=2))


class ActionExecutor:
    @staticmethod
    def open_app(path):
        try:
            subprocess.Popen(path, shell=True)
            return True, f"Opened {path}"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def media_control(key):
        VK_MAP = {
            "play_pause": 0xB3,
            "next_track": 0xB0,
            "prev_track": 0xB1,
            "stop": 0xB2,
        }

        vk = VK_MAP.get(key)
        if not vk:
            return False, "Invalid media key"

        ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
        time.sleep(0.05)
        ctypes.windll.user32.keybd_event(vk, 0, 2, 0)

        return True, f"Media: {key}"

    @staticmethod
    def system_control(cmd):
        if cmd == "lock":
            ctypes.windll.user32.LockWorkStation()
            return True, "Locked"

        KEY_MAP = {
            "volume_up": 0xAF,
            "volume_down": 0xAE,
            "mute": 0xAD,
        }

        vk = KEY_MAP.get(cmd)
        if vk:
            for _ in range(2):
                ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
                time.sleep(0.05)
                ctypes.windll.user32.keybd_event(vk, 0, 2, 0)
            return True, cmd

        if cmd == "brightness_up":
            subprocess.run(
                [
                    "powershell",
                    "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,100)"
                ],
                shell=True,
            )
            return True, "Brightness up"

        if cmd == "brightness_down":
            subprocess.run(
                [
                    "powershell",
                    "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,10)"
                ],
                shell=True,
            )
            return True, "Brightness down"

        return False, "Unknown system command"

    @staticmethod
    def hotkey(keys):
        if not pyautogui:
            return False, "pyautogui not installed"
        pyautogui.hotkey(*keys.split("+"))
        return True, f"Hotkey {keys}"

    @staticmethod
    def type_text(text):
        if not pyautogui:
            return False, "pyautogui not installed"
        pyautogui.write(text, interval=0.02)
        return True, "Typed text"

    @staticmethod
    def delay(ms):
        time.sleep(ms / 1000)
        return True, f"Delay {ms}ms"

    @staticmethod
    def execute(action):
        atype = action.get("type")

        if atype == "open_app":
            return ActionExecutor.open_app(action.get("path"))

        elif atype == "media":
            return ActionExecutor.media_control(action.get("key"))

        elif atype == "system":
            return ActionExecutor.system_control(action.get("cmd"))

        elif atype == "hotkey":
            return ActionExecutor.hotkey(action.get("keys"))

        elif atype == "type_text":
            return ActionExecutor.type_text(action.get("text"))

        elif atype == "delay":
            return ActionExecutor.delay(action.get("ms", 500))

        elif atype == "sequence":
            for step in action.get("steps", []):
                ok, msg = ActionExecutor.execute(step)
                if not ok:
                    return False, msg
            return True, "Sequence executed"

        return False, "Unknown action"



# HOTKEY MANAGER (Debug the memory leak error)

class HotkeyManager:
    def __init__(self):
        self.active = False
        self.lock = threading.Lock()

    def start(self, macros):
        if not keyboard:
            print("keyboard module not installed")
            return

        with self.lock:
            keyboard.unhook_all()

            for macro in macros:
                hk = macro.get("hotkey")
                action = macro.get("action")

                if not hk:
                    continue

                try:
                    keyboard.add_hotkey(
                        hk,
                        lambda a=action: ActionExecutor.execute(a)
                    )
                except Exception as e:
                    print("Hotkey error:", e)

            self.active = True


hotkey_manager = HotkeyManager()


def restart_hotkeys():
    macros = load_macros()
    threading.Thread(
        target=lambda: hotkey_manager.start(macros),
        daemon=True
    ).start()



# API ROUTES

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/macros", methods=["GET"])
def get_macros():
    return jsonify(load_macros())


@app.route("/api/macros", methods=["POST"])
def create_macro():
    macros = load_macros()
    data = request.json

    data["id"] = str(int(time.time() * 1000))
    macros.append(data)

    save_macros(macros)
    restart_hotkeys()

    return jsonify(data)


@app.route("/api/macros/<macro_id>", methods=["PUT"])
def update_macro(macro_id):
    macros = load_macros()

    for i, m in enumerate(macros):
        if m["id"] == macro_id:
            macros[i] = request.json
            save_macros(macros)
            restart_hotkeys()
            return jsonify(macros[i])

    return jsonify({"error": "Not found"}), 404


@app.route("/api/macros/<macro_id>", methods=["DELETE"])
def delete_macro(macro_id):
    macros = load_macros()
    macros = [m for m in macros if m["id"] != macro_id]

    save_macros(macros)
    restart_hotkeys()

    return jsonify({"ok": True})


@app.route("/api/execute/<macro_id>", methods=["POST"])
def execute_macro(macro_id):
    macros = load_macros()

    for m in macros:
        if m["id"] == macro_id:
            ok, msg = ActionExecutor.execute(m["action"])
            return jsonify({"ok": ok, "message": msg})

    return jsonify({"error": "Not found"}), 404


@app.route("/api/status")
def status():
    return jsonify({
        "listener_active": hotkey_manager.active,
        "macro_count": len(load_macros())
    })



# MAIN (Webapp implementation is not ez, need to build it)

if __name__ == "__main__":
    restart_hotkeys()
    print("\n🚀 MacroPad running at http://localhost:5000\n")
    app.run(port=5000, debug=False)
