"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Search, ChevronLeft, ChevronRight, Loader2, Filter } from "lucide-react"
import { useState, useEffect } from "react"
import { fetchPrices } from "@/lib/api"

const categoryColors: Record<string, string> = {
  Rice: "bg-amber-500/10 text-amber-500 border-amber-500/20",
  Fish: "bg-blue-500/10 text-blue-500 border-blue-500/20",
  Meat: "bg-rose-500/10 text-rose-500 border-rose-500/20",
  Poultry: "bg-orange-500/10 text-orange-500 border-orange-500/20",
  Vegetables: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20",
  Fruits: "bg-pink-500/10 text-pink-500 border-pink-500/20",
  Spices: "bg-red-500/10 text-red-500 border-red-500/20",
}

interface PriceEntry {
  id: string
  commodity?: {
    name: string
    category: string
  }
  market?: {
    name: string
  }
  price_prevailing?: number
  price_low?: number
  price_high?: number
  report_date: string
}

interface CommodityTableProps {
  market: string
}

export function CommodityTable({ market }: CommodityTableProps) {
  const [prices, setPrices] = useState<PriceEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [page, setPage] = useState(1)
  const perPage = 10

  useEffect(() => {
    async function loadPrices() {
      try {
        setLoading(true)
        const data = await fetchPrices()
        setPrices(data)
      } catch (error) {
        console.error("Error fetching prices:", error)
      } finally {
        setLoading(false)
      }
    }
    loadPrices()
  }, [])

  const filtered = prices.filter(
    (p) =>
      (market === "all" || (p.market?.name || "").toLowerCase().includes(market.toLowerCase())) &&
      (p.commodity?.name || "").toLowerCase().includes(search.toLowerCase()),
  )

  const totalPages = Math.ceil(filtered.length / perPage) || 1
  const paginated = filtered.slice((page - 1) * perPage, page * perPage)

  return (
    <Card className="glass-card border-none ring-1 ring-white/10 shadow-2xl overflow-hidden">
      <CardHeader className="pb-4">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="space-y-1">
            <CardTitle className="text-xl font-black tracking-tight text-foreground flex items-center gap-2">
              <Filter className="size-5 text-primary" />
              Real-time Market Prices
            </CardTitle>
            <p className="text-[11px] font-bold text-muted-foreground uppercase tracking-widest">
              {prices.length > 0 ? `Showing data for ${new Date(prices[0].report_date).toLocaleDateString(undefined, { dateStyle: 'long' })}` : "Verifying latest price indices..."}
            </p>
          </div>
          <div className="relative w-full sm:w-80">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
            <Input
              placeholder="Search by commodity name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-11 bg-background/50 border-border/50 h-11 rounded-xl font-medium focus-visible:ring-primary/30"
            />
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-32 gap-6 opacity-60">
            <div className="relative size-16">
              <Loader2 className="size-full animate-spin text-primary" />
              <div className="absolute inset-0 size-full blur-xl bg-primary/20 animate-pulse" />
            </div>
            <p className="text-xs font-black uppercase tracking-[0.3em] text-muted-foreground">Synchronizing Price Database</p>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-muted/30 border-b border-border/50">
                    <th className="text-left h-12 px-6 font-black text-muted-foreground uppercase text-[10px] tracking-widest">
                      Commodity
                    </th>
                    <th className="text-left h-12 px-6 font-black text-muted-foreground uppercase text-[10px] tracking-widest hidden sm:table-cell">
                      Category
                    </th>
                    <th className="text-right h-12 px-6 font-black text-muted-foreground uppercase text-[10px] tracking-widest">
                      Prevailing
                    </th>
                    <th className="text-right h-12 px-6 font-black text-muted-foreground uppercase text-[10px] tracking-widest hidden md:table-cell">
                      Market Range
                    </th>
                    <th className="text-left h-12 px-6 font-black text-muted-foreground uppercase text-[10px] tracking-widest hidden lg:table-cell w-48">
                      Location
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/30">
                  {paginated.map((price) => (
                    <tr
                      key={price.id}
                      className="group hover:bg-primary/5 transition-all duration-300"
                    >
                      <td className="py-4 px-6">
                        <span className="font-bold text-foreground group-hover:text-primary transition-colors text-base tracking-tight">
                          {price.commodity?.name || "Unknown Commodity"}
                        </span>
                      </td>
                      <td className="py-4 px-6 hidden sm:table-cell">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-tighter border ${categoryColors[price.commodity?.category || ""] || "bg-muted text-muted-foreground border-border"}`}>
                          {price.commodity?.category || "Industrial"}
                        </span>
                      </td>
                      <td className="py-4 px-6 text-right">
                        <div className="inline-flex flex-col items-end">
                          <span className="font-black text-base tabular-nums text-foreground">
                            ₱{price.price_prevailing?.toFixed(2) || "N/A"}
                          </span>
                        </div>
                      </td>
                      <td className="py-4 px-6 text-right hidden md:table-cell">
                        <span className="text-xs font-black text-foreground/80 tabular-nums bg-muted/80 px-2 py-1 rounded-lg border border-border">
                          ₱{price.price_low?.toFixed(2) || "0.00"} - ₱{price.price_high?.toFixed(2) || "0.00"}
                        </span>
                      </td>
                      <td className="py-4 px-6 hidden lg:table-cell">
                        <span className="text-xs font-black text-foreground/70 flex items-center gap-2">
                          <div className="size-2 rounded-full bg-primary shadow-sm" />
                          {price.market?.name || "Metro Manila"}
                        </span>
                      </td>
                    </tr>
                  ))}
                  {paginated.length === 0 && (
                    <tr>
                      <td colSpan={5} className="py-32 text-center">
                        <div className="flex flex-col items-center gap-4 opacity-30">
                          <Search className="size-12" />
                          <p className="font-black uppercase tracking-widest text-xs">No matching price trails found</p>
                        </div>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="flex items-center justify-between p-6 bg-muted/10 border-t border-border/50">
              <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">
                Displaying {filtered.length > 0 ? (page - 1) * perPage + 1 : 0}-{Math.min(page * perPage, filtered.length)} of {filtered.length} entries
              </p>
              <div className="flex items-center gap-3">
                <Button
                  variant="outline"
                  size="sm"
                  className="rounded-xl border-border/50 bg-background/50 backdrop-blur-sm font-bold active:scale-95 transition-all h-9"
                  disabled={page === 1}
                  onClick={() => setPage((p) => p - 1)}
                >
                  <ChevronLeft className="size-4 mr-1" /> Prev
                </Button>
                <div className="px-4 py-1.5 bg-background/50 rounded-lg text-xs font-black ring-1 ring-border/50">
                  {page} <span className="text-muted-foreground/50 mx-1">/</span> {totalPages}
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  className="rounded-xl border-border/50 bg-background/50 backdrop-blur-sm font-bold active:scale-95 transition-all h-9"
                  disabled={page === totalPages}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Next <ChevronRight className="size-4 ml-1" />
                </Button>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}
