// AGY_MEME_COLLECTION_READER_V1
;(() => {
  const {ipcMain, BrowserWindow, nativeImage} = require('electron');
  const {DatabaseSync} = require('node:sqlite');
  const fs = require('node:fs');
  const path = require('node:path');
  const home = require('node:os').homedir();
  const databases = [
    path.join(home,'.gemini','antigravity','plugin_data','agy-meme','collection.sqlite3'),
    path.join(home,'.gemini','config','agy-meme-data','collection.sqlite3')
  ];
  ipcMain.handle('agy-meme:collection-v1',(event,name) => {
    const frame = event.senderFrame;
    if (!frame || frame !== event.sender.mainFrame || (!BrowserWindow.fromWebContents(event.sender) && !["browserView","window"].includes(event.sender.getType())) ||
        !/^https?:\/\/(?:127\.0\.0\.1|localhost|\[::1\])(?::\d+)?\//.test(frame.url)) return null;
    const file = databases.find(p=>fs.existsSync(p));
    if (!file) return name == null ? [] : null;
    const db = new DatabaseSync(file,{readOnly:true});
    try {
      if (name == null) return db.prepare('SELECT name,category,keywords FROM stickers ORDER BY rowid').all();
      if (typeof name !== 'string' || name.length>80) return null;
      const row=db.prepare('SELECT coalesce(preview,image) AS bytes, preview IS NULL AS original FROM stickers WHERE name=?').get(name);
      if (!row) return null;
      const bytes=Buffer.from(row.bytes);
      if (bytes.length>8388608) return null;
      if (row.original) {
        const img=nativeImage.createFromBuffer(bytes);
        if (!img.isEmpty()) {
          const {width,height}=img.getSize();
          if (Math.max(width,height)>96) return img.resize(width>=height?{width:96}:{height:96}).toDataURL();
        }
      }
      let mime;
      if(bytes[0]===137) mime='png';
      else if(bytes[0]===255) mime='jpeg';
      else if(bytes.toString('ascii',0,3)==='GIF') mime='gif';
      else if(bytes.toString('ascii',8,12)==='WEBP') mime='webp';
      else return null;
      return 'data:image/'+mime+';base64,'+bytes.toString('base64');
    } finally { db.close(); }
  });
})();
