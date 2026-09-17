# Unity 6 Web Reference

> Platform: `Unity 6 Web`
> Sources: [Web optimization: C# and Unity settings](https://docs.unity3d.com/Manual/web-optimization-c-sharp.html), [Node.js server configuration](https://docs.unity3d.com/Manual/web-server-config-nodejs.html), [Web Player memory](https://docs.unity3d.com/Manual/web-optimization-player.html), [System requirements](https://docs.unity3d.com/Manual/system-requirements.html), [JavaScript to Unity interaction](https://docs.unity3d.com/Manual/web-interacting-browser-js-to-unity.html), [Unity to JavaScript interaction](https://docs.unity3d.com/Manual/web-interacting-browser-unity-to-js.html), [Interacting with browser scripting example](https://docs.unity3d.com/Manual/web-interacting-code-example.html), [JavaScript plug-in interaction](https://docs.unity3d.com/Manual/web-interacting-browser-js.html), [Deprecated browser interaction API](https://docs.unity3d.com/Manual/web-interacting-browser-deprecated.html), [Web template structure](https://docs.unity3d.com/Manual/web-templates-structure.html), [Web templates introduction](https://docs.unity3d.com/Manual/web-templates-intro.html)

---

## 1. Custom HTML template and startup

Unity supports production-oriented custom JavaScript Web templates. A custom template can place the Unity canvas inside a real deployment page, use custom template variables, and connect the Unity player to other page elements through Unity's external-call interface.

The generated loader creates the player asynchronously:

```js
createUnityInstance(canvas, config, onProgress)
  .then((unityInstance) => {
    // Keep this instance where the page integration code can access it.
  })
  .catch((error) => {
    // Surface the startup error to the page.
  })
```

The resolved `unityInstance` is the browser page's handle to the Unity runtime. Store it in a scope available to the integration code when JavaScript must invoke engine-side functions. For Unity-to-page communication, use the external-call interface exposed by the custom Web template.

Do not build new integration code around the deprecated `unity.Instance` API; `createUnityInstance` is its replacement.

## 2. Server MIME types and compression headers

The deployment server must describe Unity build artifacts correctly. Use these MIME types:

| Asset | `Content-Type` |
| --- | --- |
| `.wasm` | `application/wasm` |
| `.js` | `application/javascript` |
| `.data`, `.bundle`, `.unityweb` | `application/octet-stream` |

When the build output is precompressed, send the matching `Content-Encoding` header:

- Brotli files: `Content-Encoding: br`
- gzip files: `Content-Encoding: gzip`

The Unity Node.js server example also demonstrates CORS handling. Treat response-header configuration as part of deployment rather than assuming that any static-file server will serve a compressed Unity build correctly.

## 3. WebAssembly multithreading headers

When WebAssembly multithreading is enabled, the server configuration must provide cross-origin isolation. Unity's server example applies the following values to HTML and JavaScript responses:

```http
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Embedder-Policy: require-corp
Cross-Origin-Resource-Policy: cross-origin
```

These headers affect the embedding page and its resources, so multithreading is a deployment-level choice, not only a Unity Player setting.

## 4. Data caching and build-size settings

Set `dataCaching = true` when the Unity Web build should cache its downloaded data locally. Unity's Web optimization guidance also lists the following size-oriented settings:

- IL2CPP: `Optimize Size`
- Managed Stripping Level: `High`
- `stripUnusedMeshComponents = true`
- Compression format: Brotli
- Exception Support: `None`
- Debug symbols: `Off`
- `wasm2023 = true`
- `DiskSizeLTO`

These are optimization controls, not substitutes for correct server headers. In particular, a Brotli build still requires the server to return the corresponding encoding and MIME metadata.

## 5. Memory and mobile browsers

Unity exposes `maximumMemorySize` for Web Player memory configuration. The documented upper limit is `4096 MB`.

Unity Web supports mobile browsers on Android and iOS. For iOS Safari, the documented minimum is version 15; Unity recommends 18.2 or newer because it provides a higher memory limit.

Do not treat the 4096 MB maximum as a target for mobile. Build size, runtime allocation, and the browser's practical memory ceiling still need to be tested on the intended devices.

## 6. Project application

For this project, use a custom Unity Web template as the integration seam:

- Mount the Unity canvas in the existing prototype's 3D scene region.
- Keep the narrative/dialogue controls as normal HTML elements outside the canvas.
- Retain the `unityInstance` returned by `createUnityInstance` as the JavaScript-to-Unity bridge; route Unity-to-HTML events through the template's external-call interface.
- Show loading progress and startup errors through the `onProgress`, `then`, and `catch` paths instead of leaving an opaque canvas.
- Enable `dataCaching` for the Unity payload and use a production server configured for the selected compression format and Unity MIME types.
- Start without WebAssembly multithreading unless the project needs it; if enabled later, deploy the COOP, COEP, and CORP headers together and verify the complete embedding page under cross-origin isolation.
- Test the actual iOS target explicitly, with iOS Safari 18.2+ as the preferred baseline, and keep memory usage conservative rather than raising `maximumMemorySize` by default.

## 7. JavaScript and C# interoperability

### Browser JavaScript to Unity

Keep the Unity instance returned after `createUnityInstance` resolves. Browser code invokes a method on a component attached to a named GameObject through:

```js
unityInstance.SendMessage(objectName, methodName, value)
```

The target C# method can accept no argument, one string argument, or one numeric argument. Do not design this boundary around multiple parameters or direct transfer of complex JavaScript objects.

### Unity C# to browser JavaScript

C# declares browser-side functions with `DllImport("__Internal")`. The matching functions live in a Unity Web `.jslib` plug-in and are registered through `mergeInto(LibraryManager.library, { ... })`.

Unity Web `.jslib` plug-ins must use ES5-compatible syntax; ES6 syntax is not supported there. A string passed from C# arrives as a pointer and must be decoded with `UTF8ToString` before browser code uses it.

### Returning strings to C#

When a JavaScript function returns a string to C#, it cannot return an ordinary JavaScript string directly. The plug-in must:

1. Calculate the UTF-8 byte count with `lengthBytesUTF8` and include the null terminator.
2. Allocate the return buffer with `_malloc`.
3. Copy the value with `stringToUTF8`.
4. Return the allocated pointer.

### Project boundary

The HTML host should retain the resolved Unity instance and centralize calls to `SendMessage`. Unity-to-HTML calls should likewise pass through one project-owned `.jslib` plug-in. This keeps the two supported interop directions explicit and prevents page modules from depending directly on Unity runtime details.

## Project Notes

<!-- Auto-appended by fetch-sdk skill. Lessons learned during implementation. -->
- 2026-09-17: The intended boundary is Unity Web for the left-side 3D scene and the existing HTML UI for dialogue and narrative controls. The custom template and its `unityInstance` bridge should be the only integration surface between them.
- 2026-09-17: Before replacing the prototype renderer, create a minimal Unity Web build and validate loader startup, compression/MIME headers, data caching, and JS/Unity round trips in the same hosting path used by the presentation page.
- 2026-09-17: WebAssembly multithreading is deferred until profiling shows a need because enabling it also commits the hosting page to the documented cross-origin isolation headers.
- 2026-09-17: `SceneHost` should be the sole owner of the `unityInstance` returned by `createUnityInstance`; other HTML modules should not call `SendMessage` directly.
- 2026-09-17: Keep Unity-to-HTML calls behind one `.jslib` plug-in written with ES5-compatible syntax, and decode incoming C# string pointers with `UTF8ToString`.
- 2026-09-17: Prefer a string payload for structured cross-boundary messages because `SendMessage` supports only no argument, one string, or one number; if JavaScript returns a string to C#, it must use `_malloc`, `lengthBytesUTF8`, and `stringToUTF8`.
