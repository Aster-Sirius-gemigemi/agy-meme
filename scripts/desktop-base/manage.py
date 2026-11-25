import hashlib
from pathlib import Path

begin = b"\n// HAKIMI_STICKERS_BEGIN_2\n"
end = b"\n// HAKIMI_STICKERS_END_2\n"
legacy = b"\n// Hakimi sticker UI for Antigravity App 2.34."
legacy_size = 616727
legacy_hash = "fd0bfe0628c5b7b5d2b9e4c3844ba34d26ee707ca0da408f63bbcafcb291145d"

def hash_bytes(data):
    return hashlib.sha256(data).hexdigest()


if __name__=="__main__":
    import runpy
    runpy.run_path(str(Path(__file__).resolve().parents[1]/"desktop.py"),run_name="__main__")
