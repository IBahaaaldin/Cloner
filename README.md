# 👥 Cloner for macOS

> Run multiple independent accounts simultaneously for AI desktop apps (ChatGPT, Claude, Antigravity, Codex, and more) with zero extra disk storage and completely separate profiles.

![Cloner Cover Banner](cover.png)

<div align="center">

[![Download Cloner DMG](https://img.shields.io/badge/Download_DMG-v1.0.3_macOS-0066cc?style=for-the-badge&logo=apple&logoColor=white)](https://github.com/IBahaaaldin/Cloner/raw/main/Cloner.dmg)
[![Download Cloner ZIP](https://img.shields.io/badge/Download_ZIP-v1.0.3_macOS-10B981?style=for-the-badge&logo=apple&logoColor=white)](https://github.com/IBahaaaldin/Cloner/raw/main/Cloner.zip)
[![macOS 14+](https://img.shields.io/badge/macOS-14.0%2B-000000?style=for-the-badge&logo=apple)](https://apple.com)
[![Architecture: Apple Silicon](https://img.shields.io/badge/Architecture-Apple_Silicon_arm64-8B5CF6?style=for-the-badge)](https://apple.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-10B981?style=for-the-badge)](LICENSE)

</div>

---

## 🌐 Visual Previews & Post Slides

| Slide 1: Editorial Cover (2160x2160) | Slide 2: In-Action App Showcase (2160x2160) | Animated Reel Promo (1080x1920) |
| :---: | :---: | :---: |
| <img src="cover-instagram.png" width="280" alt="Instagram Cover" /> | <img src="app-showcase.png" width="280" alt="Application Showcase" /> | [🎬 **Watch cloner-promo.mp4**](cloner-promo.mp4) |

*(High-resolution post pack + 60fps animated Reel video formatted for Instagram [@ibahaaaldincoding](https://www.instagram.com/ibahaaaldincoding))*

---

## ⚡ Fast & Flexible Installation

Choose whatever installation method fits you best:

### Option 1: Standalone ZIP (Easiest — Direct App, Zero Disk Mounting)
1. **[Click here to download Cloner.zip](https://github.com/IBahaaaldin/Cloner/raw/main/Cloner.zip)**
2. Unzip the file. You will get **`Cloner.app`** directly.
3. Move **`Cloner.app`** to your **Applications** folder or keep it on your **Desktop**.
4. Double-click to run! (No disk images to eject, no files locked).

---

### Option 2: 1-Line Terminal Auto-Installer
Automatically downloads, installs to `/Applications`, clears macOS Gatekeeper quarantine, and launches Cloner:
```bash
curl -sSL https://raw.githubusercontent.com/IBahaaaldin/Cloner/main/install.sh | bash
```

---

### Option 3: Traditional Disk Image (`.dmg`)
1. **[Click here to download Cloner.dmg](https://github.com/IBahaaaldin/Cloner/raw/main/Cloner.dmg)**
2. Double-click **`Cloner.dmg`** to open it.
3. Drag **`Cloner.app`** to the **Applications** shortcut.
4. **Auto-Install Prompt**: If you open Cloner directly from the disk image, Cloner will automatically offer to move itself to `/Applications` for you.
5. **How to eject/delete the DMG**: Once Cloner is installed in Applications, eject the disk from Finder's sidebar (⏏ icon), then move `Cloner.dmg` to the Trash!

> [!TIP]
> **First-Time macOS Permission Note**:  
> If macOS displays *"cannot check for malicious software"* because Cloner is an open-source tool, simply open **System Settings → Privacy & Security** and click **Open Anyway**, or double-click the included `Launch Cloner (First-Time Bypass).command`!

---

## ✨ Core Features

- **⚡ Instant APFS Cloning (<1s)**: Leverages Apple File System copy-on-write (`cp -cR`). A full application clone creates in under a second and takes **0 extra disk space**.
- **🔄 Auto-Sync Clone Updates**: Cloned apps automatically sync to match base app updates on launch (or in 1 click inside Cloner) without losing logins, sessions, or chats.
- **🚀 Built-in Cloner Auto-Updater**: Checks GitHub in the background for new Cloner releases with 1-click update & relaunch.
- **👥 Simultaneous Multi-Account Sessions**: Launch and keep your **Work** and **Personal** accounts open side-by-side at the same time. Never log out or switch profiles again.
- **🔒 True ProcessSingleton Isolation**: Overrides Chromium & Electron singleton sockets and profile directories, allowing multiple identical apps to run concurrently without redirecting focus to the main window.
- **🛡️ macOS Keychain & Privacy Safe**: Automatic Keychain linkage guarantees that macOS Security Services will never prompt you to reset your keychain passwords.
- **🎨 Custom Badged Squircle Icons**: Automatically extracts high-resolution icons and draws a color-coded profile badge with your custom initials and color accent.
- **📂 Copy Chats Option**: Want to branch off from your existing chats? Toggle **"Copy existing chats & history from primary app"** to clone your conversations, or leave it off for a completely fresh account.
- **🗑️ Safe macOS Trash Deletion**: Deleting a clone moves it safely to macOS Trash via Finder AppleEvents. Zero unrecoverable `rm -rf`.

---

## 🔬 Supported Applications

Cloner automatically detects installed macOS desktop applications that have authentication/login systems:

| Application | Supported | Profile Isolation Engine |
| :--- | :---: | :--- |
| **ChatGPT** | ✅ | Codex Framework + `--user-data-dir` + `CODEX_ELECTRON_USER_DATA_PATH` |
| **Claude Desktop** | ✅ | Electron `userData` + `--user-data-dir` |
| **Google Antigravity** | ✅ | Isolated `~/.gemini/antigravity` + dynamic port + singleton lock |
| **Antigravity IDE** | ✅ | Code engine + `--user-data-dir` + `--extensions-dir` |
| **Google Chrome / Browsers** | ✅ | Chromium `--user-data-dir` + independent profile directory |
| **Custom macOS Apps** | ✅ | Use "+ Add App..." to pick any `.app` from `/Applications` |

---

## 📁 Repository Structure

```text
├── Cloner.dmg              # 1-Click standalone macOS distribution installer
├── Cloner-1.0.3.dmg        # Versioned distribution disk image
├── Cloner.zip              # Direct standalone app archive (no DMG mounting)
├── Cloner.app/             # Pre-built standalone native macOS application bundle
├── cover.png               # Widescreen cover banner for GitHub (2560x1280)
├── cover-instagram.png     # Slide 1: High-res square Instagram cover (2160x2160)
├── app-showcase.png        # Slide 2: High-res in-action application showcase (2160x2160)
├── CAPTION.md              # Instagram post caption for @ibahaaaldincoding
├── build_app.sh            # Native Swiftc compilation and bundle assembly script
├── package_dmg.sh          # One-click DMG packaging script
├── src/
│   ├── cloner_engine.py    # APFS clone engine, login checker, badged icon generator
│   └── main.swift          # Native Cocoa + WebKit bridge and window host
├── ui/
│   ├── index.html          # Dark matte squircle user interface
│   ├── style.css           # Utility CSS matching macOS Sonoma/Sequoia aesthetic
│   └── app.js              # Native WKScriptMessageHandler client
├── tests/
│   ├── test_engine.py      # Unit test suite for clone generation
│   └── test_e2e.py         # Full end-to-end multi-app workflow verification
└── LICENSE                 # MIT License
```

---

## 🛠️ Building From Source

If you want to compile and package Cloner yourself:

```bash
# 1. Clone repository
git clone https://github.com/IBahaaaldin/Cloner.git
cd Cloner

# 2. Compile native macOS application
./build_app.sh

# 3. Package standalone distribution DMG
./package_dmg.sh

# 4. Run automated test suite
python3 -m unittest discover -s tests -p "test_*.py"
```

---

## 👤 Author & Connect

**Bahaa Mohammed**  
Creative Developer & Software Engineer  
- 📸 **Instagram**: [@ibahaaaldincoding](https://www.instagram.com/ibahaaaldincoding)  
- 🐙 **GitHub**: [@IBahaaaldin](https://github.com/IBahaaaldin)  
- 💼 **LinkedIn**: [Bahaa Mohammed](https://www.linkedin.com/in/bahaa-mohammed-371259369)  
- 📧 **Email**: bahaam.coding@gmail.com  

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
