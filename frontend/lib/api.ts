const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

export async function fetchCommodities(category?: string) {
  const url = category && category !== "all"
    ? `${API_BASE_URL}/commodities?category=${encodeURIComponent(category)}`
    : `${API_BASE_URL}/commodities`

  const response = await fetch(url)
  if (!response.ok) throw new Error("Failed to fetch commodities")
  return response.json()
}

export async function fetchMarkets() {
  const response = await fetch(`${API_BASE_URL}/markets`)
  if (!response.ok) throw new Error("Failed to fetch markets")
  return response.json()
}

export async function fetchPrices(date?: string) {
  const url = date ? `${API_BASE_URL}/prices/daily?report_date=${date}` : `${API_BASE_URL}/prices/daily`
  const response = await fetch(url)
  if (!response.ok) throw new Error("Failed to fetch prices")
  return response.json()
}

export async function fetchHistory(commodityId: string, limit: number = 30) {
  const response = await fetch(`${API_BASE_URL}/trends/history/${commodityId}?limit=${limit}`)
  if (!response.ok) throw new Error("Failed to fetch history")
  return response.json()
}

export async function fetchStats() {
  // This seems unused or incorrect in original code, ignoring for now or mapping to new endpoint if needed
  // Keeping original signature if something uses it, but implementing new one below
  const response = await fetch(`${API_BASE_URL}/stats/dashboard`)
  if (!response.ok) throw new Error("Failed to fetch stats")
  return response.json()
}

export async function fetchDashboardStats() {
  const response = await fetch(`${API_BASE_URL}/stats/dashboard`)
  if (!response.ok) throw new Error("Failed to fetch dashboard stats")
  return response.json()
}
