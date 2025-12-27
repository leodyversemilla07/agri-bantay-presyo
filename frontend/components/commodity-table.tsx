"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { TrendingUp, TrendingDown, Search, ChevronLeft, ChevronRight, Minus } from "lucide-react"
import { useState } from "react"

const commodities = [
  { id: 1, name: "Rice (Well-Milled)", category: "Grains", price: 52.5, change: 2.3, market: "Divisoria" },
  { id: 2, name: "Rice (Regular)", category: "Grains", price: 46.0, change: 1.8, market: "Balintawak" },
  { id: 3, name: "Galunggong", category: "Fish", price: 180.0, change: -1.5, market: "Navotas" },
  { id: 4, name: "Tilapia", category: "Fish", price: 140.0, change: 0.8, market: "Farmers" },
  { id: 5, name: "Bangus", category: "Fish", price: 200.0, change: 2.1, market: "Navotas" },
  { id: 6, name: "Pork Kasim", category: "Meat", price: 320.0, change: -0.5, market: "Balintawak" },
  { id: 7, name: "Pork Liempo", category: "Meat", price: 380.0, change: 1.2, market: "Farmers" },
  { id: 8, name: "Chicken (Whole)", category: "Poultry", price: 185.0, change: 1.2, market: "Divisoria" },
  { id: 9, name: "Egg (Medium)", category: "Eggs", price: 8.5, change: 3.5, market: "Balintawak" },
  { id: 10, name: "Tomato", category: "Vegetables", price: 80.0, change: -5.2, market: "Divisoria" },
  { id: 11, name: "Onion (Red)", category: "Vegetables", price: 120.0, change: -2.1, market: "Farmers" },
  { id: 12, name: "Garlic (Local)", category: "Vegetables", price: 180.0, change: 0.0, market: "Balintawak" },
]

const categoryColors: Record<string, string> = {
  Grains: "bg-amber-100 text-amber-800",
  Fish: "bg-blue-100 text-blue-800",
  Meat: "bg-red-100 text-red-800",
  Poultry: "bg-orange-100 text-orange-800",
  Eggs: "bg-yellow-100 text-yellow-800",
  Vegetables: "bg-green-100 text-green-800",
  Fruits: "bg-pink-100 text-pink-800",
}

interface CommodityTableProps {
  market: string
}

export function CommodityTable({ market }: CommodityTableProps) {
  const [search, setSearch] = useState("")
  const [page, setPage] = useState(1)
  const perPage = 8

  const filtered = commodities.filter(
    (c) =>
      (market === "all" || c.market.toLowerCase().includes(market.toLowerCase())) &&
      c.name.toLowerCase().includes(search.toLowerCase()),
  )

  const totalPages = Math.ceil(filtered.length / perPage)
  const paginated = filtered.slice((page - 1) * perPage, page * perPage)

  return (
    <Card className="bg-card border-border shadow-sm">
      <CardHeader className="pb-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <CardTitle className="text-base font-semibold text-foreground">Latest Commodity Prices</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">Updated as of December 27, 2025</p>
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
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border bg-muted/30">
                <th className="text-left py-3 px-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Commodity
                </th>
                <th className="text-left py-3 px-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider hidden sm:table-cell">
                  Category
                </th>
                <th className="text-right py-3 px-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Price/kg
                </th>
                <th className="text-right py-3 px-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Change
                </th>
                <th className="text-left py-3 px-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider hidden md:table-cell">
                  Market
                </th>
              </tr>
            </thead>
            <tbody>
              {paginated.map((commodity) => (
                <tr
                  key={commodity.id}
                  className="border-b border-border/50 hover:bg-muted/30 transition-colors cursor-pointer"
                >
                  <td className="py-3.5 px-4">
                    <span className="text-sm font-medium text-foreground">{commodity.name}</span>
                  </td>
                  <td className="py-3.5 px-4 hidden sm:table-cell">
                    <Badge
                      variant="secondary"
                      className={`text-xs font-medium ${categoryColors[commodity.category] || ""}`}
                    >
                      {commodity.category}
                    </Badge>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <span className="text-sm font-mono font-semibold text-foreground">
                      ₱{commodity.price.toFixed(2)}
                    </span>
                  </td>
                  <td className="py-3.5 px-4 text-right">
                    <span
                      className={`inline-flex items-center gap-1 text-sm font-semibold px-2 py-0.5 rounded-full ${
                        commodity.change > 0
                          ? "text-primary bg-primary/10"
                          : commodity.change < 0
                            ? "text-destructive bg-destructive/10"
                            : "text-muted-foreground bg-muted"
                      }`}
                    >
                      {commodity.change > 0 ? (
                        <TrendingUp className="size-3" />
                      ) : commodity.change < 0 ? (
                        <TrendingDown className="size-3" />
                      ) : (
                        <Minus className="size-3" />
                      )}
                      {commodity.change > 0 ? "+" : ""}
                      {commodity.change}%
                    </span>
                  </td>
                  <td className="py-3.5 px-4 hidden md:table-cell">
                    <span className="text-sm text-muted-foreground">{commodity.market}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="flex items-center justify-between mt-4 pt-4 border-t border-border">
          <p className="text-sm text-muted-foreground">
            Showing {(page - 1) * perPage + 1}-{Math.min(page * perPage, filtered.length)} of {filtered.length}
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
      </CardContent>
    </Card>
  )
}
