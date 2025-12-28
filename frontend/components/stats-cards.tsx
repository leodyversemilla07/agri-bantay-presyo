"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Database, Activity, MapPin, AlertTriangle } from "lucide-react"
import { useEffect, useState } from "react"
import { fetchDashboardStats } from "@/lib/api"

export function StatsCards() {
  const [data, setData] = useState({
    commodities: { count: 0, change: 0 },
    markets: { count: 0, change: 0 },
    prices: { count: 0, change: 0 }
  })

  useEffect(() => {
    async function load() {
      try {
        const res = await fetchDashboardStats()
        setData(res)
      } catch (e) {
        console.error(e)
      }
    }
    load()
  }, [])

  const stats = [
    {
      title: "Commodities Tracked",
      value: data.commodities.count.toString(),
      change: "+0",
      changeLabel: "this week",
      icon: Database,
      trend: "up",
    },
    {
      title: "Markets Monitored",
      value: data.markets.count.toString(),
      change: "+0",
      changeLabel: "new markets",
      icon: MapPin,
      trend: "up",
    },
    {
      title: "Price Entries",
      value: data.prices.count.toString(),
      change: "+0",
      changeLabel: "total entries",
      icon: Activity,
      trend: "up",
    },
  ]

  return (
    <div className="grid gap-4 sm:grid-cols-3">
      {stats.map((stat) => {
        const Icon = stat.icon
        return (
          <Card key={stat.title} className="bg-card border-border shadow-sm">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide">{stat.title}</p>
                  <p className="mt-1 text-2xl font-bold text-foreground tracking-tight">{stat.value}</p>
                </div>
                <div className="size-10 rounded-full bg-primary/5 flex items-center justify-center">
                  <Icon className="size-5 text-primary" />
                </div>
              </div>
              <div className="mt-2 flex items-center text-xs">
                <span className={`${stat.trend === "up" ? "text-emerald-600" : "text-rose-600"} font-medium`}>
                  {stat.change}
                </span>
                <span className="text-muted-foreground ml-1.5">{stat.changeLabel}</span>
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
