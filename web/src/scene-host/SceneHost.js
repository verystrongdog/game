// Unity Web/Three.js 共用宿主接缝。
// 来源：design/presentation/Unity Web集成设计.md §四—§六。
export const PROTOCOL_VERSION = 1

export function parseEnvelope(value) {
  const envelope = typeof value === 'string' ? JSON.parse(value) : value

  if (!envelope || typeof envelope !== 'object' || Array.isArray(envelope)) {
    throw new TypeError('Scene message must be an object')
  }
  if (envelope.v !== PROTOCOL_VERSION) {
    throw new RangeError(`Unsupported scene protocol version: ${envelope.v}`)
  }
  if (!['command', 'event', 'snapshot', 'error'].includes(envelope.kind)) {
    throw new TypeError(`Unsupported scene message kind: ${envelope.kind}`)
  }
  if (typeof envelope.type !== 'string' || envelope.type.length === 0) {
    throw new TypeError('Scene message type must be a non-empty string')
  }

  return {
    v: PROTOCOL_VERSION,
    kind: envelope.kind,
    type: envelope.type,
    ...(envelope.requestId ? { requestId: String(envelope.requestId) } : {}),
    payload: envelope.payload && typeof envelope.payload === 'object' ? envelope.payload : {},
  }
}

export function createSceneHost({ adapters, onStatus = () => {} }) {
  if (!adapters || typeof adapters !== 'object') {
    throw new TypeError('SceneHost requires an adapter map')
  }

  let active = null
  let nextSessionId = 0

  const publishStatus = status => {
    try {
      onStatus(status)
    } catch (error) {
      console.error('[SceneHost] status listener failed', error)
    }
  }

  return {
    async mount({ adapter: adapterName, container, build }) {
      if (active) throw new Error('A scene session is already active')
      if (!container) throw new TypeError('SceneHost requires a container')

      const adapter = adapters[adapterName]
      if (!adapter || typeof adapter.mount !== 'function') {
        throw new Error(`Unknown scene adapter: ${adapterName}`)
      }

      const sessionId = ++nextSessionId
      const listeners = new Set()
      const pendingMessages = []
      let readyAccepted = false
      const slot = { sessionId, state: 'mounting' }
      active = slot

      const emit = rawMessage => {
        if (active?.sessionId !== sessionId) return

        let message
        try {
          message = parseEnvelope(rawMessage)
        } catch (error) {
          publishStatus({ state: 'message-error', error })
          return
        }

        if (message.kind === 'event' && message.type === 'runtime.ready') {
          if (readyAccepted) return
          readyAccepted = true
        }

        if (listeners.size === 0) pendingMessages.push(message)
        for (const listener of listeners) {
          try {
            listener(message)
          } catch (error) {
            console.error('[SceneHost] message listener failed', error)
          }
        }
      }

      publishStatus({ state: 'loading', adapter: adapterName, progress: 0 })

      let adapterSession
      try {
        adapterSession = await adapter.mount({
          container,
          build,
          emit,
          onProgress(progress) {
            if (active?.sessionId !== sessionId) return
            publishStatus({ state: 'loading', adapter: adapterName, progress })
          },
        })
      } catch (error) {
        if (active?.sessionId === sessionId) active = null
        publishStatus({ state: 'error', adapter: adapterName, error })
        throw error
      }

      let disposed = false
      const session = {
        dispatch(rawMessage) {
          if (disposed || active?.sessionId !== sessionId) {
            throw new Error('Scene session is not active')
          }
          const message = parseEnvelope(rawMessage)
          if (message.kind !== 'command') {
            throw new TypeError('Only command messages can be dispatched to a scene')
          }
          return adapterSession.dispatch(message)
        },

        subscribe(listener) {
          if (typeof listener !== 'function') throw new TypeError('Listener must be a function')
          if (disposed) throw new Error('Scene session is not active')
          listeners.add(listener)
          if (pendingMessages.length > 0) {
            const replay = pendingMessages.splice(0)
            for (const message of replay) listener(message)
          }
          return () => listeners.delete(listener)
        },

        async dispose() {
          if (disposed) return
          disposed = true
          if (active?.sessionId === sessionId) active = null
          listeners.clear()
          pendingMessages.length = 0
          await adapterSession.dispose()
          publishStatus({ state: 'idle', adapter: adapterName })
        },
      }

      slot.state = 'mounted'
      slot.session = session
      publishStatus({ state: 'mounted', adapter: adapterName, progress: 1 })
      return session
    },
  }
}
