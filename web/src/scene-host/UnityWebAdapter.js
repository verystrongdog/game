// Unity Web Loader、Canvas 与 SendMessage 的唯一网页适配器。
// 来源：design/presentation/Unity Web集成设计.md §四·1、§六；
//       docs/reference/unity-webgl.md §一、§七。
const loaderPromises = new WeakMap()

function loadUnityLoader(documentObject, loaderUrl) {
  let byUrl = loaderPromises.get(documentObject)
  if (!byUrl) {
    byUrl = new Map()
    loaderPromises.set(documentObject, byUrl)
  }
  if (byUrl.has(loaderUrl)) return byUrl.get(loaderUrl)

  const promise = new Promise((resolve, reject) => {
    const script = documentObject.createElement('script')
    script.src = loaderUrl
    script.async = true
    script.onload = resolve
    script.onerror = () => {
      byUrl.delete(loaderUrl)
      script.remove()
      reject(new Error(`Unable to load Unity loader: ${loaderUrl}`))
    }
    documentObject.head.append(script)
  })
  byUrl.set(loaderUrl, promise)
  return promise
}

export async function loadUnityBuildManifest(manifestUrl, {
  fetchFunction = fetch,
  pageUrl = window.location.href,
} = {}) {
  const absoluteManifestUrl = new URL(manifestUrl, pageUrl)
  const response = await fetchFunction(absoluteManifestUrl.href)
  if (!response.ok) {
    throw new Error(`Unable to load Unity manifest (${response.status}): ${absoluteManifestUrl.href}`)
  }

  const manifest = await response.json()
  const requiredConfigUrls = ['dataUrl', 'frameworkUrl', 'codeUrl', 'streamingAssetsUrl']
  if (
    manifest.v !== 1
    || !manifest.loaderUrl
    || !manifest.config
    || requiredConfigUrls.some(key => !manifest.config[key])
  ) {
    throw new TypeError('Unity manifest is missing a supported version, loaderUrl, or config')
  }

  const resolveFromManifest = value => new URL(value, absoluteManifestUrl).href
  return {
    loaderUrl: resolveFromManifest(manifest.loaderUrl),
    config: {
      ...manifest.config,
      dataUrl: resolveFromManifest(manifest.config.dataUrl),
      frameworkUrl: resolveFromManifest(manifest.config.frameworkUrl),
      codeUrl: resolveFromManifest(manifest.config.codeUrl),
      streamingAssetsUrl: resolveFromManifest(manifest.config.streamingAssetsUrl),
    },
  }
}

export function createUnityWebAdapter({ windowObject = window, documentObject = document } = {}) {
  return {
    async mount({ container, build, emit, onProgress }) {
      const resolvedBuild = build?.manifestUrl
        ? await loadUnityBuildManifest(build.manifestUrl, {
            fetchFunction: windowObject.fetch.bind(windowObject),
            pageUrl: windowObject.location.href,
          })
        : build

      if (!resolvedBuild?.loaderUrl || !resolvedBuild?.config) {
        throw new TypeError('Unity build requires loaderUrl and config')
      }
      if (windowObject.yantfUnityBridge) {
        throw new Error('Another Unity Web bridge is already active')
      }

      const canvas = documentObject.createElement('canvas')
      canvas.className = 'unity-web-canvas'
      canvas.tabIndex = 0
      canvas.setAttribute('aria-label', '三维游戏场景')
      container.append(canvas)

      const bridge = {
        emit(rawMessage) {
          emit(rawMessage)
        },
      }
      windowObject.yantfUnityBridge = bridge

      let instance = null
      try {
        await loadUnityLoader(documentObject, resolvedBuild.loaderUrl)
        if (typeof windowObject.createUnityInstance !== 'function') {
          throw new Error('Unity loader did not expose createUnityInstance')
        }
        instance = await windowObject.createUnityInstance(canvas, resolvedBuild.config, onProgress)
      } catch (error) {
        if (windowObject.yantfUnityBridge === bridge) delete windowObject.yantfUnityBridge
        canvas.remove()
        throw error
      }

      return {
        dispatch(message) {
          instance.SendMessage('WebPresentationBridge', 'Receive', JSON.stringify(message))
        },

        async dispose() {
          if (windowObject.yantfUnityBridge === bridge) delete windowObject.yantfUnityBridge
          if (instance && typeof instance.Quit === 'function') await instance.Quit()
          canvas.remove()
        },
      }
    },
  }
}
