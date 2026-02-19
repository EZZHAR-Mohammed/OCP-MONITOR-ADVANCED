const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"

async function fetchApi<T>(endpoint: string): Promise<T | null> {
  try {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 8000)

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      cache: "no-store",
      signal: controller.signal,
    })

    clearTimeout(timeoutId)

    if (!response.ok) {
      console.error(`❌ API error ${response.status} ${response.statusText} → ${endpoint}`)
      return null
    }

    return (await response.json()) as T
  } catch (error: any) {
    if (error.name === "AbortError") {
      console.error(`⏱️ Timeout API → ${endpoint}`)
    } else {
      console.error(`❌ Fetch failed → ${endpoint}`, error)
    }
    return null
  }
}

export async function fetchNodes() {
  return fetchApi<
    Array<{
      id: number
      node_id: string
      name: string
      category: "system" | "sensor"
      unit: string
    }>
  >("/nodes")
}

export async function fetchLatestMeasurements(limit: number = 50) {
  return fetchApi<
    Array<{
      name: string
      node_id: string
      category: "system" | "sensor"
      unit: string
      numeric_value: number | null
      text_value: string | null
      timestamp: string
      readable_time: string | null
    }>
  >(`/measurements/latest?limit=${limit}`)
}

export async function fetchNodeHistory(nodeId: number, limit = 100) {
  return fetchApi<
    Array<{
      id: number
      name: string
      node_id: string
      category: "system" | "sensor"
      unit: string
      numeric_value: number | null
      text_value: string | null
      timestamp: string
      readable_time: string | null
    }>
  >(`/measurements/${nodeId}?limit=${limit}`)
}