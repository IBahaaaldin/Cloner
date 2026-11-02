# Cloner: Multi-Account macOS App Cloner
**Design Document**
**Date:** 2026-11-02
**Target Location:** `/Users/bahaam/Desktop/Cloner`

---

## 1. Intent and the "Why"
AI desktop applications—specifically **ChatGPT**, **Claude Desktop**, and **AntiGravity / AntiGravity IDE**—do not natively support signing into multiple accounts at the same time within a single application instance. Logging out and back in is slow, disrupts open chats and active sessions, and limits productivity.

**Cloner** is a dedicated visual macOS tool placed in `/Users/bahaam/Desktop/Cloner`. It creates independent, isolated application clones (e.g., `ChatGPT (Work).app`, `Claude (Client A).app`, `AntiGravity (Personal).app`) that run side-by-side simultaneously with their own separate logins and chat histories.

---

## 2. Goals, Non-Goals, and Anti-Goals

### Goals
1. **Dedicated Visual Mac App (`Cloner.app`):**
   - Resides in `/Users/bahaam/Desktop/Cloner/Cloner.app`.
   - Clean, modern dark macOS UI directly matching the user's reference screenshot (dark `#0D0D10` surface, squircle app cards with subtle glow, crisp sans-serif typography).
2. **Instant Profile App Generation:**
   - Detects installed target AI apps: **ChatGPT**, **Claude Desktop**, **AntiGravity**, and **AntiGravity IDE** (plus custom app support).
   - Generates dedicated `.app` bundles directly inside `~/Desktop/Cloner/` in seconds.
   - Each clone is draggable to the Dock or Applications folder.
3. **Session and Data Isolation:**
   - Electron apps (Claude Desktop, AntiGravity, AntiGravity IDE) use dedicated `--user-data-dir` inside `~/Library/Application Support/Cloner/<AppName>/<ProfileName>/`.
   - Native apps (ChatGPT) use isolated WebKit cookie and data storage so sessions, tokens, and active chats never collide with the primary app.
4. **Clean Login Window for New Clones:**
   - Authentication opens in an isolated login session rather than inheriting cookies from the user's personal default browser (Safari/Chrome), making signing into a distinct account seamless.
5. **Visual Differentiation:**
   - Badged macOS squircle icons with color accents and profile tags.
   - Shows as an independent app in the Dock with its own name and icon.
6. **Automatic Upstream Compatibility:**
   - Clones reference the parent app executable while maintaining isolated data. When the parent app in `/Applications` updates, all clones immediately benefit from the update without breaking or requiring re-cloning.
7. **Lifecycle Management:**
   - View all created clones.
   - 1-click **Launch**.
   - 1-click **Reveal in Finder**.
   - 1-click **Open Data Folder**.
   - 1-click **Delete** (with optional data cleanup).

### Non-Goals
- Modifying closed-source vendor binaries via memory injection or patching.
- Cloud syncing profile data between different physical Mac computers.

### Anti-Goals
- Never modify or write to original apps in `/Applications`.
- Never leak or share credentials between profiles.
- Never require terminal commands for normal user workflows.

---

## 3. UI / UX Design Specifications

### Aesthetic (Matching Reference Screenshot)
- **Background:** Deep dark `#0C0D10` with subtle border borders (`#1F2028`).
- **App Gallery Bar:** Horizontal row of dark squircle cards (matching the user's image with apps like MenuKit / Purge style), showing app icon, title, and "Create Clone" trigger.
- **Creator Modal / Sheet:**
  - App icon with live preview of the badge.
  - Profile Name field (e.g. "Work", "Secondary", "Client X").
  - Color badge picker (Electric Blue, Emerald Green, Violet, Amber, Crimson, Cyan).
  - "Create Clone" primary action.
- **Active Clones Dashboard:**
  - Card grid of all active clones.
  - Status indicator (Ready / Running).
  - Quick action buttons: **Open App**, **Show in Finder**, **Storage**, **Delete**.

---

## 4. Technical Architecture

### 4.1 Cloner App (`Cloner.app`)
- **Native Host:** macOS Cocoa/WebKit application compiled with `swiftc` into a lightweight, standalone app bundle with zero external dependencies.
- **Bridge:** Bidirectional messaging via `WKScriptMessageHandler`:
  - `detectApps`: Scans `/Applications` for ChatGPT, Claude, AntiGravity, AntiGravity IDE.
  - `listClones`: Scans `/Users/bahaam/Desktop/Cloner/` for `.app` bundles and reads metadata.
  - `createClone`: Generates the badged `.app` bundle and initializes profile storage.
  - `launchClone`: Launches the clone via `NSWorkspace`.
  - `deleteClone`: Moves the clone `.app` to Trash and removes profile data if confirmed.
  - `revealInFinder`: Focuses the file in Finder.

### 4.2 Clone App Bundle Architecture
For a clone named `ChatGPT (Work).app`:
```
/Users/bahaam/Desktop/Cloner/ChatGPT (Work).app/
├── Contents/
│   ├── Info.plist               # CFBundleIdentifier: com.cloner.chatgpt.work
│   │                            # CFBundleName: ChatGPT (Work)
│   ├── MacOS/
│   │   └── launcher             # Native launcher script setting up isolated env
│   └── Resources/
│       └── AppIcon.icns         # Custom badged icon generated at creation time
```

### 4.3 Profile Isolation
- **Claude Desktop & AntiGravity:**
  Launcher executes:
  `"/Applications/<AppName>.app/Contents/MacOS/<Executable>" --user-data-dir="~/Library/Application Support/Cloner/<AppName>/<ProfileName>"`
- **ChatGPT:**
  Launcher executes with isolated WebKit data store and application support directory in `~/Library/Application Support/Cloner/ChatGPT/<ProfileName>`, ensuring total separation of cookies, local storage, and history.

---

## 5. Builder Review Decisions
1. **Upstream Updates:** Clones act as dedicated wrappers around `/Applications/<App>.app`, so vendor auto-updates never break clones and clones never bloat disk space.
2. **Login Isolation:** Clean, isolated authentication window to prevent auto-login collisions with the default web browser.
3. **App Scope:** Tailored out of the box for ChatGPT, Claude Desktop, AntiGravity, and AntiGravity IDE, with an extensible architecture for other macOS apps.
