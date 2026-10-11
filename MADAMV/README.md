# 视频检索（MADAMV）

简约美观的 MAD / AMV 视频收藏页：支持 B 站链接展示、标题/标签检索、自定义背景、头像和顶部文字轮播。

## 🚀 在线部署（GitHub Pages，自动更新）

### 第一次上传
1. **注册 GitHub**：打开 https://github.com 注册账号（免费）
2. **新建仓库**：点右上角 `+` → New repository
   - 仓库名任意（如 `MADAMV`）
   - 设为**公开**
   - 勾选 `Add a README file`（可选）
3. **上传本文件夹的全部文件**，把仓库变成这样：
   ```
   (仓库)
   ├── index.html
   ├── videos.json
   ├── settings.json
   ├── server.py
   ├── css...（如有）
   └── .github/workflows/deploy.yml
   ```
   可通过网页端逐个上传，或用桌面客户端 GitHub Desktop 拖拽整个文件夹。
4. **启用 Pages**：仓库 `Settings` → 左侧 `Pages`
   - Source 选 **GitHub Actions**
5. 等待 1~2 分钟，站点地址为：
   `https://你的用户名.github.io/仓库名/`

### 以后每次修改
- **网页在线改**：直接在 GitHub 仓库网页里点开文件 → 铅笔图标编辑 → Commit changes，站点**自动重新部署**，无需任何操作
- **本地改完同步**：用 GitHub Desktop 或 `git push`，也自动更新

> 在线版本说明：GitHub 上无法运行 Python 后端，因此新增视频、图片上传、设置保存会存在**浏览器本地**（换浏览器会丢失）；本地运行的完整功能版本（含 B 站自动抓取封面标题）见下方。

## 💻 本地运行（完整功能版）

需要电脑安装 Python（https://www.python.org 下载勾选 Add to PATH）。

- 方式一：双击 `启动网站.bat`，浏览器自动打开
- 手动：在本目录打开命令行执行 `python server.py`，访问 http://127.0.0.1:8080/

本地版功能：
- ✅ 粘贴 B 站链接自动抓取标题、封面
- ✅ 新增视频永久保存到 videos.json
- ✅ 背景图、头像支持本地上传，永久保存

## 🎨 个性化功能（⚙ 个性化按钮）

- **🎬 视频管理**：添加 B 站视频（链接、标题、封面）
- **🎨 外观设置**：
  - 背景图片（上传/链接）+ 透明度滑块
  - 左上角头像（上传/链接）
  - 顶部文字行：每行一句，自动淡入淡出轮播，显示时长随文字长度变化

## 📁 文件说明

| 文件 | 作用 |
|---|---|
| index.html | 主页面（含全部样式和逻辑） |
| videos.json | 视频数据 |
| settings.json | 个性化设置（背景/头像/文字） |
| server.py | 本地服务器（B站抓取/保存/上传接口） |
| 启动网站.bat | Windows 一键启动 |
| .github/workflows/deploy.yml | GitHub 自动部署配置 |
| uploads/ | 本地上传的图片 |

## 🛠️ 常见问题

**Q：在线版封面裂图？**
有些图床防盗链，网页已用 `no-referrer` 尽量避免；若仍裂图可在视频管理中重新填写封面链接。

**Q：在线版添加的视频保存到哪里？**
浏览器 localStorage，仅当前浏览器可见。长期保存请本地运行（写入 videos.json），或编辑仓库里的 videos.json 后提交。

**Q：怎么删除视频？**
本地版：编辑 videos.json 删掉对应条目；在线版：当前只有新增功能，删除需编辑仓库 videos.json（或用浏览器 F12 清 localStorage）。