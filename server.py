#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MADAMV 本地服务器（替代 python -m http.server）
- 提供静态文件服务
- /api/meta  根据 B 站链接抓取标题和封面
- /api/add   保存新视频到 videos.json

运行：python server.py  然后打开 http://127.0.0.1:8080/
"""
import base64
import json
import os
import re
import uuid
import urllib.parse
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

# 以脚本所在目录为工作目录，避免双击 bat 之外的目录启动时报错
os.chdir(os.path.dirname(os.path.abspath(__file__)))

videos文件 = "videos.json"
设置文件 = "settings.json"
图片上传目录 = "uploads"
B站接口 = "https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
请求头 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
}


def 提取BV号(链接):
    """从任意 B 站链接中提取 BV 号，找不到返回 None"""
    m = re.search(r"BV[0-9A-Za-z]{10}", 链接 or "")
    return m.group(0) if m else None


def 请求B站(bvid):
    """调用 B 站公开接口，返回标题、封面、规范化链接"""
    req = urllib.request.Request(B站接口.format(bvid=bvid), headers=请求头)
    with urllib.request.urlopen(req, timeout=10) as resp:
        数据 = json.loads(resp.read().decode("utf-8"))
    if 数据.get("code") != 0:
        raise ValueError(数据.get("message", "B 站接口返回异常"))
    info = 数据["data"]
    return {
        "title": info.get("title", ""),
        "cover": (info.get("pic") or "").replace("http://", "https://"),
        "url": "https://www.bilibili.com/video/" + bvid,
    }


def 读取视频列表():
    """读取 videos.json，文件不存在或损坏时返回空列表"""
    try:
        with open(videos文件, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def 保存视频(新视频):
    """追加一条新视频到 videos.json，自动分配 id"""
    列表 = 读取视频列表()
    最大id = max([v.get("id", 0) for v in 列表] or [0])
    新视频["id"] = 最大id + 1
    新视频["tags"] = []
    列表.append(新视频)
    with open(videos文件, "w", encoding="utf-8") as f:
        json.dump(列表, f, ensure_ascii=False, indent=4)
    return 新视频


默认设置 = {
    "background": {"image": "", "opacity": 0.65},
    "avatar": {"image": ""},
    "quotes": [],
}


def 读取设置():
    """读取 settings.json，不存在时返回默认设置"""
    try:
        with open(设置文件, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return json.loads(json.dumps(默认设置))


def 保存设置(新设置):
    """写入 settings.json"""
    with open(设置文件, "w", encoding="utf-8") as f:
        json.dump(新设置, f, ensure_ascii=False, indent=4)


图片扩展名 = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/gif": ".gif",
    "image/webp": ".webp",
}


def 保存上传图片(dataurl):
    """接收前端 FileReader 的 DataURL，保存到 uploads/ 并返回访问路径"""
    if "," not in dataurl:
        raise ValueError("图片数据格式不正确")
    头部, 数据 = dataurl.split(",", 1)
    mime = 头部.split(";")[0].replace("data:", "")
    扩展名 = 图片扩展名.get(mime, ".png")
    os.makedirs(图片上传目录, exist_ok=True)
    文件名 = "img_%s%s" % (uuid.uuid4().hex[:10], 扩展名)
    with open(os.path.join(图片上传目录, 文件名), "wb") as f:
        f.write(base64.b64decode(数据))
    return "/" + 图片上传目录 + "/" + 文件名


class 处理器(SimpleHTTPRequestHandler):
    def 返回JSON(self, 数据, 状态码=200):
        body = json.dumps(数据, ensure_ascii=False).encode("utf-8")
        self.send_response(状态码)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        路径 = urllib.parse.urlparse(self.path)
        if 路径.path == "/api/settings":
            self.返回JSON(读取设置())
            return
        if 路径.path == "/api/meta":
            查询 = urllib.parse.parse_qs(路径.query)
            url = (查询.get("url") or [""])[0]
            bvid = 提取BV号(url)
            if not bvid:
                self.返回JSON({"error": "无法识别 B 站链接，请粘贴完整的 bilibili 视频链接"}, 400)
                return
            try:
                self.返回JSON(请求B站(bvid))
            except Exception as e:
                self.返回JSON({"error": "获取失败：%s" % e}, 502)
            return
        super().do_GET()

    def do_POST(self):
        路径 = urllib.parse.urlparse(self.path)
        try:
            length = int(self.headers.get("Content-Length", 0))
            数据 = json.loads(self.rfile.read(length).decode("utf-8"))

            if 路径.path == "/api/settings":
                # 只保留已知字段，避免写入垃圾数据
                bg = 数据.get("background") or {}
                av = 数据.get("avatar") or {}
                quotes = 数据.get("quotes") or []
                if not isinstance(quotes, list):
                    quotes = []
                try:
                    背景透明度 = float(bg.get("opacity")) if bg.get("opacity") is not None else 0.65
                except (TypeError, ValueError):
                    背景透明度 = 0.65
                新设置 = {
                    "background": {
                        "image": (bg.get("image") or "").strip(),
                        "opacity": 背景透明度,
                    },
                    "avatar": {"image": (av.get("image") or "").strip()},
                    "quotes": [s.strip() for s in quotes if str(s).strip()],
                }
                保存设置(新设置)
                self.返回JSON({"ok": True})
                return

            if 路径.path == "/api/upload":
                dataurl = 数据.get("data") or ""
                if not dataurl:
                    self.返回JSON({"error": "缺少图片数据"}, 400)
                    return
                try:
                    url = 保存上传图片(dataurl)
                    self.返回JSON({"ok": True, "url": url})
                except Exception as e:
                    self.返回JSON({"error": "上传失败：%s" % e}, 400)
                return

            if 路径.path != "/api/add":
                self.send_error(404)
                return

            标题 = (数据.get("title") or "").strip()
            链接 = (数据.get("url") or "").strip()
            封面 = (数据.get("cover") or "").strip()
            if not 标题 or not 链接:
                self.返回JSON({"error": "标题和链接不能为空"}, 400)
                return
            新视频 = 保存视频({"title": 标题, "cover": 封面, "url": 链接})
            self.返回JSON({"ok": True, "video": 新视频})
        except Exception as e:
            self.返回JSON({"error": "保存失败：%s" % e}, 500)

    def log_message(self, fmt, *args):
        # 静默日志，避免控制台刷屏
        pass


if __name__ == "__main__":
    端口 = 8080
    try:
        服务器 = ThreadingHTTPServer(("127.0.0.1", 端口), 处理器)
    except OSError as e:
        print("启动失败：%s（端口 %d 可能被占用，关闭其他窗口后重试）" % (e, 端口))
        raise SystemExit(1)
    print("服务器已在 http://127.0.0.1:%d/ 启动" % 端口)
    print("请保持本窗口不要关闭，用完后按 Ctrl+C 退出。")
    try:
        服务器.serve_forever()
    except KeyboardInterrupt:
        print("\n已退出。")