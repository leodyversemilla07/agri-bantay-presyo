import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Area, AreaChart, Bar, BarChart, ResponsiveContainer, XAxis, YAxis, Tooltip } from "recharts"
import { TrendingUp, Loader2 } from "lucide-react"
import { useEffect, useState } from "react"
import { fetchHistory, fetchCommodities } from "@/lib/api"

interface PriceChartProps {
  commodity: string // This is actually the category ID from Sidebar (e.g. "rice")
  dateRange: string
  showVolume?: boolean
}

// Map frontend category IDs to DB Category names
const categoryMap: Record<string, string> = {
  rice: "Rice",
  fish: "Fish",
  poultry: "Poultry",
  meat: "Meat",
  vegetables: "Vegetables",
  fruits: "Fruits",
  eggs: "Poultry", // Eggs often under Poultry or separate
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

        // 1. Find a concrete commodity to display
        if (commodity === "all") {
          // Default to Rice Special (Local) or similar
          const all = await fetchCommodities()
          if (all.length > 0) {
            commodityId = all[0].id
            commodityName = all[0].name
          }
        } else {
          // Fetch commodities for this category
          const dbCategory = categoryMap[commodity]
          if (dbCategory) {
            const comms = await fetchCommodities(dbCategory)
            if (comms && comms.length > 0) {
              commodityId = comms[0].id
              commodityName = comms[0].name
            }
          }
        }

        if (!commodityId) {
          setData([])
          setLoading(false)
          return
        }

        setDisplayCommodity(commodityName)

        // 2. Fetch history
        let limit = 30
        if (dateRange === "1d") limit = 1
        else if (dateRange === "7d") limit = 7
        else if (dateRange === "30d") limit = 30
        else if (dateRange === "90d") limit = 90
        else limit = 365

        const history = await fetchHistory(commodityId, limit)

        // 3. Transform data
        const chartData = history.reverse().map((h: any) => ({
          date: new Date(h.report_date).toLocaleDateString("en-US", { month: "short", day: "numeric" }),
          price: h.price_prevailing || h.price_average || 0,
          volume: Math.floor(Math.random() * 5000) + 1000 // Fake volume for now
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
      <Card className="bg-card border-border shadow-sm h-75 flex items-center justify-center">
        <Loader2 className="animate-spin text-muted-foreground mr-2" />
        <span className="text-muted-foreground text-sm">Loading market data...</span>
      </Card>
    )
  }

  if (data.length === 0) {
    return (
      <Card className="bg-card border-border shadow-sm h-75 flex flex-col items-center justify-center text-center p-6">
        <div className="rounded-full bg-muted p-3 mb-3">
          <TrendingUp className="size-6 text-muted-foreground" />
        </div>
        <h3 className="text-sm font-semibold text-foreground">No Data Available</h3>
        <p className="text-xs text-muted-foreground mt-1 max-w-50">
          We couldn't find price history for this selection. Try changing the filter.
        </p>
      </Card>
    )
  }

  return (
    <Card className="bg-card border-border shadow-sm hover:shadow-md transition-shadow duration-200">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-base font-semibold text-foreground">
              {showVolume ? "Supply Volume Estimate" : `${displayCommodity} Price Trend`}
            </CardTitle>
            <p className="text-xs text-muted-foreground">
              {showVolume ? "Daily metrics in kg" : "Daily prevailing retail price"}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {!showVolume && (
              <div className="text-right">
                <div className="text-2xl font-bold text-foreground tracking-tight">₱{currentPrice.toFixed(2)}</div>
                <div className="inline-flex items-center justify-end gap-1 text-xs font-medium text-emerald-600 bg-emerald-50 dark:bg-emerald-900/20 px-2 py-0.5 rounded-full">
                  <TrendingUp className="size-3" />
                  <span>Latest</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="pb-4">
        <div className="h-60 w-full mt-2">
          <ResponsiveContainer width="100%" height="100%">
            {showVolume ? (
              <BarChart data={data} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                <XAxis
                  dataKey="date"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "var(--muted-foreground)", fontSize: 11 }}
                  interval="preserveStartEnd"
                  dy={10}
                />
                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "var(--muted-foreground)", fontSize: 11 }}
                  tickFormatter={(value) => `${(value / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  cursor={{ fill: 'var(--muted)' }}
                  contentStyle={{
                    backgroundColor: "hsl(var(--popover))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "8px",
                    fontSize: "12px",
                    boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                  }}
                  formatter={(value: number) => [`${value.toLocaleString()} kg`, "Volume"]}
                />
                <Bar dataKey="volume" fill="var(--chart-2)" radius={[4, 4, 0, 0]} />
              </BarChart>
            ) : (
              <AreaChart data={data} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--chart-1)" stopOpacity={0.2} />
                    <stop offset="100%" stopColor="var(--chart-1)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="date"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "var(--muted-foreground)", fontSize: 11 }}
                  interval="preserveStartEnd"
                  dy={10}
                />
                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "var(--muted-foreground)", fontSize: 11 }}
                  domain={['dataMin - 5', 'dataMax + 5']}
                  tickFormatter={(value) => `₱${value.toFixed(0)}`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--popover))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "8px",
                    fontSize: "12px",
                    boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                  }}
                  formatter={(value: number) => [`₱${value.toFixed(2)}`, "Price"]}
                  labelStyle={{ color: "hsl(var(--muted-foreground))", marginBottom: "0.25rem" }}
                />
                <Area
                  type="monotone"
                  dataKey="price"
                  stroke="var(--chart-1)"
                  strokeWidth={2.5}
                  fill="url(#priceGradient)"
                  activeDot={{ r: 4, strokeWidth: 2, stroke: "var(--background)" }}
                />
              </AreaChart>
            )}
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}
