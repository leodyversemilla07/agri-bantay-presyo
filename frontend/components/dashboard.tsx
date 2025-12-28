"use client"

import { useState } from "react"
import { StatsCards } from "@/components/stats-cards"
import { PriceChart } from "@/components/price-chart"
import { CommodityTable } from "@/components/commodity-table"
import { MarketFilters } from "@/components/market-filters"

export function Dashboard() {
  const [selectedCommodity, setSelectedCommodity] = useState("rice")
  const [selectedMarket, setSelectedMarket] = useState("all")
  const [dateRange, setDateRange] = useState("7d")

  return (
    <div className="flex gap-6">
      <div className="flex-1 space-y-6">
        <MarketFilters
          selectedMarket={selectedMarket}
          onSelectMarket={setSelectedMarket}
          dateRange={dateRange}
          onDateRangeChange={setDateRange}
        />
        <StatsCards />
        <div className="grid gap-6 lg:grid-cols-2">
          <PriceChart commodity={selectedCommodity} dateRange={dateRange} />
          <PriceChart commodity={selectedCommodity} dateRange={dateRange} showVolume />
        </div>
        <CommodityTable market={selectedMarket} />
      </div>
    </div>
  )
}
