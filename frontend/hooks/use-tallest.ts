import { useEffect, useRef, useState } from "react"

/** For a demo whose content grows and shrinks as it plays: the tallest its box (`ref`) has been
 * at this width, to keep as the box's min-height so the page below never moves back up. It
 * starts over when the width changes. */
export function useTallest<T extends HTMLElement>() {
  const ref = useRef<T>(null)
  const [tallest, setTallest] = useState(0)

  useEffect(() => {
    const element = ref.current

    if (!element) {
      return
    }

    let width = 0
    let height = 0
    const observer = new ResizeObserver(() => {
      const box = element.getBoundingClientRect()

      // A new width (after the first) drops the min-height; the box then settles to its
      // content and is measured again.
      if (box.width !== width) {
        const first = width === 0
        width = box.width
        height = 0

        if (!first) {
          setTallest(0)

          return
        }
      }

      if (box.height > height) {
        height = box.height
        setTallest(height)
      }
    })
    observer.observe(element)

    return () => observer.disconnect()
  }, [])

  return { ref, tallest }
}
