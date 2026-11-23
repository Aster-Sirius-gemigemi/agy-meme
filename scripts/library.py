import base64
import hashlib
import io
import json
import os
import re
import sqlite3
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets/sticker"
DATA = Path(os.getenv("PLUGIN_DATA") or Path.home()/".gemini/config/agy-meme-data").resolve()
BASE = json.loads((ASSETS/"stickers_index.json").read_text("utf-8"))
BUILTIN = {row["name"]: row for row in BASE}
MAX_IMAGE = 8 * 1024 * 1024
MAX_PACK = 64 * 1024 * 1024

def connect():
    DATA.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DATA/"collection.sqlite3", timeout=15)
    db.row_factory = sqlite3.Row
    db.execute("CREATE TABLE IF NOT EXISTS stickers(name TEXT PRIMARY KEY, category TEXT, keywords TEXT, ext TEXT, image BLOB, preview BLOB)")
    return db

def image_type(b):
    if not 12 <= len(b) <= MAX_IMAGE:
        raise ValueError("图片大小需要在 8 MiB 以内")
    if b.startswith(b"\x89PNG\r\n\x1a\n") and b[12:16] == b"IHDR": return "png"
    if b.startswith(b"\xff\xd8\xff") and b.endswith(b"\xff\xd9"): return "jpg"
    if b[:6] in (b"GIF87a",b"GIF89a"): return "gif"
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP": return "webp"
    raise ValueError("请选择 PNG、JPEG、WebP 或 GIF 图片")

def read_limited(path, limit):
    p = Path(path).expanduser()
    if not p.is_absolute() or not p.is_file() or p.stat().st_size > limit:
        raise ValueError("请提供大小符合要求的本地文件绝对路径")
    with p.open("rb") as f:
        data = f.read(limit+1)
    if len(data)>limit: raise ValueError("文件过大")
    return data

def save(db, name, category, keywords, image, preview=None):
    name = name.strip()
    if not re.fullmatch(r"[^:\[\]\s\x00-\x1f]{1,40}",name):
        raise ValueError("名称需为 1–40 个字符，不能含空格、冒号或方括号")
    if name in BUILTIN: raise ValueError("与内置表情同名，请换个名字")
    ext = image_type(image)
    if preview: image_type(preview)
    if len(category)>40 or len(keywords)>500: raise ValueError("分类或描述过长")
    current = db.execute("SELECT image FROM stickers WHERE name=?",(name,)).fetchone()
    if current:
        if current["image"] == image: return False
        raise ValueError("已存在同名的其他图片，请换个名字")
    db.execute("INSERT INTO stickers VALUES(?,?,?,?,?,?)",(name,category.strip() or "自定义",keywords.strip(),ext,image,preview))
    return True

def rows(db):
    custom = db.execute("SELECT name,category,keywords FROM stickers ORDER BY rowid")
    return [dict(name=s["name"],category=s["category"],keywords=s["keywords"],custom=False) for s in BASE]+[dict(s,custom=True) for s in custom]

def atomic_write(path, data):
    path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as f:
        tmp=Path(f.name)
    try:
        tmp.write_bytes(data)
        os.replace(tmp,path)
    finally:
        tmp.unlink(missing_ok=True)

def lookup(db,name):
    if name in BUILTIN:
        s=BUILTIN[name]
        original=ASSETS/s["filename"]
    else:
        s=db.execute("SELECT * FROM stickers WHERE name=?",(name,)).fetchone()
        if not s: raise ValueError("未找到该表情")
        image=s["image"]
        original=DATA/"images"/(hashlib.sha256(image).hexdigest()+"."+s["ext"])
        if not original.is_file(): atomic_write(original,image)
    return dict(name=name,category=s["category"],keywords=s["keywords"],token=":"+name+":",original=original.as_uri(),reply="![agy-meme · 表情]("+original.as_uri()+")")

def thumb(db,name):
    if name in BUILTIN:
        data=(ASSETS/"thumb"/(BUILTIN[name]["id"]+".webp")).read_bytes()
    else:
        s=db.execute("SELECT COALESCE(preview,image) FROM stickers WHERE name=?",(name,)).fetchone()
        if not s: raise ValueError("未找到表情")
        data=s[0]
    ext=image_type(data)
    return "data:image/"+("jpeg" if ext=="jpg" else ext)+";base64,"+base64.b64encode(data).decode()

def export_pack(db):
    buf=io.BytesIO()
    manifest=[]
    total=0
    with zipfile.ZipFile(buf,"w",zipfile.ZIP_DEFLATED) as z:
        for s in db.execute("SELECT * FROM stickers ORDER BY name"):
            total+=len(s["image"])
            if total>MAX_PACK-1024*1024 or len(manifest)>=512: raise ValueError("单个图包限 512 张、63 MiB")
            filename=f'images/{len(manifest)}.{s["ext"]}'
            z.writestr(filename,s["image"])
            manifest.append(dict(name=s["name"],category=s["category"],keywords=s["keywords"],file=filename))
        z.writestr("pack.json",json.dumps(dict(format="agy-meme/1",stickers=manifest),ensure_ascii=False))
    if not manifest: raise ValueError("请先收藏至少一张自定义表情")
    data=buf.getvalue()
    path=DATA/"exports"/("agy-meme-"+hashlib.sha256(data).hexdigest()[:12]+".zip")
    atomic_write(path,data)
    return dict(path=str(path),count=len(manifest))

def import_pack(db,data):
    if len(data)>MAX_PACK: raise ValueError("图包过大")
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        members=z.infolist()
        if len(members)>513 or sum(i.file_size for i in members)>MAX_PACK or len(set(z.namelist()))!=len(members):
            raise ValueError("图包目录无效或超出大小限制")
        if z.getinfo("pack.json").file_size>1024*1024: raise ValueError("索引过大")
        doc=json.loads(z.read("pack.json"))
        if doc.get("format")!="agy-meme/1" or len(doc["stickers"])>512: raise ValueError("不支持的图包")
        added=0
        for s in doc["stickers"]:
            f=s["file"]
            if not re.fullmatch(r"images/[0-9]+\.(png|jpg|gif|webp)",f) or z.getinfo(f).file_size>MAX_IMAGE: raise ValueError("无效图片条目")
            added+=save(db,s["name"],s["category"],s["keywords"],z.read(f))
        return dict(added=added,total=len(doc["stickers"]))
