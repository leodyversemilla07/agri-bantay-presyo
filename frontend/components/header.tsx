"use client"

import { Bell, Menu, Sprout } from "lucide-react"
import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-2 md:gap-4">
            <div className="flex size-9 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-sm">
              <Sprout className="size-5" />
            </div>
            <div className="flex flex-col gap-0.5">
              <h1 className="text-lg font-bold leading-none tracking-tight text-foreground md:text-xl">
                Agri Bantay Presyo
              </h1>
              <p className="text-[10px] font-medium text-muted-foreground uppercase tracking-wide md:text-xs">
                Official Price Monitoring
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" className="hidden md:flex text-muted-foreground hover:text-primary gap-2">
              <span className="text-xs uppercase tracking-widest font-semibold">Official Monitoring</span>
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}
