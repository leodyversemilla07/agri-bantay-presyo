"use client"

import { TrendingUp, TrendingDown, Minus } from "lucide-react"
import { useEffect, useState } from "react"

const tickerData = [
  { name: "Rice (Well-Milled)", price: 52.5, change: 2.3 },
  { name: "Galunggong", price: 180.0, change: -1.5 },
  { name: "Tilapia", price: 140.0, change: 0.8 },
  { name: "Pork Kasim", price: 320.0, change: -0.5 },
  { name: "Chicken", price: 185.0, change: 1.2 },
  { name: "Egg (Medium)", price: 8.5, change: 3.5 },
  { name: "Tomato", price: 80.0, change: -5.2 },
  { name: "Onion (Red)", price: 120.0, change: -2.1 },
  { name: "Garlic (Local)", price: 180.0, change: 0.0 },
  { name: "Cabbage", price: 60.0, change: 4.2 },
]

export function PriceTicker() {
  const [offset, setOffset] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setOffset((prev) => prev - 1)
    }, 30)
    return () => clearInterval(interval)
  }, [])

  const duplicatedData = [...tickerData, ...tickerData, ...tickerData]

  return (
    <div className="bg-primary/5 border-b border-border overflow-hidden">
      <div
        className="flex items-center gap-8 py-2.5 whitespace-nowrap"
        style={{ transform: `translateX(${offset}px)` }}
      >
        {duplicatedData.map((item, index) => (
          <div key={index} className="flex items-center gap-3 px-4">
            <span className="text-sm font-semibold text-foreground">{item.name}</span>
            <span className="text-sm font-mono font-medium text-foreground">₱{item.price.toFixed(2)}</span>
            <span
              className={`inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full ${
                item.change > 0
                  ? "text-primary bg-primary/10"
                  : item.change < 0
                    ? "text-destructive bg-destructive/10"
                    : "text-muted-foreground bg-muted"
              }`}
            >
              {item.change > 0 ? (
                <TrendingUp className="size-3" />
              ) : item.change < 0 ? (
                <TrendingDown className="size-3" />
              ) : (
                <Minus className="size-3" />
              )}
              {item.change > 0 ? "+" : ""}
              {item.change}%
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
