const { app, BrowserWindow, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let backendProcess = null;
let win = null;

function createWindow() {
    if (win) return;

    win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    });

    win.loadURL('http://127.0.0.1:5000');

    win.webContents.setWindowOpenHandler(({ url }) => {
        if (url.includes('xrpscan.com') || url.includes('github.com')) {
            shell.openExternal(url);
            return { action: 'deny' };
        }
        return { action: 'allow' };
    });

    win.webContents.on('will-navigate', (e, url) => {
        if (url.includes('xrpscan.com') || url.includes('github.com')) {
            e.preventDefault();
            shell.openExternal(url);
        }
    });

    win.on('closed', () => {
        win = null;
    });
}

function startBackend() {
    const scriptPath = path.join(__dirname, '..', 'run.py');

    backendProcess = spawn('python', [scriptPath], { cwd: path.join(__dirname, '..') });

    backendProcess.stdout.on('data', (data) => {
        const text = data.toString();
        console.log(`[Flask stdout] ${text}`);

        if (text.includes('Running on http://127.0.0.1:5000')) {
            createWindow();
        }
    });

    backendProcess.stderr.on('data', (data) => {
        console.error(`[Flask stderr] ${data.toString()}`);
    });

    backendProcess.on('close', (code) => {
        console.log(`Flask process exited with code ${code}`);
    });
}

app.whenReady().then(() => {
    startBackend();

    setTimeout(() => {
        if (!win) createWindow();
    }, 5000);

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        if (backendProcess) {
            backendProcess.kill();
        }
        app.quit();
    }
});
