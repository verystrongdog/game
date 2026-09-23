// GitHub Pages 用 index.html 当目录索引，而本仓库构建产物只有一个中文名的原型页
// （design/presentation/叙事界面原型.html 编译成 dist/叙事界面原型.html）。这里再
// 复制一份同名内容的 index.html，使 https://<owner>.github.io/<repo>/ 能直接点开，
// 不必去记百分号转义后的长文件名。仅在构建之后运行（scripts.build:pages）。
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const webRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const distRoot = path.join(webRoot, 'dist')
const prototypeFile = '叙事界面原型.html'
const source = path.join(distRoot, prototypeFile)

if (!fs.existsSync(source)) {
  throw new Error(`构建产物里没有 ${prototypeFile}，请先跑 vite build（见 web/README.md「公网预览」）`)
}

const target = path.join(distRoot, 'index.html')
fs.copyFileSync(source, target)
console.log(`${path.relative(webRoot, target)} ← ${prototypeFile}`)
