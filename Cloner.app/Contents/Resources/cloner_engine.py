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
        "type": "electron",
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

DEFAULT_CLONER_DIR = os.path.expanduser("~/Desktop")
DEFAULT_DATA_ROOT = os.path.expanduser("~/Library/Application Support/Cloner")

class ClonerEngine:
    def __init__(self, cloner_dir: str = DEFAULT_CLONER_DIR, data_root: str = DEFAULT_DATA_ROOT):
        self.cloner_dir = os.path.abspath(cloner_dir)
        self.data_root = os.path.abspath(data_root)
        os.makedirs(self.cloner_dir, exist_ok=True)
        os.makedirs(self.data_root, exist_ok=True)

    def check_has_account_login(self, app_path: str) -> tuple:
        """Determines if an application has an account/login system or is a simple local utility."""
        name = os.path.basename(app_path).replace(".app", "").lower()
        # Known account-based AI and productivity applications
        known_with_login = [
            "chatgpt", "claude", "antigravity", "gemini", "cursor", "copilot",
            "obsidian", "slack", "discord", "notion", "chrome", "firefox",
            "telegram", "whatsapp", "teams", "zoom", "postman", "linear",
            "spotify", "figma", "vscode", "visual studio code"
        ]
        if any(k in name for k in known_with_login):
            return True, "Verified account-based application"

        # Check Info.plist URL schemes for OAuth / login
        plist_path = os.path.join(app_path, "Contents", "Info.plist")
        if os.path.exists(plist_path):
            try:
                with open(plist_path, "rb") as f:
                    p = plistlib.load(f)
                url_types = p.get("CFBundleURLTypes", [])
                for ut in url_types:
                    schemes = [s.lower() for s in ut.get("CFBundleURLSchemes", [])]
                    if any("auth" in s or "login" in s or "sso" in s or "token" in s for s in schemes):
                        return True, "Registered authentication URL scheme"
            except Exception:
                pass

        # Check binary strings for auth / account management keywords
        exec_dir = os.path.join(app_path, "Contents", "MacOS")
        if os.path.exists(exec_dir):
            execs = [os.path.join(exec_dir, f) for f in os.listdir(exec_dir) if not f.startswith(".")]
            if execs:
                try:
                    res = subprocess.run(["strings", execs[0]], capture_output=True, text=True, errors="ignore")
                    text = res.stdout.lower()
                    auth_keywords = ["oauth", "sign in", "login", "user_id", "access_token", "refresh_token", "authentication", "session_token"]
                    matches = [k for k in auth_keywords if k in text]
                    if len(matches) >= 3:
                        return True, "Contains account and session infrastructure"
                except Exception:
                    pass

        return False, "Simple local utility with no account/login features"

    def scan_installed_apps(self) -> List[Dict[str, Any]]:
        """Scans the system for supported AI applications and account-based apps."""
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
                        app_info["has_login"] = True
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
                
                # Check if this app actually has a login/account feature
                has_login, reason = self.check_has_account_login(full_path)
                if not has_login:
                    continue

                app_info = self._inspect_app(full_path)
                if app_info:
                    app_info["is_featured"] = False
                    app_info["key"] = item.replace(".app", "").lower().replace(" ", "-")
                    app_info["has_login"] = True
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

    def create_app_clone(self, app_path: str, profile_name: str, badge_color: str = "#3B82F6", copy_existing_data: bool = False) -> Dict[str, Any]:
        """Creates an independent clone application bundle."""
        app_info = self._inspect_app(app_path)
        if not app_info:
            return {"success": False, "error": f"App at {app_path} is invalid or missing Info.plist"}

        # Check if the app has account/login capabilities
        has_login, reason = self.check_has_account_login(app_path)
        if not has_login:
            return {
                "success": False,
                "error": f"'{app_info['name']}' does not have an account or login system. Cloner only creates clones for apps that require multi-account management."
            }

        # Sanitize profile name
        clean_profile = "".join(c for c in profile_name if c.isalnum() or c in (" ", "-", "_")).strip()
        if not clean_profile:
            clean_profile = "Secondary"

        clone_name = f"{app_info['name']} ({clean_profile})"
        clone_app_path = os.path.join(self.cloner_dir, f"{clone_name}.app")

        # Specific isolated data directory with secure 0700 permissions
        app_slug = "".join(c for c in app_info['name'] if c.isalnum() or c == '-').lower()
        profile_slug = clean_profile.lower().replace(" ", "-")
        isolated_data_dir = os.path.join(self.data_root, app_slug, profile_slug)

        # If not copying existing data, guarantee a pristine 100% clean directory
        if not copy_existing_data and os.path.exists(isolated_data_dir):
            try:
                shutil.rmtree(isolated_data_dir, ignore_errors=True)
            except Exception:
                pass

        os.makedirs(isolated_data_dir, mode=0o700, exist_ok=True)
        try:
            os.chmod(isolated_data_dir, 0o700)
        except Exception:
            pass

        # Link real user Keychains into the isolated profile
        # This prevents macOS Security framework from thinking the login keychain was lost or corrupted
        lib_dir = os.path.join(isolated_data_dir, "Library")
        os.makedirs(lib_dir, exist_ok=True)
        kc_target = os.path.join(lib_dir, "Keychains")
        real_kc = os.path.expanduser("~/Library/Keychains")
        if os.path.exists(real_kc) and not os.path.exists(kc_target):
            try:
                os.symlink(real_kc, kc_target)
            except Exception:
                pass

        # Optional: Copy existing chat history and local workspace data
        app_key = app_info["name"].lower()
        if copy_existing_data:
            if "antigravity" in app_key:
                real_ag_dir = os.path.expanduser("~/.gemini/antigravity")
                target_ag_dir = os.path.join(isolated_data_dir, ".gemini", "antigravity")
                if os.path.exists(real_ag_dir) and not os.path.exists(target_ag_dir):
                    try:
                        os.makedirs(os.path.dirname(target_ag_dir), exist_ok=True)
                        shutil.copytree(real_ag_dir, target_ag_dir, ignore=shutil.ignore_patterns("crashes", "Singleton*"))
                    except Exception:
                        pass
                real_config = os.path.expanduser("~/.gemini/config")
                target_config = os.path.join(isolated_data_dir, ".gemini", "config")
                if os.path.exists(real_config) and not os.path.exists(target_config):
                    try:
                        shutil.copytree(real_config, target_config)
                    except Exception:
                        pass

            if "chatgpt" in app_key or "codex" in app_key:
                real_codex = os.path.expanduser("~/.codex")
                target_codex = os.path.join(isolated_data_dir, ".codex")
                if os.path.exists(real_codex) and not os.path.exists(target_codex):
                    try:
                        shutil.copytree(real_codex, target_codex)
                        # Remove existing auth.json so Account A credentials do not bleed into clone
                        auth_file = os.path.join(target_codex, "auth.json")
                        if os.path.exists(auth_file):
                            os.remove(auth_file)
                        auth_lock = os.path.join(target_codex, "auth.lock")
                        if os.path.exists(auth_lock):
                            os.remove(auth_lock)
                    except Exception:
                        pass

            if "claude" in app_key:
                real_claude = os.path.expanduser("~/.claude")
                target_claude = os.path.join(isolated_data_dir, ".claude")
                if os.path.exists(real_claude) and not os.path.exists(target_claude):
                    try:
                        shutil.copytree(real_claude, target_claude)
                    except Exception:
                        pass

        # Remove existing clone if any
        if os.path.exists(clone_app_path):
            shutil.rmtree(clone_app_path)

        # APFS instant clone of the entire app bundle (0 extra disk space on APFS)
        subprocess.run(["cp", "-cR", app_path, clone_app_path], check=True)

        contents_dir = os.path.join(clone_app_path, "Contents")
        macos_dir = os.path.join(contents_dir, "MacOS")
        resources_dir = os.path.join(contents_dir, "Resources")

        # 1. Configure Info.plist with unique bundle ID and display name
        plist_path = os.path.join(contents_dir, "Info.plist")
        with open(plist_path, "rb") as f:
            clone_plist = plistlib.load(f)

        unique_bundle_id = f"com.cloner.{app_slug}.{profile_slug}"
        clone_plist["CFBundleIdentifier"] = unique_bundle_id
        # Preserve CFBundleName so Electron can locate its Helper.app bundles in Frameworks
        orig_bundle_name = clone_plist.get("CFBundleName", app_info["name"])
        clone_plist["CFBundleName"] = orig_bundle_name
        clone_plist["CFBundleDisplayName"] = clone_name
        clone_plist["ClonerProfileName"] = clean_profile
        clone_plist["ClonerBaseAppName"] = app_info["name"]
        clone_plist["ClonerBaseAppPath"] = app_path
        clone_plist["ClonerDataDir"] = isolated_data_dir
        clone_plist["ClonerBadgeColor"] = badge_color
        clone_plist["ClonerAppType"] = app_info["type"]

        with open(plist_path, "wb") as f:
            plistlib.dump(clone_plist, f)

        # 1.5 Customise Owl / Codex framework configuration if present
        owl_ini = os.path.join(resources_dir, "owl-app.ini")
        if os.path.exists(owl_ini):
            try:
                with open(owl_ini, "r") as f:
                    content = f.read()
                content = content.replace("UserDataDirectoryName=Codex", f"UserDataDirectoryName=Codex_{clean_profile}")
                with open(owl_ini, "w") as f:
                    f.write(content)
            except Exception:
                pass

        # 2. Inject isolated profile wrapper in MacOS directory
        exec_name = app_info["executable_name"]
        orig_bin = os.path.join(macos_dir, exec_name)
        renamed_bin = os.path.join(macos_dir, f"{exec_name}_orig")

        if not os.path.exists(renamed_bin) and os.path.exists(orig_bin):
            os.rename(orig_bin, renamed_bin)

        real_home = os.path.expanduser("~")
        if "chatgpt" in app_key:
            launcher_script = f"""#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="{isolated_data_dir}"
REAL_HOME="{real_home}"

mkdir -p "$DATA_DIR/data" "$DATA_DIR/Library" "$DATA_DIR/tmp"
chmod 700 "$DATA_DIR"

if [ -d "$REAL_HOME/Library/Keychains" ] && [ ! -e "$DATA_DIR/Library/Keychains" ]; then
    ln -s "$REAL_HOME/Library/Keychains" "$DATA_DIR/Library/Keychains" 2>/dev/null || true
fi

export HOME="$DATA_DIR"
export TMPDIR="$DATA_DIR/tmp"
export CODEX_ELECTRON_USER_DATA_PATH="$DATA_DIR/data"
export XDG_CONFIG_HOME="$DATA_DIR/.config"
export XDG_DATA_HOME="$DATA_DIR/.local/share"
export XDG_CACHE_HOME="$DATA_DIR/.cache"

exec "$DIR/{exec_name}_orig" --user-data-dir="$DATA_DIR/data" "$@"
"""
        elif "antigravity ide" in app_key or "code" in app_key:
            launcher_script = f"""#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="{isolated_data_dir}"
REAL_HOME="{real_home}"

mkdir -p "$DATA_DIR/data" "$DATA_DIR/extensions" "$DATA_DIR/Library"
chmod 700 "$DATA_DIR"

if [ -d "$REAL_HOME/Library/Keychains" ] && [ ! -e "$DATA_DIR/Library/Keychains" ]; then
    ln -s "$REAL_HOME/Library/Keychains" "$DATA_DIR/Library/Keychains" 2>/dev/null || true
fi

export HOME="$DATA_DIR"
export XDG_CONFIG_HOME="$DATA_DIR/.config"
export XDG_DATA_HOME="$DATA_DIR/.local/share"
export XDG_CACHE_HOME="$DATA_DIR/.cache"

exec "$DIR/{exec_name}_orig" --user-data-dir="$DATA_DIR/data" --extensions-dir="$DATA_DIR/extensions" "$@"
"""
        else:
            launcher_script = f"""#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="{isolated_data_dir}"
REAL_HOME="{real_home}"

mkdir -p "$DATA_DIR/data" "$DATA_DIR/Library"
chmod 700 "$DATA_DIR"

if [ -d "$REAL_HOME/Library/Keychains" ] && [ ! -e "$DATA_DIR/Library/Keychains" ]; then
    ln -s "$REAL_HOME/Library/Keychains" "$DATA_DIR/Library/Keychains" 2>/dev/null || true
fi

export HOME="$DATA_DIR"
export XDG_CONFIG_HOME="$DATA_DIR/.config"
export XDG_DATA_HOME="$DATA_DIR/.local/share"
export XDG_CACHE_HOME="$DATA_DIR/.cache"

exec "$DIR/{exec_name}_orig" --user-data-dir="$DATA_DIR/data" "$@"
"""

        with open(orig_bin, "w") as f:
            f.write(launcher_script)
        os.chmod(orig_bin, 0o755)

        # 3. Create badged icon
        icon_file = clone_plist.get("CFBundleIconFile", "AppIcon")
        if not icon_file.endswith(".icns"):
            icon_file += ".icns"
        out_icns = os.path.join(resources_dir, icon_file)
        initials = clean_profile[:2]
        if app_info["icon_path"] and os.path.exists(app_info["icon_path"]):
            self.create_badged_icon(app_info["icon_path"], out_icns, badge_color, initials)

        # 4. Ad-hoc codesign the full cloned bundle
        try:
            subprocess.run(["codesign", "--force", "--deep", "--sign", "-", clone_app_path],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

        # 5. Register with LaunchServices
        lsreg = "/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
        if os.path.exists(lsreg):
            subprocess.run([lsreg, "-f", clone_app_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return {
            "success": True,
            "clone_name": clone_name,
            "clone_path": clone_app_path,
            "data_dir": isolated_data_dir,
            "bundle_id": unique_bundle_id
        }

    def list_active_clones(self) -> List[Dict[str, Any]]:
        """Scans the Desktop and legacy Cloner directory for created clone applications."""
        clones = []
        dirs_to_scan = [self.cloner_dir]
        legacy_dir = os.path.expanduser("~/Desktop/Cloner")
        if os.path.exists(legacy_dir) and os.path.abspath(legacy_dir) != os.path.abspath(self.cloner_dir):
            dirs_to_scan.append(legacy_dir)

        seen_paths = set()
        for scan_dir in dirs_to_scan:
            if not os.path.exists(scan_dir):
                continue

            for item in sorted(os.listdir(scan_dir)):
                if not item.endswith(".app"):
                    continue
                app_path = os.path.join(scan_dir, item)
                if app_path in seen_paths:
                    continue
                plist_path = os.path.join(app_path, "Contents", "Info.plist")
                if not os.path.exists(plist_path):
                    continue
                try:
                    with open(plist_path, "rb") as f:
                        plist = plistlib.load(f)
                    if "ClonerProfileName" not in plist:
                        continue

                    seen_paths.add(app_path)
                    profile_name = plist.get("ClonerProfileName", "")
                    base_name = plist.get("ClonerBaseAppName", item.replace(".app", ""))
                    base_path = plist.get("ClonerBaseAppPath", "")
                    data_dir = plist.get("ClonerDataDir", "")
                    badge_color = plist.get("ClonerBadgeColor", "#3B82F6")
                    bundle_id = plist.get("CFBundleIdentifier", "")

                    # Check if running by matching isolated data directory in arguments
                    is_running = False
                    try:
                        check = subprocess.run(["pgrep", "-f", data_dir], capture_output=True, text=True)
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
        """Deletes a clone application by moving to Trash and optionally purges its profile data."""
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

        # Unregister from LaunchServices
        lsreg = "/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
        if os.path.exists(lsreg):
            subprocess.run([lsreg, "-u", clone_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Move .app bundle to macOS Trash
        try:
            res = subprocess.run(["osascript", "-e", f'tell application "Finder" to delete POSIX file "{clone_path}"'], capture_output=True)
            if res.returncode == 0:
                return True
        except Exception:
            pass

        # Fallback to rmtree if Finder is unavailable
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
    parser.add_argument("--copy-existing-data", action="store_true", help="Copy existing chats and workspace state")
    parser.add_argument("--clone-path", help="Path to clone app bundle")
    parser.add_argument("--remove-data", action="store_true", help="Delete isolated data directory")
    parser.add_argument("--data-dir", help="Data directory path")

    args = parser.parse_args()
    engine = ClonerEngine()

    if args.command == "scan":
        apps = engine.scan_installed_apps()
        print(json.dumps(apps, indent=2))
    elif args.command == "create":
        res = engine.create_app_clone(args.app_path, args.profile, args.color, copy_existing_data=args.copy_existing_data)
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
