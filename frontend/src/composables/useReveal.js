import { onMounted, onUnmounted } from 'vue'

// Replaces 8 page-local IntersectionObservers. Reveals every [data-reveal]
// element by adding the .is-revealed class. Two failure modes the previous
// per-page observers had: (1) threshold:0.12 + negative bottom rootMargin
// could be impossible to meet for short headlines near the viewport edges;
// (2) elements rendered after fetchData() weren't always re-observed in time.
// The fix: threshold:0, no rootMargin, and prime() walks the DOM synchronously
// to reveal anything already in viewport on first paint.
export function useReveal() {
  let io = null
  let onLoad = null

  const isInViewport = (el) => {
    const r = el.getBoundingClientRect()
    return r.top < (window.innerHeight || document.documentElement.clientHeight) && r.bottom > 0
  }

  const prime = () => {
    const nodes = document.querySelectorAll('[data-reveal]:not(.is-revealed)')
    nodes.forEach((el) => {
      if (isInViewport(el)) {
        el.classList.add('is-revealed')
      } else if (io) {
        io.observe(el)
      }
    })
  }

  const observeAll = () => {
    if (!io) return
    prime()
  }

  onMounted(() => {
    io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            e.target.classList.add('is-revealed')
            io.unobserve(e.target)
          }
        })
      },
      { threshold: 0, rootMargin: '0px' },
    )
    prime()
    onLoad = () => prime()
    window.addEventListener('load', onLoad, { once: true })
  })

  onUnmounted(() => {
    if (io) io.disconnect()
    if (onLoad) window.removeEventListener('load', onLoad)
    io = null
  })

  return { observeAll }
}
