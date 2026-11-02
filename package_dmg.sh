#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_PATH="$SCRIPT_DIR/Cloner.app"
DMG_NAME="Cloner"
DMG_FILE="$SCRIPT_DIR/${DMG_NAME}.dmg"
DMG_VERSIONED="$SCRIPT_DIR/${DMG_NAME}-1.0.0.dmg"
STAGING_DIR="/tmp/cloner_dmg_staging"

echo "==> Packaging Cloner for macOS distribution..."

# 1. Ensure Cloner.app is built and up to date
if [ ! -d "$APP_PATH" ]; then
    echo "==> Building Cloner.app first..."
    "$SCRIPT_DIR/build_app.sh"
fi

# 2. Prepare staging directory
rm -rf "$STAGING_DIR"
mkdir -p "$STAGING_DIR"

echo "==> Copying application bundle to staging..."
cp -R "$APP_PATH" "$STAGING_DIR/"

echo "==> Creating /Applications symlink for drag-and-drop install..."
ln -s /Applications "$STAGING_DIR/Applications"

# Add README install guide inside DMG
cat << 'EOF' > "$STAGING_DIR/Install Instructions.txt"
============================================================
              CLONER FOR MACOS (v1.0.0)
   Run Multiple Independent Accounts Simultaneously
============================================================

INSTALLATION:
1. Drag 'Cloner.app' into your 'Applications' folder.
2. Launch Cloner from Applications or Spotlight.
3. Select any detected AI app (ChatGPT, Claude, Antigravity)
   to create an independent profile.

FEATURES:
• APFS Instant Cloning (<1 sec, 0 extra disk storage)
• Completely separate sessions, cookies, logins, and chats
• Color-coded badged dock icons
• Safe macOS Trash deletion

Author: Bahaa Mohammed (@ibahaaaldincoding)
GitHub: https://github.com/IBahaaaldin
============================================================
EOF

# 3. Create DMG using hdiutil
echo "==> Creating compressed DMG image..."
rm -f "$DMG_FILE" "$DMG_VERSIONED"

hdiutil create \
    -volname "$DMG_NAME" \
    -srcfolder "$STAGING_DIR" \
    -ov \
    -format UDZO \
    "$DMG_FILE"

cp "$DMG_FILE" "$DMG_VERSIONED"

# 4. Clean up staging
rm -rf "$STAGING_DIR"

echo "==> Successfully created:"
echo "    • $DMG_FILE"
echo "    • $DMG_VERSIONED"
ls -lh "$DMG_FILE"
