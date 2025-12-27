import { Header } from "@/components/header"
import { PriceTicker } from "@/components/price-ticker"
import { Dashboard } from "@/components/dashboard"

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <PriceTicker />
      <main className="container mx-auto px-4 py-6">
        <Dashboard />
      </main>
    </div>
  )
}
