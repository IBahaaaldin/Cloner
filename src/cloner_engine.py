#!/usr/bin/env python3
"""
Cloner Engine
Core backend logic for detecting, cloning, badging, and managing macOS AI applications.
"""

import os
import sys
import json
import time
import signal
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
            "type": app_type,
            "version": str(plist.get("CFBundleShortVersionString", "")),
            "build": str(plist.get("CFBundleVersion", ""))
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

        unique_bundle_id = f"com.cloner.{app_slug}.{profile_slug}"
        self._configure_clone_bundle(
            target_bundle_path=clone_app_path,
            base_app_path=app_path,
            app_info=app_info,
            clone_name=clone_name,
            clean_profile=clean_profile,
            unique_bundle_id=unique_bundle_id,
            isolated_data_dir=isolated_data_dir,
            badge_color=badge_color,
        )

        return {
            "success": True,
            "clone_name": clone_name,
            "clone_path": clone_app_path,
            "data_dir": isolated_data_dir,
            "bundle_id": unique_bundle_id
        }

    def _build_launcher_script(
        self,
        app_key: str,
        exec_name: str,
        isolated_data_dir: str,
        base_app_path: str,
    ) -> str:
        """Builds an isolated wrapper script with automatic base-app version sync on launch."""
        real_home = os.path.expanduser("~")
        is_chatgpt = "chatgpt" in app_key
        is_ide = ("antigravity ide" in app_key or "code" in app_key) and not is_chatgpt

        extra_dirs = ' "$DATA_DIR/tmp"' if is_chatgpt else (' "$DATA_DIR/extensions"' if is_ide else "")
        extra_exports = (
            'export TMPDIR="$DATA_DIR/tmp"\n'
            'export CODEX_ELECTRON_USER_DATA_PATH="$DATA_DIR/data"\n'
            if is_chatgpt
            else ""
        )
        extra_args = ' --extensions-dir="$DATA_DIR/extensions"' if is_ide else ""

        return f"""#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
APP_BUNDLE="$(cd "$DIR/../.." && pwd)"
DATA_DIR="{isolated_data_dir}"
REAL_HOME="{real_home}"
CLONE_PLIST="$DIR/../Info.plist"

if [ -z "$CLONER_SYNC_ATTEMPTED" ] && [ -f "$CLONE_PLIST" ]; then
    BASE_APP=$(/usr/bin/defaults read "$CLONE_PLIST" ClonerBaseAppPath 2>/dev/null)
    [ -z "$BASE_APP" ] && BASE_APP="{base_app_path}"
    BASE_PLIST="$BASE_APP/Contents/Info.plist"
    if [ -f "$BASE_PLIST" ]; then
        BASE_VER=$(/usr/bin/defaults read "$BASE_PLIST" CFBundleShortVersionString 2>/dev/null || true)
        CLONE_VER=$(/usr/bin/defaults read "$CLONE_PLIST" CFBundleShortVersionString 2>/dev/null || true)
        BASE_BUILD=$(/usr/bin/defaults read "$BASE_PLIST" CFBundleVersion 2>/dev/null || true)
        CLONE_BUILD=$(/usr/bin/defaults read "$CLONE_PLIST" CFBundleVersion 2>/dev/null || true)
        if [ -n "$BASE_VER" ] && {{ [ "$BASE_VER" != "$CLONE_VER" ] || [ "$BASE_BUILD" != "$CLONE_BUILD" ]; }}; then
            if ! /usr/bin/pgrep -f -- "--user-data-dir=$DATA_DIR[/]data" >/dev/null 2>&1; then
                CLONER_ENGINE=""
                for p in "/Applications/Cloner.app/Contents/Resources/cloner_engine.py" \\
                         "$REAL_HOME/Applications/Cloner.app/Contents/Resources/cloner_engine.py" \\
                         "$REAL_HOME/Desktop/Cloner.app/Contents/Resources/cloner_engine.py" \\
                         "$REAL_HOME/Desktop/Cloner/src/cloner_engine.py"; do
                    if [ -f "$p" ]; then
                        CLONER_ENGINE="$p"
                        break
                    fi
                done
                if [ -n "$CLONER_ENGINE" ]; then
                    export CLONER_SYNC_ATTEMPTED=1
                    if /usr/bin/python3 "$CLONER_ENGINE" sync --clone-path "$APP_BUNDLE" >/dev/null 2>&1; then
                        NEW_EXEC=$(/usr/bin/defaults read "$APP_BUNDLE/Contents/Info.plist" CFBundleExecutable 2>/dev/null || basename "$0")
                        if [ -x "$APP_BUNDLE/Contents/MacOS/$NEW_EXEC" ]; then
                            exec "$APP_BUNDLE/Contents/MacOS/$NEW_EXEC" "$@"
                        fi
                    fi
                fi
            fi
        fi
    fi
fi

mkdir -p "$DATA_DIR/data" "$DATA_DIR/Library"{extra_dirs}
chmod 700 "$DATA_DIR"

if [ -d "$REAL_HOME/Library/Keychains" ] && [ ! -e "$DATA_DIR/Library/Keychains" ]; then
    ln -s "$REAL_HOME/Library/Keychains" "$DATA_DIR/Library/Keychains" 2>/dev/null || true
fi

export HOME="$DATA_DIR"
{extra_exports}export XDG_CONFIG_HOME="$DATA_DIR/.config"
export XDG_DATA_HOME="$DATA_DIR/.local/share"
export XDG_CACHE_HOME="$DATA_DIR/.cache"

exec "$DIR/{exec_name}_orig" --user-data-dir="$DATA_DIR/data"{extra_args} "$@"
"""

    def _configure_clone_bundle(
        self,
        target_bundle_path: str,
        base_app_path: str,
        app_info: Dict[str, Any],
        clone_name: str,
        clean_profile: str,
        unique_bundle_id: str,
        isolated_data_dir: str,
        badge_color: str,
    ) -> None:
        """Applies Cloner plist metadata, launcher wrapper, badged icon, and ad-hoc signature."""
        contents_dir = os.path.join(target_bundle_path, "Contents")
        macos_dir = os.path.join(contents_dir, "MacOS")
        resources_dir = os.path.join(contents_dir, "Resources")

        plist_path = os.path.join(contents_dir, "Info.plist")
        with open(plist_path, "rb") as f:
            clone_plist = plistlib.load(f)

        clone_plist["CFBundleIdentifier"] = unique_bundle_id
        # Preserve CFBundleName so Electron can locate its Helper.app bundles in Frameworks
        orig_bundle_name = clone_plist.get("CFBundleName", app_info["name"])
        clone_plist["CFBundleName"] = orig_bundle_name
        clone_plist["CFBundleDisplayName"] = clone_name
        clone_plist["ClonerProfileName"] = clean_profile
        clone_plist["ClonerBaseAppName"] = app_info["name"]
        clone_plist["ClonerBaseAppPath"] = base_app_path
        clone_plist["ClonerDataDir"] = isolated_data_dir
        clone_plist["ClonerBadgeColor"] = badge_color
        clone_plist["ClonerAppType"] = app_info["type"]

        with open(plist_path, "wb") as f:
            plistlib.dump(clone_plist, f)

        # Customise Owl / Codex framework configuration if present
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

        # Inject isolated profile wrapper in MacOS directory
        exec_name = app_info["executable_name"]
        orig_bin = os.path.join(macos_dir, exec_name)
        renamed_bin = os.path.join(macos_dir, f"{exec_name}_orig")

        if not os.path.exists(renamed_bin) and os.path.exists(orig_bin):
            os.rename(orig_bin, renamed_bin)

        app_key = app_info["name"].lower()
        launcher_script = self._build_launcher_script(app_key, exec_name, isolated_data_dir, base_app_path)
        with open(orig_bin, "w") as f:
            f.write(launcher_script)
        os.chmod(orig_bin, 0o755)

        # Create badged icon
        icon_file = clone_plist.get("CFBundleIconFile", "AppIcon")
        if not icon_file.endswith(".icns"):
            icon_file += ".icns"
        out_icns = os.path.join(resources_dir, icon_file)
        initials = clean_profile[:2]
        if app_info["icon_path"] and os.path.exists(app_info["icon_path"]):
            self.create_badged_icon(app_info["icon_path"], out_icns, badge_color, initials)

        # Ad-hoc codesign the cloned bundle
        try:
            subprocess.run(["codesign", "--force", "--deep", "--sign", "-", target_bundle_path],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

        # Register with LaunchServices
        lsreg = "/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
        if os.path.exists(lsreg):
            subprocess.run([lsreg, "-f", target_bundle_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _resolve_base_app_path(self, base_path: str, base_name: str) -> Optional[str]:
        """Resolves the base application path, checking standard Application folders if moved."""
        candidates = []
        if base_path:
            candidates.append(base_path)
        clean_base = base_name.replace(".app", "")
        if clean_base:
            candidates.extend([
                f"/Applications/{clean_base}.app",
                os.path.expanduser(f"~/Applications/{clean_base}.app"),
            ])
        for candidate in candidates:
            if candidate and os.path.exists(candidate):
                return candidate
        return None

    def _find_clone_pids(self, clone_path: str, data_dir: str) -> List[int]:
        """Returns active PIDs belonging to a cloned application without matching self."""
        my_pids = {os.getpid(), os.getppid()}
        macos_prefix = os.path.join(clone_path, "Contents", "MacOS") + os.sep
        fw_prefix = os.path.join(clone_path, "Contents", "Frameworks") + os.sep
        data_flag = f"--user-data-dir={data_dir}/data" if data_dir else ""
        pids = []
        try:
            ps = subprocess.run(["ps", "-eo", "pid=,args="], capture_output=True, text=True)
            if ps.returncode != 0:
                return pids
            for line in ps.stdout.splitlines():
                stripped = line.strip()
                if not stripped:
                    continue
                parts = stripped.split(None, 1)
                if len(parts) < 2:
                    continue
                try:
                    pid = int(parts[0])
                except ValueError:
                    continue
                if pid in my_pids:
                    continue
                args = parts[1]
                if macos_prefix in args or fw_prefix in args or (data_flag and data_flag in args):
                    pids.append(pid)
        except Exception:
            pass
        return pids

    def _is_clone_running(self, clone_path: str, data_dir: str) -> bool:
        """Checks if a cloned application process is currently running."""
        return bool(self._find_clone_pids(clone_path, data_dir))

    def _stop_clone_processes(self, clone_path: str, data_dir: str, timeout_sec: float = 5.0) -> bool:
        """Gracefully terminates running processes for a clone before an in-place update."""
        pids = self._find_clone_pids(clone_path, data_dir)
        if not pids:
            return True
        for pid in pids:
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            except Exception:
                pass
        deadline = time.time() + timeout_sec
        while time.time() < deadline:
            if not self._find_clone_pids(clone_path, data_dir):
                return True
            time.sleep(0.15)
        return not self._find_clone_pids(clone_path, data_dir)

    def sync_app_clone(self, clone_path: str, force: bool = False, stop_if_running: bool = False) -> Dict[str, Any]:
        """Updates an existing clone bundle from its base app while preserving isolated data."""
        if not clone_path or not os.path.exists(clone_path):
            return {"success": False, "error": f"Clone bundle not found: {clone_path}"}

        plist_path = os.path.join(clone_path, "Contents", "Info.plist")
        if not os.path.exists(plist_path):
            return {"success": False, "error": "Clone Info.plist missing"}

        try:
            with open(plist_path, "rb") as f:
                clone_plist = plistlib.load(f)
        except Exception as e:
            return {"success": False, "error": f"Failed to read clone plist: {e}"}

        profile_name = clone_plist.get("ClonerProfileName")
        if not profile_name:
            return {"success": False, "error": "Target is not a valid Cloner bundle"}

        base_name = clone_plist.get("ClonerBaseAppName", os.path.basename(clone_path).replace(".app", ""))
        base_path = self._resolve_base_app_path(clone_plist.get("ClonerBaseAppPath", ""), base_name)
        if not base_path:
            return {"success": False, "error": f"Base app '{base_name}' not found"}

        app_info = self._inspect_app(base_path, default_type=clone_plist.get("ClonerAppType", "auto"))
        if not app_info:
            return {"success": False, "error": f"Base app at {base_path} is invalid"}

        old_version = str(clone_plist.get("CFBundleShortVersionString", ""))
        old_build = str(clone_plist.get("CFBundleVersion", ""))
        new_version = app_info.get("version", "")
        new_build = app_info.get("build", "")
        data_dir = clone_plist.get("ClonerDataDir", "")

        if self._is_clone_running(clone_path, data_dir):
            if not stop_if_running:
                return {"success": False, "running": True, "error": f"{os.path.basename(clone_path)} is currently running. Please quit it first."}
            if not self._stop_clone_processes(clone_path, data_dir):
                return {"success": False, "running": True, "error": f"Could not close all processes for {os.path.basename(clone_path)}. Please quit it manually."}

        exec_script = os.path.join(clone_path, "Contents", "MacOS", clone_plist.get("CFBundleExecutable", ""))
        has_auto_sync = False
        if os.path.exists(exec_script):
            try:
                with open(exec_script, "rb") as sf:
                    has_auto_sync = b"CLONER_SYNC_ATTEMPTED" in sf.read(8192)
            except Exception:
                pass

        version_changed = bool(new_version and (new_version != old_version or new_build != old_build))
        if not force and not version_changed and has_auto_sync:
            return {
                "success": True,
                "updated": False,
                "clone_path": clone_path,
                "old_version": old_version,
                "new_version": new_version,
            }

        clone_name = clone_plist.get("CFBundleDisplayName", os.path.basename(clone_path).replace(".app", ""))
        badge_color = clone_plist.get("ClonerBadgeColor", "#3B82F6")
        unique_bundle_id = clone_plist.get("CFBundleIdentifier", f"com.cloner.{base_name.lower()}.{profile_name.lower()}")

        staging_path = f"{clone_path}.sync_tmp"
        backup_path = f"{clone_path}.sync_bak"
        for tmp in (staging_path, backup_path):
            if os.path.exists(tmp):
                shutil.rmtree(tmp, ignore_errors=True)

        try:
            subprocess.run(["cp", "-cR", base_path, staging_path], check=True)
            self._configure_clone_bundle(
                target_bundle_path=staging_path,
                base_app_path=base_path,
                app_info=app_info,
                clone_name=clone_name,
                clean_profile=profile_name,
                unique_bundle_id=unique_bundle_id,
                isolated_data_dir=data_dir,
                badge_color=badge_color,
            )

            os.rename(clone_path, backup_path)
            try:
                os.rename(staging_path, clone_path)
            except Exception as swap_err:
                os.rename(backup_path, clone_path)
                raise swap_err

            try:
                os.utime(clone_path, None)
            except Exception:
                pass
            shutil.rmtree(backup_path, ignore_errors=True)

            lsreg = "/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister"
            if os.path.exists(lsreg):
                subprocess.run([lsreg, "-f", clone_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            return {
                "success": True,
                "updated": True,
                "clone_name": clone_name,
                "clone_path": clone_path,
                "old_version": old_version,
                "new_version": new_version,
            }
        except Exception as e:
            if os.path.exists(staging_path):
                shutil.rmtree(staging_path, ignore_errors=True)
            return {"success": False, "error": f"Failed to sync clone: {e}"}

    def sync_outdated_clones(self) -> Dict[str, Any]:
        """Automatically syncs all non-running outdated clones or clones missing self-sync wrappers."""
        clones = self.list_active_clones()
        synced = []
        skipped_running = []
        errors = []
        for clone in clones:
            if not clone.get("needs_update") and clone.get("has_auto_sync", True):
                continue
            if clone.get("is_running"):
                if clone.get("needs_update"):
                    skipped_running.append(clone["name"])
                continue
            res = self.sync_app_clone(clone["path"])
            if res.get("success") and res.get("updated"):
                synced.append({
                    "name": clone["name"],
                    "old_version": res.get("old_version", ""),
                    "new_version": res.get("new_version", ""),
                })
            elif not res.get("success"):
                errors.append({"name": clone["name"], "error": res.get("error", "Unknown error")})

        return {"success": True, "synced": synced, "skipped_running": skipped_running, "errors": errors}

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
                    clone_version = str(plist.get("CFBundleShortVersionString", ""))
                    clone_build = str(plist.get("CFBundleVersion", ""))

                    resolved_base = self._resolve_base_app_path(base_path, base_name)
                    base_version = ""
                    base_build = ""
                    if resolved_base:
                        base_plist_path = os.path.join(resolved_base, "Contents", "Info.plist")
                        if os.path.exists(base_plist_path):
                            try:
                                with open(base_plist_path, "rb") as bf:
                                    bplist = plistlib.load(bf)
                                base_version = str(bplist.get("CFBundleShortVersionString", ""))
                                base_build = str(bplist.get("CFBundleVersion", ""))
                            except Exception:
                                pass

                    needs_update = bool(base_version and (base_version != clone_version or base_build != clone_build))

                    exec_script = os.path.join(app_path, "Contents", "MacOS", plist.get("CFBundleExecutable", ""))
                    has_auto_sync = False
                    if os.path.exists(exec_script):
                        try:
                            with open(exec_script, "rb") as sf:
                                has_auto_sync = b"CLONER_SYNC_ATTEMPTED" in sf.read(8192)
                        except Exception:
                            pass

                    is_running = self._is_clone_running(app_path, data_dir)

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
                        "base_app_path": resolved_base or base_path,
                        "data_dir": data_dir,
                        "badge_color": badge_color,
                        "bundle_id": bundle_id,
                        "version": clone_version,
                        "base_version": base_version,
                        "needs_update": needs_update,
                        "has_auto_sync": has_auto_sync,
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
    parser.add_argument("command", choices=["scan", "create", "list", "delete", "launch", "reveal", "open-data", "sync", "sync-all"])
    parser.add_argument("--app-path", help="Path to base app")
    parser.add_argument("--profile", help="Profile name")
    parser.add_argument("--color", default="#3B82F6", help="Badge hex color")
    parser.add_argument("--copy-existing-data", action="store_true", help="Copy existing chats and workspace state")
    parser.add_argument("--clone-path", help="Path to clone app bundle")
    parser.add_argument("--remove-data", action="store_true", help="Delete isolated data directory")
    parser.add_argument("--data-dir", help="Data directory path")
    parser.add_argument("--force", action="store_true", help="Force sync even if version matches")
    parser.add_argument("--stop-if-running", action="store_true", help="Stop running clone processes before syncing")

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
    elif args.command == "sync":
        res = engine.sync_app_clone(args.clone_path, force=args.force, stop_if_running=args.stop_if_running)
        print(json.dumps(res, indent=2))
    elif args.command == "sync-all":
        res = engine.sync_outdated_clones()
        print(json.dumps(res, indent=2))
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
