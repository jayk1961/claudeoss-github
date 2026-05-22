import os
import subprocess
import json

dir_name = "Apple-macOS-Platform-Utilities"
pkg_path = os.path.join(dir_name, "package.json")
with open(pkg_path, "r") as f:
    pkg_data = json.load(f)
pkg_data["name"] = "@jayk1961/apple-macos-platform-utilities"
with open(pkg_path, "w") as f:
    json.dump(pkg_data, f, indent=2)

res = subprocess.run(["/opt/local/bin/npm", "publish", "--access", "public"], cwd=dir_name, capture_output=True, text=True)
print(res.returncode)
print(res.stdout)
print(res.stderr)
