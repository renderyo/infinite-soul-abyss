import os
import subprocess
import psutil
import time
import sys
import platform
import threading

METHODS_DIR = os.path.join(os.path.dirname(__file__), "methods")

def play_sound_blocking(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    system = platform.system()

    if system == "Windows":
        # Use PlaySync so it blocks till done
        subprocess.run([
            "powershell", "-c", f"(New-Object Media.SoundPlayer '{filepath}').PlaySync();"
        ], check=False)
    elif system == "Darwin":
        # afplay blocks until done
        subprocess.run(["afplay", filepath], check=False)
    else:
        # Linux: use ffplay or aplay blocking call
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
            print(f"[DEBUG] Found file: {filename}")
            if filename.startswith(prefix) and filename.endswith(".py"):
                full_path = os.path.join(METHODS_DIR, filename)
                scripts.append(full_path)
        # sort by method number extracted from filename
        scripts.sort(key=lambda f: int(os.path.basename(f).split("method")[1].split(".")[0]))
    except FileNotFoundError:
        print(f"[ERROR] Methods directory '{METHODS_DIR}' not found.")
    print(f"[DEBUG] Methods for layer {layer_num}: {scripts}")
    return scripts

def infinite_soul_abyss(pid):
    if not psutil.pid_exists(pid):
        print(f"Process with PID {pid} does not exist.")
        return

    print(f"Target PID: {pid}")
    print("Starting Infinite Soul Abyss...")
    music_thread = threading.Thread(target=play_sound_blocking, args=("music.wav",), daemon=True)
    music_thread.start()

    try:
        for layer in range(1, 4):
            print(f"=== Layer {layer} ===")
            methods = get_methods_for_layer(layer)
            if not methods:
                print(f"[WARN] No methods found for layer {layer}.")
            for i, method_script in enumerate(methods, 1):
                print(f"Running method {i}: {os.path.basename(method_script)}")
                success = run_method_script(method_script, pid)
                if not psutil.pid_exists(pid):
                    print("Process terminated successfully!")
                    time.sleep(0.5)
                    play_sound_blocking("end.wav")
                    play_sound_blocking("kill.wav")
                    input("Press any key to exit...")
                    return
                if success:
                    print(f"Method {i} reported success, but process still alive, continuing...")
                else:
                    print(f"Method {i} failed.")
                time.sleep(0.3)
    finally:
        music_thread.join(timeout=1)

    print("Failed to terminate process.")

def infinite_soul_abyss_debug():
    print("Starting Infinite Soul Abyss in DEBUG mode (no target process)...")
    music_thread = threading.Thread(target=play_sound_blocking, args=("music.wav",), daemon=True)
    music_thread.start()

    try:
        for layer in range(1, 4):
            print(f"=== Layer {layer} ===")
            methods = get_methods_for_layer(layer)
            if not methods:
                print(f"[WARN] No methods found for layer {layer}.")
            for i, method_script in enumerate(methods, 1):
                print(f"Running method {i}: {os.path.basename(method_script)}")
                # Use dummy PID 0 in debug mode
                success = run_method_script(method_script, 0)
                if success:
                    print(f"Method {i} executed successfully.")
                else:
                    print(f"Method {i} failed.")
                time.sleep(0.3)
    finally:
        music_thread.join(timeout=1)

    print("DEBUG mode finished.")

if __name__ == "__main__":
    target = input("Enter PID of target process (or type DEBUG): ").strip()
    print(f"[DEBUG] Raw PID input: '{target}'")
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
            print(f"[DEBUG] Parsed PID: {pid}")
            infinite_soul_abyss(pid)
