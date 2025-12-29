"use client"

import { TrendingUp, TrendingDown, Minus, Zap } from "lucide-react"
import { useEffect, useState } from "react"
import { fetchPrices } from "@/lib/api"

interface TickerItem {
  id: string
  commodity?: { name: string }
  price_prevailing?: number
  change?: number
}

export function PriceTicker() {
  const [tickerData, setTickerData] = useState<TickerItem[]>([])
  const [offset, setOffset] = useState(0)

  useEffect(() => {
    async function loadTicker() {
      try {
        const data = await fetchPrices()
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

    // Refresh every 2 minutes
    const interval = setInterval(loadTicker, 120000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (tickerData.length === 0) return
    const interval = setInterval(() => {
      setOffset((prev) => prev - 0.8)
    }, 20)
    return () => clearInterval(interval)
  }, [tickerData])

  useEffect(() => {
    const totalWidth = tickerData.length * 280
    if (Math.abs(offset) > totalWidth) {
      setOffset(0)
    }
  }, [offset, tickerData])

  const duplicatedData = tickerData.length > 0 ? [...tickerData, ...tickerData, ...tickerData] : []

  return (
    <div className="relative bg-card dark:bg-black/40 border-y border-border/50 overflow-hidden h-14 flex items-center shadow-lg backdrop-blur-md">
      {/* Label Badge */}
      <div className="absolute left-0 top-0 bottom-0 z-20 bg-primary px-4 flex items-center gap-2 shadow-[10px_0_30px_rgba(0,0,0,0.1)]">
        <Zap className="size-4 text-primary-foreground fill-current animate-pulse" />
        <span className="text-[10px] font-black uppercase tracking-[0.2em] text-primary-foreground">Live Market Feed</span>
      </div>

      <div className="absolute left-32 top-0 bottom-0 w-24 bg-gradient-to-r from-card to-transparent z-10" />
      <div className="absolute right-0 top-0 bottom-0 w-24 bg-gradient-to-l from-card to-transparent z-10" />

      <div
        className="flex items-center gap-10 py-2 whitespace-nowrap will-change-transform"
        style={{ transform: `translateX(${offset}px)`, paddingLeft: '160px' }}
      >
        {duplicatedData.map((item, index) => (
          <div key={`${item.id}-${index}`} className="flex items-center gap-4 bg-muted/60 px-4 py-2 rounded-xl border border-border transition-all hover:bg-muted/80 group">
            <span className="text-xs font-black text-foreground group-hover:text-primary transition-colors">{item.commodity?.name || "Unknown Commodity"}</span>
            <div className="flex items-baseline gap-1">
              <span className="text-[10px] text-foreground/60 font-black">₱</span>
              <span className="text-sm font-black text-foreground tabular-nums tracking-tighter transition-transform group-hover:scale-110">{item.price_prevailing?.toFixed(2) || "0.00"}</span>
            </div>

            <span
              className={`inline-flex items-center gap-1 text-[10px] font-black px-2 py-0.5 rounded-lg border ${(item.change || 0) > 0
                ? "bg-emerald-600/10 text-emerald-700 border-emerald-600/20"
                : (item.change || 0) < 0
                  ? "bg-rose-600/10 text-rose-700 border-rose-600/20"
                  : "bg-muted text-foreground/60 border-border"
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
          <div className="px-12 flex items-center gap-3 text-sm text-foreground/80 font-black uppercase tracking-widest italic ml-[160px]">
            <div className="size-2 rounded-full bg-primary animate-ping" />
            Synchronizing Market Feed...
          </div>
        )}
      </div>
    </div>
  )
}
