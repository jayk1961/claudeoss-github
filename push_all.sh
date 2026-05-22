#!/opt/local/bin/bash
export PATH=/opt/local/bin:$PATH

PROJECTS=(
  "Apple-macOS-Platform-Utilities"
  "Compression-and-Archiving-Utilities"
  "Core-Utilities-and-Scripting-Runtimes"
  "Development-Build-and-Version-Control-Tools"
  "Networking-DNS-SNMP-Tools"
  "Perl-Ecosystem-Tools"
  "System-Diagnostics-and-Debugging-Tools"
  "Text-Processing-Utilities"
  "grocery-coupon-auto-clicker"
  "arora"
  "docmanager-nectarine"
  "jayk"
  "stuffs"
)

for proj in "${PROJECTS[@]}"; do
  echo "Processing $proj..."
  cd "$proj"
  
  # Ensure package.json exists
  if [ ! -f package.json ]; then
    echo '{"name": "'$(echo "$proj" | tr '[:upper:]' '[:lower:]')'", "version": "1.0.0"}' > package.json
  fi
  
  git add .
  git commit -m "chore: clean up for npm publish"
  git push origin HEAD
  
  npm version patch
  npm publish --access public
  
  cd ..
done

# Now for the root project
echo "Processing root project..."
git add .
git commit -m "chore: clean up for npm publish"
git push origin main
npm version patch
npm publish --access public

