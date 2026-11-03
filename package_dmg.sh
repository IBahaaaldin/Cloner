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

# Add Instant Safe Launch Command inside DMG (Bypasses Gatekeeper with 1-click)
cat << 'EOF' > "$STAGING_DIR/Launch Cloner (First-Time Bypass).command"
#!/bin/bash
clear
echo "============================================================"
echo "          CLONER FOR MACOS — INSTANT SAFE LAUNCH            "
echo "        Created by Bahaa Mohammed (@ibahaaaldincoding)      "
echo "============================================================"
echo ""

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DEST="/Applications/Cloner.app"

if [ ! -d "$APP_DEST" ]; then
    echo "==> Copying Cloner.app to /Applications..."
    cp -R "$DIR/Cloner.app" /Applications/
fi

echo "==> Removing macOS Gatekeeper quarantine..."
xattr -cr "$APP_DEST" 2>/dev/null || true

echo "==> Launching Cloner..."
open "$APP_DEST"

echo ""
echo "✓ Cloner is ready and running!"
echo "You can close this Terminal window."
exit 0
EOF
chmod +x "$STAGING_DIR/Launch Cloner (First-Time Bypass).command"

# Add README install guide inside DMG with complete author credentials
cat << 'EOF' > "$STAGING_DIR/Install Instructions.txt"
============================================================
              CLONER FOR MACOS (v1.0.0)
   Run Multiple Independent Accounts Simultaneously
============================================================

INSTALLATION METHODS:

Option A (Recommended & Instant):
• Double-click "Launch Cloner (First-Time Bypass).command" right 
  here in this folder! It automatically copies Cloner to /Applications,
  clears any macOS Gatekeeper warning, and opens it instantly.

Option B (Drag and Drop):
1. Drag 'Cloner.app' into the 'Applications' shortcut.
2. Launch Cloner from Spotlight or Launchpad.
3. If macOS says "cannot check for malicious software":
   Go to System Settings -> Privacy & Security -> Click "Open Anyway".

HOW TO SAFELY EJECT & DELETE THIS DMG:
1. Make sure Cloner is closed or moved to Applications.
2. In Finder, click the Eject icon next to "Cloner" in the left sidebar,
   or right-click the Cloner disk icon on your desktop and select "Eject".
3. Now you can move the downloaded "Cloner.dmg" file to the Trash!

------------------------------------------------------------
FEATURES:
• APFS Instant Cloning (<1 sec, 0 extra disk storage)
• Clones appear directly on your Desktop as standalone apps
• Completely separate sessions, cookies, logins, and chats
• Color-coded badged squircle dock icons
• Automatic Keychain linkage (Zero password reset prompts)
• Safe macOS Trash deletion

------------------------------------------------------------
AUTHOR & CREDENTIALS:
• Name: Bahaa Mohammed
• Instagram: @ibahaaaldincoding (https://www.instagram.com/ibahaaaldincoding)
• GitHub: @IBahaaaldin (https://github.com/IBahaaaldin)
• LinkedIn: Bahaa Mohammed (https://www.linkedin.com/in/bahaa-mohammed-371259369)
• Email: bahaam.coding@gmail.com
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

# 4. Also create a direct standalone ZIP distribution (for users who prefer direct app download without DMG)
echo "==> Creating standalone Cloner.zip..."
ZIP_FILE="$SCRIPT_DIR/Cloner.zip"
rm -f "$ZIP_FILE"
(cd "$SCRIPT_DIR" && zip -r -y -q "$ZIP_FILE" "Cloner.app")

# 5. Clean up staging
rm -rf "$STAGING_DIR"

echo "==> Successfully created:"
echo "    • $DMG_FILE"
echo "    • $DMG_VERSIONED"
echo "    • $ZIP_FILE"
ls -lh "$DMG_FILE" "$ZIP_FILE"
