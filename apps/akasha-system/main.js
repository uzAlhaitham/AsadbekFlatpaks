const {
  app, BrowserWindow, WebContentsView,
  screen, session, shell, Notification, Menu, ipcMain
} = require('electron');
const path = require('path');
const fs = require('fs');

process.env.ELECTRON_DISABLE_SECURITY_WARNINGS = 'true';
Menu.setApplicationMenu(null);

const STATE_FILE = path.join(app.getPath('userData'), 'window-state.json');

function computeDefaultSize() {
  const primary = screen.getPrimaryDisplay();
  const wa = primary.workAreaSize;
  return {
    width: Math.min(1000, Math.floor(wa.width * 0.75)),
    height: Math.min(700, Math.floor(wa.height * 0.75)),
  };
}

function loadWindowState() {
  try {
    const s = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
    if (s && typeof s.width === 'number' && typeof s.height === 'number') {
      return {
        width: s.width, height: s.height,
        x: typeof s.x === 'number' ? s.x : undefined,
        y: typeof s.y === 'number' ? s.y : undefined,
      };
    }
  } catch (e) {}
  return computeDefaultSize();
}

function saveWindowState(win) {
  if (!win || win.isDestroyed()) return;
  try {
    const isMax = win.isMaximized();
    const b = isMax ? win.getNormalBounds() : win.getBounds();
    fs.writeFileSync(STATE_FILE, JSON.stringify({
      width: b.width, height: b.height, x: b.x, y: b.y,
    }, null, 2));
  } catch (e) {}
}

const AD_DOMAINS = [
  'playwire.com', 'playwire-ads.com', 'intergi.com', 'pw.media',
  'ads.playwire.com', 'cdn.playwire.com', 'config.playwire.com',
  'doubleclick.net', 'googlesyndication.com', 'googleadservices.com',
  'google-analytics.com', 'googletagmanager.com', 'adservice.google.com',
  'amazon-adsystem.com', 'adsafeprotected.com', 'scorecardresearch.com',
  'quantserve.com', 'taboola.com', 'outbrain.com', 'criteo.com', 'criteo.net',
  'pubmatic.com', 'rubiconproject.com', 'openx.net', 'casalemedia.com',
  'sharethrough.com', 'teads.tv', 'adnxs.com', 'moatads.com', 'yieldmo.com',
  'smartadserver.com', 'adform.net', 'adroll.com', 'bidswitch.net',
  'gumgum.com', 'indexww.com', 'inmobi.com', 'lijit.com', 'loopme.me',
  'media.net', 'mgid.com', 'revcontent.com', 'seedtag.com', 'smaato.com',
  'sonobi.com', 'spotxchange.com', 'tapad.com', 'tremorhub.com',
  'triplelift.com', 'yieldlab.net', 'zedo.com',
];

const EXTERNAL_DOMAINS = ['enka.network'];

function hostOf(url) {
  try { return new URL(url).hostname.toLowerCase(); } catch (e) { return ''; }
}
function isAd(url) {
  const host = hostOf(url);
  return AD_DOMAINS.some(function(d) {
    return host === d || host.endsWith('.' + d);
  });
}
function isExternal(url) {
  const host = hostOf(url);
  return EXTERNAL_DOMAINS.some(function(d) {
    return host === d || host.endsWith('.' + d);
  });
}

// ===== TOZA CSS =====
// Faqat 3 narsa: no-drag, scrollbar, display:none (reklama/footer/ikonka)
const AD_HIDE_CSS = `
  html, body {
    -webkit-app-region: no-drag !important;
  }

  /* Native scrollbar — ingichka qora */
  ::-webkit-scrollbar {
    width: 10px;
    height: 10px;
  }
  ::-webkit-scrollbar-track {
    background: transparent;
  }
  ::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 5px;
  }
  ::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.30);
  }
  ::-webkit-scrollbar-thumb:active {
    background: rgba(255, 255, 255, 0.45);
  }
  ::-webkit-scrollbar-button {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
  }
  ::-webkit-scrollbar-corner {
    background: transparent;
  }

  /* Reklama, footer, ikonkalar */
  .pw-container, .playwire-ad-unit, .ad-debug,
  .ad-leaderboard_atf, .ad-leaderboard_btf,
  .ad-sidebar_atf, .ad-sidebar_btf,
  [id^="pw-leaderboard"], [id^="pw-sidebar"], [id^="pw-banner"],
  ins.adsbygoogle, div.adsbygoogle,
  div[id^="div-gpt-ad"], div[id^="google_ads_"],
  iframe[id^="aswift_"], iframe[id^="google_ads_iframe"],
  iframe[src*="doubleclick.net"], iframe[src*="googlesyndication.com"],
  iframe[src*="playwire.com"],
  /* .flex-special-container FAQAT reklama bo'lsa va ID input bo'lmasa yashiriladi */
  .flex-special-container:has(.playwire-ad-unit):not(:has(.input-and-card-result)),
  .patreons-only,
  .footer-wrapper, .footer, .footer-main, .pw-badge,
  a[href*="patreon.com"], a[href*="patreon."],
  a[href*="discord.com"], a[href*="discord.gg"],
  a[href*="discordapp.com"],
  a[href*="playwire.com"], a[href*="playwire."] {
    display: none !important;
  }
`;

app.commandLine.appendSwitch('ignore-gpu-blocklist');
app.commandLine.appendSwitch('enable-gpu-rasterization');
app.commandLine.appendSwitch('enable-zero-copy');
app.commandLine.appendSwitch('enable-features',
  'VaapiVideoDecoder,VaapiIgnoreDriverChecks,CanvasOopRasterization,BackForwardCache');
app.commandLine.appendSwitch('enable-accelerated-2d-canvas');
app.commandLine.appendSwitch('enable-quic');

const TITLEBAR_HEIGHT = 48;
const BORDER_TOP = 6;
const BORDER_LEFT = 6;
const BORDER_RIGHT = 6;
const BORDER_BOTTOM = 6;

const PARTITION = 'persist:akasha';
const UA =
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ' +
  '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36';

const DEFAULT_DOWNLOAD_DIR = path.join(app.getPath('home'), 'Downloads');
if (!fs.existsSync(DEFAULT_DOWNLOAD_DIR)) {
  fs.mkdirSync(DEFAULT_DOWNLOAD_DIR, { recursive: true });
}

function setupDownloads(ses) {
  ses.on('will-download', function(event, item) {
    const fileName = item.getFilename() || 'download';
    item.setSaveDialogOptions({
      title: 'Faylni saqlash',
      defaultPath: path.join(DEFAULT_DOWNLOAD_DIR, fileName),
      buttonLabel: 'Saqlash',
    });
    item.once('done', function(event, state) {
      if (state === 'completed') {
        const savePath = item.getSavePath();
        console.log('Saqlandi: ' + savePath);
        if (Notification.isSupported()) {
          try {
            const n = new Notification({
              title: 'Yuklab olindi',
              body: path.basename(savePath),
            });
            n.on('click', function() { shell.showItemInFolder(savePath); });
            n.show();
          } catch (e) {}
        }
      }
    });
  });
}

let mainWindow = null;
let titlebarView = null;
let contentView = null;
let stateSaveTimer = null;

function sendLoadingState(isLoading) {
  try {
    if (titlebarView && !titlebarView.webContents.isDestroyed()) {
      titlebarView.webContents.send('loading-state', isLoading);
    }
  } catch (e) {}
}

function broadcastNavState() {
  if (!titlebarView || !contentView || !mainWindow) return;
  try {
    if (titlebarView.webContents.isDestroyed()) return;
    const wc = contentView.webContents;
    let canGoBack = false, canGoForward = false, title = 'Akasha Client';
    try {
      canGoBack = wc.navigationHistory.canGoBack();
      canGoForward = wc.navigationHistory.canGoForward();
      title = wc.getTitle() || 'Akasha Client';
    } catch (e) {}
    titlebarView.webContents.send('nav-state', {
      canGoBack: canGoBack,
      canGoForward: canGoForward,
      title: title,
      isMaximized: mainWindow.isMaximized(),
    });
  } catch (e) {}
}

function layoutViews() {
  if (!mainWindow || mainWindow.isDestroyed()) return;
  const b = mainWindow.getBounds();
  const w = b.width, h = b.height;

  const isMax = mainWindow.isMaximized();
  const bt = isMax ? 0 : BORDER_TOP;
  const bl = isMax ? 0 : BORDER_LEFT;
  const br = isMax ? 0 : BORDER_RIGHT;
  const bb = isMax ? 0 : BORDER_BOTTOM;

  if (titlebarView && !titlebarView.webContents.isDestroyed()) {
    titlebarView.setBounds({
      x: bl, y: bt,
      width: Math.max(0, w - bl - br),
      height: TITLEBAR_HEIGHT,
    });
  }
  if (contentView && !contentView.webContents.isDestroyed()) {
    contentView.setBounds({
      x: bl,
      y: TITLEBAR_HEIGHT + bt,
      width: Math.max(0, w - bl - br),
      height: Math.max(0, h - TITLEBAR_HEIGHT - bt - bb),
    });
  }
}

function relayoutRepeatedly() {
  layoutViews();
  [30, 80, 150, 300, 500].forEach(function(t) { setTimeout(layoutViews, t); });
}

function scheduleStateSave() {
  if (stateSaveTimer) clearTimeout(stateSaveTimer);
  stateSaveTimer = setTimeout(function() {
    if (mainWindow && !mainWindow.isDestroyed()) saveWindowState(mainWindow);
    stateSaveTimer = null;
  }, 500);
}

function createWindow() {
  const saved = loadWindowState();
  const ses = session.fromPartition(PARTITION);

  ses.webRequest.onBeforeRequest({ urls: ['*://*/*'] }, function(details, callback) {
    if (isAd(details.url)) return callback({ cancel: true });
    callback({});
  });

  setupDownloads(ses);
  ses.setUserAgent(UA);

  const winOpts = {
    width: saved.width, height: saved.height,
    minWidth: 925, minHeight: 625,
    frame: false, resizable: true, maximizable: true,
    backgroundColor: '#1e1f22',
    title: 'Akasha Client',
    show: false,
  };
  if (typeof saved.x === 'number' && typeof saved.y === 'number') {
    winOpts.x = saved.x;
    winOpts.y = saved.y;
  }

  mainWindow = new BrowserWindow(winOpts);

  titlebarView = new WebContentsView({
    webPreferences: {
      preload: path.join(__dirname, 'titlebar-preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
    },
  });
  mainWindow.contentView.addChildView(titlebarView);
  titlebarView.webContents.loadFile(path.join(__dirname, 'titlebar.html'));

  contentView = new WebContentsView({
    webPreferences: {
      partition: PARTITION,
      nodeIntegration: false,
      contextIsolation: true,
      backgroundThrottling: false,
      spellcheck: false,
      webgl: true,
    },
  });
  mainWindow.contentView.addChildView(contentView);
  contentView.webContents.setUserAgent(UA);

  layoutViews();

  mainWindow.on('resize', function() { layoutViews(); scheduleStateSave(); });
  mainWindow.on('move', function() { scheduleStateSave(); });
  mainWindow.on('maximize', function() { relayoutRepeatedly(); broadcastNavState(); });
  mainWindow.on('unmaximize', function() {
    relayoutRepeatedly(); scheduleStateSave(); broadcastNavState();
  });

  const wc = contentView.webContents;

  wc.on('did-stop-loading', function() { sendLoadingState(false); });
  wc.on('did-finish-load', function() {
    wc.insertCSS(AD_HIDE_CSS).catch(function() {});
    broadcastNavState();
    sendLoadingState(false);
    try { wc.focus(); } catch (e) {}
  });
  wc.on('did-fail-load', function(e, code, desc, url) {
    console.error('Xato - yuklanmadi:', code, desc, url);
    sendLoadingState(false);
  });
  wc.on('did-navigate', function() {
    broadcastNavState();
    setTimeout(function() {
      wc.insertCSS(AD_HIDE_CSS).catch(function() {});
      }, 100);
  });
  wc.on('did-navigate-in-page', broadcastNavState);
  wc.on('page-title-updated', broadcastNavState);

  wc.setWindowOpenHandler(function(details) {
    if (isExternal(details.url)) {
      shell.openExternal(details.url);
      return { action: 'deny' };
    }
    return {
      action: 'allow',
      overrideBrowserWindowOptions: {
        width: 640, height: 820,
        autoHideMenuBar: true, parent: mainWindow,
        webPreferences: {
          partition: PARTITION,
          nodeIntegration: false, contextIsolation: true,
        },
      },
    };
  });

  wc.on('will-navigate', function(event, url) {
    if (isExternal(url)) { event.preventDefault(); shell.openExternal(url); }
  });
  wc.on('will-redirect', function(event, url) {
    if (isExternal(url)) { event.preventDefault(); shell.openExternal(url); }
  });

  // ===== F12 — DevTools =====
  wc.on('before-input-event', function(event, input) {
    if (input.type !== 'keyDown') return;
    if (input.key === 'F12') {
      try { wc.toggleDevTools(); } catch (e) {}
      event.preventDefault(); return;
    }
    if (input.control && input.shift && input.key.toLowerCase() === 'i') {
      try { wc.toggleDevTools(); } catch (e) {}
      event.preventDefault(); return;
    }
  });

  wc.loadURL('https://akasha.cv');
  mainWindow.show();

  mainWindow.on('close', function() { saveWindowState(mainWindow); });
  mainWindow.on('closed', function() {
    mainWindow = null; titlebarView = null; contentView = null;
  });
}

ipcMain.on('win-minimize', function() { if (mainWindow) mainWindow.minimize(); });
ipcMain.on('win-maximize', function() {
  if (!mainWindow) return;
  if (mainWindow.isMaximized()) mainWindow.unmaximize();
  else mainWindow.maximize();
  relayoutRepeatedly();
  setTimeout(broadcastNavState, 100);
});
ipcMain.on('win-close', function() { if (mainWindow) mainWindow.close(); });
ipcMain.on('nav-back', function() {
  if (!contentView) return;
  try {
    const wc = contentView.webContents;
    if (wc.navigationHistory.canGoBack()) wc.navigationHistory.goBack();
  } catch (e) {}
});
ipcMain.on('nav-forward', function() {
  if (!contentView) return;
  try {
    const wc = contentView.webContents;
    if (wc.navigationHistory.canGoForward()) wc.navigationHistory.goForward();
  } catch (e) {}
});
ipcMain.on('nav-refresh', function() {
  if (!contentView) return;
  try {
    sendLoadingState(true);
    contentView.webContents.reload();
  } catch (e) { sendLoadingState(false); }
});

const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) { app.quit(); }
else {
  app.on('second-instance', function() {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
  app.whenReady().then(function() {
    createWindow();
    app.on('activate', function() {
      if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
  });
}

app.on('window-all-closed', function() {
  if (process.platform !== 'darwin') app.quit();
});
