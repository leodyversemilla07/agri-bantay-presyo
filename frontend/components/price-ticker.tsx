"use client"

import { TrendingUp, TrendingDown, Minus } from "lucide-react"
import { useEffect, useState } from "react"
import { fetchPrices } from "@/lib/api"

interface TickerItem {
  id: string
  commodity?: { name: string }
  price_prevailing?: number
  change?: number // To be calculated or fetched from stats
}

export function PriceTicker() {
  const [tickerData, setTickerData] = useState<TickerItem[]>([])
  const [offset, setOffset] = useState(0)

  useEffect(() => {
    async function loadTicker() {
      try {
        const data = await fetchPrices()
        // Simulate trends for visual demonstration since API doesn't return daily change yet
        const enriched = data.slice(0, 30).map((item: any) => ({
          ...item,
          change: Number((Math.random() * 4 * (Math.random() > 0.5 ? 1 : -1)).toFixed(1))
        }))
        setTickerData(enriched)
      } catch (error) {
        console.error("Error loading ticker:", error)
      }
    }
    loadTicker()
  }, [])

  useEffect(() => {
    if (tickerData.length === 0) return
    const interval = setInterval(() => {
      setOffset((prev) => prev - 1)
    }, 30)
    return () => clearInterval(interval)
  }, [tickerData])

  // Reset offset if it goes too far left
  useEffect(() => {
    if (Math.abs(offset) > tickerData.length * 300) {
      setOffset(0)
    }
  }, [offset, tickerData])

  const duplicatedData = tickerData.length > 0 ? [...tickerData, ...tickerData, ...tickerData] : []

  return (
    <div className="relative bg-primary/5 border-b border-border overflow-hidden h-12 flex items-center shadow-inner">
      <div className="absolute left-0 top-0 bottom-0 w-16 bg-linear-to-r from-background to-transparent z-10" />
      <div className="absolute right-0 top-0 bottom-0 w-16 bg-linear-to-l from-background to-transparent z-10" />

      <div
        className="flex items-center gap-12 py-2 whitespace-nowrap will-change-transform"
        style={{ transform: `translateX(${offset}px)` }}
      >
        {duplicatedData.map((item, index) => (
          <div key={`${item.id}-${index}`} className="flex items-center gap-3">
            <span className="text-sm font-semibold text-foreground uppercase tracking-tight">{item.commodity?.name || "Unknown"}</span>
            <div className="flex items-baseline gap-1">
              <span className="text-xs text-muted-foreground">₱</span>
              <span className="text-base font-mono font-bold text-foreground">{item.price_prevailing?.toFixed(2) || "0.00"}</span>
            </div>
            {/* Price Change Indicator */}
            <span
              className={`inline-flex items-center gap-0.5 text-[10px] font-bold px-1.5 py-0.5 rounded uppercase ${(item.change || 0) > 0
                ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
                : (item.change || 0) < 0
                  ? "bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400"
                  : "bg-muted text-muted-foreground"
                }`}
            >
              {(item.change || 0) > 0 ? (
                <TrendingUp className="size-3" />
              ) : (item.change || 0) < 0 ? (
                <TrendingDown className="size-3" />
              ) : (
                <Minus className="size-3" />
              )}
              {Math.abs(item.change || 0).toFixed(1)}%
            </span>
          </div>
        ))}
        {tickerData.length === 0 && (
          <div className="px-12 flex items-center gap-3 text-sm text-amber-600 font-medium">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-500 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500"></span>
            </span>
            Waiting for live price update...
          </div>
        )}
      </div>
    </div>
  )
}
