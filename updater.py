import logging

logger = logging.getLogger(__name__)

try:
    import json
    import os
    import shutil
    import subprocess
    import sys
    import time
    import urllib.error
    import urllib.request
    import zipfile

    callbacks = {}
    new_version = None
    attempts = 5


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

        for attempt in range(attempts):
            try:
                with urllib.request.urlopen(url, timeout=15) as response:
                    return response.read()

            except urllib.error.HTTPError as f:
                last_error = f
                logger.exception("Updater.py error")

            except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as f:
                last_error = f
                logger.exception("Updater.py error")

            if attempt < attempts - 1:
                time.sleep(attempt * 2)
            else:
                trigger_event("error", last_error)
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

        except Exception as f:
            logger.exception("Updater error")
            trigger_event("error", f)

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

        except Exception as f:
            logger.exception("Updater error")
            trigger_event("error", f)


    if __name__ == "__main__":
        try:
            download_update(sys.argv[1], sys.argv[2])
        except Exception as e:
            logger.exception("updater.py error")
            trigger_event("error", e)

except Exception as r:
    logger.exception("updater.py error during startup")
