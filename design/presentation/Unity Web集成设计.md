# Unity Web 集成设计

> 《子非鱼》浏览器版的呈现架构：Unity Web 负责左侧三维世界，HTML 负责右侧叙事界面，两者通过单一消息接缝协作。本文只定义呈现集成，不新增剧情状态、结算规则或正式玩家行为。

## 一、结论与范围

最终发布形态是浏览器游戏，不以 Windows `Unity.exe` 作为主产品。Unity 是三维场景、人物动画、移动与空间交互的运行时；现有 HTML 是叙事历史、回应选项和笔记的运行时。两者共同存在于同一网页中，继续遵守[叙事界面布局 §二](叙事界面布局.md)的“左侧世界、右侧叙事流”。

本设计决定：

- Unity Web Canvas 只占据左侧世界区域，不渲染右侧叙事栏；
- HTML 不再实现人物骨架、动作重定向、碰撞或三维相机；
- Unity 不复制右侧对话排版、滚动历史或笔记页签；
- 网页与 Unity 之间只有一个消息接缝，不允许页面脚本散落调用任意 GameObject；
- `ActionLab` 保留为动作基准场，不直接作为最终 Web 场景；
- 当前 Three.js 世界是迁移适配器，Unity Web 达到验收条件后整体删除，不长期维护两套三维实现。

本文不决定：

- 正式医院关卡的空间布局；
- StoryEngine 尚未确定的数据字段；
- 对话节点、检定结果或数值结算；
- 战斗界面进入浏览器版后的最终组合方式。

## 二、必须保持的不变量

### 2.1 设计与逻辑所有权

依赖方向继续遵守[架构 §一—§二](../../ARCHITECTURE.md)：设计是唯一真相源，`code/src/` 是规则结算的唯一实现，`code/unity/` 是呈现沙盘。Unity Web 改变发布载体，不改变逻辑所有权。

因此：

- HTML 发送“玩家选择了哪个选项”，不得自行判定选项后果；
- Unity 可以检测角色靠近某个可交互物，不得自行生成正式剧情结论；
- StoryEngine 接入后，由 Core 返回新的只读视图模型，再由 HTML 渲染；
- 原型期的静态文本继续标为非正典，不因进入 Unity Web 而转为正式内容。

### 2.2 单一状态所有者

| 状态 | 唯一所有者 | 其他侧可见形式 |
|---|---|---|
| 角色位置、朝向、碰撞、当前动作 | Unity | 只读事件或调试快照 |
| 相机、灯光、空间热点、交互距离 | Unity | 交互焦点事件 |
| 对话历史的排版、滚动位置、当前页签 | HTML | 不回写 Unity |
| 当前选项及其可用性 | StoryEngine（接入前为静态原型） | HTML 只读视图模型 |
| 选择产生的规则结果 | Core / StoryEngine | Unity 和 HTML 分别消费结果 |
| 输入焦点（世界或界面） | Web Host | 同步为 Unity 输入模式 |

任何状态不得由 HTML 与 Unity 同时写入。跨侧消息表达事实或意图，不复制一个长期可变对象。

## 三、运行时结构

```text
浏览器页面
├── HTML Narrative UI
│   ├── 叙事历史
│   ├── 回应选项
│   └── 笔记页
│
├── SceneHost 模块                         ← 唯一网页接缝
│   ├── UnityWebAdapter                    ← 最终适配器
│   └── ThreePrototypeAdapter              ← 迁移期适配器，验收后删除
│
└── Unity Web Canvas
    ├── NarrativeWebScene                  ← Web 专用场景
    ├── WebPresentationBridge 模块         ← 唯一 Unity 接缝
    ├── X Bot / Animator / ActionPlayer
    ├── 移动、碰撞、相机、空间交互
    └── Core / StoryEngine Adapter         ← 后续接线，不在首个切片伪造
```

`SceneHost` 是网页侧的深模块：它隐藏 Unity Loader、构建路径、加载进度、Canvas 尺寸、焦点恢复、错误显示和消息序列化。页面其他代码不需要知道 `createUnityInstance`、GameObject 名称或 `.wasm` 文件位置。

`WebPresentationBridge` 是 Unity 侧的深模块：它隐藏浏览器平台条件、JSON 解析、主线程派发、JavaScript 插件调用和错误隔离。场景脚本不直接调用浏览器函数。

现有 Three.js 原型与 Unity Web 是两个真实适配器，因此 `SceneHost` 接缝不是为假想替换点预留。Unity 版本通过验收后删除 Three.js 适配器，接缝仍负责加载、焦点、消息和错误处理。

## 四、模块接口

### 4.1 网页侧 `SceneHost`

页面只学习以下接口：

```js
const session = await sceneHost.mount({ container, build });
session.dispatch(message);
const unsubscribe = session.subscribe(message => render(message));
await session.dispose();
```

接口约束：

- `mount` 在 Canvas 可接收消息后才完成；加载进度通过宿主状态呈现；
- `dispatch` 接受结构化消息，不接受 GameObject 名称与方法名；
- `subscribe` 按 Unity 发出顺序交付消息；监听者异常不得中断后续消息；
- `dispose` 可重复调用，必须释放监听、Canvas 与 Unity 实例；
- 同一容器同时最多存在一个会话；重复挂载先明确失败，不静默创建第二个 Unity 实例。

### 4.2 Unity 侧 `WebPresentationBridge`

Unity 暴露一个入站方法并使用一个出站通道：

```csharp
public void Receive(string envelopeJson);
```

```text
Emit(envelopeJson)  // Unity → JavaScript，由 Web 平台适配器实现
```

接口约束：

- `Receive` 只负责校验、解析与路由，不包含具体剧情或动作判断；
- 未知消息类型返回结构化错误，不抛出到 Unity Player 循环；
- 非 Web 平台使用日志适配器，使场景仍可在 Editor 中运行；
- 出站消息必须在 Unity 主线程产生并保持顺序；
- 场景脚本通过桥内部的类型化命令与事件工作，不自行拼 JSON。

## 五、消息信封与首个消息集

所有跨侧消息使用同一个信封：

```json
{
  "v": 1,
  "kind": "command",
  "type": "input.mode.set",
  "requestId": "optional-correlation-id",
  "payload": {}
}
```

字段语义：

| 字段 | 规则 |
|---|---|
| `v` | 协议版本；不支持时显式拒绝 |
| `kind` | `command`、`event`、`snapshot` 或 `error` |
| `type` | 稳定的点分名称，不使用 C# 类名或 GameObject 名称 |
| `requestId` | 需要关联回应时使用；普通连续事件可省略 |
| `payload` | 该消息的最小数据；不得塞入整个 Unity 场景状态 |

首个集成切片只实现以下消息：

| 方向 | `type` | 用途 |
|---|---|---|
| Unity → HTML | `runtime.ready` | Canvas、场景和桥都已可用 |
| Unity → HTML | `runtime.error` | 可恢复或不可恢复的运行时错误 |
| Unity → HTML | `interaction.focus.changed` | 当前可交互对象及提示发生变化 |
| Unity → HTML | `interaction.activated` | 玩家在世界中确认了一次交互 |
| HTML → Unity | `input.mode.set` | 在 `world` 与 `ui` 输入模式间切换 |
| HTML → Unity | `dialogue.choice.selected` | 传递选择意图；首个切片只回显，不判定正式结果 |

首个切片不加入传送、任意 Animator 状态切换或任意方法调用。这些能力会把小接口扩成远程控制台，破坏状态所有权。

## 六、输入、焦点与生命周期

### 6.1 输入模式

Web Host 维护两种输入模式：

- `world`：Canvas 获得键盘焦点，Unity 接收移动、跳跃与场景交互；
- `ui`：回应、笔记或文本控件获得焦点，Unity 清空持续输入并停止读取游戏快捷键。

模式切换必须显式发送 `input.mode.set`。仅调用 DOM `focus()` 不足以成为游戏状态，因为浏览器焦点可能因页签切换、弹窗或触控输入变化。

### 6.2 启动序列

```text
HTML 壳出现
  → SceneHost 显示真实加载进度
  → createUnityInstance
  → NarrativeWebScene 完成装配
  → WebPresentationBridge 发 runtime.ready
  → SceneHost 进入 world 模式
  → 玩家获得控制
```

若 Unity 构建不存在或启动失败，右侧叙事界面仍应可读，左侧显示明确错误与重试入口；不得无限停留在“正在加载”。

### 6.3 会话结束

页面卸载、开发热更新或显式重启场景时统一调用 `dispose`。旧会话产生的迟到事件必须丢弃，不能写入新会话的叙事历史。

## 七、场景与资产策略

### 7.1 新建 Web 专用场景

新增 `NarrativeWebScene`，只复用经过验证的模块：

- X Bot 人物与 Humanoid Avatar；
- `ActionPlayer` 及已经接线的动作；
- `ActionLabDriver` 中可复用的移动口径，但正式场景应使用面向探索的装配，不继承调试按键与 IMGUI；
- 等距正交相机的跟随原则；
- 医院场景、护士和空间热点的 Web 呈现资产。

不得把 `ActionLab.unity` 改造成正式关卡。它继续用于动作状态、Root Motion、IK 和交互实验，避免呈现需求污染动作基准。

### 7.2 生成物与源码目录

计划目录：

```text
code/unity/Assets/Scripts/Web/                 Unity 桥与 Web 场景装配源码
code/unity/Assets/Plugins/WebGL/                Unity → JavaScript 平台适配器
code/unity/Assets/WebGLTemplates/ZhiFeiYu/      可追踪的自定义模板源码
code/unity/Assets/Scenes/NarrativeWebScene.unity
web/src/scene-host/                              网页宿主模块与适配器
web/public/unity/                                Unity 构建生成物，不入库
```

Unity 构建生成物不作为源码提交；部署流程把它与 Vite 产物组合。服务器的 MIME、压缩编码和可选多线程响应头遵守[Unity 6 Web 参考](../../docs/reference/unity-webgl.md)。

## 八、构建与托管策略

首个可运行切片采用保守配置：

- 不启用 WebAssembly 多线程；只有性能测量证明需要时才承担跨源隔离配置；
- 保留数据缓存；
- 开发构建显示可诊断错误，发布构建再开启尺寸优化；
- Vite 继续作为本地统一入口，页面不要求用户分别启动两个服务；
- Unity Loader 的路径由构建清单提供，不在 HTML 中散落文件名；
- 压缩格式与服务器 `Content-Encoding` 必须成对验证。

当前 `ProjectSettings.asset` 已存在 Web 平台配置，但尚未把默认模板、内存值或压缩值视为已验收参数。首个真实构建应记录产物大小、启动时间、峰值内存和浏览器控制台错误，再决定发布配置。

## 九、迁移阶段

### 阶段 A：最小宿主

- 建立 `SceneHost` 与 `WebPresentationBridge`；
- Unity Web 只加载空的 `NarrativeWebScene`，完成 `runtime.ready` 往返；
- Vite 页面显示真实进度、错误和重试；
- Three.js 原型仍为默认适配器。

### 阶段 B：世界替换

- 在 `NarrativeWebScene` 复用 X Bot、正式 Idle/Walk/Run/Jump 与等距相机；
- 加入护士站最小几何、护士与一个交互热点；
- Unity 适配器成为默认，Three.js 只保留回退开关。

### 阶段 C：交互闭环

- Unity 发出交互焦点与确认事件；
- HTML 回应选项切换输入模式并发送选择意图；
- 场景视觉反馈由 Unity 消费呈现命令；
- Three.js 适配器及其 FBX Web 重定向代码删除。

### 阶段 D：StoryEngine 接线

- 使用 `code/src/` 的 Unity 兼容桥接面；
- HTML 改为渲染只读视图模型；
- 删除原型静态剧情响应；
- 形成“输入意图 → Core 判定 → 双侧呈现”的单向数据流。

## 十、阶段 A 验收条件

1. 一个页面地址同时呈现左侧 Unity Canvas 与右侧 HTML 叙事栏。
2. 页面只通过 `SceneHost` 使用 Unity，不直接出现 `SendMessage(GameObject, method, value)` 调用。
3. `runtime.ready` 在每个会话只被接受一次，重复或旧会话事件不会污染当前页面。
4. 点击右侧界面后 Unity 停止读取移动输入；返回场景后可恢复。
5. Unity 构建缺失、加载失败或协议不兼容时，页面显示明确错误并可重试。
6. `ActionLab` 的场景、控制器和动作验证用途不被修改。
7. Unity 生成物不进入 Git，源码、模板和接口测试进入 Git。
8. Vite 开发与生产构建都能定位 Unity 产物，生产构建不存在本机绝对路径。

阶段 A 只证明集成接缝成立，不证明正式关卡、正式剧情或性能目标已经完成。

---
*创建: 2026-09-17 · 状态: 设计基线，尚未形成 Unity Web 可运行构建*
*关联: [叙事界面布局](叙事界面布局.md), [动作库规格](动作库规格.md), [架构](../../ARCHITECTURE.md), [Unity Web 参考](../../docs/reference/unity-webgl.md)*
