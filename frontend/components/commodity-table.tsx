"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { TrendingUp, TrendingDown, Search, ChevronLeft, ChevronRight, Minus, Loader2 } from "lucide-react"
import { useState, useEffect } from "react"
import { fetchPrices } from "@/lib/api"

const categoryColors: Record<string, string> = {
  Rice: "bg-amber-100 text-amber-800",
  Grains: "bg-amber-100 text-amber-800",
  Fish: "bg-blue-100 text-blue-800",
  Meat: "bg-rose-100 text-rose-800",
  Poultry: "bg-orange-100 text-orange-800",
  Eggs: "bg-yellow-100 text-yellow-800",
  Vegetables: "bg-emerald-100 text-emerald-800",
  Fruits: "bg-pink-100 text-pink-800",
  Spices: "bg-red-100 text-red-800",
  "Sugar": "bg-stone-100 text-stone-800",
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
  const perPage = 8

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
    <Card className="bg-card border-border shadow-sm">
      <CardHeader className="pb-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <CardTitle className="text-base font-semibold text-foreground">Latest Commodity Prices</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              {prices.length > 0 ? `Updated as of ${new Date(prices[0].report_date).toLocaleDateString()}` : "Loading latest prices..."}
            </p>
          </div>
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
            <Input
              placeholder="Search commodities..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 bg-background border-border h-10"
            />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 gap-4">
            <Loader2 className="size-8 animate-spin text-primary" />
            <p className="text-sm text-muted-foreground font-medium">Fetching real-time price data...</p>
          </div>
        ) : (
          <>
            <div className="overflow-hidden rounded-md border border-border">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-muted/50 border-b border-border">
                    <th className="text-left h-10 px-4 font-medium text-muted-foreground uppercase text-[11px] tracking-wider w-[240px]">
                      Commodity
                    </th>
                    <th className="text-left h-10 px-4 font-medium text-muted-foreground uppercase text-[11px] tracking-wider hidden sm:table-cell">
                      Category
                    </th>
                    <th className="text-right h-10 px-4 font-medium text-muted-foreground uppercase text-[11px] tracking-wider">
                      Prevailing Price
                    </th>
                    <th className="text-right h-10 px-4 font-medium text-muted-foreground uppercase text-[11px] tracking-wider hidden md:table-cell">
                      Daily Range (Low-High)
                    </th>
                    <th className="text-left h-10 px-4 font-medium text-muted-foreground uppercase text-[11px] tracking-wider hidden lg:table-cell">
                      Market Location
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {paginated.map((price) => (
                    <tr
                      key={price.id}
                      className="hover:bg-muted/30 transition-colors"
                    >
                      <td className="py-3 px-4 font-medium text-foreground">
                        {price.commodity?.name || "Unknown"}
                      </td>
                      <td className="py-3 px-4 hidden sm:table-cell">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded textxs font-medium ${categoryColors[price.commodity?.category || ""] || "bg-gray-100 text-gray-800"}`}>
                          {price.commodity?.category || "Other"}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <span className="font-mono font-bold text-foreground">
                          ₱{price.price_prevailing?.toFixed(2) || "N/A"}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right hidden md:table-cell text-muted-foreground font-mono text-xs">
                        ₱{price.price_low?.toFixed(2) || "0.00"} - ₱{price.price_high?.toFixed(2) || "0.00"}
                      </td>
                      <td className="py-3 px-4 hidden lg:table-cell text-muted-foreground">
                        {price.market?.name || "N/A"}
                      </td>
                    </tr>
                  ))}
                  {paginated.length === 0 && (
                    <tr>
                      <td colSpan={5} className="py-16 text-center text-muted-foreground">
                        <div className="flex flex-col items-center gap-2">
                          <Search className="size-8 text-muted-foreground/30" />
                          <p>No price data found matching your filters.</p>
                        </div>
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            <div className="flex items-center justify-between mt-4 pt-4 border-t border-border">
              <p className="text-sm text-muted-foreground">
                Showing {filtered.length > 0 ? (page - 1) * perPage + 1 : 0}-{Math.min(page * perPage, filtered.length)} of {filtered.length}
              </p>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="icon"
                  className="size-8 bg-transparent"
                  disabled={page === 1}
                  onClick={() => setPage((p) => p - 1)}
                >
                  <ChevronLeft className="size-4" />
                </Button>
                <span className="text-sm font-medium text-foreground px-2">
                  {page} of {totalPages}
                </span>
                <Button
                  variant="outline"
                  size="icon"
                  className="size-8 bg-transparent"
                  disabled={page === totalPages}
                  onClick={() => setPage((p) => p + 1)}
                >
                  <ChevronRight className="size-4" />
                </Button>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}
