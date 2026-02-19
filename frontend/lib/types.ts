/**
 * OPC UA Node (monitored variable)
 */
export interface OpcNode {
  id: number
  node_id: string
  name: string
  category: "system" | "sensor"
  unit: string
}

/**
 * Measurement from OPC UA
 * numeric_value OU text_value (jamais les deux)
 */
export interface Measurement {
  name: string
  node_id: string
  category: "system" | "sensor"
  unit: string

  numeric_value: number | null
  text_value: string | null

  timestamp: string
  readable_time: string | null
}

/**
 * Measurement normalisée pour l’UI
 * (utile pour table + cards)
 */
export interface UiMeasurement {
  name: string
  node_id: string
  category: "system" | "sensor"
  unit: string
  value: number | string | null
  timestamp: string
}

/**
 * API health status
 */
export interface ApiStatus {
  status: string
  message: string
}
