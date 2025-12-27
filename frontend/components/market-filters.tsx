"use client"

import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Calendar, Download, RefreshCw } from "lucide-react"

const markets = [
  { id: "all", name: "All Markets" },
  { id: "ncr", name: "NCR Markets" },
  { id: "luzon", name: "Luzon Markets" },
  { id: "visayas", name: "Visayas Markets" },
  { id: "mindanao", name: "Mindanao Markets" },
]

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
  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 bg-card rounded-xl border border-border shadow-sm">
      <div className="flex items-center gap-3">
        <Select value={selectedMarket} onValueChange={onSelectMarket}>
          <SelectTrigger className="w-44 bg-background border-border">
            <SelectValue placeholder="Select market" />
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
          <SelectTrigger className="w-36 bg-background border-border">
            <Calendar className="size-4 mr-2 text-muted-foreground" />
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

        <Button variant="ghost" size="icon" className="size-9">
          <RefreshCw className="size-4" />
        </Button>
      </div>

      <Button variant="default" size="sm" className="gap-2">
        <Download className="size-4" />
        Export Data
      </Button>
    </div>
  )
}
