import updater
import tkinter as tk
from tkinter import ttk
import threading
import sys
import queue

root = tk.Tk()
updates = queue.Queue()
status = None


def show_window(zip_url, version):
    font = ("Sans", 12)

    root.title("SultanChat Updater")
    root.geometry("400x200")
    root.minsize(400, 200)
    root.maxsize(400, 200)

    global status
    status = tk.StringVar(value="Starting Update...")

    label = tk.Label(root, textvariable=status, font=font)
    label.pack()

    style = ttk.Style()
    style.theme_use("xpnative")

    progress = ttk.Progressbar(
        root,
        length=300,
        mode="indeterminate",
        maximum=100
    )
    progress.pack(pady=20)

    progress.start(3)

    threading.Thread(
        target=updater.download_update,
        args=(zip_url, version),
        daemon=False
    ).start()


def update_status(message):
    updates.put(message)


def process_updates():
    while True:
        try:
            message = updates.get_nowait()
        except queue.Empty:
            break

        status.set(str(message))

        if message == "Update completed!":
            root.after(1500, root.destroy)

    root.after(100, process_updates)


for event in ("download", "extract", "replace", "version", "finished", "error", "retry"):
    updater.set_callback(event, update_status)


zip_url = sys.argv[1]
version = sys.argv[2]

show_window(zip_url, version)

root.after(100, process_updates)
root.mainloop()