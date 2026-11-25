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


if __name__=="__main__":
    import runpy,sys
    sys.argv[1:]=["install"]
    runpy.run_path(str(HERE.parent/"desktop.py"),run_name="__main__")
