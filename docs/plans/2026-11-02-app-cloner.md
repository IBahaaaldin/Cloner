# Cloner: Multi-Account macOS App Cloner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone, dark-themed visual macOS application (`Cloner.app`) in `~/Desktop/Cloner` that enables users to create and manage independent, simultaneously runnable account clones of ChatGPT, Claude Desktop, AntiGravity, and AntiGravity IDE with isolated profiles and badged icons.

**Architecture:** A native Swift Cocoa + WKWebView desktop application (`Cloner.app`) hosting a pixel-perfect dark UI inspired by the user's reference image, backed by a Swift/Python cloning engine that dynamically creates customized `.app` wrapper bundles with isolated data directories, custom bundle IDs, badged `.icns` icons, and ad-hoc code signatures.

**Tech Stack:** Swift (Cocoa, WebKit, CoreGraphics), Python 3 / Shell, HTML5 / CSS3 / Vanilla JS, macOS LaunchServices & `codesign`.

**Spec:** `/Users/bahaam/Desktop/Cloner/docs/specs/2026-11-02-app-cloner-design.md`

## Global Constraints
- Target location: `/Users/bahaam/Desktop/Cloner/`
- Target platform: macOS 14+ / Sonoma / Sequoia / 26.6 on Apple Silicon (arm64)
- Zero modification to primary apps in `/Applications`
- Isolated data root: `~/Library/Application Support/Cloner/<AppName>/<ProfileName>/`
- Clones must be standalone `.app` bundles runnable via Finder or Dock with independent Dock items
- Ad-hoc code signing (`codesign --force --deep --sign -`) on all created clone bundles

## Review Focus
1. **Spaces in app paths or profile names:** Profile names like "Work Account" or "Client A & B" must be safely quoted and sanitized in Info.plist, launcher scripts, and file paths.
2. **Concurrent launches:** Launching the clone while the original app is running must open a separate window/instance instead of activating the already open parent instance.
3. **Data directory permissions:** Newly initialized profile directories must have standard `0700` user permissions and proper directory scaffolding.
4. **Dock icon and bundle cache:** macOS LaunchServices sometimes caches old icons; clones must register their icon bundle properly via `touch` or `lsregister`.
5. **Clean deletion:** Removing a clone must cleanly remove the `.app` bundle from `Desktop/Cloner` and give the option to purge or keep the isolated profile data.

---

### Task 1: Core Cloning Engine & Icon Badging Utilities

**Files:**
- Create: `/Users/bahaam/Desktop/Cloner/src/cloner_engine.py`
- Create: `/Users/bahaam/Desktop/Cloner/tests/test_engine.py`

**Interfaces:**
- Produces:
  - `scan_installed_apps() -> List[Dict]`
  - `generate_badged_icon(src_icns: str, out_icns: str, badge_color: str, badge_label: str) -> bool`
  - `create_app_clone(app_key: str, profile_name: str, badge_color: str) -> Dict`
  - `list_active_clones() -> List[Dict]`
  - `delete_app_clone(clone_name: str, remove_data: bool) -> bool`
  - `launch_app_clone(clone_name: str) -> bool`

- [ ] **Step 1: Write test for app detection and clone generation**
  Create `tests/test_engine.py` asserting:
  - `scan_installed_apps()` detects `/Applications/ChatGPT.app`, `/Applications/Claude.app`, `/Applications/Antigravity.app`.
  - `create_app_clone()` creates a valid `.app` bundle in `/Users/bahaam/Desktop/Cloner/` with valid `Contents/Info.plist` containing unique `CFBundleIdentifier`.
  - Clone contains executable launcher with isolated `--user-data-dir` or profile path.

- [ ] **Step 2: Run test to verify it fails**
  Run: `python3 -m unittest tests/test_engine.py`
  Expected: FAIL (module not found)

- [ ] **Step 3: Implement `cloner_engine.py`**
  - App scanning for ChatGPT, Claude, AntiGravity, AntiGravity IDE.
  - Icon badging pipeline using Python `PIL` or native `sips` / `iconutil` / CoreGraphics to overlay squircle color badges onto the app icon.
  - Bundle scaffolding: `Contents/Info.plist`, `Contents/MacOS/launcher`, `Contents/Resources/AppIcon.icns`.
  - Electron launcher template with `--user-data-dir="<path>"`.
  - ChatGPT launcher template with isolated WebKit data store and application support directory.
  - Ad-hoc codesigning with `codesign --force --deep --sign -`.

- [ ] **Step 4: Run test to verify it passes**
  Run: `python3 -m unittest tests/test_engine.py`
  Expected: PASS

---

### Task 2: Modern Dark Web UI (Matching Reference Screenshot)

**Files:**
- Create: `/Users/bahaam/Desktop/Cloner/ui/index.html`
- Create: `/Users/bahaam/Desktop/Cloner/ui/style.css`
- Create: `/Users/bahaam/Desktop/Cloner/ui/app.js`

**Interfaces:**
- Consumes: `cloner_engine` JSON endpoints / Native WebKit Bridge (`window.webkit.messageHandlers.clonerBridge`).
- Produces:
  - Interactive app cards row (matching the user's uploaded reference screenshot: dark squircle icon badges, subtle glow, crisp white text labels).
  - Profile creation sheet with live badged icon preview, profile name input, and 6 vibrant accent color options.
  - Active clones grid with status badges, 1-click Launch, Finder reveal, Profile Storage, and Delete actions.

- [ ] **Step 1: Build the UI HTML structure**
  - Header: Cloner branding, status pill, "New Clone" button.
  - App Gallery: Horizontal scrollable row of detected app squircle cards (ChatGPT, Claude, AntiGravity, AntiGravity IDE).
  - Clone Configuration Modal / Drawer: App icon, profile name input, color badge picker, preview, submit button.
  - Active Clones Section: List/grid of currently created clones with action triggers.

- [ ] **Step 2: Style with CSS matching the reference image**
  - Background `#0D0D10`, elevated cards `#15161A`, borders `#22242B`.
  - Rounded squircle icons (`border-radius: 22%`) with inset highlight and subtle drop shadow.
  - Modern typography using system SF Pro fonts.
  - Smooth micro-interactions and transitions (hover lifts, active presses).

- [ ] **Step 3: Implement client-side logic (`app.js`)**
  - Bridge abstraction: calls native `window.webkit.messageHandlers.clonerBridge.postMessage()` or local fallback.
  - Dynamic rendering of detected apps and active clones.
  - Form validation for profile name (no invalid filesystem characters).
  - Instant optimistic updates and feedback toasts.

- [ ] **Step 4: Test UI rendering and interactions**
  Verify HTML/CSS layout in headless browser or WebKit to ensure responsive sizing, crisp fonts, and zero visual glitches.

---

### Task 3: Native Swift macOS Wrapper App (`Cloner.app`)

**Files:**
- Create: `/Users/bahaam/Desktop/Cloner/src/main.swift`
- Create: `/Users/bahaam/Desktop/Cloner/build_app.sh`

**Interfaces:**
- Consumes: `ui/` web assets, `src/cloner_engine.py`.
- Produces:
  - Compiled native Mac application bundle: `/Users/bahaam/Desktop/Cloner/Cloner.app`.
  - Seamless WKScriptMessageHandler IPC bridge routing UI requests to the cloning engine.

- [ ] **Step 1: Implement `main.swift`**
  - Initialize NSApplication with `.regular` activation policy.
  - Create borderless / unified titlebar dark window (`NSWindow.StyleMask.titled`, `.closable`, `.miniaturizable`, `.fullSizeContentView`).
  - Configure `WKWebView` with dark background and register `clonerBridge` script message handler.
  - Implement native message dispatch for:
    - `getApps` -> calls engine app scanner and responds with JSON.
    - `getClones` -> lists existing clones.
    - `createClone` -> executes clone generator, returns status.
    - `launchClone` -> opens app with `NSWorkspace.shared.openApplication()`.
    - `revealClone` -> selects clone in Finder.
    - `openDataFolder` -> opens profile directory in Finder.
    - `deleteClone` -> moves clone `.app` to trash.

- [ ] **Step 2: Create `build_app.sh` build script**
  - Compiles `main.swift` using `swiftc -O -target arm64-apple-macos14.0 -framework Cocoa -framework WebKit`.
  - Scaffolds `Cloner.app` bundle in `/Users/bahaam/Desktop/Cloner/`.
  - Embeds UI assets and engine into `Cloner.app/Contents/Resources/`.
  - Generates a sleek dark squircle app icon for `Cloner.app`.
  - Signs ad-hoc with `codesign --force --deep --sign -`.

- [ ] **Step 3: Run `build_app.sh` and verify compilation**
  Run: `bash /Users/bahaam/Desktop/Cloner/build_app.sh`
  Expected: Builds `/Users/bahaam/Desktop/Cloner/Cloner.app` with returncode 0.

---

### Task 4: End-to-End Testing & Verification

**Files:**
- Test: `/Users/bahaam/Desktop/Cloner/tests/test_e2e.py`

- [ ] **Step 1: Write and run end-to-end clone tests**
  - Test creating a clone of AntiGravity with profile "Work".
  - Verify `~/Desktop/Cloner/AntiGravity (Work).app` exists and is a valid macOS bundle.
  - Verify `Contents/Info.plist` has `CFBundleIdentifier = com.cloner.antigravity.work`.
  - Verify isolated data directory `~/Library/Application Support/Cloner/AntiGravity/Work` exists.
  - Test launching the clone and verifying it runs independently without disturbing the main app.
  - Test creating a clone of Claude Desktop and ChatGPT.

- [ ] **Step 2: Clean up test artifacts & verify production bundle**
  - Verify `Cloner.app` launches smoothly from Desktop.
  - Verify all detected apps appear in the UI gallery.
  - Verify active clones are listed with working 1-click actions.
