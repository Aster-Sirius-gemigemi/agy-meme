"""Install or remove the bundled Hakimi sticker UI in Antigravity 2.34.0."""
import hashlib
import json
import os
import struct
import sys
import tempfile
from pathlib import Path

begin = b"\n// HAKIMI_STICKERS_BEGIN_2\n"
end = b"\n// HAKIMI_STICKERS_END_2\n"
legacy = b"\n// Hakimi sticker UI for Antigravity App 2.34."
legacy_size = 616727
legacy_hash = "fd0bfe0628c5b7b5d2b9e4c3844ba34d26ee707ca0da408f63bbcafcb291145d"

def hash_bytes(data):
    return hashlib.sha256(data).hexdigest()

def edit_script(script, install):
    if begin in script or end in script:
        if script.count(begin) != 1 or script.count(end) != 1:
            raise ValueError("Incomplete Hakimi markers.")
        a = script.index(begin)
        b = script.index(end, a) + len(end)
        script = script[:a] + script[b:]
    if legacy in script:
        a = script.index(legacy)
        if hash_bytes(script[a:a+legacy_size]) != legacy_hash:
            raise ValueError("Unrecognized previous Hakimi version.")
        script = script[:a] + script[a+legacy_size:]
    if install:
        script += begin + Path(__file__).with_name("stickers.js").read_bytes() + end
    return script

def packed_entries(files):
    for item in files.values():
        if "files" in item:
            yield from packed_entries(item["files"])
        elif "offset" in item:
            yield item

def rebuild(original, install):
    _, header_size, _, length = struct.unpack_from("<4I", original)
    tree = json.loads(original[16:16+length])
    payload = original[8+header_size:]
    def content(entry):
        start = int(entry["offset"])
        return payload[start:start+entry["size"]]
    files = tree["files"]
    if install and json.loads(content(files["package.json"]))["version"] != "2.34.0":
        raise ValueError("This release supports Antigravity 2.34.0.")
    target = files["dist"]["files"]["preload.js"]
    before = content(target)
    after = edit_script(before, install)
    if after == before:
        return original
    start = int(target["offset"])
    stop = start + len(before)
    changed = payload[:start] + after + payload[stop:]
    for entry in packed_entries(files):
        expected = after if entry is target else content(entry)
        offset = int(entry["offset"])
        if offset >= stop:
            offset += len(after) - len(before)
            entry["offset"] = str(offset)
        if changed[offset:offset+len(expected)] != expected:
            raise ValueError("Archive verification failed.")
    target["size"] = len(after)
    if "integrity" in target:
        info = target["integrity"]
        if info["algorithm"] != "SHA256":
            raise ValueError("Unknown archive format.")
        block = info["blockSize"]
        info.update(hash=hash_bytes(after), blocks=[hash_bytes(after[i:i+block]) for i in range(0,len(after),block)])
    header = json.dumps(tree,separators=(",",":"),ensure_ascii=False).encode()
    padded = (len(header)+3) & ~3
    return struct.pack("<4I",4,padded+8,padded+4,len(header))+header+bytes(padded-len(header))+changed

def main(action):
    if action not in ("install","uninstall"):
        raise ValueError("Expected install or uninstall.")
    archive = Path(os.environ["LOCALAPPDATA"]) / "Programs/antigravity/resources/app.asar"
    original = archive.read_bytes()
    result = rebuild(original, action == "install")
    if result != original:
        with tempfile.NamedTemporaryFile(dir=archive.parent, delete=False) as temp:
            path = Path(temp.name)
        try:
            path.write_bytes(result)
            if path.read_bytes() != result or archive.read_bytes() != original:
                raise ValueError("Archive changed during installation. Retry.")
            os.replace(path, archive)
        finally:
            path.unlink(missing_ok=True)
    print("Done. Restart Antigravity to apply.")

if __name__ == "__main__":
    main(sys.argv[1])
