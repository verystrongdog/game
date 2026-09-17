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
  root: presentationRoot,
  cacheDir: resolve(import.meta.dirname, 'node_modules/.vite'),
  publicDir: false,
  appType: 'mpa',
  plugins: [narrativePrototypeEntry()],
  resolve: {
    // FBXLoader/controls use the package-style `three` specifier. Keep them on
    // the same vendored module as the page instead of adding a second copy.
    alias: {
      three: resolve(presentationRoot, 'vendor/three/build/three.module.js'),
    },
  },
  server: {
    // Match ev-logistics: the host browser resolves localhost to IPv6 loopback.
    host: 'localhost',
    port: 5174,
    strictPort: true,
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
      input: resolve(presentationRoot, prototypeFile),
    },
  },
})
