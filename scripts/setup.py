import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def main(action):
    plugins=Path.home()/".gemini/config/plugins"
    plugins.mkdir(parents=True,exist_ok=True)
    target=plugins/"agy-meme"
    if target.is_symlink() or target.resolve().parent!=plugins.resolve():
        raise ValueError("Unexpected plugin target.")
    if target.exists() and (not (target/".agy-meme-install").is_file() or json.loads((target/"plugin.json").read_text("utf8")).get("name")!="agy-meme"):
        raise ValueError("An unmanaged agy-meme folder already exists.")
    if action=="uninstall":
        if target.exists(): shutil.rmtree(target)
        print("agy-meme removed. Personal stickers retained.")
        return
    if action!="install": raise ValueError("Expected install or uninstall.")
    if ROOT==target.resolve():
        print("Already installed.");return
    with tempfile.TemporaryDirectory(dir=plugins,prefix=".agy-meme-stage-") as tmp:
        stage=Path(tmp)/"new";previous=Path(tmp)/"previous"
        shutil.copytree(ROOT,stage,ignore=shutil.ignore_patterns(".git","__pycache__","*.pyc"))
        (stage/".agy-meme-install").write_text("agy-meme\n","ascii")
        if target.exists(): target.rename(previous)
        try: stage.rename(target)
        except OSError:
            if previous.exists(): previous.rename(target)
            raise
    print("agy-meme installed. Open Customizations > Installed, or restart Antigravity.")
if __name__=="__main__":
    main(sys.argv[1])
