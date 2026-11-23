"""Update the existing 2.34.0 cat picker with read-only collection access."""
import hashlib
import json
import os
import struct
import tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent

def renderer(source):
    def change(old,new):
        nonlocal source
        if source.count(old)!=1: raise ValueError("Unrecognized cat picker: "+old[:60])
        source=source.replace(old,new)
    if 'const previewRequests = new Map();' in source: return source
    change('  function make(tag, text)',(HERE/'sync.js').read_text('utf8')+'\n  function make(tag, text)')
    change('    img.src = s.dataUri;', '    loadPreview(img,s);')
    change("    for (const name of ['全部',", "    function categories() {\n      nav.replaceChildren();\n      for (const name of ['全部',")
    change('    search.oninput = filter;', '''    }
    categories();
    refreshOpenPicker=()=>{categories();filter();};
    syncCatalog();
    const timer=setInterval(syncCatalog,1200);
    search.oninput = filter;''')
    change('      resize.disconnect();','      clearInterval(timer); refreshOpenPicker=null;\n      resize.disconnect();')
    change('    scan(document.body);','    scan(document.body);\n    syncCatalog();\n    window.addEventListener("focus",syncCatalog);')
    return source

def entries(tree):
    for entry in tree.values():
        if "files" in entry: yield from entries(entry["files"])
        elif "offset" in entry: yield entry

def rebuild(original, remove_reader=False):
    _,hs,_,n=struct.unpack_from("<4I",original)
    tree=json.loads(original[16:16+n]);payload=original[8+hs:];files=tree["files"]
    def content(e):
        a=int(e["offset"]);return payload[a:a+e["size"]]
    if json.loads(content(files["package.json"]))["version"]!="2.34.0": raise ValueError("Unsupported Antigravity version")
    dist=files["dist"]["files"]; pre=content(dist["preload.js"]).decode()
    begin="// HAKIMI_STICKERS_BEGIN_2";end="// HAKIMI_STICKERS_END_2"
    main=content(dist["main.js"]);reader=(HERE/'reader.js').read_bytes()
    if remove_reader:
        pre=pre.encode()
        if b'// AGY_MEME_COLLECTION_READER_V1' not in main:return original
        segment=b'\n'+reader+b'\n'
        if main.count(segment)!=1:raise ValueError("Conflicting desktop collection reader")
        main=main.replace(segment,b'',1)
    else:
        if pre.count(begin)!=1 or pre.count(end)!=1: raise ValueError("Existing cat picker required")
        prefix,sep,body=pre.partition(begin);body,sep2,suffix=body.partition(end)
        pre=(prefix+sep+renderer(body)+sep2+suffix).encode()
        if b'// AGY_MEME_COLLECTION_READER_V1' not in main: main+=b'\n'+reader+b'\n'
        elif reader not in main: raise ValueError("Conflicting desktop collection reader")
    edits={id(dist["main.js"]):main,id(dist["preload.js"]):pre}
    if all(edits[id(e)]==content(e) for e in [dist["main.js"],dist["preload.js"]]):return original
    new=bytearray()
    for e in sorted(entries(files),key=lambda v:int(v["offset"])):
        data=edits[id(e)] if id(e) in edits else content(e)
        e.update(offset=str(len(new)),size=len(data));new.extend(data)
        if id(e) in edits and "integrity" in e:
            info=e["integrity"];assert info["algorithm"]=="SHA256"
            block=info["blockSize"];digest=lambda b:hashlib.sha256(b).hexdigest()
            info.update(hash=digest(data),blocks=[digest(data[i:i+block]) for i in range(0,len(data),block)])
    header=json.dumps(tree,ensure_ascii=False,separators=(",",":")).encode()
    pad=(len(header)+3)&~3
    return struct.pack("<4I",4,pad+8,pad+4,len(header))+header+bytes(pad-len(header))+new

if __name__=="__main__":
    archive=Path(os.environ['LOCALAPPDATA'])/'Programs/antigravity/resources/app.asar'
    old=archive.read_bytes();new=rebuild(old)
    if old!=new:
        with tempfile.NamedTemporaryFile(dir=archive.parent,delete=False) as f: tmp=Path(f.name)
        try:
            tmp.write_bytes(new)
            assert tmp.read_bytes()==new and rebuild(new)==new
            if archive.read_bytes()!=old:raise ValueError("Application changed during install")
            os.replace(tmp,archive)
        finally:tmp.unlink(missing_ok=True)
