const { chromium } = require('/Users/bahaam/Desktop/Bahaa-Coding/Projects/Ready-UIs/node_modules/playwright');
const path = require('path');
const fs = require('fs');
const { execSync } = require('child_process');

(async () => {
  console.log('==> Starting automated video render for Cloner (1080x1920 Reel)...');
  const dir = path.join(__dirname, '..');
  const htmlPath = 'file://' + path.join(__dirname, 'video-reel.html');
  const tempDir = path.join(__dirname, '.temp_video');

  if (fs.existsSync(tempDir)) fs.rmSync(tempDir, { recursive: true, force: true });
  fs.mkdirSync(tempDir, { recursive: true });

  const browser = await chromium.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: true,
    args: ['--enable-webgl', '--use-gl=angle', '--use-angle=metal']
  });

  const context = await browser.newContext({
    viewport: { width: 1080, height: 1920 },
    deviceScaleFactor: 1,
    recordVideo: {
      dir: tempDir,
      size: { width: 1080, height: 1920 }
    }
  });

  const page = await context.newPage();
  await page.goto(htmlPath, { waitUntil: 'networkidle' });
  await page.waitForTimeout(400);

  console.log('==> Directing scene transitions across 14 seconds timeline...');

  // Scene 1: 0.0s - 3.2s
  await page.evaluate(() => window.setPlaybackTime(1.0));
  await page.waitForTimeout(3200);

  // Scene 2: 3.2s - 6.8s
  console.log('==> Transitioning to Scene 2: Meet Cloner...');
  await page.evaluate(() => window.setPlaybackTime(4.5));
  await page.waitForTimeout(3600);

  // Scene 3: 6.8s - 10.6s
  console.log('==> Transitioning to Scene 3: Cloner in Action...');
  await page.evaluate(() => window.setPlaybackTime(8.0));
  await page.waitForTimeout(3800);

  // Scene 4: 10.6s - 14.5s
  console.log('==> Transitioning to Scene 4: Dual Workspace & 1-Line Install...');
  await page.evaluate(() => window.setPlaybackTime(12.0));
  await page.waitForTimeout(4000);

  await page.close();
  await context.close();
  await browser.close();

  console.log('==> Browser capture complete. Encoding with FFmpeg...');
  const recordedFiles = fs.readdirSync(tempDir).filter(f => f.endsWith('.webm'));
  if (recordedFiles.length === 0) {
    console.error('Error: No recorded webm video found in', tempDir);
    process.exit(1);
  }

  const inputWebm = path.join(tempDir, recordedFiles[0]);
  const outputMp4 = path.join(dir, 'cloner-promo.mp4');
  const instagramOutput = path.join(process.env.HOME, 'Desktop', 'Instagram-Posts', 'Post-App-01-Cloner', 'slide-2.mp4');
  const readyUIsOutput = path.join(dir, '..', 'Bahaa-Coding', 'Projects', 'Ready-UIs', 'social-posts', 'Post-App-01-Cloner', 'cloner-promo.mp4');

  // Transcode to standard H.264 MP4 with yuv420p for Instagram / Mobile compatibility
  const ffmpegCmd = `ffmpeg -y -i "${inputWebm}" -c:v libx264 -preset fast -pix_fmt yuv420p -r 30 -b:v 4M -movflags +faststart "${outputMp4}"`;
  console.log('Executing:', ffmpegCmd);
  execSync(ffmpegCmd);

  // Distribute copies
  if (fs.existsSync(path.dirname(instagramOutput))) {
    fs.copyFileSync(outputMp4, instagramOutput);
    console.log('✓ Copied to Instagram post folder:', instagramOutput);
  }

  if (fs.existsSync(path.dirname(readyUIsOutput))) {
    fs.copyFileSync(outputMp4, readyUIsOutput);
    console.log('✓ Copied to Ready-UIs social pack:', readyUIsOutput);
  }

  // Clean temp recording directory
  fs.rmSync(tempDir, { recursive: true, force: true });

  console.log('============================================================');
  console.log('  ✓ Successfully rendered 1080x1920 MP4 Video:');
  console.log('    • ' + outputMp4);
  console.log('============================================================');
})();