import json
import urllib.request
import zipfile
import os
import shutil
import sys
import subprocess
import time
import logging
import urllib.error


logging.basicConfig(
    filename="updater.log",
    filemode="w",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(message)s"
)

callbacks = {}
new_version = None

def set_callback(event, new_function):
    if event in callbacks:
        callbacks[event].append(new_function)
    else:
        callbacks[event] = [new_function]


def trigger_event(event, data):
    if event in callbacks:
        for new_function in callbacks[event]:
            new_function(data)


def download_data(url):
    last_error = None
    retryable_codes = (408, 425, 429, 500, 502, 503, 504)

    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                return response.read()

        except urllib.error.HTTPError as e:
            if e.code not in retryable_codes:
                raise
            last_error = e

        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            last_error = e

        if attempt < 2:
            trigger_event(
                "retry",
                f"Connection interrupted. Retrying ({attempt + 1}/2)..."
            )
            time.sleep(2 ** attempt)
        else:
            raise last_error
    return None


# ---------- GitHub Release ----------
def detect_update():
    try:
        url = "https://api.github.com/repos/sultanwa-crypto/SultanChat/releases/latest"

        response = urllib.request.urlopen(url, timeout=15)
        data = response.read()
        text = data.decode()
        release = json.loads(text)

        # ---------- Version Information ----------

        version_file = open("version.txt", "r")
        current_version = version_file.read().strip()
        version_file.close()

        global new_version
        new_version = release["tag_name"]
        zip_url = release["zipball_url"]

        if new_version != current_version:
            return zip_url, new_version
        else:
            return None, None

    except Exception:
        logging.exception("Update installation failed")

        trigger_event(
            "error",
            "Unable to complete the update. Please try again."
        )

        return None, None


def download_update(zip_url, version):
    try:
        # ---------- Download ----------
        trigger_event("download", "Starting download...")

        if os.path.exists("update.zip"):
            os.remove("update.zip")

        if os.path.exists("update_temp"):
            shutil.rmtree("update_temp")

        zip_data = download_data(zip_url)

        zip_file = open("update.zip", "wb")
        zip_file.write(zip_data)
        zip_file.close()

        # ---------- Extraction ----------

        new_code = zipfile.ZipFile("update.zip", "r")
        new_code.extractall("update_temp")
        new_code.close()

        folders = os.listdir("update_temp")
        source_folder = os.path.join("update_temp", folders[0])

        # ---------- File Replacement ----------

        trigger_event("replace", "Replacing files...")

        front_path = os.path.join(source_folder, "front.py")
        back_path = os.path.join(source_folder, "back.py")

        shutil.copy2(front_path, "front.py")
        shutil.copy2(back_path, "back.py")

        os.remove("update.zip")
        shutil.rmtree("update_temp")

        # ---------- Version Update ----------

        version_file = open("version.txt", "w")
        version_file.write(version)
        version_file.close()

        trigger_event("finished", "Update completed!")

        app_dir = os.path.dirname(os.path.abspath(__file__))

        subprocess.Popen(
            [sys.executable, os.path.join(app_dir, "front.py")],
            cwd=app_dir,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )

    except Exception as e:
        trigger_event("error", e)


if __name__ == "__main__":
    download_update(sys.argv[1], sys.argv[2])