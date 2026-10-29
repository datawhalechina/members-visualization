#!/usr/bin/env node
/** Generate public badge images only when their rendered inputs change. */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { spawn } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const OUTPUT_DIR = path.join(ROOT, 'docs/public/badges');
const DATA_DIR = path.join(ROOT, 'docs/public/data');
const CACHE_FILE = path.join(ROOT, '.cache/repo-badges.json');
const BASE_URL = 'http://127.0.0.1:4173/members-visualization';
const normalizeRepo = value => String(value || '').trim().replace(/^datawhalechina\//i, '').toLowerCase();
const digest = value => crypto.createHash('sha256').update(value).digest('hex');
const readJSON = filename => JSON.parse(fs.readFileSync(filename, 'utf8'));

function badgeInputs(repo, repoData, members, weekly, repoList) {
  const recent = Object.entries(weekly.user_commits || {}).flatMap(([username, payload]) => {
    const count = Object.entries(payload.repo_commits || {}).reduce(
      (sum, [name, amount]) => sum + (normalizeRepo(name) === repo ? Number(amount) || 0 : 0), 0);
    return count > 0 ? [[username, count]] : [];
  });
  const activeUsers = new Set(recent.map(([username]) => username.toLowerCase()));
  const isRepoMember = member => String(member.repositories || '').split(';').some(name => normalizeRepo(name) === repo);
  const people = members.filter(member => activeUsers.has(String(member.id).toLowerCase()) || isRepoMember(member))
    .map(member => ({
      id: member.id, name: member.name, avatar: member.avatar,
      memberOfRepo: isRepoMember(member),
      contributions: Object.entries(member.repo_contributions || {}).reduce(
        (sum, [name, count]) => sum + (normalizeRepo(name) === repo ? Number(count) || 0 : 0), 0)
    }));
  const ranked = repoList.map(item => ({
    repo: normalizeRepo(String(item.name || '').split('/').pop()), stars: Number(item.star_count) || 0
  })).filter(item => item.repo).sort((a, b) => b.stars - a.stars);
  const displayedRepoData = {
    repo_name: repoData.repo_name, star_count: repoData.star_count,
    monthly_stars: repoData.monthly_stars, monthly_total_stars: repoData.monthly_total_stars
  };
  return {repoData: displayedRepoData, recent, people, rank: ranked.findIndex(item => item.repo === repo), population: ranked.length};
}

function rendererFingerprint() {
  const files = [
    'scripts/generate_repo_screenshots.js', 'package-lock.json',
    'docs/.vitepress/theme/repo/RepoBadge.vue', 'docs/.vitepress/theme/repo/RepoBadgeGenerator.vue',
    'docs/.vitepress/theme/custom.css', 'docs/.vitepress/theme/index.js',
    'docs/repo-badge.md', 'docs/public/default-avatar.svg'
  ];
  return digest(Buffer.concat(files.map(filename => fs.readFileSync(path.join(ROOT, filename)))));
}

function inputFingerprint(inputs, renderer) {
  const avatarHashes = inputs.people.map(person => {
    const filename = path.resolve(ROOT, 'docs/public', person.avatar || 'default-avatar.svg');
    return fs.existsSync(filename) ? digest(fs.readFileSync(filename)) : 'missing';
  });
  return digest(JSON.stringify({inputs, renderer, avatarHashes}));
}

function needsCapture(previous, inputHash, outputPath) {
  return !previous || previous.input !== inputHash || !fs.existsSync(outputPath) ||
    previous.image !== digest(fs.readFileSync(outputPath));
}

async function startPreviewServer() {
  const vitepressBin = path.join(path.dirname(require.resolve('vitepress/package.json')), 'bin/vitepress.js');
  const server = spawn(process.execPath, [vitepressBin, 'preview', 'docs', '--host', '127.0.0.1', '--port', '4173', '--strictPort'],
    {cwd: ROOT, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe']});
  try {
    await new Promise((resolve, reject) => {
      const timer = setTimeout(() => { cleanup(); reject(new Error('Preview server start timeout')); }, 30000);
      const cleanup = () => {
        clearTimeout(timer);
        server.removeListener('error', onError);
        server.removeListener('exit', onExit);
        server.stdout.removeListener('data', onData);
      };
      const onError = error => { cleanup(); reject(error); };
      const onExit = code => { cleanup(); reject(new Error('Preview server exited (' + code + ')')); };
      const onData = data => {
        process.stdout.write(data);
        if (data.toString().includes('127.0.0.1:4173')) { cleanup(); resolve(); }
      };
      server.on('error', onError);
      server.on('exit', onExit);
      server.stdout.on('data', onData);
      server.stderr.on('data', data => process.stderr.write(data));
    });
    return server;
  } catch (error) {
    server.kill();
    throw error;
  }
}

async function captureRepoBadge(browser, repoName, outputPath, baseURL = BASE_URL) {
  const page = await browser.newPage();
  try {
    await page.setViewport({width: 1200, height: 800, deviceScaleFactor: 2});
    await page.emulateMediaFeatures([{name: 'prefers-color-scheme', value: 'light'}]);
    await page.goto(baseURL + '/repo-badge?repo=' + encodeURIComponent(repoName) + '&embed=1',
      {waitUntil: 'networkidle0', timeout: 30000});
    await page.waitForSelector('.badge-card canvas', {timeout: 15000});
    await page.evaluate(() => document.fonts.ready);
    const element = await page.$('.badge-card');
    const png = Buffer.from(await element.screenshot({omitBackground: true}));
    if (!fs.existsSync(outputPath) || !png.equals(fs.readFileSync(outputPath))) fs.writeFileSync(outputPath, png);
    return digest(png);
  } finally {
    await page.close();
  }
}

async function main() {
  fs.mkdirSync(OUTPUT_DIR, {recursive: true});
  const repoDir = path.join(DATA_DIR, 'datawhalechina/repo');
  const files = fs.readdirSync(repoDir).filter(filename => filename.endsWith('.json')).sort();
  const slugs = files.map(filename => normalizeRepo(path.basename(filename, '.json')));
  if (new Set(slugs).size !== slugs.length) throw new Error('Case-colliding repository data files; deduplicate before generating badges.');
  const members = readJSON(path.join(DATA_DIR, 'members.json'));
  const weekly = readJSON(path.join(DATA_DIR, 'commits_weekly.json'));
  const repoList = readJSON(path.join(DATA_DIR, 'datawhalechina/organization/repo_list.json'));
  let previous = {};
  try { previous = readJSON(CACHE_FILE); } catch (error) {
    if (error.code !== 'ENOENT' && !(error instanceof SyntaxError)) throw error;
  }
  const renderer = rendererFingerprint();
  const next = {};
  const pending = [];
  files.forEach((filename, index) => {
    const slug = slugs[index];
    const inputs = badgeInputs(slug, readJSON(path.join(repoDir, filename)), members, weekly, repoList);
    const input = inputFingerprint(inputs, renderer);
    const outputPath = path.join(OUTPUT_DIR, slug + '.png');
    if (process.argv.includes('--force') || needsCapture(previous[slug], input, outputPath)) pending.push({slug, input, outputPath});
    else next[slug] = previous[slug];
  });
  console.log('Badges: ' + pending.length + ' changed / ' + files.length + ' total');
  if (process.argv.includes('--dry-run')) return;
  if (!pending.length) return;
  const server = await startPreviewServer();
  let browser;
  try {
    browser = await require('puppeteer').launch({headless: true, args: ['--no-sandbox', '--disable-setuid-sandbox', '--font-render-hinting=none', '--disable-font-subpixel-positioning']});
    for (const job of pending) {
      const image = await captureRepoBadge(browser, job.slug, job.outputPath);
      next[job.slug] = {input: job.input, image};
      console.log('Generated: ' + job.slug + '.png');
    }
    fs.mkdirSync(path.dirname(CACHE_FILE), {recursive: true});
    fs.writeFileSync(CACHE_FILE, JSON.stringify(next, null, 2) + '\n');
  } finally {
    if (browser) await browser.close();
    server.kill();
  }
}

module.exports = {badgeInputs, needsCapture, normalizeRepo, captureRepoBadge};
if (require.main === module) main().catch(error => { console.error(error); process.exitCode = 1; });
