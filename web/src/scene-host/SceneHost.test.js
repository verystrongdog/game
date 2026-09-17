import { describe, expect, test } from 'bun:test'
import { createSceneHost, parseEnvelope } from './SceneHost.js'

const ready = {
  v: 1,
  kind: 'event',
  type: 'runtime.ready',
  payload: {},
}

describe('SceneHost', () => {
  test('buffers adapter messages until the page subscribes', async () => {
    const adapter = {
      async mount({ emit }) {
        emit(ready)
        return { dispatch() {}, async dispose() {} }
      },
    }
    const host = createSceneHost({ adapters: { test: adapter } })
    const session = await host.mount({ adapter: 'test', container: {} })
    const messages = []

    session.subscribe(message => messages.push(message))

    expect(messages).toEqual([ready])
    await session.dispose()
  })

  test('rejects a second mount while a session is active', async () => {
    const adapter = {
      async mount() {
        return { dispatch() {}, async dispose() {} }
      },
    }
    const host = createSceneHost({ adapters: { test: adapter } })
    const session = await host.mount({ adapter: 'test', container: {} })

    expect(host.mount({ adapter: 'test', container: {} })).rejects.toThrow('already active')
    await session.dispose()
  })

  test('stops stale adapter events after dispose', async () => {
    let emit
    const adapter = {
      async mount(context) {
        emit = context.emit
        return { dispatch() {}, async dispose() {} }
      },
    }
    const host = createSceneHost({ adapters: { test: adapter } })
    const session = await host.mount({ adapter: 'test', container: {} })
    const messages = []
    session.subscribe(message => messages.push(message))

    await session.dispose()
    emit(ready)

    expect(messages).toHaveLength(0)
  })

  test('accepts runtime.ready only once per session', async () => {
    const adapter = {
      async mount({ emit }) {
        emit(ready)
        emit(ready)
        return { dispatch() {}, async dispose() {} }
      },
    }
    const host = createSceneHost({ adapters: { test: adapter } })
    const session = await host.mount({ adapter: 'test', container: {} })
    const messages = []

    session.subscribe(message => messages.push(message))

    expect(messages).toEqual([ready])
    await session.dispose()
  })

  test('only dispatches valid command envelopes', async () => {
    const dispatched = []
    const adapter = {
      async mount() {
        return {
          dispatch(message) { dispatched.push(message) },
          async dispose() {},
        }
      },
    }
    const host = createSceneHost({ adapters: { test: adapter } })
    const session = await host.mount({ adapter: 'test', container: {} })

    session.dispatch({ v: 1, kind: 'command', type: 'input.mode.set', payload: { mode: 'ui' } })
    expect(dispatched[0].type).toBe('input.mode.set')
    expect(() => session.dispatch(ready)).toThrow('Only command')
    await session.dispose()
  })
})

describe('parseEnvelope', () => {
  test('rejects unsupported protocol versions', () => {
    expect(() => parseEnvelope({ ...ready, v: 2 })).toThrow('protocol version')
  })
})
