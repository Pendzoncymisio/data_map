import { app, BrowserWindow } from 'electron';
import { loadDataForCanvas } from './main2.js';

function createWindow () {
  let win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    }
  })

  win.loadFile('index.html') // replace 'index.html' with the path to your HTML file
  win.webContents.openDevTools()

  loadDataForCanvas(win)
}

app.whenReady().then(createWindow)