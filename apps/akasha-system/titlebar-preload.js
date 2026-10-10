const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('titlebarAPI', {
  minimize: function() { ipcRenderer.send('win-minimize'); },
  maximize: function() { ipcRenderer.send('win-maximize'); },
  close:    function() { ipcRenderer.send('win-close'); },
  back:     function() { ipcRenderer.send('nav-back'); },
  forward:  function() { ipcRenderer.send('nav-forward'); },
  refresh:  function() { ipcRenderer.send('nav-refresh'); },
  onNavState: function(cb) {
    ipcRenderer.on('nav-state', function(e, state) { cb(state); });
  },
  onLoadingState: function(cb) {
    ipcRenderer.on('loading-state', function(e, isLoading) { cb(isLoading); });
  },
});
