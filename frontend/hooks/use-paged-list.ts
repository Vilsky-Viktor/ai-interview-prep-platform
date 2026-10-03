"use client"

import { useTranslations } from "next-intl"
import { useCallback, useEffect, useRef, useState } from "react"
import { toast } from "sonner"

import { PAGE_SIZE } from "@/constants/lists"
import { apiFetch } from "@/lib/api"

function pagePath(path: string, offset: number) {
  const separator = path.includes("?") ? "&" : "?"

  return `${path}${separator}offset=${offset}&limit=${PAGE_SIZE}`
}

/** A list the API serves a page at a time. `initial` is the first page the server already
rendered; without it, the first page loads on mount. */
export function usePagedList<T>(path: string, initial?: T[]) {
  const t = useTranslations("common")
  const [items, setItems] = useState<T[]>(initial ?? [])
  const [hasMore, setHasMore] = useState(
    initial === undefined || initial.length === PAGE_SIZE
  )
  const [loaded, setLoaded] = useState(initial !== undefined)
  const [source, setSource] = useState({ path, initial })
  const loading = useRef(false)

  // A new search or page starts the list over (reset during render, as React recommends).
  if (source.path !== path || source.initial !== initial) {
    setSource({ path, initial })
    setItems(initial ?? [])
    setHasMore(initial === undefined || initial.length === PAGE_SIZE)
    setLoaded(initial !== undefined)
  }

  // Lists the server didn't render load their first page here.
  useEffect(() => {
    if (loaded) {
      return
    }

    let current = true
    apiFetch<T[]>(pagePath(path, 0))
      .then((page) => {
        if (current) {
          setItems(page)
          setHasMore(page.length === PAGE_SIZE)
        }
      })
      .catch(() => current && setHasMore(false))
      .finally(() => current && setLoaded(true))

    return () => {
      current = false
    }
  }, [path, loaded])

  const loadMore = useCallback(async () => {
    if (loading.current || !hasMore || !loaded) {
      return
    }

    loading.current = true

    try {
      const page = await apiFetch<T[]>(pagePath(path, items.length))
      setItems((current) => [...current, ...page])
      setHasMore(page.length === PAGE_SIZE)
    } catch {
      toast.error(t("loadMoreFailed"))
      setHasMore(false)
    } finally {
      loading.current = false
    }
  }, [path, items.length, hasMore, loaded, t])

  return { items, setItems, hasMore, loaded, loadMore }
}
