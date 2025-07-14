import argparse
import time
import os

VERSION = "V1.0 OPI"

def init_project():
    print("🦉 Initializing new Owl project...")
    time.sleep(1)
    os.makedirs(".owl_brain", exist_ok=True)
    with open(".owl_brain/project.info", "w") as f:
        f.write("Project initialized with Owl\n")
    print("✅ Project initialized. Owl brain is ready.")

def build_environment():
    print("🔧 Building environment...")
    time.sleep(1)
    print("📦 Installing required packages...")
    time.sleep(1)
    print("✅ Environment built successfully.")

def show_status():
    print("📊 Owl Status Report")
    if os.path.exists(".owl_brain/project.info"):
        print("🧠 Owl brain detected.")
    else:
        print("⚠️ No Owl brain found. Run 'opi init' first.")
    print("📦 Environment: Ready (simulated)")

def show_version():
    print(f"🦉 Owl Package Installer — Version {VERSION}")

def main():
    parser = argparse.ArgumentParser(description="Owl Package Installer CLI")
    parser.add_argument("command", nargs="?", help="Command to run (init, build, status, --version)")
    args = parser.parse_args()

    if args.command == "init":
        init_project()
    elif args.command == "build":
        build_environment()
    elif args.command == "status":
        show_status()
    elif args.command == "--version":
        show_version()
    else:
        print("🦉 Unknown command. Try: init, build, status, --version")

if __name__ == "__main__":
    main()
