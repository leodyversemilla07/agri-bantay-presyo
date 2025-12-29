"use client"

import { Search, Wheat } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useState } from "react"
import { useRouter } from "next/navigation"

export function Hero() {
    const [query, setQuery] = useState("")
    const router = useRouter()

    const handleSearch = () => {
        if (query.trim()) {
            router.push(`/analytics?q=${encodeURIComponent(query)}`)
        }
    }

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter") {
            handleSearch()
        }
    }

    return (
        <section className="relative overflow-hidden pt-24 pb-28 border-b border-border/40 bg-zinc-50/50">
            {/* Minimal Background Glow */}
            <div className="absolute inset-0 z-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent" />

            <div className="container relative z-10 mx-auto px-4">
                <div className="mx-auto max-w-3xl space-y-10 text-center">
                    <div className="mx-auto inline-flex items-center gap-2">
                        <a
                            href="https://www.da.gov.ph/price-monitoring/"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="group flex items-center gap-2 rounded-full border border-primary/20 bg-white px-4 py-1.5 text-xs font-bold text-primary shadow-sm transition-all hover:bg-primary/5 hover:border-primary/40 active:scale-95"
                        >
                            <Wheat className="size-3" />
                            <span className="opacity-70">Source:</span>
                            <span className="font-black group-hover:underline">Department of Agriculture Price Watch</span>
                        </a>
                    </div>

                    <div className="space-y-4">
                        <h1 className="text-4xl font-black tracking-tight text-foreground sm:text-6xl lg:text-7xl">
                            Agri <span className="text-primary italic">Bantay</span> Presyo
                        </h1>

                        <p className="mx-auto max-w-xl text-lg text-foreground/80 leading-relaxed font-bold">
                            An independent, community-driven monitoring project tracking
                            <span className="text-foreground font-black px-1 underline decoration-primary/40 underline-offset-4 mx-1">Daily Retail Prices</span>
                            across Metro Manila's major trading hubs.
                        </p>
                    </div>

                    <div className="mx-auto mt-8 flex max-w-xl items-center gap-2 rounded-2xl border border-primary/20 bg-background p-2 shadow-2xl ring-1 ring-black/5">
                        <div className="flex flex-1 items-center px-4 gap-3">
                            <Search className="h-5 w-5 text-foreground/50" />
                            <Input
                                type="text"
                                placeholder="Track any commodity price (e.g. Rice, Onion)..."
                                className="border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0 h-10 text-base font-bold placeholder:text-foreground/40"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                onKeyDown={handleKeyDown}
                            />
                        </div>
                        <Button
                            size="lg"
                            className="rounded-xl px-8 font-black shadow-lg shadow-primary/20 transition-all hover:scale-105 active:scale-95"
                            onClick={handleSearch}
                        >
                            Search
                        </Button>
                    </div>
                </div>
            </div>
        </section>
    )
}
