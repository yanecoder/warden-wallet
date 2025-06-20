const { app, BrowserWindow, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let backendProcess = null;

function createWindow() {
    const win = new BrowserWindow({
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
}

function startBackend() {
    const exePath = path.join(__dirname, 'run.exe');
    backendProcess = spawn(exePath, [], { cwd: __dirname });

    backendProcess = spawn(exePath);

    backendProcess.stdout.on('data', (data) => {
        console.log(`[Flask stdout] ${data}`);
    });

    backendProcess.stderr.on('data', (data) => {
        console.error(`[Flask stderr] ${data}`);
    });

    backendProcess.on('close', (code) => {
        console.log(`Flask process exited with code ${code}`);
    });
}

app.whenReady().then(() => {
    startBackend();
    setTimeout(createWindow, 100);
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        if (backendProcess) {
            backendProcess.kill();
        }
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});
