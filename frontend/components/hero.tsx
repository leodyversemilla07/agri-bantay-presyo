import { Search } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

export function Hero() {
    return (
        <section className="relative overflow-hidden bg-primary/5 py-10">
            {/* Background Pattern */}
            <div className="absolute inset-0 z-0 opacity-10"
                style={{ backgroundImage: 'radial-gradient(circle at 1px 1px, #1a4d2e 1px, transparent 0)', backgroundSize: '40px 40px' }}>
            </div>

            <div className="container relative z-10 mx-auto px-4 text-center">
                <div className="mx-auto max-w-2xl space-y-4">
                    <h1 className="text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl">
                        Agri Bantay Presyo
                    </h1>

                    <p className="text-muted-foreground">
                        Monitoring the <span className="font-semibold text-foreground/80">Daily Retail Price Range</span> for Metro Manila markets.
                        <br />
                        <span className="text-xs font-medium text-muted-foreground/80">
                            Data source: <a href="https://www.da.gov.ph/price-monitoring/" target="_blank" rel="noopener noreferrer" className="text-primary underline decoration-primary/30 underline-offset-2 hover:decoration-primary transition-all">Department of Agriculture (DA) Price Groups</a>
                        </span>
                    </p>

                    <div className="mx-auto mt-6 flex max-w-lg items-center space-x-2 rounded-xl border bg-background p-1.5 shadow-sm">
                        <Search className="ml-3 h-4 w-4 text-muted-foreground" />
                        <Input
                            type="text"
                            placeholder="Find price for (e.g. Rice, Onion)..."
                            className="border-0 focus-visible:ring-0 focus-visible:ring-offset-0 h-9"
                        />
                        <Button size="sm">Search</Button>
                    </div>
                </div>
            </div>
        </section>
    )
}
