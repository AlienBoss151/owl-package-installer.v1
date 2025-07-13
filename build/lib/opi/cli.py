import os
import sys
import subprocess
import platform
import socket
import json
import argparse
from datetime import datetime
import urllib.request

VERSION = "V1.0 OPI"
USER = os.environ.get("USERNAME") or os.environ.get("USER") or socket.gethostname()
CURRENT_DIR = os.getcwd()
LAST_FOLDER = os.path.basename(CURRENT_DIR)
BRAIN_DIR = os.path.join(CURRENT_DIR, ".owl_brain")
CHILD_LOG = os.path.join(BRAIN_DIR, "activate_owl_child.logs")
LOG_DIR = os.path.join(os.path.expanduser("~"), ".owl_dev", "owl_logs")
LOG_FILE = os.path.join(LOG_DIR, "owl_dev_installer.logs")
REG_URL = "https://api/register_user"
STATUS_URL = "https://my/api/app_status"

def color(text, code="36"):
    return f"\033[{code}m{text}\033[0m"

def get_country():
    try:
        with urllib.request.urlopen("https://ipinfo.io/json", timeout=5) as url:
            data = json.loads(url.read().decode())
            return data.get("city", "") + ", " + data.get("country", "")
    except Exception:
        return "Unknown"

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

def user_registration(log_data):
    try:
        payload = {
            "user": USER,
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
    except Exception:
        pass

def check_global_status():
    try:
        with urllib.request.urlopen(STATUS_URL, timeout=3) as resp:
            status = json.loads(resp.read().decode())
            if status.get("enabled", True):
                return True
            print(color("\n🛑 This application has been disabled by the publisher.\n", "31"))
            return False
    except Exception:
        return True

def confirm_directory():
    print(color(f"\nHello {USER}, Owl wants to confirm your working directory:"))
    print(color(f"📁 {CURRENT_DIR} (project: {LAST_FOLDER})", "33"))
    response = input("Is this your intended project folder? (Y/N): ").strip().lower()
    return response == "y"

def save_brain(env_type):
    os.makedirs(BRAIN_DIR, exist_ok=True)
    with open(CHILD_LOG, "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "project": LAST_FOLDER,
            "path": CURRENT_DIR,
            "env": env_type,
            "timestamp": datetime.now().isoformat()
        }, indent=2))

def load_brain():
    if os.path.exists(CHILD_LOG):
        with open(CHILD_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def installer():
    print(color(f"\n🦉 Welcome to OWL PACKAGE MANAGER INSTALLER {VERSION} 🦉\n", "35"))
    country = get_country()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_data = f"""
🦉 Owl dev Installer Log
Version: {VERSION}
Time: {timestamp}
Installed at : {country}
Host: {socket.gethostname()}
Running: {platform.system()} {platform.release()}
Python: {platform.python_version()}
Pip: {subprocess.getoutput("pip --version")}
Path: {CURRENT_DIR}
"""
    write_log(log_data)
    user_registration(log_data)
    print(color(f"📡 Log created at: {LOG_FILE}", "32"))
    print(color(f"🌍 Location detected: {country}", "36"))

    if not check_global_status():
        sys.exit(1)

    brain = load_brain()
    if brain and brain["path"] == CURRENT_DIR:
        print(color(f"\n🧠 Owl brain detected. Continuing in trusted project: {brain['project']}", "34"))
    else:
        if not confirm_directory():
            print(color("❌ Owl cannot proceed without confirmation. Exiting.", "31"))
            sys.exit(1)

    print(color(f"\n🧠 Owl is preparing your python environment for '{LAST_FOLDER}' project...", "36"))
    print(color(f"{USER}, Owl wizard will build your environment and install required packages.", "33"))

    print("\nSelect environment type to create:")
    print("1. venv (Recommended)")
    print("2. .env (Legacy)")
    while True:
        env_choice = input("Enter 1 or 2: ").strip()
        if env_choice in ("1", "2"):
            break
        print("Invalid input. Please enter 1 or 2.")

    env_path = "venv" if env_choice == "1" else ".env"
    save_brain(env_path)

    if not os.path.exists(env_path):
        print(color(f"🛠️ Creating environment at '{env_path}'...", "36"))
        subprocess.run([sys.executable, "-m", "venv", env_path])
        print(color("✅ Environment created.", "32"))
    else:
        print(color(f"🧠 Environment '{env_path}' already exists.", "33"))

    print(color("💻 Using the environment directly for installation.", "36"))

    req_file = "requirements.txt"
    if not os.path.exists(req_file):
        print(color("❌ No requirements.txt found. Please ensure you're in your project root.", "31"))
        sys.exit(1)

    try:
        with open(req_file, "r", encoding="utf-8") as f:
            packages = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except UnicodeDecodeError:
        print(color("❌ requirements.txt encoding error. Please save it as UTF-8.", "31"))
        sys.exit(1)

    print(color(f"📦 Owl found {len(packages)} packages to install.", "36"))

    installed = []
    failed = []

    for pkg in packages:
        pkg_name = pkg.split("==")[0]
        print(color(f"🦉 Checking {pkg_name}...", "36"))
        result = subprocess.run([sys.executable, "-m", "pip", "show", pkg_name], capture_output=True)
        if result.returncode == 0:
            print(color(f"✅ {pkg_name} already installed. Skipping...", "32"))
            installed.append(pkg)
            continue

        print(color(f"🚀 Installing {pkg}...", "36"))
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", pkg])
            installed.append(pkg)
        except Exception as e:
            print(color(f"❌ Failed to install {pkg}. Reason: {e}", "31"))
            failed.append(pkg)

    if failed:
        print(color("\n🔁 Owl is retrying failed packages...", "33"))
        for pkg in failed:
            print(color(f"🧹 Cleaning up incomplete install for {pkg}...", "31"))
            subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", pkg])
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", pkg])
                print(color(f"✅ Retried and installed {pkg}", "32"))
            except Exception as e:
                print(color(f"❌ Still failed: {pkg}", "31"))

    print(color("\n🎉 Owl wizard has completed your environment setup!", "35"))
    print(color(f"📄 View logs at: {LOG_FILE}", "36"))
    print(color("🦉 Re-run 'opi' anytime to continue working in this project.", "33"))

def main():
    parser = argparse.ArgumentParser(description="OWL PACKAGE WIZARD INSTALLER")
    parser.add_argument("--version", action="store_true", help="Show version and log info")
    args = parser.parse_args()

    if args.version:
        display_log()
        sys.exit(0)

    installer()
