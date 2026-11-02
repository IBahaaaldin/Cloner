#!/usr/bin/env python3
"""
Cloner Engine
Core backend logic for detecting, cloning, badging, and managing macOS AI applications.
"""

import os
import sys
import json
import shutil
import subprocess
import plistlib
from pathlib import Path
from typing import List, Dict, Optional, Any

# Primary targeted applications
KNOWN_APPS = [
    {
        "key": "chatgpt",
        "name": "ChatGPT",
        "bundle_id": "com.openai.codex",
        "default_paths": ["/Applications/ChatGPT.app"],
        "type": "native",
        "icon_name": "ChatGPT"
    },
    {
        "key": "claude",
        "name": "Claude",
        "bundle_id": "com.anthropic.claudefordesktop",
        "default_paths": ["/Applications/Claude.app"],
        "type": "electron",
        "icon_name": "Claude"
    },
    {
        "key": "antigravity",
        "name": "AntiGravity",
        "bundle_id": "com.google.antigravity",
        "default_paths": ["/Applications/Antigravity.app"],
        "type": "electron",
        "icon_name": "Antigravity"
    },
    {
        "key": "antigravity-ide",
        "name": "AntiGravity IDE",
        "bundle_id": "com.google.antigravity-ide",
        "default_paths": ["/Applications/Antigravity IDE.app"],
        "type": "electron",
        "icon_name": "Antigravity IDE"
    }
]

DEFAULT_CLONER_DIR = os.path.expanduser("~/Desktop/Cloner")
DEFAULT_DATA_ROOT = os.path.expanduser("~/Library/Application Support/Cloner")

class ClonerEngine:
    def __init__(self, cloner_dir: str = DEFAULT_CLONER_DIR, data_root: str = DEFAULT_DATA_ROOT):
        self.cloner_dir = os.path.abspath(cloner_dir)
        self.data_root = os.path.abspath(data_root)
        os.makedirs(self.cloner_dir, exist_ok=True)
        os.makedirs(self.data_root, exist_ok=True)

    def scan_installed_apps(self) -> List[Dict[str, Any]]:
        """Scans the system for supported AI applications and any other valid apps."""
        results = []
        seen_paths = set()

        # 1. Check known primary apps first
        for known in KNOWN_APPS:
            for p in known["default_paths"]:
                if os.path.exists(p) and p not in seen_paths:
                    app_info = self._inspect_app(p, default_type=known["type"])
                    if app_info:
                        app_info["is_featured"] = True
                        app_info["key"] = known["key"]
                        results.append(app_info)
                        seen_paths.add(p)

        # 2. Check other apps in /Applications
        search_dirs = ["/Applications", os.path.expanduser("~/Applications")]
        for d in search_dirs:
            if not os.path.exists(d):
                continue
            for item in sorted(os.listdir(d)):
                if not item.endswith(".app"):
                    continue
                full_path = os.path.join(d, item)
                if full_path in seen_paths:
                    continue
                # Skip helper apps or system internals
                if "Helper" in item or "Service" in item or "Uninstaller" in item:
                    continue
                app_info = self._inspect_app(full_path)
                if app_info:
                    app_info["is_featured"] = False
                    app_info["key"] = item.replace(".app", "").lower().replace(" ", "-")
                    results.append(app_info)
                    seen_paths.add(full_path)

        return results

    def _inspect_app(self, app_path: str, default_type: str = "auto") -> Optional[Dict[str, Any]]:
        """Inspects an .app bundle to read plist, executable, and icon."""
        plist_path = os.path.join(app_path, "Contents", "Info.plist")
        if not os.path.exists(plist_path):
            return None

        try:
            with open(plist_path, "rb") as f:
                plist = plistlib.load(f)
        except Exception:
            return None

        name = plist.get("CFBundleDisplayName") or plist.get("CFBundleName") or os.path.basename(app_path).replace(".app", "")
        bundle_id = plist.get("CFBundleIdentifier", "")
        executable_name = plist.get("CFBundleExecutable", "")
        exec_path = os.path.join(app_path, "Contents", "MacOS", executable_name)
        if not os.path.exists(exec_path):
            return None

        # Icon file
        icon_file = plist.get("CFBundleIconFile", "")
        if icon_file and not icon_file.endswith(".icns"):
            icon_file += ".icns"
        icon_path = os.path.join(app_path, "Contents", "Resources", icon_file) if icon_file else ""
        if not os.path.exists(icon_path):
            # Try to find any .icns in Resources
            res_dir = os.path.join(app_path, "Contents", "Resources")
            if os.path.exists(res_dir):
                for f in os.listdir(res_dir):
                    if f.endswith(".icns"):
                        icon_path = os.path.join(res_dir, f)
                        break

        # Detect Electron / Chromium vs Native
        frameworks_dir = os.path.join(app_path, "Contents", "Frameworks")
        is_electron = False
        if os.path.exists(frameworks_dir):
            fw_list = os.listdir(frameworks_dir)
            if any("Electron" in fw or "Chromium" in fw for fw in fw_list):
                is_electron = True

        app_type = default_type if default_type != "auto" else ("electron" if is_electron else "native")

        return {
            "name": name,
            "path": app_path,
            "bundle_id": bundle_id,
            "executable_name": executable_name,
            "icon_path": icon_path,
            "type": app_type
        }

    def create_badged_icon(self, src_icns: str, out_icns: str, badge_color: str, badge_text: str = "") -> bool:
        """
        Creates a custom badged icon by extracting high-res PNG, drawing a squircle badge,
        and packaging it back into an .icns using macOS built-in sips and iconutil.
        """
        if not os.path.exists(src_icns):
            return False

        temp_iconset = out_icns + ".iconset"
        os.makedirs(temp_iconset, exist_ok=True)
        try:
            # 1. Extract 512x512 PNG using sips
            png_512 = os.path.join(temp_iconset, "icon_512x512.png")
            subprocess.run([
                "sips", "-s", "format", "png",
                "--resampleHeightWidth", "512", "512",
                src_icns, "--out", png_512
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

            # 2. Overlay badge using Python (without external dependencies, using CoreGraphics via sips / script)
            # We generate a badge overlay image with python
            self._draw_badge_on_png(png_512, badge_color, badge_text)

            # 3. Generate iconset sizes
            sizes = [16, 32, 64, 128, 256, 512]
            for s in sizes:
                target = os.path.join(temp_iconset, f"icon_{s}x{s}.png")
                target_2x = os.path.join(temp_iconset, f"icon_{s}x{s}@2x.png")
                subprocess.run(["sips", "-z", str(s), str(s), png_512, "--out", target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if s * 2 <= 512:
                    subprocess.run(["sips", "-z", str(s * 2), str(s * 2), png_512, "--out", target_2x], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # 4. Pack into .icns using iconutil
            res = subprocess.run(["iconutil", "-c", "icns", temp_iconset, "-o", out_icns], capture_output=True)
            return res.returncode == 0 and os.path.exists(out_icns)
        except Exception as e:
            # Fallback to direct copy
            shutil.copy2(src_icns, out_icns)
            return True
        finally:
            if os.path.exists(temp_iconset):
                shutil.rmtree(temp_iconset)

    def _draw_badge_on_png(self, png_path: str, badge_color: str, badge_text: str):
        """Draws a sleek colored badge circle/squircle onto the bottom right of the 512x512 image."""
        try:
            from PIL import Image, ImageDraw, ImageFont
            img = Image.open(png_path).convert("RGBA")
            draw = ImageDraw.Draw(img)

            # Badge parameters (bottom-right)
            badge_size = 140
            padding = 24
            x1 = 512 - padding - badge_size
            y1 = 512 - padding - badge_size
            x2 = 512 - padding
            y2 = 512 - padding

            # Dark shadow ring
            draw.ellipse([x1 - 6, y1 - 6, x2 + 6, y2 + 6], fill=(13, 14, 17, 240))
            # Primary badge color
            # Parse hex
            c = badge_color.lstrip('#')
            rgb = tuple(int(c[i:i+2], 16) for i in (0, 2, 4))
            draw.ellipse([x1, y1, x2, y2], fill=(*rgb, 255))
            # Inner border
            draw.ellipse([x1, y1, x2, y2], outline=(255, 255, 255, 120), width=4)

            # Draw initial text if available
            if badge_text:
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/SFPro-Bold.ttf", 64)
                except Exception:
                    try:
                        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
                    except Exception:
                        font = ImageFont.load_default()
                text = badge_text[:3].upper()
                bbox = draw.textbbox((0, 0), text, font=font)
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                tx = x1 + (badge_size - tw) / 2
                ty = y1 + (badge_size - th) / 2 - 4
                draw.text((tx, ty), text, fill=(255, 255, 255, 255), font=font)

            img.save(png_path, "PNG")
        except ImportError:
            # If PIL is not installed, we can draw a raw badge or leave clean
            pass

    def create_app_clone(self, app_path: str, profile_name: str, badge_color: str = "#3B82F6") -> Dict[str, Any]:
        """Creates an independent clone application bundle."""
        app_info = self._inspect_app(app_path)
        if not app_info:
            return {"success": False, "error": f"App at {app_path} is invalid or missing Info.plist"}

        # Sanitize profile name
        clean_profile = "".join(c for c in profile_name if c.isalnum() or c in (" ", "-", "_")).strip()
        if not clean_profile:
            clean_profile = "Secondary"

        clone_name = f"{app_info['name']} ({clean_profile})"
        clone_app_path = os.path.join(self.cloner_dir, f"{clone_name}.app")

        # Specific isolated data directory
        app_slug = "".join(c for c in app_info['name'] if c.isalnum() or c == '-').lower()
        profile_slug = clean_profile.lower().replace(" ", "-")
        isolated_data_dir = os.path.join(self.data_root, app_slug, profile_slug)
        os.makedirs(isolated_data_dir, exist_ok=True)

        # Scaffolding clone bundle
        contents_dir = os.path.join(clone_app_path, "Contents")
        macos_dir = os.path.join(contents_dir, "MacOS")
        resources_dir = os.path.join(contents_dir, "Resources")

        if os.path.exists(clone_app_path):
            shutil.rmtree(clone_app_path)

        os.makedirs(macos_dir, exist_ok=True)
        os.makedirs(resources_dir, exist_ok=True)

        # 1. Create badged icon
        out_icns = os.path.join(resources_dir, "AppIcon.icns")
        initials = clean_profile[:2]
        if app_info["icon_path"] and os.path.exists(app_info["icon_path"]):
            self.create_badged_icon(app_info["icon_path"], out_icns, badge_color, initials)

        # 2. Configure Info.plist
        unique_bundle_id = f"com.cloner.{app_slug}.{profile_slug}"
        clone_plist = {
            "CFBundleDevelopmentRegion": "en",
            "CFBundleDisplayName": clone_name,
            "CFBundleExecutable": "launcher",
            "CFBundleIconFile": "AppIcon",
            "CFBundleIdentifier": unique_bundle_id,
            "CFBundleInfoDictionaryVersion": "6.0",
            "CFBundleName": clone_name,
            "CFBundlePackageType": "APPL",
            "CFBundleShortVersionString": "1.0",
            "CFBundleVersion": "1",
            "LSMinimumSystemVersion": "14.0",
            "NSHighResolutionCapable": True,
            "ClonerBaseAppPath": app_path,
            "ClonerProfileName": clean_profile,
            "ClonerBaseAppName": app_info["name"],
            "ClonerDataDir": isolated_data_dir,
            "ClonerBadgeColor": badge_color,
            "ClonerAppType": app_info["type"]
        }

        with open(os.path.join(contents_dir, "Info.plist"), "wb") as f:
            plistlib.dump(clone_plist, f)

        # 3. Create launcher script
        launcher_path = os.path.join(macos_dir, "launcher")
        original_exec = os.path.join(app_path, "Contents", "MacOS", app_info["executable_name"])

        if app_info["type"] == "electron":
            launcher_script = f"""#!/bin/bash
# Cloner Launcher for Electron app: {app_info['name']} ({clean_profile})
DATA_DIR="{isolated_data_dir}"
ORIGINAL_EXEC="{original_exec}"

mkdir -p "$DATA_DIR"
exec "$ORIGINAL_EXEC" --user-data-dir="$DATA_DIR" "$@"
"""
        else:
            # Native Cocoa app (ChatGPT)
            launcher_script = f"""#!/bin/bash
# Cloner Launcher for Native app: {app_info['name']} ({clean_profile})
DATA_DIR="{isolated_data_dir}"
ORIGINAL_EXEC="{original_exec}"

mkdir -p "$DATA_DIR/Library/Application Support"
mkdir -p "$DATA_DIR/Library/WebKit"
mkdir -p "$DATA_DIR/Library/Caches"
mkdir -p "$DATA_DIR/Library/Preferences"

export HOME="$DATA_DIR"
exec "$ORIGINAL_EXEC" "$@"
"""

        with open(launcher_path, "w") as f:
            f.write(launcher_script)
        os.chmod(launcher_path, 0o755)

        # 4. Ad-hoc codesign
        try:
            subprocess.run(["codesign", "--force", "--deep", "--sign", "-", clone_app_path],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

        # 5. Refresh LaunchServices
        try:
            subprocess.run(["touch", clone_app_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

        return {
            "success": True,
            "clone_name": clone_name,
            "clone_path": clone_app_path,
            "data_dir": isolated_data_dir,
            "bundle_id": unique_bundle_id
        }

    def list_active_clones(self) -> List[Dict[str, Any]]:
        """Scans the Cloner directory for created clone applications."""
        clones = []
        if not os.path.exists(self.cloner_dir):
            return clones

        for item in sorted(os.listdir(self.cloner_dir)):
            if not item.endswith(".app"):
                continue
            app_path = os.path.join(self.cloner_dir, item)
            plist_path = os.path.join(app_path, "Contents", "Info.plist")
            if not os.path.exists(plist_path):
                continue
            try:
                with open(plist_path, "rb") as f:
                    plist = plistlib.load(f)
                if "ClonerProfileName" not in plist:
                    continue

                profile_name = plist.get("ClonerProfileName", "")
                base_name = plist.get("ClonerBaseAppName", item.replace(".app", ""))
                base_path = plist.get("ClonerBaseAppPath", "")
                data_dir = plist.get("ClonerDataDir", "")
                badge_color = plist.get("ClonerBadgeColor", "#3B82F6")
                bundle_id = plist.get("CFBundleIdentifier", "")

                # Check if running
                is_running = False
                try:
                    check = subprocess.run(["pgrep", "-f", bundle_id], capture_output=True, text=True)
                    is_running = (check.returncode == 0)
                except Exception:
                    pass

                # Check data directory size
                data_size_str = "0 MB"
                if os.path.exists(data_dir):
                    try:
                        du = subprocess.run(["du", "-sh", data_dir], capture_output=True, text=True)
                        if du.returncode == 0 and du.stdout:
                            data_size_str = du.stdout.split()[0]
                    except Exception:
                        pass

                clones.append({
                    "name": item.replace(".app", ""),
                    "path": app_path,
                    "profile_name": profile_name,
                    "base_app_name": base_name,
                    "base_app_path": base_path,
                    "data_dir": data_dir,
                    "badge_color": badge_color,
                    "bundle_id": bundle_id,
                    "is_running": is_running,
                    "data_size": data_size_str
                })
            except Exception:
                continue

        return clones

    def delete_app_clone(self, clone_path: str, remove_data: bool = False) -> bool:
        """Deletes a clone application and optionally purges its profile data."""
        if not os.path.exists(clone_path):
            return False

        if remove_data:
            plist_path = os.path.join(clone_path, "Contents", "Info.plist")
            if os.path.exists(plist_path):
                try:
                    with open(plist_path, "rb") as f:
                        plist = plistlib.load(f)
                    data_dir = plist.get("ClonerDataDir")
                    if data_dir and os.path.exists(data_dir) and self.data_root in os.path.abspath(data_dir):
                        shutil.rmtree(data_dir)
                except Exception:
                    pass

        try:
            shutil.rmtree(clone_path)
            return True
        except Exception:
            return False

    def launch_app_clone(self, clone_path: str) -> bool:
        """Launches a clone using macOS open -n."""
        if not os.path.exists(clone_path):
            return False
        try:
            res = subprocess.run(["open", "-n", clone_path], capture_output=True)
            return res.returncode == 0
        except Exception:
            return False

    def reveal_in_finder(self, path: str) -> bool:
        """Selects the specified file or folder in Finder."""
        if not os.path.exists(path):
            return False
        try:
            subprocess.run(["open", "-R", path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            return False

    def open_data_folder(self, data_dir: str) -> bool:
        """Opens the data folder in Finder."""
        os.makedirs(data_dir, exist_ok=True)
        try:
            subprocess.run(["open", data_dir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            return False

# CLI interface for direct command invocation or Swift integration
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Cloner Engine CLI")
    parser.add_argument("command", choices=["scan", "create", "list", "delete", "launch", "reveal", "open-data"])
    parser.add_argument("--app-path", help="Path to base app")
    parser.add_argument("--profile", help="Profile name")
    parser.add_argument("--color", default="#3B82F6", help="Badge hex color")
    parser.add_argument("--clone-path", help="Path to clone app bundle")
    parser.add_argument("--remove-data", action="store_true", help="Delete isolated data directory")
    parser.add_argument("--data-dir", help="Data directory path")

    args = parser.parse_args()
    engine = ClonerEngine()

    if args.command == "scan":
        apps = engine.scan_installed_apps()
        print(json.dumps(apps, indent=2))
    elif args.command == "create":
        res = engine.create_app_clone(args.app_path, args.profile, args.color)
        print(json.dumps(res, indent=2))
    elif args.command == "list":
        clones = engine.list_active_clones()
        print(json.dumps(clones, indent=2))
    elif args.command == "delete":
        res = engine.delete_app_clone(args.clone_path, args.remove_data)
        print(json.dumps({"success": res}))
    elif args.command == "launch":
        res = engine.launch_app_clone(args.clone_path)
        print(json.dumps({"success": res}))
    elif args.command == "reveal":
        res = engine.reveal_in_finder(args.clone_path)
        print(json.dumps({"success": res}))
    elif args.command == "open-data":
        res = engine.open_data_folder(args.data_dir)
        print(json.dumps({"success": res}))
