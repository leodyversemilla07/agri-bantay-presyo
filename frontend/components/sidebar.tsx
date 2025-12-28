"use client"

import { cn } from "@/lib/utils"
import { Wheat, Fish, Drumstick, Beef, Carrot, Apple, Egg, ChevronRight, Sprout } from "lucide-react"

const categories = [
  { id: "all", name: "All Commodities", icon: Sprout, count: 115 },
  { id: "rice", name: "Rice & Grains", icon: Wheat, count: 12 },
  { id: "fish", name: "Fish & Seafood", icon: Fish, count: 24 },
  { id: "meat", name: "Meat & Poultry", icon: Beef, count: 23 },
  { id: "vegetables", name: "Vegetables", icon: Carrot, count: 32 },
  { id: "fruits", name: "Fruits", icon: Apple, count: 18 },
  { id: "eggs", name: "Eggs", icon: Egg, count: 6 },
]

interface SidebarProps {
  selectedCommodity: string
  onSelectCommodity: (id: string) => void
}

export function Sidebar({ selectedCommodity, onSelectCommodity }: SidebarProps) {
  return (
    <aside className="hidden lg:block w-64 shrink-0">
      <div className="bg-card rounded-xl border border-border p-3 shadow-sm sticky top-24">
        <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3 px-3 mt-1">
          Data Categories
        </h3>
        <nav className="space-y-0.5">
          {categories.map((category) => {
            const Icon = category.icon
            const isSelected = selectedCommodity === category.id
            return (
              <button
                key={category.id}
                onClick={() => onSelectCommodity(category.id)}
                className={cn(
                  "w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-all duration-200 font-medium",
                  isSelected
                    ? "bg-primary text-primary-foreground shadow-md"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted",
                )}
              >
                <Icon className={cn("size-4", isSelected ? "text-primary-foreground" : "text-muted-foreground")} />
                <span className="flex-1 text-left">{category.name}</span>
                {isSelected && <ChevronRight className="size-3.5 opacity-80" />}
              </button>
            )
          })}
        </nav>
      </div>
    </aside>
  )
}
