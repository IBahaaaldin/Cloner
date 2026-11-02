const path = require('path');
const fs = require('fs');
const { chromium } = require('/Users/bahaam/Desktop/Bahaa-Coding/Projects/Ready-UIs/node_modules/playwright');

const clonerB64 = fs.readFileSync('/tmp/cloner_icons/cloner.b64', 'utf8').trim();
const chatgptB64 = fs.readFileSync('/tmp/cloner_icons/chatgpt.b64', 'utf8').trim();
const claudeB64 = fs.readFileSync('/tmp/cloner_icons/claude.b64', 'utf8').trim();
const agB64 = fs.readFileSync('/tmp/cloner_icons/antigravity.b64', 'utf8').trim();

const clonerDir = '/Users/bahaam/Desktop/Cloner';
const readyUIsPostDir = '/Users/bahaam/Desktop/Bahaa-Coding/Projects/Ready-UIs/social-posts/Post-App-01-Cloner';
const desktopInstagramDir = '/Users/bahaam/Desktop/Instagram-Posts/Post-App-01-Cloner';

[readyUIsPostDir, desktopInstagramDir, path.join(clonerDir, 'assets')].forEach(dir => {
  fs.mkdirSync(dir, { recursive: true });
});

async function run() {
  console.log('==> Launching Playwright browser...');
  const browser = await chromium.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
  });
  const context = await browser.newContext({
    deviceScaleFactor: 2
  });
  const page = await context.newPage();

  // =========================================================================
  // SLIDE 1: High-End Editorial Cover (1080x1080 @ 2x = 2160x2160)
  // =========================================================================
  console.log('==> Rendering Slide 1 (Instagram Cover)...');
  await page.setViewportSize({ width: 1080, height: 1080 });

  const slide1Html = `
  <!DOCTYPE html>
  <html>
  <head>
    <meta charset="utf-8">
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
      * { margin: 0; padding: 0; box-sizing: border-box; }
      body {
        width: 1080px;
        height: 1080px;
        background: #090A0D;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        color: #FFFFFF;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 56px 64px;
      }

      /* Ambient Light Effects */
      .glow-top-left {
        position: absolute;
        width: 600px;
        height: 600px;
        top: -150px;
        left: -100px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.16) 0%, rgba(59, 130, 246, 0.08) 40%, transparent 70%);
        filter: blur(80px);
        pointer-events: none;
      }
      .glow-center {
        position: absolute;
        width: 800px;
        height: 800px;
        top: 200px;
        left: 140px;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.14) 0%, rgba(59, 130, 246, 0.06) 45%, transparent 70%);
        filter: blur(100px);
        pointer-events: none;
      }

      /* Top Bar */
      .top-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: relative;
        z-index: 10;
      }
      .author-pill {
        display: flex;
        align-items: center;
        gap: 12px;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 8px 18px;
        border-radius: 999px;
        backdrop-filter: blur(12px);
      }
      .author-avatar {
        width: 26px;
        height: 26px;
        border-radius: 50%;
        background: linear-gradient(135deg, #38BDF8, #8B5CF6);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        font-weight: 800;
        color: #0A0B0E;
      }
      .author-name {
        font-size: 13px;
        font-weight: 700;
        letter-spacing: -0.01em;
        color: #F1F5F9;
      }
      .author-handle {
        font-size: 12px;
        font-weight: 500;
        color: #94A3B8;
        font-family: 'JetBrains Mono', monospace;
      }
      .version-badge {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.25);
        color: #38BDF8;
        padding: 8px 16px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.02em;
        text-transform: uppercase;
      }
      .pulse-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #38BDF8;
        box-shadow: 0 0 8px #38BDF8;
      }

      /* Center Hero Showcase */
      .center-hero {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        position: relative;
        z-index: 10;
        margin-top: -10px;
      }

      /* Floating Icon Trio */
      .icon-cluster {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 24px;
        margin-bottom: 40px;
        position: relative;
      }

      .floating-app-icon {
        width: 104px;
        height: 104px;
        border-radius: 26px;
        background: #151722;
        border: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.15);
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 14px;
      }

      .floating-app-icon.main-icon {
        width: 136px;
        height: 136px;
        border-radius: 34px;
        background: linear-gradient(145deg, #1A1D2D, #10121D);
        border: 1px solid rgba(56, 189, 248, 0.35);
        box-shadow: 0 25px 60px -10px rgba(56, 189, 248, 0.25), inset 0 2px 2px rgba(255, 255, 255, 0.25);
        transform: translateY(-8px);
        padding: 16px;
      }

      .floating-app-icon img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        filter: drop-shadow(0 8px 16px rgba(0, 0, 0, 0.4));
      }

      /* Mini Badges on Icons */
      .icon-badge {
        position: absolute;
        bottom: -6px;
        right: -6px;
        padding: 4px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.02em;
        text-transform: uppercase;
        border: 2px solid #090A0D;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
      }
      .badge-blue { background: #3B82F6; color: white; }
      .badge-green { background: #10B981; color: white; }
      .badge-purple { background: #8B5CF6; color: white; }

      /* Title & Typography */
      .app-title {
        font-size: 64px;
        font-weight: 800;
        letter-spacing: -0.04em;
        line-height: 1.05;
        margin-bottom: 16px;
        background: linear-gradient(135deg, #FFFFFF 30%, #94A3B8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
      }

      .app-tagline {
        font-size: 24px;
        font-weight: 500;
        color: #94A3B8;
        line-height: 1.4;
        max-width: 720px;
        letter-spacing: -0.01em;
        margin-bottom: 36px;
      }
      .app-tagline strong {
        color: #38BDF8;
        font-weight: 600;
      }

      /* Feature Chips */
      .feature-chips {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 12px;
        max-width: 820px;
      }

      .chip {
        display: flex;
        align-items: center;
        gap: 10px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 10px 20px;
        border-radius: 14px;
        font-size: 14px;
        font-weight: 600;
        color: #E2E8F0;
        backdrop-filter: blur(10px);
      }
      .chip-icon {
        width: 18px;
        height: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
      }

      /* Bottom Action Bar */
      .bottom-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 20px;
        padding: 16px 24px;
        position: relative;
        z-index: 10;
        backdrop-filter: blur(16px);
      }
      .cta-info {
        display: flex;
        flex-direction: column;
        gap: 2px;
      }
      .cta-headline {
        font-size: 14px;
        font-weight: 700;
        color: #F8FAFC;
        letter-spacing: -0.01em;
      }
      .cta-subtext {
        font-size: 12px;
        color: #64748B;
        font-family: 'JetBrains Mono', monospace;
      }
      .btn-download-pill {
        display: flex;
        align-items: center;
        gap: 10px;
        background: linear-gradient(135deg, #38BDF8, #2563EB);
        color: #FFFFFF;
        padding: 12px 24px;
        border-radius: 12px;
        font-size: 14px;
        font-weight: 700;
        box-shadow: 0 8px 24px -4px rgba(37, 99, 235, 0.5);
      }
      .btn-download-pill svg {
        width: 16px;
        height: 16px;
      }
    </style>
  </head>
  <body>
    <div class="glow-top-left"></div>
    <div class="glow-center"></div>

    <!-- Top Bar -->
    <div class="top-bar">
      <div class="author-pill">
        <div class="author-avatar">BA</div>
        <div class="author-name">Bahaa Mohammed</div>
        <div class="author-handle">@ibahaaaldincoding</div>
      </div>
      <div class="version-badge">
        <span class="pulse-dot"></span>
        <span>macOS Native • v1.0.0</span>
      </div>
    </div>

    <!-- Center Hero -->
    <div class="center-hero">
      <div class="icon-cluster">
        <div class="floating-app-icon">
          <img src="data:image/png;base64,${chatgptB64}" alt="ChatGPT">
          <span class="icon-badge badge-blue">Work</span>
        </div>
        <div class="floating-app-icon main-icon">
          <img src="data:image/png;base64,${clonerB64}" alt="Cloner">
        </div>
        <div class="floating-app-icon">
          <img src="data:image/png;base64,${agB64}" alt="Antigravity">
          <span class="icon-badge badge-purple">Personal</span>
        </div>
      </div>

      <h1 class="app-title">CLONER</h1>
      <p class="app-tagline">
        Run <strong>multiple independent accounts</strong> simultaneously for <strong>ChatGPT</strong>, <strong>Claude</strong>, <strong>Antigravity</strong>, and more.
      </p>

      <div class="feature-chips">
        <div class="chip">
          <span class="chip-icon">⚡</span>
          <span>APFS Instant Cloning (&lt;1s)</span>
        </div>
        <div class="chip">
          <span class="chip-icon">💾</span>
          <span>Zero Extra Disk Space</span>
        </div>
        <div class="chip">
          <span class="chip-icon">🔒</span>
          <span>100% Isolated Profiles</span>
        </div>
        <div class="chip">
          <span class="chip-icon">🎨</span>
          <span>Color-Badged Dock Icons</span>
        </div>
        <div class="chip">
          <span class="chip-icon">🛡️</span>
          <span>macOS Keychain Safe</span>
        </div>
      </div>
    </div>

    <!-- Bottom Bar -->
    <div class="bottom-bar">
      <div class="cta-info">
        <span class="cta-headline">1-Click Install (.DMG Available Now)</span>
        <span class="cta-subtext">github.com/IBahaaaldin/Cloner</span>
      </div>
      <div class="btn-download-pill">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="7 10 12 15 17 10"></polyline>
          <line x1="12" y1="15" x2="12" y2="3"></line>
        </svg>
        <span>Download Free App</span>
      </div>
    </div>
  </body>
  </html>
  `;

  await page.setContent(slide1Html, { waitUntil: 'networkidle' });
  const slide1Path = path.join(clonerDir, 'assets', 'slide-1.png');
  const slide1PostPath = path.join(readyUIsPostDir, 'slide-1.png');
  const slide1DesktopPath = path.join(desktopInstagramDir, 'slide-1.png');
  const coverInstaPath = path.join(clonerDir, 'cover-instagram.png');

  await page.screenshot({ path: slide1Path });
  fs.copyFileSync(slide1Path, slide1PostPath);
  fs.copyFileSync(slide1Path, slide1DesktopPath);
  fs.copyFileSync(slide1Path, coverInstaPath);
  console.log('✓ Slide 1 saved to:', slide1Path);

  // =========================================================================
  // SLIDE 2: Live App Showcase (1080x1080 @ 2x = 2160x2160)
  // =========================================================================
  console.log('==> Rendering Slide 2 (App Showcase)...');
  const slide2Html = `
  <!DOCTYPE html>
  <html>
  <head>
    <meta charset="utf-8">
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
      * { margin: 0; padding: 0; box-sizing: border-box; }
      body {
        width: 1080px;
        height: 1080px;
        background: #090A0D;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        color: #FFFFFF;
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 48px 56px;
      }

      /* Glow background */
      .glow-app {
        position: absolute;
        width: 900px;
        height: 600px;
        top: 240px;
        left: 90px;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.12) 0%, rgba(139, 92, 246, 0.08) 50%, transparent 75%);
        filter: blur(90px);
        pointer-events: none;
      }

      /* Top Header */
      .top-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
        z-index: 10;
      }
      .badge-group {
        display: flex;
        align-items: center;
        gap: 10px;
      }
      .tag-pill {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        color: #94A3B8;
        letter-spacing: 0.02em;
        text-transform: uppercase;
      }
      .tag-pill.blue {
        background: rgba(56, 189, 248, 0.1);
        border-color: rgba(56, 189, 248, 0.3);
        color: #38BDF8;
      }
      .handle-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        color: #64748B;
        font-weight: 500;
      }

      /* App Window Showcase */
      .window-wrapper {
        position: relative;
        z-index: 10;
        margin: 20px 0;
      }

      .mac-window {
        width: 100%;
        background: #0E0F14;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 20px;
        box-shadow: 0 35px 80px -20px rgba(0, 0, 0, 0.9), 0 0 0 1px rgba(255, 255, 255, 0.05);
        overflow: hidden;
      }

      /* Title bar */
      .mac-titlebar {
        background: #151720;
        padding: 14px 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
      }
      .traffic-lights {
        display: flex;
        gap: 8px;
      }
      .traffic-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
      }
      .dot-red { background: #FF5F56; }
      .dot-yellow { background: #FFBD2E; }
      .dot-green { background: #27C93F; }

      .window-brand {
        display: flex;
        align-items: center;
        gap: 10px;
      }
      .window-brand img {
        width: 20px;
        height: 20px;
        border-radius: 5px;
      }
      .window-title {
        font-size: 13px;
        font-weight: 700;
        color: #F8FAFC;
      }
      .window-status-pill {
        background: rgba(59, 130, 246, 0.15);
        color: #60A5FA;
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 10px;
        font-weight: 700;
      }

      .window-right-status {
        font-size: 11px;
        color: #64748B;
        font-family: 'JetBrains Mono', monospace;
      }

      /* Window Content */
      .window-content {
        padding: 28px 32px;
      }

      .section-heading {
        margin-bottom: 20px;
      }
      .heading-title {
        font-size: 22px;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #FFFFFF;
        margin-bottom: 6px;
      }
      .heading-desc {
        font-size: 13px;
        color: #94A3B8;
      }

      /* Squircles Row */
      .apps-label {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: #64748B;
        text-transform: uppercase;
        margin-bottom: 14px;
      }

      .squircles-row {
        display: flex;
        gap: 16px;
        margin-bottom: 28px;
      }

      .app-squircle {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
      }
      .squircle-box {
        width: 68px;
        height: 68px;
        background: #181A26;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 10px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
      }
      .squircle-box img {
        width: 100%;
        height: 100%;
        object-fit: contain;
      }
      .squircle-name {
        font-size: 11px;
        font-weight: 600;
        color: #E2E8F0;
      }

      /* Active Clones Showcase Cards */
      .clones-label {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.08em;
        color: #64748B;
        text-transform: uppercase;
        margin-bottom: 14px;
      }

      .clones-showcase {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
      }

      .clone-card {
        background: #13151F;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 16px;
        display: flex;
        flex-direction: column;
        gap: 12px;
      }

      .clone-top {
        display: flex;
        align-items: center;
        gap: 14px;
      }

      .clone-icon-wrapper {
        position: relative;
        width: 44px;
        height: 44px;
      }
      .clone-icon-wrapper img {
        width: 100%;
        height: 100%;
        border-radius: 12px;
      }
      .dot-badge {
        position: absolute;
        bottom: -2px;
        right: -2px;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        border: 2px solid #13151F;
      }

      .clone-meta h4 {
        font-size: 14px;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 2px;
      }
      .clone-status-line {
        font-size: 11px;
        color: #10B981;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
      }

      .btn-clone-open {
        background: linear-gradient(135deg, #3B82F6, #2563EB);
        color: white;
        padding: 8px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 700;
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
      }

      /* Callout Pills at Bottom */
      .callouts-footer {
        display: grid;
        grid-template-columns: 1fr 1fr 1fr;
        gap: 16px;
        position: relative;
        z-index: 10;
      }
      .callout-box {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 14px 16px;
      }
      .callout-title {
        font-size: 12px;
        font-weight: 800;
        color: #38BDF8;
        text-transform: uppercase;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 6px;
      }
      .callout-text {
        font-size: 11px;
        color: #94A3B8;
        line-height: 1.4;
      }
    </style>
  </head>
  <body>
    <div class="glow-app"></div>

    <div class="top-header">
      <div class="badge-group">
        <span class="tag-pill blue">Application Showcase</span>
        <span class="tag-pill">Side-by-Side Instances</span>
      </div>
      <div class="handle-label">@ibahaaaldincoding</div>
    </div>

    <!-- macOS Window Showcase -->
    <div class="window-wrapper">
      <div class="mac-window">
        <div class="mac-titlebar">
          <div class="traffic-lights">
            <span class="traffic-dot dot-red"></span>
            <span class="traffic-dot dot-yellow"></span>
            <span class="traffic-dot dot-green"></span>
          </div>
          <div class="window-brand">
            <img src="data:image/png;base64,${clonerB64}" alt="Cloner">
            <span class="window-title">Cloner</span>
            <span class="window-status-pill">Multi-Account</span>
          </div>
          <div class="window-right-status">27 AI apps detected</div>
        </div>

        <div class="window-content">
          <div class="section-heading">
            <h2 class="heading-title">Run multiple accounts simultaneously.</h2>
            <p class="heading-desc">Clone your AI desktop apps into independent, side-by-side instances with separate profiles and logins.</p>
          </div>

          <div class="apps-label">CHOOSE AN APP TO CLONE</div>
          <div class="squircles-row">
            <div class="app-squircle">
              <div class="squircle-box"><img src="data:image/png;base64,${chatgptB64}"></div>
              <span class="squircle-name">ChatGPT</span>
            </div>
            <div class="app-squircle">
              <div class="squircle-box"><img src="data:image/png;base64,${claudeB64}"></div>
              <span class="squircle-name">Claude</span>
            </div>
            <div class="app-squircle">
              <div class="squircle-box"><img src="data:image/png;base64,${agB64}"></div>
              <span class="squircle-name">Antigravity</span>
            </div>
            <div class="app-squircle">
              <div class="squircle-box"><img src="data:image/png;base64,${agB64}"></div>
              <span class="squircle-name">AG IDE</span>
            </div>
          </div>

          <div class="clones-label">ACTIVE CLONES ON DESKTOP (RUNNING SIMULTANEOUSLY)</div>
          <div class="clones-showcase">
            <div class="clone-card">
              <div class="clone-top">
                <div class="clone-icon-wrapper">
                  <img src="data:image/png;base64,${chatgptB64}">
                  <span class="dot-badge" style="background: #3B82F6;"></span>
                </div>
                <div class="clone-meta">
                  <h4>ChatGPT (Work)</h4>
                  <div class="clone-status-line">● READY • SEPARATE SESSION</div>
                </div>
              </div>
              <div class="btn-clone-open">▶ Open Work Account</div>
            </div>

            <div class="clone-card">
              <div class="clone-top">
                <div class="clone-icon-wrapper">
                  <img src="data:image/png;base64,${agB64}">
                  <span class="dot-badge" style="background: #8B5CF6;"></span>
                </div>
                <div class="clone-meta">
                  <h4>Antigravity (Work)</h4>
                  <div class="clone-status-line">● READY • SEPARATE SESSION</div>
                </div>
              </div>
              <div class="btn-clone-open">▶ Open Work Account</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Callouts Footer -->
    <div class="callouts-footer">
      <div class="callout-box">
        <div class="callout-title">⚡ Instant APFS Cloning</div>
        <div class="callout-text">Clones in &lt;1s using copy-on-write without taking extra disk space.</div>
      </div>
      <div class="callout-box">
        <div class="callout-title">🔒 Process Singleton Lock</div>
        <div class="callout-text">Bypasses Chromium single-instance forwarding so both run together.</div>
      </div>
      <div class="callout-box">
        <div class="callout-title">🛡️ Keychain Safe</div>
        <div class="callout-text">Integrates smoothly with macOS security without password reset prompts.</div>
      </div>
    </div>
  </body>
  </html>
  `;

  await page.setContent(slide2Html, { waitUntil: 'networkidle' });
  const slide2Path = path.join(clonerDir, 'assets', 'slide-2.png');
  const slide2PostPath = path.join(readyUIsPostDir, 'slide-2.png');
  const slide2DesktopPath = path.join(desktopInstagramDir, 'slide-2.png');
  const appShowcasePath = path.join(clonerDir, 'app-showcase.png');

  await page.screenshot({ path: slide2Path });
  fs.copyFileSync(slide2Path, slide2PostPath);
  fs.copyFileSync(slide2Path, slide2DesktopPath);
  fs.copyFileSync(slide2Path, appShowcasePath);
  console.log('✓ Slide 2 saved to:', slide2Path);

  // =========================================================================
  // COVER BANNER: Widescreen GitHub Banner (2560x1280 @ 1x or 1280x640 @ 2x)
  // =========================================================================
  console.log('==> Rendering Widescreen GitHub Cover Banner...');
  await page.setViewportSize({ width: 1280, height: 640 });

  const coverBannerHtml = `
  <!DOCTYPE html>
  <html>
  <head>
    <meta charset="utf-8">
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
      * { margin: 0; padding: 0; box-sizing: border-box; }
      body {
        width: 1280px;
        height: 640px;
        background: #090A0D;
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
        color: #FFFFFF;
        position: relative;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 80px;
      }
      .glow-banner {
        position: absolute;
        width: 700px;
        height: 700px;
        top: -100px;
        right: -100px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.18) 0%, rgba(139, 92, 246, 0.1) 40%, transparent 70%);
        filter: blur(90px);
        pointer-events: none;
      }
      .left-col {
        display: flex;
        flex-direction: column;
        gap: 18px;
        max-width: 600px;
        position: relative;
        z-index: 10;
      }
      .badge-row {
        display: flex;
        align-items: center;
        gap: 12px;
      }
      .pill {
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.3);
        color: #38BDF8;
        padding: 6px 14px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
      }
      .creator-tag {
        font-size: 12px;
        color: #94A3B8;
        font-family: 'JetBrains Mono', monospace;
      }
      .title {
        font-size: 56px;
        font-weight: 800;
        letter-spacing: -0.04em;
        line-height: 1.05;
        background: linear-gradient(135deg, #FFFFFF 40%, #94A3B8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
      }
      .sub {
        font-size: 18px;
        color: #94A3B8;
        line-height: 1.45;
      }
      .sub strong { color: #38BDF8; }
      .chips {
        display: flex;
        gap: 10px;
        margin-top: 6px;
      }
      .chip-sm {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 600;
        color: #E2E8F0;
      }

      .right-col {
        position: relative;
        z-index: 10;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      .hero-cluster {
        position: relative;
        width: 380px;
        height: 380px;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      .main-app-card {
        width: 160px;
        height: 160px;
        background: #141622;
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-radius: 40px;
        box-shadow: 0 30px 60px -15px rgba(56, 189, 248, 0.3), inset 0 2px 2px rgba(255, 255, 255, 0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 24px;
        z-index: 5;
      }
      .main-app-card img { width: 100%; height: 100%; object-fit: contain; }

      .sat-card {
        position: absolute;
        width: 90px;
        height: 90px;
        background: #12141E;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 22px;
        box-shadow: 0 16px 32px rgba(0, 0, 0, 0.6);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 12px;
      }
      .sat-card img { width: 100%; height: 100%; object-fit: contain; }
      .sat-1 { top: 20px; left: 20px; }
      .sat-2 { bottom: 20px; right: 20px; }

      .pill-badge {
        position: absolute;
        bottom: -6px;
        right: -6px;
        font-size: 10px;
        font-weight: 800;
        padding: 2px 8px;
        border-radius: 999px;
        border: 2px solid #090A0D;
        text-transform: uppercase;
      }
    </style>
  </head>
  <body>
    <div class="glow-banner"></div>
    <div class="left-col">
      <div class="badge-row">
        <span class="pill">macOS Native Tool</span>
        <span class="creator-tag">by Bahaa Mohammed</span>
      </div>
      <h1 class="title">CLONER</h1>
      <p class="sub">
        Run <strong>multiple accounts simultaneously</strong> for AI desktop apps on macOS. Zero disk duplication, 100% isolated sessions.
      </p>
      <div class="chips">
        <span class="chip-sm">⚡ Instant APFS Clone</span>
        <span class="chip-sm">🔒 Independent Keychains</span>
        <span class="chip-sm">🎨 Badged Dock Icons</span>
      </div>
    </div>
    <div class="right-col">
      <div class="hero-cluster">
        <div class="sat-card sat-1">
          <img src="data:image/png;base64,${chatgptB64}">
          <span class="pill-badge" style="background: #3B82F6; color: white;">Work</span>
        </div>
        <div class="main-app-card">
          <img src="data:image/png;base64,${clonerB64}">
        </div>
        <div class="sat-card sat-2">
          <img src="data:image/png;base64,${agB64}">
          <span class="pill-badge" style="background: #8B5CF6; color: white;">Work</span>
        </div>
      </div>
    </div>
  </body>
  </html>
  `;

  await page.setContent(coverBannerHtml, { waitUntil: 'networkidle' });
  const coverPath = path.join(clonerDir, 'cover.png');
  const coverPostPath = path.join(readyUIsPostDir, 'cover.png');
  await page.screenshot({ path: coverPath });
  fs.copyFileSync(coverPath, coverPostPath);
  console.log('✓ Cover banner saved to:', coverPath);

  // =========================================================================
  // CAPTION.MD & CAPTION.TXT
  // =========================================================================
  const captionText = `Ready-Apps #01: Cloner for macOS ⚡👥

Run multiple accounts simultaneously for your AI desktop apps! 

Ever wanted to keep your Work ChatGPT and Personal ChatGPT open side-by-side? Or run separate sessions for Antigravity, Claude, or Codex without constantly logging out and switching profiles?

I built Cloner — a native macOS utility that clones any desktop app into independent, simultaneous instances with their own sessions, cookies, logins, and color-coded badged dock icons.

🔥 Core Features & Engineering:
• Instant APFS Cloning: Clones in under 1 second with 0 extra disk storage using Apple File System copy-on-write
• 100% Isolated Sessions: Custom ProcessSingleton lock isolation lets multiple instances run simultaneously side-by-side
• Auto Account Detection: Scans your Mac and automatically identifies apps with login/auth systems
• Color-Badged Dock Icons: Generate custom squircle dock icons with your chosen profile initials and accent colors
• Keychain & Privacy Safe: Dedicated profile storage preserves your system login keychain integrity
• One-Click DMG Install: Download and drag directly to /Applications

👇 Which AI apps do you use the most with multiple accounts? Let me know in the comments!

💾 Save this post for later!
🔗 Download the 1-Click DMG installer on my GitHub: github.com/IBahaaaldin/Cloner

—
#macos #macapps #developer #softwareengineer #coding #swift #apple #chatgpt #openai #claude #anthropic #antigravity #devtools #programming #tech #cloner #uiux #indiedev #buildinpublic`;

  fs.writeFileSync(path.join(clonerDir, 'CAPTION.md'), captionText);
  fs.writeFileSync(path.join(readyUIsPostDir, 'caption.txt'), captionText);
  fs.writeFileSync(path.join(desktopInstagramDir, 'caption.txt'), captionText);
  console.log('✓ Caption generated successfully.');

  await browser.close();
  console.log('==> All visual assets and social post packs generated successfully!');
}

run().catch(err => {
  console.error('Error rendering social assets:', err);
  process.exit(1);
});
