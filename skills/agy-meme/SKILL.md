---
name: agy-meme
description: 在用户要选表情、用图库回图、收藏新图片或分享个人图包时使用。
---

打开 library 以显示 🐱 图库。search 用关键词或分类检索。get_sticker 返回当前电脑可用的原图 URI、表情暗号、关键词和回复用 Markdown。

收图使用 collect，提供用户指定图片的真实本地绝对路径、简短名称、分类和关键词。导出个人图库用 export_pack，并告知用户返回的 ZIP 路径；导入用户指定的 agy-meme ZIP 用 import_pack。重名异图时提示换名。

用户要求删除指定收藏时，调用 delete_sticker 并传入完整名称。名称不明确时先用 search 确定目标。64 张内置表情受保护。
