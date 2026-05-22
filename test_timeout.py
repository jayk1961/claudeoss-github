import subprocess
import threading
import os
import time

def worker():
    subprocess.run(["sleep", "10"], stderr=subprocess.PIPE)

t = threading.Thread(target=worker)
t.start()
time.sleep(1)
os._exit(0)
