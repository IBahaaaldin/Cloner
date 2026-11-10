import Cocoa
import WebKit

class ClonerBridgeHandler: NSObject, WKScriptMessageHandler {
    weak var webView: WKWebView?
    let enginePath: String

    init(enginePath: String) {
        self.enginePath = enginePath
        super.init()
    }

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        guard let dict = message.body as? [String: Any],
              let action = dict["action"] as? String,
              let callbackId = dict["callbackId"] as? String else {
            return
        }

        let payload = dict["payload"] as? [String: Any] ?? [:]
        handleAction(action: action, payload: payload, callbackId: callbackId)
    }

    private func handleAction(action: String, payload: [String: Any], callbackId: String) {
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self = self else { return }
            var responseData: [String: Any] = [:]

            switch action {
            case "getApps":
                var apps = self.runEngine(args: ["scan"])
                // Enrich every app with its real macOS system icon
                for i in 0..<apps.count {
                    if let appPath = apps[i]["path"] as? String {
                        if let b64 = self.getAppIconBase64(appPath: appPath) {
                            apps[i]["icon_base64"] = b64
                        }
                    }
                }
                responseData["apps"] = apps

            case "getClones":
                var clones = self.runEngine(args: ["list"])
                // Enrich every clone with its real badged icon
                for i in 0..<clones.count {
                    if let clonePath = clones[i]["path"] as? String {
                        if let b64 = self.getAppIconBase64(appPath: clonePath) {
                            clones[i]["icon_base64"] = b64
                        }
                    }
                }
                responseData["clones"] = clones
                responseData["app_version"] = Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0.3"

            case "pickCustomApp":
                DispatchQueue.main.async {
                    let panel = NSOpenPanel()
                    panel.canChooseFiles = true
                    panel.canChooseDirectories = false
                    panel.allowsMultipleSelection = false
                    panel.allowedContentTypes = [.application]
                    panel.prompt = "Choose App"
                    panel.directoryURL = URL(fileURLWithPath: "/Applications")

                    if panel.runModal() == .OK, let selectedURL = panel.url {
                        let path = selectedURL.path
                        let name = selectedURL.deletingPathExtension().lastPathComponent
                        let iconB64 = self.getAppIconBase64(appPath: path) ?? ""

                        let customApp: [String: Any] = [
                            "name": name,
                            "path": path,
                            "key": name.lowercased().replacingOccurrences(of: " ", with: "-"),
                            "is_featured": false,
                            "icon_base64": iconB64,
                            "type": "auto"
                        ]
                        self.sendResponse(callbackId: callbackId, data: ["app": customApp, "success": true])
                    } else {
                        self.sendResponse(callbackId: callbackId, data: ["cancelled": true])
                    }
                }
                return

            case "createClone":
                let appPath = payload["app_path"] as? String ?? ""
                let profileName = payload["profile_name"] as? String ?? "Work"
                let badgeColor = payload["badge_color"] as? String ?? "#3B82F6"
                let copyData = payload["copy_existing_data"] as? Bool ?? false
                var args = [
                    "create",
                    "--app-path", appPath,
                    "--profile", profileName,
                    "--color", badgeColor
                ]
                if copyData {
                    args.append("--copy-existing-data")
                }
                let result = self.runEngineDict(args: args)
                responseData = result

            case "launchClone":
                if let clonePath = payload["clone_path"] as? String {
                    let url = URL(fileURLWithPath: clonePath)
                    let config = NSWorkspace.OpenConfiguration()
                    config.createsNewApplicationInstance = true
                    DispatchQueue.main.async {
                        NSWorkspace.shared.openApplication(at: url, configuration: config) { _, error in
                            if let error = error {
                                print("Launch error:", error)
                            }
                        }
                    }
                    responseData["success"] = true
                }

            case "revealClone":
                if let path = payload["path"] as? String {
                    let url = URL(fileURLWithPath: path)
                    DispatchQueue.main.async {
                        NSWorkspace.shared.activateFileViewerSelecting([url])
                    }
                    responseData["success"] = true
                }

            case "openDataFolder":
                if let dataDir = payload["data_dir"] as? String {
                    let url = URL(fileURLWithPath: dataDir)
                    DispatchQueue.main.async {
                        NSWorkspace.shared.open(url)
                    }
                    responseData["success"] = true
                }

            case "syncClone":
                let clonePath = payload["clone_path"] as? String ?? ""
                let stopIfRunning = payload["stop_if_running"] as? Bool ?? false
                var args = ["sync", "--clone-path", clonePath, "--force"]
                if stopIfRunning {
                    args.append("--stop-if-running")
                }
                let result = self.runEngineDict(args: args)
                responseData = result

            case "syncAllClones":
                let result = self.runEngineDict(args: ["sync-all"])
                responseData = result

            case "deleteClone":
                let clonePath = payload["clone_path"] as? String ?? ""
                let removeData = payload["remove_data"] as? Bool ?? false
                var args = ["delete", "--clone-path", clonePath]
                if removeData {
                    args.append("--remove-data")
                }
                let result = self.runEngineDict(args: args)
                responseData = result

            case "openUrl":
                if let urlString = payload["url"] as? String, let url = URL(string: urlString) {
                    DispatchQueue.main.async {
                        NSWorkspace.shared.open(url)
                    }
                    responseData["success"] = true
                }

            default:
                responseData["error"] = "Unknown action \(action)"
            }

            self.sendResponse(callbackId: callbackId, data: responseData)
        }
    }

    private func getAppIconBase64(appPath: String) -> String? {
        let icon = NSWorkspace.shared.icon(forFile: appPath)
        let targetSize = NSSize(width: 96, height: 96)
        guard let bitmapRep = NSBitmapImageRep(
            bitmapDataPlanes: nil,
            pixelsWide: Int(targetSize.width),
            pixelsHigh: Int(targetSize.height),
            bitsPerSample: 8,
            samplesPerPixel: 4,
            hasAlpha: true,
            isPlanar: false,
            colorSpaceName: .calibratedRGB,
            bytesPerRow: 0,
            bitsPerPixel: 0
        ) else { return nil }

        NSGraphicsContext.saveGraphicsState()
        let context = NSGraphicsContext(bitmapImageRep: bitmapRep)
        NSGraphicsContext.current = context
        icon.draw(in: NSRect(origin: .zero, size: targetSize))
        NSGraphicsContext.restoreGraphicsState()

        guard let pngData = bitmapRep.representation(using: .png, properties: [:]) else { return nil }
        return pngData.base64EncodedString()
    }

    private func getPythonPath() -> String {
        let candidates = [
            "/usr/bin/python3",
            "/opt/homebrew/bin/python3",
            "/usr/local/bin/python3"
        ]
        for path in candidates {
            if FileManager.default.isExecutableFile(atPath: path) {
                return path
            }
        }
        return "/usr/bin/python3"
    }

    private func runEngine(args: [String]) -> [[String: Any]] {
        let task = Process()
        task.launchPath = self.getPythonPath()
        task.arguments = [self.enginePath] + args

        let pipe = Pipe()
        task.standardOutput = pipe
        task.standardError = Pipe()

        do {
            try task.run()
            let data = pipe.fileHandleForReading.readDataToEndOfFile()
            task.waitUntilExit()
            if let json = try? JSONSerialization.jsonObject(with: data) as? [[String: Any]] {
                return json
            }
        } catch {
            print("Engine error:", error)
        }
        return []
    }

    private func runEngineDict(args: [String]) -> [String: Any] {
        let task = Process()
        task.launchPath = self.getPythonPath()
        task.arguments = [self.enginePath] + args

        let pipe = Pipe()
        task.standardOutput = pipe
        task.standardError = Pipe()

        do {
            try task.run()
            let data = pipe.fileHandleForReading.readDataToEndOfFile()
            task.waitUntilExit()
            if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] {
                return json
            }
        } catch {
            print("Engine dict error:", error)
        }
        return ["success": false]
    }

    private func sendResponse(callbackId: String, data: [String: Any]) {
        guard let jsonData = try? JSONSerialization.data(withJSONObject: data, options: []),
              let jsonString = String(data: jsonData, encoding: .utf8) else {
            return
        }

        let js = "window.handleNativeResponse('\(callbackId)', \(jsonString));"
        DispatchQueue.main.async { [weak self] in
            self?.webView?.evaluateJavaScript(js, completionHandler: nil)
        }
    }
}

class AppDelegate: NSObject, NSApplicationDelegate, NSWindowDelegate, WKUIDelegate, WKNavigationDelegate {
    var window: NSWindow!
    var webView: WKWebView!
    var bridgeHandler: ClonerBridgeHandler!

    func applicationDidFinishLaunching(_ notification: Notification) {
        let bundle = Bundle.main
        if bundle.bundlePath.hasPrefix("/Volumes/") {
            if checkDiskImageRunning(bundlePath: bundle.bundlePath) {
                return
            }
        }

        setupMainMenu()

        let windowWidth: CGFloat = 880
        let windowHeight: CGFloat = 680

        let windowRect = NSRect(x: 0, y: 0, width: windowWidth, height: windowHeight)
        window = NSWindow(
            contentRect: windowRect,
            styleMask: [.titled, .closable, .miniaturizable, .resizable, .fullSizeContentView],
            backing: .buffered,
            defer: false
        )
        window.center()
        window.setFrameAutosaveName("ClonerMainWindow")
        window.title = "Cloner"
        window.titleVisibility = .hidden
        window.titlebarAppearsTransparent = true
        window.backgroundColor = NSColor(red: 11/255, green: 12/255, blue: 14/255, alpha: 1.0)
        window.isMovableByWindowBackground = true
        window.minSize = NSSize(width: 760, height: 560)
        window.delegate = self

        // Locate resources
        let enginePath = bundle.path(forResource: "cloner_engine", ofType: "py") ??
            (bundle.bundlePath as NSString).deletingLastPathComponent + "/src/cloner_engine.py"

        let uiDirectory = bundle.resourceURL?.appendingPathComponent("ui") ??
            URL(fileURLWithPath: (bundle.bundlePath as NSString).deletingLastPathComponent + "/ui")

        // Setup WebKit
        let contentController = WKUserContentController()
        bridgeHandler = ClonerBridgeHandler(enginePath: enginePath)
        contentController.add(bridgeHandler, name: "clonerBridge")

        let config = WKWebViewConfiguration()
        config.userContentController = contentController
        config.preferences.setValue(true, forKey: "developerExtrasEnabled")

        webView = WKWebView(frame: window.contentView!.bounds, configuration: config)
        webView.autoresizingMask = [.width, .height]
        webView.setValue(false, forKey: "drawsBackground") // Transparent WKWebView
        webView.uiDelegate = self
        webView.navigationDelegate = self
        bridgeHandler.webView = webView

        window.contentView?.addSubview(webView)

        let indexHtml = uiDirectory.appendingPathComponent("index.html")
        webView.loadFileURL(indexHtml, allowingReadAccessTo: uiDirectory)

        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)

        // Silent background update check after 3 seconds
        DispatchQueue.main.asyncAfter(deadline: .now() + 3.0) { [weak self] in
            self?.checkForUpdates(silent: true)
        }
    }

    func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        if let url = navigationAction.request.url, let scheme = url.scheme?.lowercased(), scheme == "http" || scheme == "https" {
            NSWorkspace.shared.open(url)
            decisionHandler(.cancel)
            return
        }
        decisionHandler(.allow)
    }

    func webView(_ webView: WKWebView, createWebViewWith configuration: WKWebViewConfiguration, for navigationAction: WKNavigationAction, windowFeatures: WKWindowFeatures) -> WKWebView? {
        if let url = navigationAction.request.url {
            NSWorkspace.shared.open(url)
        }
        return nil
    }

    @objc func showAboutPanel() {
        let appVersion = Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0.3"
        let options: [NSApplication.AboutPanelOptionKey: Any] = [
            .applicationName: "Cloner",
            .applicationVersion: appVersion,
            .version: "v\(appVersion) (Apple Silicon)",
            .credits: NSAttributedString(
                string: "Created by Bahaa Mohammed\n• Instagram: @ibahaaaldincoding\n• GitHub: @IBahaaaldin\n• LinkedIn: Bahaa Mohammed\n• Email: bahaam.coding@gmail.com",
                attributes: [
                    .foregroundColor: NSColor.secondaryLabelColor,
                    .font: NSFont.systemFont(ofSize: 11)
                ]
            )
        ]
        NSApp.orderFrontStandardAboutPanel(options: options)
    }

    // MARK: - Auto-Updater
    let updateCheckURL = URL(string: "https://raw.githubusercontent.com/IBahaaaldin/Cloner/main/version.json")!

    @objc func menuCheckForUpdates() {
        checkForUpdates(silent: false)
    }

    func checkForUpdates(silent: Bool) {
        let task = URLSession.shared.dataTask(with: updateCheckURL) { [weak self] data, response, error in
            guard let self = self else { return }

            if let error = error {
                if !silent {
                    DispatchQueue.main.async {
                        let alert = NSAlert()
                        alert.messageText = "Update Check Failed"
                        alert.informativeText = "Could not check for updates. Please check your internet connection and try again.\n\nError: \(error.localizedDescription)"
                        alert.alertStyle = .warning
                        alert.addButton(withTitle: "OK")
                        alert.runModal()
                    }
                }
                return
            }

            guard let data = data,
                  let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
                  let remoteVersion = json["version"] as? String,
                  let downloadUrl = json["download_url"] as? String else {
                if !silent {
                    DispatchQueue.main.async {
                        let alert = NSAlert()
                        alert.messageText = "Update Check Failed"
                        alert.informativeText = "Received invalid update response from server."
                        alert.alertStyle = .warning
                        alert.addButton(withTitle: "OK")
                        alert.runModal()
                    }
                }
                return
            }

            let releaseNotes = json["release_notes"] as? String ?? "Includes latest stability improvements and features."
            let currentVersion = Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0.3"

            DispatchQueue.main.async {
                if currentVersion.compare(remoteVersion, options: .numeric) == .orderedAscending {
                    let alert = NSAlert()
                    alert.messageText = "Update Available: Cloner v\(remoteVersion)"
                    alert.informativeText = "A new version of Cloner is available (currently using v\(currentVersion)).\n\nWhat's New:\n\(releaseNotes)\n\nWould you like to install the update now?"
                    alert.alertStyle = .informational
                    alert.addButton(withTitle: "Update & Relaunch")
                    alert.addButton(withTitle: "Later")

                    if alert.runModal() == .alertFirstButtonReturn {
                        self.performAutoUpdate(downloadUrlString: downloadUrl, newVersion: remoteVersion)
                    }
                } else if !silent {
                    let alert = NSAlert()
                    alert.messageText = "You're Up to Date!"
                    alert.informativeText = "Cloner v\(currentVersion) is the newest version available."
                    alert.alertStyle = .informational
                    alert.addButton(withTitle: "OK")
                    alert.runModal()
                }
            }
        }
        task.resume()
    }

    private func performAutoUpdate(downloadUrlString: String, newVersion: String) {
        guard let url = URL(string: downloadUrlString) else { return }

        let currentPath = Bundle.main.bundlePath
        let targetAppPath: String
        if currentPath.hasPrefix("/Volumes/") {
            targetAppPath = "/Applications/Cloner.app"
        } else {
            targetAppPath = currentPath
        }

        let downloadTask = URLSession.shared.downloadTask(with: url) { tempURL, response, error in
            guard let tempURL = tempURL, error == nil else {
                DispatchQueue.main.async {
                    let errAlert = NSAlert()
                    errAlert.messageText = "Update Download Failed"
                    errAlert.informativeText = "Could not download update: \(error?.localizedDescription ?? "Network error")"
                    errAlert.alertStyle = .critical
                    errAlert.addButton(withTitle: "OK")
                    errAlert.runModal()
                }
                return
            }

            let fileManager = FileManager.default
            let updateDir = URL(fileURLWithPath: "/tmp/ClonerUpdate")
            let zipPath = updateDir.appendingPathComponent("Cloner.zip")
            let extractDir = updateDir.appendingPathComponent("extracted")

            do {
                if fileManager.fileExists(atPath: updateDir.path) {
                    try fileManager.removeItem(at: updateDir)
                }
                try fileManager.createDirectory(at: extractDir, withIntermediateDirectories: true)
                try fileManager.moveItem(at: tempURL, to: zipPath)

                let ditto = Process()
                ditto.executableURL = URL(fileURLWithPath: "/usr/bin/ditto")
                ditto.arguments = ["-xk", zipPath.path, extractDir.path]
                try ditto.run()
                ditto.waitUntilExit()

                let newAppBundle = extractDir.appendingPathComponent("Cloner.app")
                guard fileManager.fileExists(atPath: newAppBundle.path) else {
                    throw NSError(domain: "ClonerUpdate", code: 1, userInfo: [NSLocalizedDescriptionKey: "Extracted update bundle not found."])
                }

                let scriptContent = """
                sleep 0.8
                rm -rf "\(targetAppPath)"
                cp -R "\(newAppBundle.path)" "\(targetAppPath)"
                xattr -cr "\(targetAppPath)" 2>/dev/null || true
                open "\(targetAppPath)"
                rm -rf "\(updateDir.path)"
                """
                let scriptPath = updateDir.appendingPathComponent("relaunch.sh")
                try scriptContent.write(to: scriptPath, atomically: true, encoding: .utf8)
                try fileManager.setAttributes([.posixPermissions: 0o755], ofItemAtPath: scriptPath.path)

                let restartProc = Process()
                restartProc.executableURL = URL(fileURLWithPath: "/bin/bash")
                restartProc.arguments = [scriptPath.path]
                try restartProc.run()

                DispatchQueue.main.async {
                    exit(0)
                }
            } catch {
                DispatchQueue.main.async {
                    let errAlert = NSAlert()
                    errAlert.messageText = "Update Installation Failed"
                    errAlert.informativeText = "Error installing update: \(error.localizedDescription)"
                    errAlert.alertStyle = .critical
                    errAlert.addButton(withTitle: "OK")
                    errAlert.runModal()
                }
            }
        }
        downloadTask.resume()
    }

    func webView(_ webView: WKWebView, runJavaScriptAlertPanelWithMessage message: String, initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping () -> Void) {
        let alert = NSAlert()
        alert.messageText = "Cloner"
        alert.informativeText = message
        alert.addButton(withTitle: "OK")
        alert.runModal()
        completionHandler()
    }

    func webView(_ webView: WKWebView, runJavaScriptConfirmPanelWithMessage message: String, initiatedByFrame frame: WKFrameInfo, completionHandler: @escaping (Bool) -> Void) {
        let alert = NSAlert()
        alert.messageText = "Cloner"
        alert.informativeText = message
        alert.addButton(withTitle: "Continue")
        alert.addButton(withTitle: "Cancel")
        let res = alert.runModal()
        completionHandler(res == .alertFirstButtonReturn)
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        return true
    }

    private func checkDiskImageRunning(bundlePath: String) -> Bool {
        let alert = NSAlert()
        alert.messageText = "Install Cloner to Applications?"
        alert.informativeText = "Cloner is currently running from a downloaded disk image (.dmg).\n\nMoving it to your Applications folder installs it as a normal macOS application, unlocks the .dmg so you can delete it immediately, and makes Cloner accessible from Launchpad and Spotlight."
        alert.alertStyle = .informational
        alert.addButton(withTitle: "Move to Applications")
        alert.addButton(withTitle: "Run Once from Disk Image")

        let response = alert.runModal()
        if response == .alertFirstButtonReturn {
            let destPath = "/Applications/Cloner.app"
            let fileManager = FileManager.default

            do {
                if fileManager.fileExists(atPath: destPath) {
                    try fileManager.removeItem(atPath: destPath)
                }
                try fileManager.copyItem(atPath: bundlePath, toPath: destPath)

                // Remove quarantine attribute
                let xattr = Process()
                xattr.executableURL = URL(fileURLWithPath: "/usr/bin/xattr")
                xattr.arguments = ["-cr", destPath]
                try? xattr.run()
                xattr.waitUntilExit()

                // Launch from Applications
                let openProcess = Process()
                openProcess.executableURL = URL(fileURLWithPath: "/usr/bin/open")
                openProcess.arguments = [destPath]
                try? openProcess.run()

                // Terminate volume process so DMG can be unmounted and deleted immediately
                exit(0)
            } catch {
                print("Failed to auto-move to Applications: \(error)")
            }
        }
        return false
    }

    private func setupMainMenu() {
        let mainMenu = NSMenu()
        let appMenuItem = NSMenuItem()
        mainMenu.addItem(appMenuItem)

        let appMenu = NSMenu()
        appMenuItem.submenu = appMenu

        let appName = "Cloner"
        let aboutItem = NSMenuItem(title: "About \(appName)", action: #selector(showAboutPanel), keyEquivalent: "")
        aboutItem.target = self
        appMenu.addItem(aboutItem)

        let updateItem = NSMenuItem(title: "Check for Updates...", action: #selector(menuCheckForUpdates), keyEquivalent: "u")
        updateItem.keyEquivalentModifierMask = [.command]
        updateItem.target = self
        appMenu.addItem(updateItem)

        appMenu.addItem(NSMenuItem.separator())
        appMenu.addItem(withTitle: "Hide \(appName)", action: #selector(NSApplication.hide(_:)), keyEquivalent: "h")
        let hideOthers = NSMenuItem(title: "Hide Others", action: #selector(NSApplication.hideOtherApplications(_:)), keyEquivalent: "h")
        hideOthers.keyEquivalentModifierMask = [.command, .option]
        appMenu.addItem(hideOthers)
        appMenu.addItem(withTitle: "Show All", action: #selector(NSApplication.unhideAllApplications(_:)), keyEquivalent: "")
        appMenu.addItem(NSMenuItem.separator())
        appMenu.addItem(withTitle: "Quit \(appName)", action: #selector(NSApplication.terminate(_:)), keyEquivalent: "q")

        NSApp.mainMenu = mainMenu
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.setActivationPolicy(.regular)
app.run()
