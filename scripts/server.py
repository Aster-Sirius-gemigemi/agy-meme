import base64
import json
import sys
from library import BUILTIN, ROOT, MAX_IMAGE, MAX_PACK, connect, rows, lookup, save, thumb, export_pack, import_pack, read_limited

URI="ui://agy-meme/library.html"
MIME="text/html;profile=mcp-app"
def tool(name,description,fields=(),required=(),meta=None):
    schema=dict(type="object",properties={s:{"type":"string"} for s in fields},required=list(required),additionalProperties=False)
    return dict(name=name,description=description,inputSchema=schema,**({"_meta":meta} if meta else {}))
ui_only={"ui":{"visibility":["app"]}}
TOOLS=[
    tool("library","打开 🐱 表情图库。",meta={"ui":{"resourceUri":URI},"com.google.antigravity/ui":{"entrypoints":[{"type":"aux_pane","title":"🐱 表情图库"}]}}),
    tool("search","按名称、分类或描述搜索，返回暗号和含义。",["query"]),
    tool("get_sticker","取得一张已知表情的含义、原图地址和可直接用于回复的 Markdown。",["name"],["name"]),
    tool("collect","应用户明确要求收藏指定本地图片。path 为该附件已确认的绝对路径。",["name","path","category","keywords"],["name","path"]),
    tool("delete_sticker","按用户明确指定的完整名称删除一张个人收藏。内置表情受保护。",["name"],["name"]),
    tool("export_pack","把个人图库导出为可分享的 ZIP，返回本机路径。"),
    tool("import_pack","从用户指定的本机 ZIP 导入 agy-meme 图包。",["path"],["path"]),
    tool("list_ui","选择器列表",meta=ui_only),
    tool("thumbnail","获取指定表情的预览",["name"],["name"],ui_only),
    tool("collect_upload","收藏文件选择器选定的图片",["name","image","preview","category","keywords"],["name","image"],ui_only),
    tool("import_upload","导入文件选择器选定的图包",["zip"],["zip"],ui_only),
]
def decode(s,limit):
    if len(s)>4*((limit+2)//3): raise ValueError("文件过大")
    return base64.b64decode(s,validate=True)

def invoke(name,a):
    db=connect()
    try:
        with db:
            if name=="library": return {"message":"已打开 🐱 表情图库。"}
            if name in ("search","list_ui"):
                q=a.get("query","").strip().casefold()
                return {"stickers":[s for s in rows(db) if q in (s["name"]+s["category"]+s["keywords"]).casefold()]}
            if name=="get_sticker": return lookup(db,a["name"])
            if name=="thumbnail": return {"url":thumb(db,a["name"])}
            if name=="delete_sticker":
                sticker=a["name"].strip()
                if sticker in BUILTIN: raise ValueError("这张是内置表情，不能删除")
                if not sticker: raise ValueError("请指定要删除的自定义表情全名")
                deleted=db.execute("DELETE FROM stickers WHERE name=?",(sticker,)).rowcount
                if not deleted: raise ValueError("个人图库中没有这张表情")
                return {"deleted":True,"name":sticker}
            if name in ("collect","collect_upload"):
                data=read_limited(a["path"],MAX_IMAGE) if name=="collect" else decode(a["image"],MAX_IMAGE)
                preview=decode(a["preview"],256*1024) if a.get("preview") else None
                db.execute("BEGIN IMMEDIATE")
                added=save(db,a["name"],a.get("category","自定义"),a.get("keywords",""),data,preview)
                return {"added":added,"name":a["name"].strip()}
            if name=="export_pack": return export_pack(db)
            if name in ("import_pack","import_upload"):
                data=read_limited(a["path"],MAX_PACK) if name=="import_pack" else decode(a["zip"],MAX_PACK)
                db.execute("BEGIN IMMEDIATE")
                return import_pack(db,data)
            raise ValueError("未知工具")
    finally: db.close()

def dispatch(req):
    method=req["method"];p=req.get("params",{})
    if method=="initialize":
        versions=("2025-11-25","2025-06-18","2025-03-26","2024-11-05")
        v=p.get("protocolVersion")
        return dict(protocolVersion=v if v in versions else versions[0],capabilities={"tools":{},"resources":{}},serverInfo={"name":"agy-meme","version":"0.1.1"})
    if method=="ping": return {}
    if method=="tools/list": return {"tools":TOOLS}
    if method=="resources/list": return {"resources":[{"uri":URI,"name":"🐱 表情图库","mimeType":MIME}]}
    if method=="resources/templates/list": return {"resourceTemplates":[]}
    if method=="resources/read" and p["uri"]==URI:
        return {"contents":[{"uri":URI,"mimeType":MIME,"text":(ROOT/"scripts/panel.html").read_text("utf8")}]}
    if method=="tools/call":
        try:
            data=invoke(p["name"],p.get("arguments",{}))
            summary=data.get("message") or ("已加载预览" if "url" in data else json.dumps(data,ensure_ascii=False))
            return {"content":[{"type":"text","text":summary}],"structuredContent":data}
        except Exception as e: return {"isError":True,"content":[{"type":"text","text":str(e)}]}
    raise KeyError(method)

if __name__=="__main__":
    for line in sys.stdin:
        req={}
        try:
            req=json.loads(line)
            if "id" not in req: continue
            reply={"result":dispatch(req)}
        except KeyError as e: reply={"error":{"code":-32601,"message":str(e)}}
        except Exception as e: reply={"error":{"code":-32603,"message":str(e)}}
        print(json.dumps({"jsonrpc":"2.0","id":req.get("id"),**reply},ensure_ascii=False),flush=True)
