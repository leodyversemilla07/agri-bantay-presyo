import { Hero } from "@/components/hero"
import { PriceTicker } from "@/components/price-ticker"
import { StatsCards } from "@/components/stats-cards"
import { PriceChart } from "@/components/price-chart"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { ArrowRight, Table } from "lucide-react"

export default function Home() {
  return (
    <div className="min-h-screen bg-background font-sans">
      <main>
        <Hero />
        <PriceTicker />

        <div className="container mx-auto px-4 py-12 space-y-20">
          {/* Executive Overview Section */}
          <section className="space-y-8">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
              <div className="space-y-1">
                <h2 className="text-3xl font-black tracking-tighter">Market Overview</h2>
                <p className="text-foreground/60 font-bold">Consolidated metrics from major trading hubs across the region.</p>
              </div>
              <Link href="/analytics">
                <Button variant="ghost" className="font-black text-primary hover:text-primary hover:bg-primary/10 gap-2">
                  View Full Analytics <ArrowRight className="size-4" />
                </Button>
              </Link>
            </div>
            <StatsCards />
          </section>

          {/* Quick Data Preview Section */}
          <section className="grid lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-6">
              <div className="space-y-1 text-center lg:text-left">
                <h2 className="text-2xl font-black tracking-tight">Price Trends</h2>
                <p className="text-sm font-bold text-foreground/50 uppercase tracking-widest">Local Special Rice (Prevailing)</p>
              </div>
              <div className="h-[400px]">
                <PriceChart commodity="Local Special Rice" dateRange="30d" />
              </div>
            </div>

            <div className="glass-card p-8 rounded-3xl border-none ring-1 ring-primary/20 flex flex-col justify-center gap-6 text-center">
              <div className="size-16 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto">
                <Table className="size-8 text-primary" />
              </div>
              <div className="space-y-2">
                <h3 className="text-xl font-black">Full Market Data</h3>
                <p className="text-sm font-bold text-foreground/60 leading-relaxed">
                  Access the complete inventory of tracked commodities, market ranges, and localized data points.
                </p>
              </div>
              <Link href="/markets" className="pt-4">
                <Button size="lg" className="w-full rounded-2xl font-black shadow-xl shadow-primary/20">
                  Open Market Hub
                </Button>
              </Link>
            </div>
          </section>
        </div>
      </main>
    </div>
  )
}
