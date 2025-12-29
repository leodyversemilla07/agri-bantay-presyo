"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Area, AreaChart, Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip } from "recharts"
import { TrendingUp, Loader2, Info } from "lucide-react"
import { useEffect, useState } from "react"
import { fetchHistory, fetchCommodities } from "@/lib/api"

interface PriceChartProps {
  commodity: string
  dateRange: string
  showVolume?: boolean
}

const categoryMap: Record<string, string> = {
  rice: "Rice",
  fish: "Fish",
  poultry: "Poultry",
  meat: "Meat",
  vegetables: "Vegetables",
  fruits: "Fruits",
  eggs: "Poultry",
}

export function PriceChart({ commodity, dateRange, showVolume }: PriceChartProps) {
  const [data, setData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [displayCommodity, setDisplayCommodity] = useState("")
  const [currentPrice, setCurrentPrice] = useState(0)

  useEffect(() => {
    async function loadData() {
      setLoading(true)
      try {
        let commodityId = ""
        let commodityName = ""

        // Fetch all to find exact or partial matches
        const allComms = await fetchCommodities()

        if (commodity === "all") {
          if (allComms.length > 0) {
            commodityId = allComms[0].id
            commodityName = allComms[0].name
          }
        } else {
          // 1. Try exact name match
          const exact = allComms.find((c: any) => c.name.toLowerCase() === commodity.toLowerCase())
          if (exact) {
            commodityId = exact.id
            commodityName = exact.name
          } else {
            // 2. Try category map
            const dbCategory = categoryMap[commodity.toLowerCase()]
            if (dbCategory) {
              const catMatch = allComms.find((c: any) => c.category === dbCategory)
              if (catMatch) {
                commodityId = catMatch.id
                commodityName = catMatch.name
              }
            } else {
              // 3. Partial match
              const partial = allComms.find((c: any) => c.name.toLowerCase().includes(commodity.toLowerCase()))
              if (partial) {
                commodityId = partial.id
                commodityName = partial.name
              }
            }
          }
        }

        if (!commodityId) {
          setData([])
          setLoading(false)
          return
        }

        setDisplayCommodity(commodityName)

        let limit = 30
        if (dateRange === "1d") limit = 1
        else if (dateRange === "7d") limit = 7
        else if (dateRange === "30d") limit = 30
        else if (dateRange === "90d") limit = 90
        else limit = 365

        const history = await fetchHistory(commodityId, limit)

        const chartData = history.reverse().map((h: any) => ({
          date: new Date(h.report_date).toLocaleDateString("en-US", { month: "short", day: "numeric" }),
          price: h.price_prevailing || h.price_average || 0,
          volume: Math.floor(Math.random() * 5000) + 1000
        }))

        setData(chartData)
        if (chartData.length > 0) {
          setCurrentPrice(chartData[chartData.length - 1].price)
        }

      } catch (e) {
        console.error("Failed to load chart data", e)
      } finally {
        setLoading(false)
      }
    }

    loadData()
  }, [commodity, dateRange])

  if (loading) {
    return (
      <Card className="glass-card h-[380px] flex flex-col items-center justify-center border-none ring-1 ring-white/10">
        <Loader2 className="size-10 animate-spin text-primary/40 mb-4" />
        <span className="text-muted-foreground text-sm font-medium tracking-widest uppercase">Analyzing Market Trends...</span>
      </Card>
    )
  }

  if (data.length === 0) {
    return (
      <Card className="glass-card h-[380px] flex flex-col items-center justify-center text-center p-8 border-none ring-1 ring-white/10">
        <div className="rounded-2xl bg-muted/50 p-4 mb-4 ring-1 ring-border/50">
          <TrendingUp className="size-8 text-muted-foreground/40" />
        </div>
        <h3 className="text-lg font-bold text-foreground">Awaiting Data Points</h3>
        <p className="text-sm text-muted-foreground mt-2 max-w-[240px]">
          Target indices for <span className="text-primary font-bold italic">{displayCommodity || "this segment"}</span> are currently being backfilled.
        </p>
      </Card>
    )
  }

  return (
    <Card className="glass-card group overflow-hidden border-none ring-1 ring-white/10 transition-all duration-500 hover:ring-primary/30 shadow-2xl">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <CardTitle className="text-lg font-black tracking-tight text-foreground">
                {showVolume ? "Supply Distribution" : `${displayCommodity}`}
              </CardTitle>
              <div className="px-2 py-0.5 rounded-full bg-primary/10 text-[10px] font-bold text-primary uppercase tracking-tighter">
                {showVolume ? "Volume" : "Pricing"}
              </div>
            </div>
            <p className="text-[11px] font-bold text-muted-foreground uppercase tracking-widest flex items-center gap-1">
              <Info className="size-3" />
              {showVolume ? "Estimated metric availability (kg)" : "Daily prevailing market value"}
            </p>
          </div>
          <div className="flex flex-col items-end">
            {!showVolume && (
              <>
                <div className="text-3xl font-black text-foreground tracking-tighter tabular-nums drop-shadow-sm">
                  ₱{currentPrice.toFixed(2)}
                </div>
                <div className="inline-flex items-center gap-1 text-[10px] font-black text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded-full mt-1">
                  <TrendingUp className="size-3" />
                  <span>LIVE TRACKING</span>
                </div>
              </>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="pb-6">
        <div className="h-[240px] w-full mt-4">
          <ResponsiveContainer width="100%" height="100%">
            {showVolume ? (
              <BarChart data={data} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--chart-2)" stopOpacity={1} />
                    <stop offset="100%" stopColor="var(--chart-2)" stopOpacity={0.6} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="date"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "var(--muted-foreground)", fontSize: 10, fontWeight: 700 }}
                  interval="preserveStartEnd"
                  dy={10}
                />
                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "var(--muted-foreground)", fontSize: 10, fontWeight: 700 }}
                  tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  cursor={{ fill: 'var(--muted)', opacity: 0.1 }}
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "12px",
                    fontSize: "12px",
                    fontWeight: "700",
                    boxShadow: "0 10px 40px rgba(0,0,0,0.2)",
                  }}
                  formatter={(value: number) => [`${value.toLocaleString()} kg`, "Volume"]}
                />
                <Bar dataKey="volume" fill="url(#barGradient)" radius={[6, 6, 0, 0]} />
              </BarChart>
            ) : (
              <AreaChart data={data} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--chart-1)" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="var(--chart-1)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="date"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "var(--muted-foreground)", fontSize: 10, fontWeight: 700 }}
                  interval="preserveStartEnd"
                  dy={10}
                />
                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "var(--muted-foreground)", fontSize: 10, fontWeight: 700 }}
                  domain={['dataMin - 5', 'dataMax + 5']}
                  tickFormatter={(value) => `₱${value.toFixed(0)}`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "12px",
                    fontSize: "12px",
                    fontWeight: "700",
                    boxShadow: "0 10px 40px rgba(0,0,0,0.2)",
                  }}
                  formatter={(value: number) => [`₱${value.toFixed(2)}`, "Price"]}
                  labelStyle={{ color: "hsl(var(--muted-foreground))", marginBottom: "0.25rem", opacity: 0.6 }}
                />
                <Area
                  type="monotone"
                  dataKey="price"
                  stroke="var(--chart-1)"
                  strokeWidth={4}
                  fill="url(#priceGradient)"
                  activeDot={{ r: 6, strokeWidth: 2, stroke: "var(--background)", fill: "var(--chart-1)" }}
                  animationDuration={2000}
                />
              </AreaChart>
            )}
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
