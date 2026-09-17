# Vite 8 Reference

> SDK: `vite@8.0.10`
> Minimum Node version: Node.js `20.19+` or `22.12+`
> Sources: [Vite Getting Started](https://vite.dev/guide/), [Vite CLI](https://vite.dev/guide/cli), [Server Options](https://vite.dev/config/server-options), [Build Options](https://vite.dev/config/build-options), [Static Deploy](https://vite.dev/guide/static-deploy)

---

## 1. Installation and scripts

Install Vite as a development dependency and expose the standard commands:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "devDependencies": {
    "vite": "8.0.10"
  }
}
```

`vite preview` is only for checking a production build locally. It is not a production server.

## 2. Static HTML and custom root

Vite serves plain HTML without requiring a UI framework. Set `root` when the HTML source is outside the package directory:

```js
import { defineConfig } from 'vite'

export default defineConfig({
  root: 'design/presentation',
})
```

Any HTML file under the root is directly addressable. A root request normally expects `index.html`; an existing named HTML artifact can instead be exposed through an explicit route rewrite. If the build has no `index.html`, configure the named HTML as the build input.

## 3. Development server

```js
export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 5174,
    strictPort: true,
  },
  preview: {
    host: '0.0.0.0',
    port: 4173,
    strictPort: true,
  },
})
```

- `0.0.0.0` listens on every interface and is suitable for WSL, containers, and remote workspaces.
- `strictPort: true` fails when the configured port is busy instead of silently choosing a different address.
- Preview has separate settings and defaults to port `4173`.
- Do not set `server.allowedHosts` to `true`; allow only explicit trusted hostnames when custom hosts are required.

Listening on every interface does not itself publish a container port. The host environment must still forward or expose that port.

## 4. Build and preview

Vite 8 accepts HTML build inputs through `build.rolldownOptions.input`. Keep `outDir` dedicated to generated files, especially when it is outside `root`, because `emptyOutDir` removes existing output contents.

```bash
bun run build
bun run preview
```

Use `base: './'` only when a build must use location-independent relative asset paths.

## 5. Operational checks

- Prefer HTTP preview over opening the HTML with `file://`; modules and absolute paths behave differently.
- Keep the server process running while reviewing the page.
- Check the actual listening address and port when the browser cannot connect.
- Binding to `0.0.0.0` can expose the development server to a trusted LAN; never expose it directly to the public internet.
- Changing `root` changes the meaning of absolute asset paths and the default public directory.

## Project Notes

<!-- Auto-appended by fetch-sdk skill. Lessons learned during implementation. -->
- 2026-09-17: The game keeps the authoritative prototype at `design/presentation/叙事界面原型.html`; `web/vite.config.js` rewrites `/` to that source instead of copying it.
- 2026-09-17: This host resolves `localhost` to IPv6 loopback. The game therefore mirrors the working `ev-logistics` listener and uses `localhost:5174` with `strictPort`; `5174` avoids its long-running server on `5173`.
