import type React from "react"
import type { Metadata } from "next"
import { Plus_Jakarta_Sans, Geist_Mono } from "next/font/google"
import { Analytics } from "@vercel/analytics/next"
import { Navbar } from "@/components/navbar"
import "./globals.css"

const plusJakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-plus-jakarta",
  display: "swap",
})

const geistMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-geist-mono",
  display: "swap",
})

export const metadata: Metadata = {
  title: "Agri Bantay Presyo - Agricultural Price Monitoring",
  description:
    "An independent, community-driven agricultural price monitoring project for Philippine farm commodities. Track real-time market trends and historical data.",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`${plusJakarta.variable} ${geistMono.variable} font-sans antialiased text-foreground bg-background`}>
        <Navbar />
        {children}
        <Analytics />
      </body>
    </html>
  )
}
