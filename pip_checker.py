import os
import sys
import subprocess
import urllib.request

def check_internet():
    try:
        urllib.request.urlopen('https://pypi.org', timeout=5)
        return True
    except Exception as e:
        print(f"❌ Keine Internetverbindung oder PyPI nicht erreichbar: {e}")
        return False

def check_pip_version():
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', '--version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ Pip Version: {result.stdout.strip()}")
        else:
            print(f"❌ Fehler beim Abrufen der Pip-Version: {result.stderr.strip()}")
    except Exception as e:
        print(f"❌ Ausnahme beim Prüfen der Pip-Version: {e}")

def check_pip_upgrade_possible():
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list', '--outdated'],
            capture_output=True,
            text=True
        )
        if 'pip' in result.stdout:
            print("⚠️ Es gibt eine neuere Pip-Version!")
        else:
            print("✅ Pip ist aktuell.")
    except Exception as e:
        print(f"❌ Ausnahme beim Prüfen auf neue Pip-Version: {e}")

if __name__ == "__main__":
    print("🔍 Starte Pip-Checker...\n")

    if check_internet():
        print("🌐 Internetzugang vorhanden.\n")
        check_pip_version()
        check_pip_upgrade_possible()
    else:
        print("🚫 Kein Internet – Pip-Upgrade nicht möglich.")

    print("\n🏁 Fertig!")