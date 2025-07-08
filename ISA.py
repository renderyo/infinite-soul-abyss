import os
import subprocess
import psutil
import time
import sys
import platform
import threading

# 🔧 Change this to define how many layers ISA will descend through
ISA_LAYER_COUNT = 3

METHODS_DIR = os.path.join(os.path.dirname(__file__), "methods")

def play_sound_blocking(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    system = platform.system()

    if system == "Windows":
        subprocess.run([
            "powershell", "-c", f"(New-Object Media.SoundPlayer '{filepath}').PlaySync();"
        ], check=False)
    elif system == "Darwin":
        subprocess.run(["afplay", filepath], check=False)
    else:
        try:
            subprocess.run(
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", filepath],
                check=False
            )
        except FileNotFoundError:
            try:
                subprocess.run(["aplay", filepath], check=False)
            except FileNotFoundError:
                print("[Sound Error] No supported sound player found.")

def run_method_script(script_path, pid):
    print(f"[DEBUG] Running method script: {script_path} with python: {sys.executable}")
    try:
        result = subprocess.run(
            [sys.executable, script_path, str(pid)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=15
        )
        stdout = result.stdout.decode().strip()
        stderr = result.stderr.decode().strip()
        print(f"[DEBUG] Return code: {result.returncode}")
        if stdout:
            print(f"[DEBUG] Stdout:\n{stdout}")
        if stderr:
            print(f"[DEBUG] Stderr:\n{stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"[ERROR] Failed to run {script_path}: {e}")
        return False

def get_methods_for_layer(layer_num):
    prefix = f"layer{layer_num}_method"
    scripts = []
    print(f"[DEBUG] Looking for method scripts in folder: {METHODS_DIR}")
    try:
        for filename in os.listdir(METHODS_DIR):
            if filename.startswith(prefix) and filename.endswith(".py"):
                scripts.append(os.path.join(METHODS_DIR, filename))
        scripts.sort(key=lambda f: int(os.path.basename(f).split("method")[1].split(".")[0]))
    except FileNotFoundError:
        print(f"[ERROR] Methods directory '{METHODS_DIR}' not found.")
    return scripts

def fancy_banner(method_name):
    print("\n" + "="*60)
    print(f"⛧ DESCENDING INTO: {method_name.upper()} ⛧")
    print("="*60 + "\n")

def infinite_soul_abyss(pid):
    if not psutil.pid_exists(pid):
        print(f"Process with PID {pid} does not exist.")
        return

    print(f"Target PID: {pid}")
    print("Launching INFINITE SOUL ABYSS...\n")
    music_thread = threading.Thread(target=play_sound_blocking, args=("music.wav",), daemon=True)
    music_thread.start()

    try:
        for layer in range(1, ISA_LAYER_COUNT + 1):
            print(f"=== Entering Layer {layer} ===")
            methods = get_methods_for_layer(layer)
            if not methods:
                print(f"[WARN] No methods found for layer {layer}.")
            for i, method_script in enumerate(methods, 1):
                method_name = os.path.basename(method_script)
                fancy_banner(method_name)

                play_sound_blocking("descend.wav")
                play_sound_blocking("attack.wav")

                print(f"Running method {i}: {method_name}")
                success = run_method_script(method_script, pid)

                if not psutil.pid_exists(pid):
                    print("Process terminated successfully!")
                    time.sleep(0.5)
                    play_sound_blocking("end.wav")
                    play_sound_blocking("kill.wav")
                    input("Press any key to exit...")
                    return

                if success:
                    print(f"Method {i} reported success, but process still alive. Continuing...\n")
                else:
                    print(f"Method {i} failed.\n")

                time.sleep(0.1)
    finally:
        music_thread.join(timeout=1)

    print("Infinite Soul Abyss failed to terminate the target process.")

def infinite_soul_abyss_debug():
    print("DEBUG MODE: Infinite Soul Abyss Visual Test")
    music_thread = threading.Thread(target=play_sound_blocking, args=("music.wav",), daemon=True)
    music_thread.start()

    try:
        for layer in range(1, ISA_LAYER_COUNT + 1):
            print(f"=== Simulating Layer {layer} ===")
            methods = get_methods_for_layer(layer)
            if not methods:
                print(f"[WARN] No methods found for layer {layer}.")
            for i, method_script in enumerate(methods, 1):
                method_name = os.path.basename(method_script)
                fancy_banner(method_name)

                play_sound_blocking("descend.wav")
                play_sound_blocking("attack.wav")

                print(f"DEBUG Running method {i}: {method_name}")
                success = run_method_script(method_script, 0)
                print("✓ Executed." if success else "✗ Failed.")
                time.sleep(0.3)
    finally:
        music_thread.join(timeout=1)

    print("DEBUG sequence complete.")

if __name__ == "__main__":
    target = input("Enter PID of target process (or type DEBUG): ").strip()
    if target.upper() == "DEBUG":
        infinite_soul_abyss_debug()
        input("Press any key to exit...")
    elif not target.isdigit():
        print("Invalid PID: input is not numeric.")
    else:
        pid = int(target)
        if not psutil.pid_exists(pid):
            print(f"Process with PID {pid} does not exist.")
        else:
            infinite_soul_abyss(pid)
