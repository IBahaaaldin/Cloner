# Cloner ⚡ Multi-Account macOS App Cloner

A lightweight, dark-mode native macOS utility that allows you to run multiple independent accounts for **ChatGPT**, **Claude Desktop**, **AntiGravity**, and **AntiGravity IDE** side-by-side simultaneously.

---

## 🌟 Features

- **True Account Isolation:** Each clone maintains its own completely isolated storage, cookies, local database, and chat history.
- **Side-by-Side Simultaneous Execution:** Run your personal and work accounts at the exact same time without logging out.
- **Dock & Finder Integration:** Every clone is an authentic macOS `.app` bundle placed right in `Desktop/Cloner/`. Drag them to your Dock or Applications folder.
- **Badged App Icons:** Clones receive a customized icon with a distinct profile accent color (Electric Blue, Emerald, Purple, Amber, Crimson, Cyan).
- **Auto-Updating Engine:** Clones reference the parent app engine while keeping data separate, meaning clones automatically inherit app updates when the main app in `/Applications` updates.
- **Dark macOS UI:** Modern, matte dark aesthetic matching macOS power-user utilities with squircle app cards.

---

## 🚀 Quick Start

1. Open **Cloner**:
   - Double-click `Cloner.app` inside this folder, or run:
     ```bash
     open ~/Desktop/Cloner/Cloner.app
     ```
2. Select any detected application (**ChatGPT**, **Claude**, **AntiGravity**, etc.).
3. Enter your profile name (e.g. `Work`, `Client A`, `Personal 2`).
4. Pick a badge accent color and click **Create Clone**.
5. Your new app (e.g., `ChatGPT (Work).app`) is created instantly in this folder!

---

## 📂 Where is Profile Data Stored?

Each clone's data is safely sandboxed in:
```
~/Library/Application Support/Cloner/<App>/<Profile>/
```
Inside the Cloner app, you can click the **Data** icon on any clone to immediately open that clone's isolated folder in Finder.

---

## 🛠️ Rebuilding from Source

To recompile `Cloner.app` at any time:
```bash
./build_app.sh
```

To run the test suite:
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```
