"use client"

import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Calendar, Download, RefreshCw } from "lucide-react"
import { useEffect, useState } from "react"
import { fetchMarkets } from "@/lib/api"

interface Market {
  id: string
  name: string
  region?: string
}

const dateRanges = [
  { id: "1d", name: "24 hours" },
  { id: "7d", name: "7 days" },
  { id: "30d", name: "30 days" },
  { id: "90d", name: "90 days" },
  { id: "1y", name: "1 year" },
]

interface MarketFiltersProps {
  selectedMarket: string
  onSelectMarket: (market: string) => void
  dateRange: string
  onDateRangeChange: (range: string) => void
}

export function MarketFilters({ selectedMarket, onSelectMarket, dateRange, onDateRangeChange }: MarketFiltersProps) {
  const [markets, setMarkets] = useState<Market[]>([{ id: "all", name: "All Markets" }])

  useEffect(() => {
    async function getMarkets() {
      try {
        const data = await fetchMarkets()
        setMarkets([{ id: "all", name: "All Markets" }, ...data])
      } catch (error) {
        console.error("Error fetching markets:", error)
      }
    }
    getMarkets()
  }, [])

  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 py-2">
      <div className="flex flex-wrap items-center gap-3 w-full sm:w-auto">
        <Select value={selectedMarket} onValueChange={onSelectMarket}>
          <SelectTrigger className="w-50 h-9 bg-background border-border shadow-sm">
            <SelectValue placeholder="All Markets" />
          </SelectTrigger>
          <SelectContent>
            {markets.map((market) => (
              <SelectItem key={market.id} value={market.id}>
                {market.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={dateRange} onValueChange={onDateRangeChange}>
          <SelectTrigger className="w-35 h-9 bg-background border-border shadow-sm">
            <Calendar className="size-3.5 mr-2 text-muted-foreground" />
            <SelectValue placeholder="Date range" />
          </SelectTrigger>
          <SelectContent>
            {dateRanges.map((range) => (
              <SelectItem key={range.id} value={range.id}>
                {range.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Button variant="outline" size="icon" className="size-9 shadow-sm" onClick={() => window.location.reload()}>
          <RefreshCw className="size-4" />
        </Button>
      </div>

      <Button variant="outline" size="sm" className="gap-2 shadow-sm font-medium ml-auto sm:ml-0">
        <Download className="size-3.5" />
        Export CSV
      </Button>
    </div>
  )
}
