# 🐱 agy-meme
<img width="591" height="122" alt="Antigravity_HEHCbU67ni" src="https://github.com/user-attachments/assets/3bb36e0e-aed3-4b80-ac6e-9adb0b576fef" />

## Antigravity 的独立表情图库省token版。随包附 64 张哈基米原图、原比例兼容副本和预览图。
<img width="592" height="193" alt="Antigravity_YDEZelS5k4" src="https://github.com/user-attachments/assets/6b96868b-6662-4ac0-ab5a-5f3338ebaf10" />

## 💡 基咪是怎么省 Token 发表情的？

基咪：很多朋友担心高频发表情包会像传图片附件一样狂烧多模态 Token，其实我采用的是 **「暗号驱动 + 按需拆盲盒」** 的超省流机制：
1. **已知表情零看图消耗**：
   - **内置 64 张哈基米表情** 与 **填写了「含义/关键词」的自定义表情**：当你发送 `:满地打滚:` 等表情时，前端在你气泡里渲染贴图，而我收到的是轻量文本暗号与文字释义。我不必加载图片像素就能读懂你的意思并回敬表情包，**全程 0 图片 Token 消耗**。
2. **无描述新表情「只看第一眼」**：
   - 如果你在 🐱 图库添加了新表情却把「含义或关键词」留空，我会在它**本轮对话首次出场**时自动调阅一次原图（你甚至可以用这个机制故意不填描述，考考我能不能看懂新梗图！）。
   - 看过第一眼后，本轮对话后续再收到该表情我就心中有数了，只需读取暗号，不会重复读图。
   - *省流小贴士：在图库添加自定义表情时顺手填一句画面描述，连新开对话的“第一眼读图”都能省掉哦！如果你想让基咪知道表情具体内容，可以留空或者和她说：看一下刚才的表情*
  
## 安装

**[点我直接下载](https://github.com/Aster-Sirius-gemigemi/agy-meme/releases/download/v0.1.2/agy-meme-0.1.2.zip)**





下载并解压整个压缩包。Windows 双击 `install.bat`，macOS 或 Linux 在插件目录运行 `sh install.sh`。需要 Python 3.8 或更新版本，以及 Antigravity 桌面端。安装位置是当前用户的 `~/.gemini/config/plugins/agy-meme`。重新打开「自定义项 → 已安装」，必要时重启 Antigravity，启用 agy-meme。插件的 MCP 服务通过 Node 启动，Antigravity 2.34.0 支持使用应用内置 Node。

---

**[点我下载claude64张表情扩展包](https://github.com/user-attachments/files/35328852/claude_64_agy-meme_pack.zip)**

<img width="409" height="392" alt="image" src="https://github.com/user-attachments/assets/89c089e3-300c-4841-af72-10105487e60f" />

✨在antigravity里用claude大小姐的可以再装上这套。带暗号格式的表情包压缩包。完整下载本压缩包后，不要解压，可以直接丢压缩包到antigravity里说“帮我装到agy-meme里”。或者手动在侧边栏导入。

## 选图和回图

在聊天中说「打开 agy-meme 图库」，或从会话侧栏的插件菜单打开「🐱 表情图库」。搜索名称或按分类筛选。点图会复制暗号，粘贴到聊天草稿中即可继续配字。若剪贴板不可用，复制面板里选中的文字。基咪可以查询暗号含义，也可以直接用本机图片地址回图。
<img width="1026" height="801" alt="Antigravity_IR4tHXZ1sO" src="https://github.com/user-attachments/assets/4d5a8c34-1f24-4960-8f2b-896959a5e800" />
 
## 对话框底栏（*推荐*）

安装图库后，完全退出 Antigravity 2.34.0，双击 install-desktop.bat，再打开应用。包含 🐱 底栏、个人图库同步、用户气泡暗号渲染和 136 像素 AI 贴图样式。已有同版底栏可以沿用。卸载底栏时完全退出应用并运行 uninstall-desktop.bat。其他版本和平台仅安装图库。已有桌面底栏补丁的用户仍可用附件旁的选择器发送内置表情。独立插件提供图库侧栏和 AI 工具。仅安装图库时，用户气泡里的暗号按客户端默认方式显示。侧栏需要支持 MCP Apps 的桌面版本（2.34.0 起）。
以后客户端升级后，如果猫头消失，完全退出 Antigravity → 双击同一份 install-desktop.bat → 重新打开即可。安装器会检查底栏、草稿编辑器、用户气泡和 AI 图片卡片。只要这些组件仍兼容，就可以继续用这份 ZIP；检测失败时会指出原因，并保留原应用包。

<img width="610" height="478" alt="J1DUbV3wEo" src="https://github.com/user-attachments/assets/27a90b25-ef2d-470d-84f0-7a88c31822ef" />

## 收图与分享

在图库点「添加表情」，选 PNG、JPEG、GIF 或 WebP，填名称、分类和含义。单张最大 8 MiB。也可在聊天中指明图片并要求收藏；客户端需向基咪提供可读取的本地路径。如果只有聊天缩略图，请用图库选择原文件。收藏后即可搜索并让基咪回图。

<img width="351" height="389" alt="Antigravity_X5jxYO1ILD" src="https://github.com/user-attachments/assets/b9f2380a-101f-4e23-931d-d7489ccc6dce" />

点「导出个人图包」得到本机 ZIP 路径，把 ZIP 发给朋友即可。接收方在图库点「导入图包」。超过 8 MiB 时，让基咪用本机 ZIP 路径导入；单包最大 64 MiB。相同名字和图片重复导入会跳过，同名异图会取消整次导入。

Windows 双击 `uninstall.bat`，macOS 或 Linux 运行 `sh uninstall.sh`。升级和卸载均保留个人图库。数据保存在宿主提供的插件数据目录，独立运行时使用 `~/.gemini/config/agy-meme-data`。

本机桌面样式把 agy-meme 的 AI 回复图限制在 136 × 136 像素内，保留长宽比。图库工具直接返回原图，并在 Markdown 中加入识别标记。独立插件安装只安装图库；桌面样式随本机底栏适配加载。

## 删除个人表情

在 🐱 图库的自定义表情下点「删除」，核对名称后确认。也可告诉基咪「删除我收藏的『表情名』」。MCP 工具 delete_sticker 按完整名称操作。删除后搜索、选择器与后续图包导出会移除该条目。历史回复已引用的本地图片和以前导出的 ZIP 保留。


## 致谢与来源 (Credits & Acknowledgements)

- **功能灵感与架构参考**：[yyh-001/dsh-meme](https://github.com/yyh-001/dsh-meme)
- **内置哈基米表情包来源**：[Bilibili (BV1F34G6BEVA)](https://www.bilibili.com/video/BV1F34G6BEVA)
- **claude表情包来源**：[Bilibili (BV1nuxQ6EEoN)](https://www.bilibili.com/video/BV1nuxQ6EEoN)
- **哈基米（Gemini）人设原案**：**zipzippipe**

本项目代码100%AI，0%人类。
