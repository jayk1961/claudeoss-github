#!/opt/local/bin/bash
export PATH=/opt/local/bin:$PATH

REPOS=(
  "jayk1961/claudeoss-github"
  "jayk1961/grocery-coupon-auto-clicker"
  "jayk1961/Core-Utilities-and-Scripting-Runtimes"
  "jayk1961/Text-Processing-Utilities"
  "jayk1961/System-Diagnostics-and-Debugging-Tools"
  "jayk1961/Perl-Ecosystem-Tools"
  "jayk1961/Networking-DNS-SNMP-Tools"
  "jayk1961/Development-Build-and-Version-Control-Tools"
  "jayk1961/Compression-and-Archiving-Utilities"
  "jayk1961/Apple-macOS-Platform-Utilities"
  "jayk1961/stuffs"
  "jayk1961/arora"
  "jayk1961/docmanager-nectarine"
  "jayk1961/jayk"
)

if [ $# -eq 0 ]; then
  ./npm.py --fast "${REPOS[@]}"
else
  ./npm.py --fast "$@"
fi
