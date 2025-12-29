"use client"

import { useState } from "react"
import { CommodityTable } from "@/components/commodity-table"
import { MarketFilters } from "@/components/market-filters"
import { PriceTicker } from "@/components/price-ticker"
import { Database } from "lucide-react"

export default function MarketsPage() {
    const [selectedMarket, setSelectedMarket] = useState("all")
    const [dateRange, setDateRange] = useState("7d")

    return (
        <div className="min-h-screen bg-background font-sans pb-8">
            <PriceTicker />

            <div className="container mx-auto px-4 pt-6 space-y-8">
                <header className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                    <div className="space-y-2">
                        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-[10px] font-black uppercase tracking-widest border border-primary/20">
                            <Database className="size-3" />
                            Live Repository
                        </div>
                        <h1 className="text-4xl font-black tracking-tighter sm:text-5xl">Market <span className="text-primary italic">Hub</span></h1>
                        <p className="text-foreground/60 font-bold max-w-xl">
                            Filter through thousands of price entries collected from major trading centers across the Philippines.
                        </p>
                    </div>

                    <div className="flex-shrink-0">
                        <MarketFilters
                            selectedMarket={selectedMarket}
                            onSelectMarket={setSelectedMarket}
                            dateRange={dateRange}
                            onDateRangeChange={setDateRange}
                        />
                    </div>
                </header>

                <div>
                    <CommodityTable market={selectedMarket} />
                </div>
            </div>
        </div>
    )
}
