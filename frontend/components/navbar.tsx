"use client"

import Link from "next/link"
import Image from "next/image"
import { usePathname } from "next/navigation"
import { LayoutDashboard, Table, BarChart3 } from "lucide-react"

export function Navbar() {
    const pathname = usePathname()

    const links = [
        { href: "/", label: "Overview", icon: LayoutDashboard },
        { href: "/markets", label: "Market Data", icon: Table },
        { href: "/analytics", label: "Deep Analytics", icon: BarChart3 },
    ]

    return (
        <nav className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/80 backdrop-blur-xl">
            <div className="container mx-auto px-4">
                <div className="flex h-16 items-center justify-between">
                    <div className="flex items-center gap-6">
                        <Link href="/" className="flex items-center gap-2 group">
                            <div className="size-10 flex items-center justify-center transition-transform group-hover:scale-105">
                                <Image
                                    src="/logo.svg"
                                    alt="Agri Bantay Presyo Logo"
                                    width={40}
                                    height={40}
                                    className="w-full h-full object-contain"
                                />
                            </div>
                            <span className="font-black text-lg tracking-tighter">
                                Agri <span className="text-primary italic">Bantay</span>
                            </span>
                        </Link>

                        <div className="hidden md:flex items-center gap-1 ml-4">
                            {links.map((link) => {
                                const Icon = link.icon
                                const isActive = pathname === link.href
                                return (
                                    <Link
                                        key={link.href}
                                        href={link.href}
                                        className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold transition-all active:scale-95 ${isActive
                                            ? "bg-primary text-primary-foreground shadow-lg shadow-primary/20"
                                            : "text-foreground/60 hover:text-foreground hover:bg-muted"
                                            }`}
                                    >
                                        <Icon className="size-4" />
                                        {link.label}
                                    </Link>
                                )
                            })}
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <div className="hidden sm:flex flex-col items-end mr-2">
                            <span className="text-[10px] font-black text-primary uppercase tracking-widest leading-none">Status</span>
                            <span className="text-xs font-bold text-foreground/60">System Online</span>
                        </div>
                        <div className="size-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_12px_rgba(16,185,129,0.5)]" />
                    </div>
                </div>
            </div>

            {/* Mobile nav indicator - just a simple underline for now */}
            <div className="md:hidden flex h-12 bg-muted/30 border-t border-border/20 px-4 overflow-x-auto gap-4 items-center no-scrollbar">
                {links.map((link) => {
                    const isActive = pathname === link.href
                    return (
                        <Link
                            key={link.href}
                            href={link.href}
                            className={`text-xs font-black uppercase tracking-widest whitespace-nowrap px-2 pb-1 border-b-2 transition-all ${isActive ? "border-primary text-primary" : "border-transparent text-foreground/40"
                                }`}
                        >
                            {link.label}
                        </Link>
                    )
                })}
            </div>
        </nav>
    )
}
