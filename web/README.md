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

当前页面是交互原型，不连接游戏后端或 Unity StoryEngine；加入 Vite 只解决稳定托管、热更新和宿主浏览器访问。

页面左上角的“开局人物”入口提供五屏角色创建预览：48 段去重经历、0–10 属性结算、疾病候选、疾病选择与镜子总结。每段经历的原始属性净值固定为 +2，支持 `+2`、`+1/+1` 与少量 `+3/−1`；属性页为五项属性的五个程度分别显示“能做什么、做到什么程度”，卡片顶部保留插画空位。经历未选满时也可查看后续屏，界面会持续提示剩余数量。经历卡的“负担”文案仍是**未接入游戏的原型提案**，与已实际结算的属性 `−1` 不同。规则镜像位于 `src/character-creation/`，来源是 `design/entities/疾病特长.md` §二—§六；疾病可选数量等未决项只在界面标注，不由 Web 原型代替设计定案。疾病结算后的面具外观整理已写入设计，但因低优先级且尚无美术/物理依赖，本 Web 原型暂时仍停在镜子总结页。

同一区域的“显示设置”可把本地显示亮度调到 70%–140%，选择保存在浏览器本地；它不改变 Three/Unity 场景灯光参数。

## Unity Web 阶段 A

Unity 生成物写入 `web/public/unity/`，该目录不入库。Vite 会把它以 `/unity/` 暴露，并在生产构建时复制到 `web/dist/unity/`。Unity Editor 中执行菜单 `YANTF → Web → 构建阶段 A 到 web/public/unity` 后，网页宿主从 `/unity/manifest.json` 读取带哈希或压缩后缀的实际文件名。

`web/src/scene-host/` 是网页与三维运行时之间的唯一接缝；页面代码不得直接持有 Unity 实例或调用 `SendMessage`。
