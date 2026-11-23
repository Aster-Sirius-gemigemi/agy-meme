"""Install/remove the optional desktop integration as one atomic file update."""
import os
import sys
import tempfile
from pathlib import Path

root=Path(__file__).resolve().parent
sys.path[:0]=[str(root/"desktop-base"),str(root/"desktop-picker-sync")]
import manage as base
import install as sync

def change(archive,action):
    if action=="install": return sync.rebuild(base.rebuild(archive,True))
    if action=="uninstall": return base.rebuild(sync.rebuild(archive,remove_reader=True),False)
    raise ValueError("Expected install or uninstall.")

if __name__=="__main__":
    target=Path(os.environ["LOCALAPPDATA"])/"Programs/antigravity/resources/app.asar"
    before=target.read_bytes()
    after=change(before,sys.argv[1])
    if before!=after:
        with tempfile.NamedTemporaryFile(dir=target.parent,delete=False) as f: tmp=Path(f.name)
        try:
            tmp.write_bytes(after)
            if tmp.read_bytes()!=after or target.read_bytes()!=before: raise RuntimeError("Archive changed; retry.")
            os.replace(tmp,target)
        finally: tmp.unlink(missing_ok=True)
    print("Done. Open Antigravity to apply.")
