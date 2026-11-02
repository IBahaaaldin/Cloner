#!/bin/bash
set -e

echo "============================================================"
echo "          Installing Cloner for macOS (v1.0.0)             "
echo "      by Bahaa Mohammed (@ibahaaaldincoding)              "
echo "============================================================"

TEMP_DMG="/tmp/Cloner.dmg"
RELEASE_URL="https://github.com/IBahaaaldin/Cloner/releases/download/v1.0.0/Cloner.dmg"

echo "==> Downloading Cloner.dmg from GitHub..."
curl -sSL -L "$RELEASE_URL" -o "$TEMP_DMG"

echo "==> Mounting disk image..."
MOUNT_DIR=$(mktemp -d /tmp/cloner_mount_XXXXXX)
hdiutil attach "$TEMP_DMG" -mountpoint "$MOUNT_DIR" -nobrowse -quiet

echo "==> Installing Cloner.app to /Applications..."
rm -rf "/Applications/Cloner.app"
cp -R "$MOUNT_DIR/Cloner.app" /Applications/

echo "==> Removing macOS Gatekeeper quarantine (Instant Safe Launch)..."
xattr -cr /Applications/Cloner.app 2>/dev/null || true

echo "==> Cleaning up installer..."
hdiutil detach "$MOUNT_DIR" -quiet || true
rm -rf "$MOUNT_DIR" "$TEMP_DMG"

echo "============================================================"
echo "  ✓ Cloner successfully installed to /Applications/Cloner.app"
echo "  ✓ Gatekeeper cleared — ready to use instantly!"
echo "============================================================"
echo "==> Launching Cloner..."
open /Applications/Cloner.app
