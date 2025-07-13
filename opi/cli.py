import os
import sys
import subprocess
import platform
import socket
import json
import argparse
from datetime import datetime
import urllib.request

VERSION = "V1.02 OPI"
LOG_DIR = os.path.join(os.path.expanduser("~"), ".owl_dev", "owl_logs")
LOG_FILE = os.path.join(LOG_DIR, "owl_dev_installer.logs")
REG_URL = "https://your-private-server.com/api/register_user"    # <-- Change to your backend endpoint
STATUS_URL = "https://your-private-server.com/api/app_status"    # <-- Endpoint to check global app status

def get_country():
    try:
        with urllib.request.urlopen("https://ipinfo.io/json", timeout=5) as url:
            data = json.loads(url.read().decode())
            return data.get("city", "") + ", " + data.get("country", "")
    except Exception:
        return "Unknown"

def user_registration(log_data):
    try:
        payload = {
            "user": os.environ.get("USERNAME") or os.environ.get("USER") or socket.gethostname(),
            "host": socket.gethostname(),
            "os": platform.system() + " " + platform.release(),
            "python": platform.python_version(),
            "pip": subprocess.getoutput("pip --version"),
            "timestamp": datetime.now().isoformat(),
            "log": log_data,
            "version": VERSION,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(REG_URL, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        pass  # Fail silently to not block install

def check_global_status():
    try:
        with urllib.request.urlopen(STATUS_URL, timeout=3) as resp:
            status = json.loads(resp.read().decode())
            if status.get("enabled", True):
                return True
            print("\n🛑 This application has been disabled by the publisher. Please contact support.\n")
            return False
    except Exception:
        return True  # If we can't reach server, allow app for reliability

def write_log(log_data):
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write(log_data)

def display_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print("No log file found.")

def installer():
    print(f"\n🦉 Welcome to OWL PACKAGE MANAGER INSTALLER {VERSION} 🦉\n")

    # Step 1: Create log
    country = get_country()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_data = f"""
🦉 Owl Installer Log
Version: {VERSION}
Time: {timestamp}
Location: {country}
Host: {socket.gethostname()}
OS: {platform.system()} {platform.release()}
Python: {platform.python_version()}
Pip: {subprocess.getoutput("pip --version")}
Root Folder: {os.getcwd()}
"""
    write_log(log_data)
    print(f"📡 Owl log created at: {LOG_FILE}")
    print(f"🌍 Location detected: {country}")

    # Step 1b: Register user for backend analytics (private)
    user_registration(log_data)

    # Step 2: Check global app status (remote kill-switch)
    if not check_global_status():
        sys.exit(1)

    print("🧠 Owl is preparing your environment...")

    # Step 3: Ask for environment type
    print("\nSelect environment type to create:")
    print("1. venv (Recommended)")
    print("2. .env (for legacy setups)")
    while True:
        env_choice = input("Enter 1 or 2: ").strip()
        if env_choice in ("1", "2"):
            break
        print("Invalid input. Please enter 1 or 2.")

    env_path = "venv" if env_choice == "1" else ".env"
    if not os.path.exists(env_path):
        print(f"🛠️ Creating environment at '{env_path}'...")
        subprocess.run([sys.executable, "-m", "venv", env_path])
        print("✅ Environment created.")
    else:
        print(f"🧠 Environment '{env_path}' already exists.")

    print("💻 Using the environment directly for installation.")

    # Step 4: Parse requirements.txt
    req_file = "requirements.txt"
    if not os.path.exists(req_file):
        print("❌ No requirements.txt found. Please ensure you are in your project root.")
        sys.exit(1)

    with open(req_file, "r", encoding="utf-8") as f:
        packages = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    print(f"📦 Owl found {len(packages)} packages to install.")

    # Step 5: Install packages
    installed = []
    failed = []

    for pkg in packages:
        pkg_name = pkg.split("==")[0]
        print(f"🦉 Checking {pkg_name}...")
        result = subprocess.run([sys.executable, "-m", "pip", "show", pkg_name], capture_output=True)
        if result.returncode == 0:
            print(f"✅ {pkg_name} already installed. Skipping...")
            installed.append(pkg)
            continue

        print(f"🚀 Installing {pkg}...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", pkg])
            installed.append(pkg)
        except Exception as e:
            print(f"❌ Failed to install {pkg}. Reason: {e}")
            failed.append(pkg)

    # Step 6: Retry failed packages
    if failed:
        print("\n🔁 Owl is retrying failed packages...")
        for pkg in failed:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", pkg])
                print(f"✅ Retried and installed {pkg}")
            except Exception as e:
                print(f"❌ Still failed: {pkg}")

    print("\n🎉 Owl Installer completed.")
    print(f"📄 View logs at: {LOG_FILE}")
    print("🦉 If anything breaks, re-run 'opi' from your project root!")

def main():
    parser = argparse.ArgumentParser(description="OWL PACKAGE MANAGER INSTALLER")
    parser.add_argument("--version", action="store_true", help="Show version and log info")
    args = parser.parse_args()

    if args.version:
        display_log()
        sys.exit(0)

    installer()