"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Database, Activity, MapPin, AlertTriangle } from "lucide-react"

const stats = [
  {
    title: "Commodities Tracked",
    value: "127",
    change: "+5",
    changeLabel: "this week",
    icon: Database,
    trend: "up",
  },
  {
    title: "Average Price Change",
    value: "+2.4%",
    change: "0.3%",
    changeLabel: "vs last week",
    icon: Activity,
    trend: "up",
  },
  {
    title: "Markets Monitored",
    value: "48",
    change: "+2",
    changeLabel: "new markets",
    icon: MapPin,
    trend: "up",
  },
  {
    title: "Price Alerts",
    value: "12",
    change: "-3",
    changeLabel: "vs yesterday",
    icon: AlertTriangle,
    trend: "down",
  },
]

export function StatsCards() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat) => {
        const Icon = stat.icon
        return (
          <Card key={stat.title} className="bg-card border-border shadow-sm">
            <CardContent className="p-5">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium text-muted-foreground">{stat.title}</p>
                <div className="size-9 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Icon className="size-4 text-primary" />
                </div>
              </div>
              <div className="mt-3 flex items-baseline gap-2">
                <p className="text-2xl font-bold text-foreground">{stat.value}</p>
                <span
                  className={`text-xs font-semibold px-1.5 py-0.5 rounded ${stat.trend === "up" ? "text-primary bg-primary/10" : "text-destructive bg-destructive/10"}`}
                >
                  {stat.change}
                </span>
              </div>
              <p className="mt-1 text-xs text-muted-foreground">{stat.changeLabel}</p>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
