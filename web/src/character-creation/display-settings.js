// 来源：design/presentation/叙事界面布局.md §五。亮度只改变浏览器呈现，不改变场景灯光或游戏状态。
const STORAGE_KEY = 'yantf-display-brightness'
const MIN_BRIGHTNESS = 70
const MAX_BRIGHTNESS = 140
const DEFAULT_BRIGHTNESS = 100

export function clampBrightness(value) {
  return Math.min(MAX_BRIGHTNESS, Math.max(MIN_BRIGHTNESS, Number(value) || DEFAULT_BRIGHTNESS))
}

export function createDisplaySettings({ trigger, panel, input, output }) {
  if (!trigger || !panel || !input || !output) return null

  const storedValue = globalThis.localStorage?.getItem(STORAGE_KEY)
  let brightness = clampBrightness(storedValue ?? DEFAULT_BRIGHTNESS)

  function apply(value) {
    brightness = clampBrightness(value)
    input.value = String(brightness)
    output.value = `${brightness}%`
    output.textContent = `${brightness}%`
    document.documentElement.style.setProperty('--display-brightness', String(brightness / 100))
    globalThis.localStorage?.setItem(STORAGE_KEY, String(brightness))
  }

  function setOpen(open) {
    panel.hidden = !open
    trigger.setAttribute('aria-expanded', String(open))
  }

  trigger.addEventListener('click', event => {
    event.stopPropagation()
    setOpen(panel.hidden)
  })
  panel.addEventListener('click', event => event.stopPropagation())
  input.addEventListener('input', () => apply(input.value))
  document.addEventListener('click', () => setOpen(false))
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') setOpen(false)
  })

  apply(brightness)
  return { apply, get value() { return brightness } }
}
