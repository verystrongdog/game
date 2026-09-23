import { resolve } from 'node:path'
import { defineConfig } from 'vite'

const presentationRoot = resolve(import.meta.dirname, '../design/presentation')
const prototypeFile = '叙事界面原型.html'
const prototypeUrl = `/${encodeURIComponent(prototypeFile)}`

/**
 * Keep the design artifact in design/presentation while making `/` a stable,
 * browser-friendly entry point. The middleware changes only the request URL;
 * Vite still serves and watches the original HTML file directly.
 */
function narrativePrototypeEntry() {
  const rewriteRoot = (req, _res, next) => {
    if (req.url === '/' || req.url?.startsWith('/?')) {
      const query = req.url.includes('?') ? req.url.slice(req.url.indexOf('?')) : ''
      req.url = prototypeUrl + query
    }
    next()
  }

  return {
    name: 'yantf-narrative-prototype-entry',
    configureServer(server) {
      server.middlewares.use(rewriteRoot)
    },
    configurePreviewServer(server) {
      server.middlewares.use(rewriteRoot)
    },
  }
}

export default defineConfig({
  // 子路径托管（GitHub Pages 项目站点是 /<repo>/ 而不是 /）时由 PAGES_BASE 注入 base，
  // 否则打包出的 /assets/* 会指到域名根、整页 404。本地 dev/build 不设该变量，
  // base 仍为 '/'，行为与加这个字段之前完全一致。见 web/README.md「公网预览」。
  base: process.env.PAGES_BASE || '/',
  root: presentationRoot,
  cacheDir: resolve(import.meta.dirname, 'node_modules/.vite'),
  publicDir: resolve(import.meta.dirname, 'public'),
  appType: 'mpa',
  plugins: [narrativePrototypeEntry()],
  resolve: {
    // FBXLoader/controls use the package-style `three` specifier. Keep them on
    // the same vendored module as the page instead of adding a second copy.
    alias: {
      three: resolve(presentationRoot, 'vendor/three/build/three.module.js'),
      '/three-addons': resolve(import.meta.dirname, 'node_modules/three/examples/jsm'),
      '/hospital': resolve(import.meta.dirname, 'src/hospital'),
      '/hospital-map-prototype': resolve(import.meta.dirname, 'src/hospital-map-prototype'),
      '/scene-host': resolve(import.meta.dirname, 'src/scene-host'),
      '/character-creation': resolve(import.meta.dirname, 'src/character-creation'),
      '/opening-exploration': resolve(import.meta.dirname, 'src/opening-exploration'),
      '/dialogue': resolve(import.meta.dirname, 'src/dialogue'),
      '/prototype-bootstrap': resolve(import.meta.dirname, 'src/prototype-bootstrap'),
    },
  },
  server: {
    // SSH tunnel contract: client 127.0.0.1:8901 -> server 127.0.0.1:8899.
    host: '127.0.0.1',
    port: 8899,
    strictPort: true,
    fs: {
      // Presentation FBX symlinks resolve into code/unity; allow this repository
      // only, not the user's home directory.
      allow: [resolve(import.meta.dirname, '..')],
    },
  },
  preview: {
    host: 'localhost',
    port: 4173,
    strictPort: true,
  },
  build: {
    outDir: resolve(import.meta.dirname, 'dist'),
    emptyOutDir: true,
    rolldownOptions: {
      input: {
        narrative: resolve(presentationRoot, prototypeFile),
      },
    },
  },
})
