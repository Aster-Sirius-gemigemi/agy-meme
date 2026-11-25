"""Install the desktop sticker UI only when the client exposes the required components."""
import contextlib
import hashlib
import json
import mmap
import os
import re
import struct
import sys
import tempfile
import zipfile
import zlib
from pathlib import Path

root = Path(__file__).resolve().parent
sys.path[:0] = [str(root/"desktop-base"), str(root/"desktop-picker-sync")]
import manage as base
import install as sync

FEATURES = {
    "附件底栏": (b"agy-composer-footer", b'"agent-input-box"'),
    "可编辑草稿": (b"data-lexical-editor",),
    "用户气泡": (b'"user-message-content"', b'"data-quotable"'),
    "AI 图片卡片": (b"group/media", b"data-carousel-media-src", b"rounded-lg border"),
}

def verify_ui(resource_dir):
    binary = resource_dir/"bin/language_server.exe"
    missing = list(FEATURES)
    with binary.open("rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as data:
        for hit in re.finditer(rb"PK\x03\x04", data):
            offset = hit.start()
            if offset+30 > len(data):
                continue
            _, _, flags, method, _, _, crc, size, raw_size, n, extra = struct.unpack_from("<I5H3I2H", data, offset)
            filename = data[offset+30:offset+30+n]
            if filename.rsplit(b"/",1)[-1] != b"main.js" or flags & 1 or raw_size > 96*1024*1024:
                continue
            start = offset+30+n+extra
            if start+size > len(data) or method not in (zipfile.ZIP_DEFLATED, zipfile.ZIP_STORED):
                continue
            blob = data[start:start+size]
            ui = zlib.decompress(blob,-15) if method==zipfile.ZIP_DEFLATED else blob
            if len(ui)!=raw_size or zlib.crc32(ui)!=crc:
                continue
            absent = [name for name, tokens in FEATURES.items() if not all(t in ui for t in tokens)]
            if not absent:
                return
            if len(absent)<len(missing):
                missing = absent
    raise ValueError("找不到兼容的前端组件："+"、".join(missing))

def managed_preload(old, installing):
    owned = base.begin in old or base.end in old
    if owned:
        if old.count(base.begin)!=1 or old.count(base.end)!=1:
            raise ValueError("底栏补丁标记不完整或重复")
        left, _, tail = old.partition(base.begin)
        middle, match, right = tail.partition(base.end)
        if not match or not middle.startswith(base.legacy.lstrip(b"\n")):
            raise ValueError("无法识别底栏补丁内容")
    else:
        left, right = old, b""
    if base.legacy in left+right:
        if owned or left.count(base.legacy)!=1:
            raise ValueError("检测到冲突的旧底栏")
        pos = left.index(base.legacy)
        if base.hash_bytes(left[pos:pos+base.legacy_size]) != base.legacy_hash:
            raise ValueError("旧底栏已被修改")
        left, right = left[:pos], left[pos+base.legacy_size:]
    if not installing:
        return left+right
    template=(root/"desktop-base/stickers.js").read_text("utf-8")
    return left+base.begin+sync.renderer(template).encode()+base.end+right

def managed_main(old, installing):
    reader=(root/"desktop-picker-sync/reader.js").read_bytes()
    block=b"\n"+reader+b"\n"
    if b"// AGY_MEME_COLLECTION_READER_V1" in old:
        if old.count(block)!=1 or old.count(b"// AGY_MEME_COLLECTION_READER_V1")!=1:
            raise ValueError("收藏库读取补丁内容有冲突")
        return old if installing else old.replace(block,b"",1)
    return old+block if installing else old

def entries(files):
    for entry in files.values():
        if "files" in entry:
            yield from entries(entry["files"])
        elif "offset" in entry:
            yield entry

def unpack(archive):
    marker, header_size, padded, length=struct.unpack_from("<4I",archive)
    if marker!=4 or padded+4!=header_size or not 16+length<=8+header_size<=len(archive):
        raise ValueError("无法识别 ASAR 文件头")
    tree=json.loads(archive[16:16+length])
    return tree,archive[8+header_size:]

def change(archive, action):
    if action not in ("install","uninstall"):
        raise ValueError("Expected install or uninstall")
    installing=action=="install"
    tree,payload=unpack(archive)
    files=tree["files"]
    def content(entry):
        offset=int(entry["offset"])
        return payload[offset:offset+entry["size"]]
    package=json.loads(content(files["package.json"]))
    if package.get("name")!="antigravity" or package.get("main") not in ("./dist/main.js","dist/main.js"):
        raise ValueError("无法识别 Antigravity 主进程入口")
    dist=files["dist"]["files"]
    main,pre=dist["main.js"],dist["preload.js"]
    orig_main,orig_pre=content(main),content(pre)
    if installing and (b'ipcRenderer' not in orig_pre or not re.search(rb"""require\(\s*['"]electron['"]\s*\)""",orig_main)):
        raise ValueError("找不到 Electron 主进程或 preload IPC 接口")
    edits={id(main):managed_main(orig_main,installing),id(pre):managed_preload(orig_pre,installing)}
    if edits[id(main)]==orig_main and edits[id(pre)]==orig_pre:
        return archive
    changes=sorted((int(e["offset"]),int(e["offset"])+e["size"],id(e),edits[id(e)])
                   for e in (main,pre) if edits[id(e)]!=content(e))
    new=bytearray()
    cursor=0
    for start,stop,_,replacement in changes:
        if not cursor<=start<=stop<=len(payload):
            raise ValueError("ASAR 入口区间无效")
        new.extend(payload[cursor:start]);new.extend(replacement);cursor=stop
    new.extend(payload[cursor:])
    for entry in entries(files):
        start=int(entry["offset"]);stop=start+entry["size"]
        if not 0<=start<=stop<=len(payload):
            raise ValueError("ASAR 文件越界")
        shift=0
        for lo,hi,owner,replacement in changes:
            if start>=hi:
                shift+=len(replacement)-(hi-lo)
            elif start<hi and stop>lo and id(entry)!=owner:
                raise ValueError("桌面入口与其他文件共享区间")
        entry["offset"]=str(start+shift)
        if id(entry) in edits and edits[id(entry)]!=payload[start:stop]:
            data=edits[id(entry)]
            if "integrity" in entry:
                info=entry["integrity"];block=info["blockSize"]
                if info["algorithm"]!="SHA256" or block<=0:raise ValueError("未知的 ASAR 完整性格式")
                info.update(hash=base.hash_bytes(data),blocks=[base.hash_bytes(data[i:i+block]) for i in range(0,len(data),block)])
            entry["size"]=len(data)
    header=json.dumps(tree,ensure_ascii=False,separators=(",",":")).encode()
    pad=(len(header)+3)&~3
    return struct.pack("<4I",4,pad+8,pad+4,len(header))+header+bytes(pad-len(header))+new

@contextlib.contextmanager
def install_lock(target):
    import msvcrt
    key=hashlib.sha256(str(target.resolve()).casefold().encode()).hexdigest()[:16]
    with (Path(tempfile.gettempdir())/("agy-meme-"+key+".lock")).open("a+b") as lock:
        lock.seek(0)
        msvcrt.locking(lock.fileno(),msvcrt.LK_LOCK,1)
        try:
            yield
        finally:
            lock.seek(0)
            msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)

def run(action):
    target=Path(os.environ["LOCALAPPDATA"])/"Programs/antigravity/resources/app.asar"
    with install_lock(target):
        if action=="install":
            verify_ui(target.parent)
        before=target.read_bytes()
        after=change(before,action)
        if before==after:
            print("已是目标状态，本次未写入应用包。")
            return
        with tempfile.NamedTemporaryFile(dir=target.parent,delete=False) as f:
            temp=Path(f.name)
        try:
            temp.write_bytes(after)
            if temp.read_bytes()!=after or change(after,action)!=after or target.read_bytes()!=before:
                raise ValueError("校验失败或客户端正在更新，请稍后重试")
            os.replace(temp,target)
        finally:
            temp.unlink(missing_ok=True)
        print("已完成。打开 Antigravity 即可生效。")

if __name__=="__main__":
    try:
        run(sys.argv[1])
    except PermissionError as error:
        sys.exit("请完全退出 Antigravity 并确认安装目录可写后重试。 "+str(error))
    except (OSError,ValueError,KeyError,struct.error,zlib.error) as error:
        sys.exit("桌面适配未写入："+str(error))
