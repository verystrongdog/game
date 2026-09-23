# 叙事 Web UI 本地预览

这里提供与 `ev-logistics/web` 相同的 Vite 本地开发服务器入口，但不复制页面内容。Vite 直接托管设计权威文件 `design/presentation/叙事界面原型.html`，并把根路径 `/` 重写到该页面。

## 启动

```bash
cd web
bun install
bun run dev
```

服务器监听远端 `127.0.0.1:8899`，端口被占用时直接报错，不会静默切换地址。当 Windows 端使用以下 SSH 隧道时：

```powershell
ssh -N -L 8901:127.0.0.1:8899 chen@100.74.30.71
```

浏览器打开 <http://127.0.0.1:8901/>。

## 构建与预览

```bash
bun run build
bun run preview
```

构建结果写入 `web/dist/`（不入库），预览地址为 <http://localhost:4173/>。

## 公网预览（GitHub Pages）

<https://verystrongdog.github.io/game/> —— 直接点开即可，不需要本机进程，也不需要 SSH 隧道。

- 发布物**只有 `web/dist`**：原型页、打包后的 JS/CSS，以及 `public/` 原样复制的资源（含 `hospital-floor/models` 的 AWS RoboMaker 模型与其 LICENSE/NOTICE）。`design/`、`data/` 的源文档不进站点。
- 由 [`.github/workflows/pages.yml`](../.github/workflows/pages.yml) 在 push 到 `main` 时构建并部署，也可在 Actions 页面手动触发（`workflow_dispatch`）。**它不是门禁**：只在 `main` 上跑，失败不拦任何 PR。
- 项目站点挂在 `/game/` 子路径，构建必须带 `PAGES_BASE=/<repo>/`（workflow 用仓库名拼出），否则打包出的 `/assets/*` 会指到域名根而整页 404。页面里的运行时资源路径同样跟随该 base，见 `src/hospital/floor-config.js`。
- GitHub Pages 用 `dist/index.html` 作目录索引，而构建产物只有中文名的 `叙事界面原型.html`，故构建后由 `scripts/make-pages-index.mjs` 复制一份 `index.html`。
- **不发布** Unity Web 阶段 A 的产物（`web/public/unity/` 不入库）：公网页面请求 `/unity/manifest.json` 会 404，表现与本机没跑过 Unity 构建时一致。
- 仓库 Settings → Pages 的 Source 需选 “GitHub Actions”；否则部署 job 会在 `deploy` 步骤失败。

本机复现同一产物（不需要 GitHub）：

```bash
cd web
PAGES_BASE=/game/ npm run build:pages     # 等价于 workflow 的构建步骤
PAGES_BASE=/game/ npx vite preview        # 在 http://localhost:4173/game/ 下按子路径查看
```

当前页面是交互原型，不连接游戏后端或 Unity StoryEngine；加入 Vite 只解决稳定托管、热更新和宿主浏览器访问。

页面左上角的“开局人物”入口提供五屏角色创建预览：48 段去重经历、0–10 属性结算、疾病候选、疾病选择与镜子总结。每段经历的原始属性净值固定为 +2，支持 `+2`、`+1/+1` 与少量 `+3/−1`；属性页为五项属性的五个程度分别显示“能做什么、做到什么程度”，卡片顶部保留插画空位。经历未选满时也可查看后续屏，界面会持续提示剩余数量。经历卡的“负担”文案仍是**未接入游戏的原型提案**，与已实际结算的属性 `−1` 不同。规则镜像位于 `src/character-creation/`，来源是 `design/entities/疾病特长.md` §二—§六；疾病可选数量等未决项只在界面标注，不由 Web 原型代替设计定案。疾病结算后的面具外观整理已写入设计，但因低优先级且尚无美术/物理依赖，本 Web 原型暂时仍停在镜子总结页。

同一区域的“显示设置”可把本地显示亮度调到 70%–140%，选择保存在浏览器本地；它不改变 Three/Unity 场景灯光参数。

## 一层地图：房间描述与开局人物

来源：[一层跑团地图原型 §2.2—§2.4](../design/presentation/500%E5%BA%8A%E4%B8%80%E5%B1%82%E8%B7%91%E5%9B%A2%E5%9C%B0%E5%9B%BE%E5%8E%9F%E5%9E%8B.md)。这三层都是**原型占位，不是正典**：

- **点击闭环 → 右侧对话框显示描述**。描述由 `src/hospital-map-prototype/room-description.js` 按几何自动生成（面积、包围盒长短边、长宽比、顶点数），分类为长走道 / 大跨空间 / 短通道 / 标准房间模块 / 常规房间 / 小房间 / 极小围合。**不含房间名称与用途**，对话框把“几何事实 / 依据 / 尚未确定”分开列出。189 个闭环的几何读数见设计文档 §2.2。
- **开局人物在对应位置**。`src/hospital-map-prototype/npc-placements.js` 把有对话数据的五位（郑晓敏 · 谭丽娟 · 吴桐 · 周卫国 · 唐念安）按 [NPC 生态台账](../design/spec/material/NPC%E7%94%9F%E6%80%81%E5%8F%B0%E8%B4%A6.md) 的驻地落到闭环上，并按上午 / 下午 / 夜晚分别落位；标记随右侧时段切换而移动。落位是占位，`basketball_court` 没有几何候选，已登记在 `unmappedLocations`。
- **点人物 → 开局那套对话浮层**。`src/map-dialogue/dialogue-overlay.js` 只调用对话运行时的 `selectNpc` / `choose` / `leave` / `subscribe`，与右侧叙事面板共用同一份状态，不自己判断条件。⚠️ 一层还没有玩家坐标，因此原型不做“同地点才能交谈”的距离判定，这条也写在浮层界面上。

验证：`bun test` 覆盖分类判据、活动文案与人物数据的逐字一致、落位与闭环/人物的引用完整性。

## Unity Web 阶段 A

Unity 生成物写入 `web/public/unity/`，该目录不入库。Vite 会把它以 `/unity/` 暴露，并在生产构建时复制到 `web/dist/unity/`。Unity Editor 中执行菜单 `YANTF → Web → 构建阶段 A 到 web/public/unity` 后，网页宿主从 `/unity/manifest.json` 读取带哈希或压缩后缀的实际文件名。

`web/src/scene-host/` 是网页与三维运行时之间的唯一接缝；页面代码不得直接持有 Unity 实例或调用 `SendMessage`。
