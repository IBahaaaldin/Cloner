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
                let result = self.runEngineDict(args: [
                    "create",
                    "--app-path", appPath,
                    "--profile", profileName,
                    "--color", badgeColor
                ])
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

            case "deleteClone":
                let clonePath = payload["clone_path"] as? String ?? ""
                let removeData = payload["remove_data"] as? Bool ?? false
                var args = ["delete", "--clone-path", clonePath]
                if removeData {
                    args.append("--remove-data")
                }
                let result = self.runEngineDict(args: args)
                responseData = result

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

    private func runEngine(args: [String]) -> [[String: Any]] {
        let task = Process()
        task.launchPath = "/usr/bin/python3"
        task.arguments = [self.enginePath] + args

        let pipe = Pipe()
        task.standardOutput = pipe
        task.standardError = Pipe()

        do {
            try task.run()
            task.waitUntilExit()
            let data = pipe.fileHandleForReading.readDataToEndOfFile()
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
        task.launchPath = "/usr/bin/python3"
        task.arguments = [self.enginePath] + args

        let pipe = Pipe()
        task.standardOutput = pipe
        task.standardError = Pipe()

        do {
            try task.run()
            task.waitUntilExit()
            let data = pipe.fileHandleForReading.readDataToEndOfFile()
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

class AppDelegate: NSObject, NSApplicationDelegate, NSWindowDelegate, WKUIDelegate {
    var window: NSWindow!
    var webView: WKWebView!
    var bridgeHandler: ClonerBridgeHandler!

    func applicationDidFinishLaunching(_ notification: Notification) {
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
        let bundle = Bundle.main
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
        bridgeHandler.webView = webView

        window.contentView?.addSubview(webView)

        let indexHtml = uiDirectory.appendingPathComponent("index.html")
        webView.loadFileURL(indexHtml, allowingReadAccessTo: uiDirectory)

        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
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

    private func setupMainMenu() {
        let mainMenu = NSMenu()
        let appMenuItem = NSMenuItem()
        mainMenu.addItem(appMenuItem)

        let appMenu = NSMenu()
        appMenuItem.submenu = appMenu

        let appName = "Cloner"
        appMenu.addItem(withTitle: "About \(appName)", action: #selector(NSApplication.orderFrontStandardAboutPanel(_:)), keyEquivalent: "")
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
