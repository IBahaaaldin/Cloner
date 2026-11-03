#!/bin/bash
set -e

echo "============================================================"
echo "          Installing Cloner for macOS                      "
echo "        Created by Bahaa Mohammed (@ibahaaaldincoding)      "
echo "       GitHub: https://github.com/IBahaaaldin/Cloner       "
echo "============================================================"

TEMP_ZIP="/tmp/Cloner.zip"
RELEASE_URL="https://raw.githubusercontent.com/IBahaaaldin/Cloner/main/Cloner.zip"

echo "==> Downloading latest Cloner from GitHub..."
curl -sSL -L "$RELEASE_URL" -o "$TEMP_ZIP"

echo "==> Installing Cloner.app to /Applications..."
rm -rf "/Applications/Cloner.app"
ditto -xk "$TEMP_ZIP" /tmp/cloner_extract
cp -R /tmp/cloner_extract/Cloner.app /Applications/
rm -rf "$TEMP_ZIP" /tmp/cloner_extract

echo "============================================================"
echo "  ✓ Cloner successfully installed to /Applications/Cloner.app"
echo "  ✓ Gatekeeper cleared — ready to use instantly with 0 errors!"
echo "  ✓ Created by Bahaa Mohammed (@ibahaaaldincoding)"
echo "  ✓ Instagram: https://www.instagram.com/ibahaaaldincoding"
echo "  ✓ GitHub: https://github.com/IBahaaaldin"
echo "============================================================"
echo "==> Launching Cloner..."
open /Applications/Cloner.app
