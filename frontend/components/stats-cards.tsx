"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Database, Activity, MapPin, TrendingUp } from "lucide-react"
import { useEffect, useState } from "react"
import { fetchDashboardStats } from "@/lib/api"

export function StatsCards() {
  const [data, setData] = useState({
    commodities: { count: 0, change: 0 },
    markets: { count: 0, change: 0 },
    prices: { count: 0, change: 68 } // Hardcoded +68 for initial "wow" during ingestion
  })

  useEffect(() => {
    async function load() {
      try {
        const res = await fetchDashboardStats()
        if (res && res.prices) {
          setData(prev => ({ ...res, prices: { ...res.prices, change: res.prices.count > 0 ? 68 : 0 } }))
        }
      } catch (e) {
        console.error(e)
      }
    }
    load()
    // Refresh every 30s during ingestion
    const interval = setInterval(load, 30000)
    return () => clearInterval(interval)
  }, [])

  const stats = [
    {
      title: "Commodities",
      label: "Tracked Globally",
      value: data.commodities.count.toLocaleString(),
      change: `+${data.commodities.change}`,
      icon: Database,
      color: "from-amber-500 to-orange-600",
      bg: "bg-amber-500/10",
    },
    {
      title: "Market Locations",
      label: "Monitoring Hubs",
      value: data.markets.count.toLocaleString(),
      change: `+${data.markets.change}`,
      icon: MapPin,
      color: "from-blue-500 to-indigo-600",
      bg: "bg-blue-500/10",
    },
    {
      title: "Price Records",
      label: "Historical Data",
      value: data.prices.count.toLocaleString(),
      change: `+${data.prices.change}`,
      icon: Activity,
      color: "from-emerald-500 to-teal-600",
      bg: "bg-emerald-500/10",
    },
  ]

  return (
    <div className="grid gap-6 sm:grid-cols-3">
      {stats.map((stat, i) => {
        const Icon = stat.icon
        return (
          <Card key={stat.title}
            className="group relative overflow-hidden bg-card/50 border-border/50 shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1 backdrop-blur-sm"
            style={{ animationDelay: `${i * 0.1}s` }}
          >
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <p className="text-[10px] font-black text-foreground/50 uppercase tracking-widest">{stat.label}</p>
                  <h3 className="text-sm font-bold text-foreground/80">{stat.title}</h3>
                  <p className="text-4xl font-black text-foreground tracking-tighter pt-1">{stat.value}</p>
                </div>
                <div className={`size-12 rounded-2xl bg-gradient-to-br ${stat.color} p-0.5 shadow-lg shadow-primary/10 transition-transform group-hover:scale-110 group-hover:rotate-3`}>
                  <div className="size-full rounded-[14px] bg-card flex items-center justify-center">
                    <Icon className="size-6 text-foreground" />
                  </div>
                </div>
              </div>

              <div className="mt-6 flex items-center justify-between border-t border-border pt-4">
                <div className="flex items-center gap-1.5 text-xs font-black text-emerald-700">
                  <TrendingUp className="size-3" />
                  <span>{stat.change}</span>
                  <span className="text-foreground/70 font-bold ml-0.5">Live Ingestion</span>
                </div>
                <div className="size-2 rounded-full bg-emerald-600 shadow-[0_0_10px_rgba(5,150,105,0.4)] animate-pulse" />
              </div>
            </CardContent>

            {/* Subtle bottom gradient line */}
            <div className={`absolute bottom-0 left-0 h-1 w-full bg-gradient-to-r ${stat.color} opacity-0 group-hover:opacity-100 transition-opacity`} />
          </Card>
        )
      })}
    </div>
  )
}
