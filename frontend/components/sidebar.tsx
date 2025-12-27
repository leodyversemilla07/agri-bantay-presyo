"use client"

import { cn } from "@/lib/utils"
import { Wheat, Fish, Drumstick, Beef, Carrot, Apple, Egg, ChevronRight, Sprout } from "lucide-react"

const categories = [
  { id: "all", name: "All Commodities", icon: Sprout, count: 115 },
  { id: "rice", name: "Rice & Grains", icon: Wheat, count: 12 },
  { id: "fish", name: "Fish & Seafood", icon: Fish, count: 24 },
  { id: "poultry", name: "Poultry", icon: Drumstick, count: 8 },
  { id: "meat", name: "Meat", icon: Beef, count: 15 },
  { id: "vegetables", name: "Vegetables", icon: Carrot, count: 32 },
  { id: "fruits", name: "Fruits", icon: Apple, count: 18 },
  { id: "eggs", name: "Eggs & Dairy", icon: Egg, count: 6 },
]

interface SidebarProps {
  selectedCommodity: string
  onSelectCommodity: (id: string) => void
}

export function Sidebar({ selectedCommodity, onSelectCommodity }: SidebarProps) {
  return (
    <aside className="hidden lg:block w-64 shrink-0">
      <div className="bg-card rounded-xl border border-border p-4 shadow-sm">
        <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4">Categories</h3>
        <nav className="space-y-1">
          {categories.map((category) => {
            const Icon = category.icon
            const isSelected = selectedCommodity === category.id
            return (
              <button
                key={category.id}
                onClick={() => onSelectCommodity(category.id)}
                className={cn(
                  "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors font-medium",
                  isSelected
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground hover:bg-secondary",
                )}
              >
                <Icon className="size-4" />
                <span className="flex-1 text-left">{category.name}</span>
                <span
                  className={cn("text-xs px-1.5 py-0.5 rounded", isSelected ? "bg-primary-foreground/20" : "bg-muted")}
                >
                  {category.count}
                </span>
                {isSelected && <ChevronRight className="size-4" />}
              </button>
            )
          })}
        </nav>
      </div>
    </aside>
  )
}
