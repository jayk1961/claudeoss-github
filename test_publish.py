import os
import subprocess

dir_name = "Apple-macOS-Platform-Utilities"
res = subprocess.run(["/opt/local/bin/npm", "publish"], cwd=dir_name, capture_output=True, text=True)
print(res.returncode)
print(res.stdout)
print(res.stderr)
