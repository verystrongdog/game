import { expect, test } from 'bun:test'
import { loadUnityBuildManifest } from './UnityWebAdapter.js'

test('resolves Unity build files relative to the manifest', async () => {
  const fetchFunction = async url => ({
    ok: true,
    async json() {
      expect(url).toBe('https://example.test/unity/manifest.json')
      return {
        v: 1,
        loaderUrl: './Build/game.loader.js',
        config: {
          dataUrl: './Build/game.data',
          frameworkUrl: './Build/game.framework.js',
          codeUrl: './Build/game.wasm',
          streamingAssetsUrl: './StreamingAssets',
        },
      }
    },
  })

  const build = await loadUnityBuildManifest('/unity/manifest.json', {
    fetchFunction,
    pageUrl: 'https://example.test/prototype/',
  })

  expect(build.loaderUrl).toBe('https://example.test/unity/Build/game.loader.js')
  expect(build.config.codeUrl).toBe('https://example.test/unity/Build/game.wasm')
  expect(build.config.streamingAssetsUrl).toBe('https://example.test/unity/StreamingAssets')
})

test('rejects a manifest with incomplete Unity build URLs', async () => {
  const fetchFunction = async () => ({
    ok: true,
    async json() {
      return {
        v: 1,
        loaderUrl: './Build/game.loader.js',
        config: { dataUrl: './Build/game.data' },
      }
    },
  })

  expect(loadUnityBuildManifest('/unity/manifest.json', {
    fetchFunction,
    pageUrl: 'https://example.test/prototype/',
  })).rejects.toThrow('missing')
})
