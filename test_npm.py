import os
import sys
import subprocess

dir_name = "Apple-macOS-Platform-Utilities"
pkg_path = os.path.join(dir_name, "package.json")
pkg_name = os.path.basename(os.path.abspath(dir_name)).lower().replace(" ", "-")
print(f"pkg_name: {pkg_name}")

res = subprocess.run(["npm", "publish"], cwd=dir_name, capture_output=True, text=True)
print(f"publish returncode: {res.returncode}")
print(f"publish stdout: {res.stdout}")
print(f"publish stderr: {res.stderr}")
