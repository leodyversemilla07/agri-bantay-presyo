"use client"

import { useEffect, useState, Suspense } from "react"
import { PriceChart } from "@/components/price-chart"
import { PriceTicker } from "@/components/price-ticker"
import { StatsCards } from "@/components/stats-cards"
import { BarChart3, TrendingUp, Search, ChevronDown } from "lucide-react"
import { fetchCommodities } from "@/lib/api"
import { useSearchParams } from "next/navigation"

function AnalyticsContent() {
    const [commodity, setCommodity] = useState("Local Special Rice")
    const [dateRange, setDateRange] = useState("30d")
    const [commodities, setCommodities] = useState<any[]>([])
    const searchParams = useSearchParams()
    const query = searchParams.get("q")

    useEffect(() => {
        async function load() {
            try {
                const data = await fetchCommodities()
                setCommodities(data)

                if (query) {
                    const match = data.find((c: any) => c.name.toLowerCase().includes(query.toLowerCase()))
                    if (match) {
                        setCommodity(match.name)
                        return
                    }
                }

                if (data.length > 0 && !commodity) {
                    setCommodity(data[0].name)
                }
            } catch (e) {
                console.error(e)
            }
        }
        load()
    }, [query])

    return (
        <div className="min-h-screen bg-background font-sans pb-8">
            <PriceTicker />

            <div className="container mx-auto px-4 pt-6 space-y-8">
                <header className="space-y-4">
                    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 text-blue-600 text-[10px] font-black uppercase tracking-widest border border-blue-500/20">
                        <BarChart3 className="size-3" />
                        Advanced Analytics
                    </div>
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                        <div className="space-y-1">
                            <h1 className="text-4xl font-black tracking-tighter">Deep <span className="text-primary italic">Trends</span></h1>
                            <p className="text-foreground/60 font-bold">Visualizing market volatility and historical price movements.</p>
                        </div>

                        <div className="flex items-center gap-3">
                            <div className="relative">
                                <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-foreground/40 pointer-events-none" />
                                <select
                                    className="h-11 pl-9 pr-10 rounded-xl border border-border bg-background font-bold text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 appearance-none min-w-[200px]"
                                    value={commodity}
                                    onChange={(e) => setCommodity(e.target.value)}
                                >
                                    {commodities.map((c) => (
                                        <option key={c.id} value={c.name}>{c.name}</option>
                                    ))}
                                </select>
                                <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 size-4 text-foreground/40 pointer-events-none" />
                            </div>
                            <select
                                className="h-11 px-4 rounded-xl border border-border bg-background font-bold text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
                                value={dateRange}
                                onChange={(e) => setDateRange(e.target.value)}
                            >
                                <option value="7d">Last 7 Days</option>
                                <option value="30d">Last 30 Days</option>
                                <option value="90d">Last 3 Months</option>
                                <option value="1y">Full Year</option>
                            </select>
                        </div>
                    </div>
                </header>

                <section className="space-y-4">
                    <StatsCards />
                </section>

                <section className="grid gap-6 lg:grid-cols-2">
                    <div className="space-y-4">
                        <div className="flex items-center gap-3 px-2">
                            <div className="size-10 rounded-xl bg-primary/10 flex items-center justify-center">
                                <TrendingUp className="size-5 text-primary" />
                            </div>
                            <div>
                                <h3 className="font-black tracking-tight">{commodity} Price Trail</h3>
                                <p className="text-[10px] font-black uppercase text-foreground/40 tracking-widest leading-none">Primary prevailing indices</p>
                            </div>
                        </div>
                        <div className="h-[450px]">
                            <PriceChart commodity={commodity} dateRange={dateRange} />
                        </div>
                    </div>

                    <div className="space-y-4">
                        <div className="flex items-center gap-3 px-2">
                            <div className="size-10 rounded-xl bg-blue-500/10 flex items-center justify-center">
                                <BarChart3 className="size-5 text-blue-500" />
                            </div>
                            <div>
                                <h3 className="font-black tracking-tight">Market Range Analysis</h3>
                                <p className="text-[10px] font-black uppercase text-foreground/40 tracking-widest leading-none">High vs Low Volatility Hubs</p>
                            </div>
                        </div>
                        <div className="h-[450px]">
                            <PriceChart commodity={commodity} dateRange={dateRange} showVolume />
                        </div>
                    </div>
                </section>
            </div>
        </div>
    )
}

export default function AnalyticsPage() {
    return (
        <Suspense fallback={<div className="min-h-screen bg-background" />}>
            <AnalyticsContent />
        </Suspense>
    )
}
