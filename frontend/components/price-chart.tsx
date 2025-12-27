"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Area, AreaChart, Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip } from "recharts"
import { TrendingUp } from "lucide-react"

const generateData = (days: number) => {
  const data = []
  const basePrice = 52
  const now = new Date()

  for (let i = days; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    data.push({
      date: date.toLocaleDateString("en-US", { month: "short", day: "numeric" }),
      price: basePrice + Math.random() * 10 - 5,
      volume: Math.floor(Math.random() * 50000) + 10000,
    })
  }
  return data
}

interface PriceChartProps {
  commodity: string
  dateRange: string
  showVolume?: boolean
}

const commodityNames: Record<string, string> = {
  all: "Rice (Well-Milled)",
  rice: "Rice (Well-Milled)",
  fish: "Galunggong",
  poultry: "Chicken",
  meat: "Pork Kasim",
  vegetables: "Tomato",
  fruits: "Banana",
  eggs: "Egg (Medium)",
}

export function PriceChart({ commodity, dateRange, showVolume }: PriceChartProps) {
  const days =
    dateRange === "1d" ? 1 : dateRange === "7d" ? 7 : dateRange === "30d" ? 30 : dateRange === "90d" ? 90 : 365
  const data = generateData(days)
  const commodityName = commodityNames[commodity] || "Rice (Well-Milled)"

  return (
    <Card className="bg-card border-border shadow-sm">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-semibold text-foreground">
            {showVolume ? "Trading Volume" : `${commodityName} Price Trend`}
          </CardTitle>
          <div className="flex items-center gap-2">
            {!showVolume && (
              <>
                <span className="text-xl font-bold text-foreground">₱{data[data.length - 1]?.price.toFixed(2)}</span>
                <span className="inline-flex items-center gap-1 text-xs font-semibold text-primary bg-primary/10 px-2 py-1 rounded-full">
                  <TrendingUp className="size-3" />
                  +2.3%
                </span>
              </>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="pb-4">
        <div className="h-[220px]">
          <ResponsiveContainer width="100%" height="100%">
            {showVolume ? (
              <BarChart data={data}>
                <XAxis
                  dataKey="date"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "var(--muted-foreground)", fontSize: 11 }}
                  interval="preserveStartEnd"
                />
                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "var(--muted-foreground)", fontSize: 11 }}
                  tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: "10px",
                    color: "var(--foreground)",
                    boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                  }}
                  formatter={(value: number) => [`${value.toLocaleString()} kg`, "Volume"]}
                />
                <Bar dataKey="volume" fill="var(--chart-2)" radius={[6, 6, 0, 0]} />
              </BarChart>
            ) : (
              <AreaChart data={data}>
                <defs>
                  <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--chart-1)" stopOpacity={0.25} />
                    <stop offset="100%" stopColor="var(--chart-1)" stopOpacity={0.02} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="date"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "var(--muted-foreground)", fontSize: 11 }}
                  interval="preserveStartEnd"
                />
                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "var(--muted-foreground)", fontSize: 11 }}
                  domain={["auto", "auto"]}
                  tickFormatter={(value) => `₱${value.toFixed(0)}`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: "10px",
                    color: "var(--foreground)",
                    boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                  }}
                  formatter={(value: number) => [`₱${value.toFixed(2)}`, "Price"]}
                />
                <Area
                  type="monotone"
                  dataKey="price"
                  stroke="var(--chart-1)"
                  strokeWidth={2}
                  fill="url(#priceGradient)"
                />
              </AreaChart>
            )}
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
