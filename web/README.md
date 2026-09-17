# 叙事 Web UI 本地预览

这里提供与 `ev-logistics/web` 相同的 Vite 本地开发服务器入口，但不复制页面内容。Vite 直接托管设计权威文件 `design/presentation/叙事界面原型.html`，并把根路径 `/` 重写到该页面。

## 启动

```bash
cd web
bun install
bun run dev
```

浏览器打开 <http://localhost:5174/>。服务器沿用电车项目的宿主访问方式，监听 `localhost`（本机实际解析为 IPv6 回环 `[::1]`）；端口被占用时直接报错，不会静默切换地址。`5174` 刻意避开电车项目前端使用的 `5173`，两个项目可以同时运行。

## 构建与预览

```bash
bun run build
bun run preview
```

构建结果写入 `web/dist/`（不入库），预览地址为 <http://localhost:4173/>。

当前页面是交互原型，不连接游戏后端或 Unity StoryEngine；加入 Vite 只解决稳定托管、热更新和宿主浏览器访问。
