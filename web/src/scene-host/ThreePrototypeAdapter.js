// 迁移期适配器：把现有 Three.js 世界接到 SceneHost，不复制其渲染实现。
// 来源：design/presentation/Unity Web集成设计.md §三、§九。
export function createThreePrototypeAdapter({ activate, deactivate, receiveCommand = () => {} }) {
  return {
    async mount({ emit }) {
      await activate()
      emit({
        v: 1,
        kind: 'event',
        type: 'runtime.ready',
        payload: { adapter: 'three-prototype' },
      })

      return {
        dispatch(message) {
          receiveCommand(message)
        },
        async dispose() {
          await deactivate()
        },
      }
    },
  }
}
