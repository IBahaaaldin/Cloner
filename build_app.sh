#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$SCRIPT_DIR/Cloner.app"
CONTENTS_DIR="$APP_DIR/Contents"
MACOS_DIR="$CONTENTS_DIR/MacOS"
RESOURCES_DIR="$CONTENTS_DIR/Resources"

echo "==> Building Cloner.app..."

# 1. Clean previous bundle
rm -rf "$APP_DIR"
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# 2. Compile Swift binary
echo "==> Compiling native Swift binary..."
swiftc -O \
  -target arm64-apple-macos14.0 \
  -framework Cocoa \
  -framework WebKit \
  "$SCRIPT_DIR/src/main.swift" \
  -o "$MACOS_DIR/Cloner"

# 3. Copy resources
echo "==> Embedding resources and web UI..."
cp "$SCRIPT_DIR/src/cloner_engine.py" "$RESOURCES_DIR/"
cp -R "$SCRIPT_DIR/ui" "$RESOURCES_DIR/"

# 4. Write Info.plist
cat << 'EOF' > "$CONTENTS_DIR/Info.plist"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleDisplayName</key>
    <string>Cloner</string>
    <key>CFBundleExecutable</key>
    <string>Cloner</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.cloner.app</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>Cloner</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>14.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
</dict>
</plist>
EOF

# 5. Generate dark squircle AppIcon.icns
echo "==> Generating AppIcon.icns..."
ICONSET_DIR="/tmp/cloner_appicon.iconset"
rm -rf "$ICONSET_DIR"
mkdir -p "$ICONSET_DIR"

python3 - << 'PYEOF'
import subprocess, os

# Create base 512x512 SVG with dark squircle and glowing clone glyph
svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="512" height="512">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#242633"/>
      <stop offset="100%" stop-color="#0E0F14"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#60A5FA"/>
      <stop offset="100%" stop-color="#2563EB"/>
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="8" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>
  <!-- Apple Squircle Shape -->
  <rect x="32" y="32" width="448" height="448" rx="100" fill="url(#bg)" stroke="rgba(255,255,255,0.12)" stroke-width="3"/>
  <!-- Cloned Windows / Boxes -->
  <rect x="130" y="190" width="180" height="180" rx="36" fill="none" stroke="#4B5563" stroke-width="16" />
  <rect x="202" y="142" width="180" height="180" rx="36" fill="#181A22" stroke="url(#accent)" stroke-width="18" filter="url(#glow)"/>
  <!-- Glowing Center Dot -->
  <circle cx="292" cy="232" r="24" fill="#60A5FA"/>
</svg>"""

with open("/tmp/cloner_icon.svg", "w") as f:
    f.write(svg_content)

# Render to 512x512 PNG using QuickLook / sips or qlmanage
res = subprocess.run(["qlmanage", "-t", "-s", "512", "-o", "/tmp", "/tmp/cloner_icon.svg"], capture_output=True)
png_src = "/tmp/cloner_icon.svg.png"

# Resize to all iconset sizes
iconset = "/tmp/cloner_appicon.iconset"
sizes = [16, 32, 64, 128, 256, 512]
if os.path.exists(png_src):
    for s in sizes:
        subprocess.run(["sips", "-z", str(s), str(s), png_src, "--out", f"{iconset}/icon_{s}x{s}.png"], stdout=subprocess.DEVNULL)
        if s * 2 <= 512:
            subprocess.run(["sips", "-z", str(s*2), str(s*2), png_src, "--out", f"{iconset}/icon_{s}x{s}@2x.png"], stdout=subprocess.DEVNULL)
PYEOF

if [ -f "/tmp/cloner_appicon.iconset/icon_512x512.png" ]; then
    iconutil -c icns /tmp/cloner_appicon.iconset -o "$RESOURCES_DIR/AppIcon.icns" || true
    rm -rf /tmp/cloner_appicon.iconset /tmp/cloner_icon.svg /tmp/cloner_icon.svg.png
fi

# 6. Ad-hoc codesign
echo "==> Ad-hoc signing Cloner.app..."
codesign --force --deep --sign - "$APP_DIR"

echo "==> Successfully created $APP_DIR"
