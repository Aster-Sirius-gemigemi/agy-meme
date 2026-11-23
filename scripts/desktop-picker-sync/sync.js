  const bundled = stickers.slice();
  const previewRequests = new Map();
  let catalogKey, reading, refreshOpenPicker;
  const collection = name => require('electron').ipcRenderer.invoke('agy-meme:collection-v1',name);
  function loadPreview(img,s) {
    if (s.dataUri) { img.src=s.dataUri; return; }
    let pending=previewRequests.get(s.name);
    if (!pending) {
      pending=collection(s.name).then(uri=>{if(uri)s.dataUri=uri;return uri;})
        .catch(()=>null).finally(()=>previewRequests.delete(s.name));
      previewRequests.set(s.name,pending);
    }
    pending.then(uri=>{if(uri)img.src=uri;});
  }
  function syncCatalog() {
    if (reading) return reading;
    reading=collection(null).then(rows=>{
      if (!Array.isArray(rows)) return;
      const key=JSON.stringify(rows);
      if(key===catalogKey)return;
      catalogKey=key;
      const previous=new Map(byName);
      stickers.length=0;byName.clear();
      for(const s of bundled){stickers.push(s);byName.set(s.name,s);}
      for(const row of rows){
        if(byName.has(row.name))continue;
        const s={...row,emoji:'',dataUri:previous.get(row.name)?.dataUri};
        stickers.push(s);byName.set(s.name,s);
      }
      refreshOpenPicker?.();
      document.querySelectorAll(message).forEach(renderMessage);
    }).catch(error=>console.warn('[agy-meme] 收藏库读取失败',error.message))
      .finally(()=>{reading=null;});
    return reading;
  }
