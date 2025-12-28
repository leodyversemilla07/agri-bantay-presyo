import { Header } from "@/components/header"
import { Hero } from "@/components/hero"
import { PriceTicker } from "@/components/price-ticker"
import { Dashboard } from "@/components/dashboard"

export default function Home() {
  return (
    <div className="min-h-screen bg-background font-sans">
      <main>
        <Hero />
        <PriceTicker />
        <div className="container mx-auto px-4 py-6">
          <Dashboard />
        </div>
      </main>
    </div>
  )
}
