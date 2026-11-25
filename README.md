# 🐱 agy-meme

Antigravity 的独立表情图库。随包附 64 张哈基米原图、原比例兼容副本和预览图。

## 安装

解压整个压缩包。Windows 双击 `install.bat`，macOS 或 Linux 在插件目录运行 `sh install.sh`。需要 Python 3.8 或更新版本，以及 Antigravity 桌面端。安装位置是当前用户的 `~/.gemini/config/plugins/agy-meme`。重新打开「自定义项 → 已安装」，必要时重启 Antigravity，启用 agy-meme。插件的 MCP 服务通过 Node 启动，Antigravity 2.34.0 支持使用应用内置 Node。

## 选图和回图

在聊天中说「打开 agy-meme 图库」，或从会话侧栏的插件菜单打开「🐱 表情图库」。搜索名称或按分类筛选。点图会复制暗号，粘贴到聊天草稿中即可继续配字。若剪贴板不可用，复制面板里选中的文字。基咪可以查询暗号含义，也可以直接用本机图片地址回图。

已有桌面底栏补丁的用户仍可用附件旁的选择器发送内置表情。独立插件提供图库侧栏和 AI 工具。仅安装图库时，用户气泡里的暗号按客户端默认方式显示。侧栏需要支持 MCP Apps 的桌面版本（2.34.0 起）。

## 收图与分享

在图库点「添加表情」，选 PNG、JPEG、GIF 或 WebP，填名称、分类和含义。单张最大 8 MiB。也可在聊天中指明图片并要求收藏；客户端需向基咪提供可读取的本地路径。如果只有聊天缩略图，请用图库选择原文件。收藏后即可搜索并让基咪回图。

点「导出个人图包」得到本机 ZIP 路径，把 ZIP 发给朋友即可。接收方在图库点「导入图包」。超过 8 MiB 时，让基咪用本机 ZIP 路径导入；单包最大 64 MiB。相同名字和图片重复导入会跳过，同名异图会取消整次导入。

Windows 双击 `uninstall.bat`，macOS 或 Linux 运行 `sh uninstall.sh`。升级和卸载均保留个人图库。数据保存在宿主提供的插件数据目录，独立运行时使用 `~/.gemini/config/agy-meme-data`。

本机桌面样式把 agy-meme 的 AI 回复图限制在 136 × 136 像素内，保留长宽比。图库工具直接返回原图，并在 Markdown 中加入识别标记。独立插件安装只安装图库；桌面样式随本机底栏适配加载。

## 删除个人表情

在 🐱 图库的自定义表情下点「删除」，核对名称后确认。也可告诉基咪「删除我收藏的『表情名』」。MCP 工具 delete_sticker 按完整名称操作。删除后搜索、选择器与后续图包导出会移除该条目。历史回复已引用的本地图片和以前导出的 ZIP 保留。

## Windows 桌面底栏（可选）

安装图库后，完全退出 Windows 版 Antigravity，双击 install-desktop.bat，再打开应用。安装器会检查当前客户端的附件底栏、草稿编辑器、用户气泡和 AI 图片卡片。客户端更新后，可用同一份 ZIP 重新安装；重复运行达到目标状态时不会改写应用包。如果检测失败，安装器会列出原因。卸载用 uninstall-desktop.bat。桌面适配包含 🐱 选择器、个人收藏同步、用户暗号转图和 136 像素 AI 贴图样式。

## 致谢与来源 (Credits & Acknowledgements)

- **功能灵感与架构参考**：[yyh-001/dsh-meme](https://github.com/yyh-001/dsh-meme)
- **内置哈基米表情包来源**：[Bilibili (BV1F34G6BEVA)](https://www.bilibili.com/video/BV1F34G6BEVA)
- **哈基米（Gemini）人设原案**：**zipzippipe**
