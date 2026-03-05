#!/usr/bin/env node
/**
 * 生成仓库统计卡片截图
 * 在 CI 中运行，先 build 站点，然后用 vitepress preview 启动服务器截图
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const BASE_URL = 'http://localhost:4173/members-visualization';
const OUTPUT_DIR = path.join(__dirname, '../docs/public/badges');
const REPO_DATA_DIR = path.join(__dirname, '../docs/public/data/datawhalechina/repo');

let previewServer = null;

async function startPreviewServer() {
  return new Promise((resolve, reject) => {
    previewServer = spawn('npm', ['run', 'docs:preview'], { shell: true });

    previewServer.stdout.on('data', (data) => {
      const output = data.toString();
      console.log(output);
      if (output.includes('http://localhost:4173')) {
        setTimeout(resolve, 2000); // 等待服务器完全启动
      }
    });

    previewServer.stderr.on('data', (data) => {
      console.error(data.toString());
    });

    setTimeout(() => reject(new Error('Server start timeout')), 30000);
  });
}

async function captureRepoBadge(browser, repoName) {
  const page = await browser.newPage();

  try {
    await page.setViewport({ width: 1200, height: 800, deviceScaleFactor: 2 });

    const url = `${BASE_URL}/repo-badge?repo=${repoName}&embed=1`;
    await page.goto(url, { waitUntil: 'networkidle0', timeout: 30000 });

    await page.waitForSelector('.badge-card', { timeout: 10000 });

    const element = await page.$('.badge-card');
    if (!element) {
      throw new Error('Badge card not found');
    }

    const outputPath = path.join(OUTPUT_DIR, `${repoName}.png`);
    await element.screenshot({ path: outputPath, omitBackground: true });
    console.log(`Generated: ${repoName}.png`);
  } catch (error) {
    console.error(`Error capturing ${repoName}: ${error.message}`);
  } finally {
    await page.close();
  }
}

async function main() {
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  const repoFiles = fs.readdirSync(REPO_DATA_DIR).filter(f => f.endsWith('.json'));
  const repoNames = repoFiles.map(f => path.basename(f, '.json'));

  console.log(`Found ${repoNames.length} repositories`);

  try {
    console.log('Starting preview server...');
    await startPreviewServer();

    const browser = await puppeteer.launch({
      headless: 'new',
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    try {
      for (const repoName of repoNames) {
        await captureRepoBadge(browser, repoName);
      }

      console.log(`\nGenerated ${repoNames.length} screenshots`);
      console.log(`Output directory: ${OUTPUT_DIR}`);
    } finally {
      await browser.close();
    }
  } finally {
    if (previewServer) {
      try {
        previewServer.kill('SIGTERM');
        // 等待一下让进程优雅退出
        await new Promise(resolve => setTimeout(resolve, 1000));
        if (!previewServer.killed) {
          previewServer.kill('SIGKILL');
        }
      } catch (e) {
        console.error('Error killing preview server:', e);
      }
    }
    // 强制退出
    process.exit(0);
  }
}

main().catch(console.error);
