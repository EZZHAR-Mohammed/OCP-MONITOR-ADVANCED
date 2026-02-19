"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  type TooltipProps,
} from "recharts"
import { BarChart3, TrendingUp } from "lucide-react"
import type { OpcNode, Measurement } from "@/lib/types"
import { fetchNodeHistory } from "@/lib/api"

interface HistoryChartProps {
  /** List of available OPC UA nodes for the dropdown selector */
  nodes: OpcNode[]
}

/**
 * Historical data chart with node selector dropdown.
 * Fetches and displays time-series data for the selected OPC UA node.
 */
export function HistoryChart({ nodes }: HistoryChartProps) {
  const [selectedNodeId, setSelectedNodeId] = useState<string>("")
  const [historyData, setHistoryData] = useState<Measurement[]>([])
  const [isLoading, setIsLoading] = useState(false)

  /** Load history data when the selected node changes */
  const loadHistory = useCallback(async (nodeDbId: number) => {
    setIsLoading(true)
    const data = await fetchNodeHistory(nodeDbId, 100)
    if (data) {
      /* Reverse to show oldest-to-newest for chart continuity */
      setHistoryData(data.reverse())
    }
    setIsLoading(false)
  }, [])

  useEffect(() => {
    if (!selectedNodeId) return
    /* Find the database ID for the selected node */
    const node = nodes.find((n) => n.node_id === selectedNodeId)
    if (node) {
      loadHistory(node.id)
    }
  }, [selectedNodeId, nodes, loadHistory])

  /** Transform measurements to chart-friendly data points */
  const chartData = historyData
    .filter((d) => d.value !== null && !isNaN(Number(d.value)))
    .map((d) => ({
      time: new Date(d.timestamp).toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      }),
      value: Number(d.value),
      fullTime: d.readable_time,
    }))

  const selectedNode = nodes.find((n) => n.node_id === selectedNodeId)

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <CardTitle className="flex items-center gap-2 text-base">
            <TrendingUp className="size-4 text-primary" />
            Historical Data
          </CardTitle>

          {/* Node selector dropdown */}
          <Select value={selectedNodeId} onValueChange={setSelectedNodeId}>
            <SelectTrigger className="w-full sm:w-[260px] bg-secondary border-border">
              <SelectValue placeholder="Select a node..." />
            </SelectTrigger>
            <SelectContent>
              {nodes.map((node) => (
                <SelectItem key={node.node_id} value={node.node_id}>
                  <span className="flex items-center gap-2">
                    <BarChart3 className="size-3.5 text-muted-foreground" />
                    {node.name}
                    {node.unit && (
                      <span className="text-muted-foreground">({node.unit})</span>
                    )}
                  </span>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </CardHeader>

      <CardContent>
        {!selectedNodeId ? (
          /* Empty state: no node selected */
          <div className="flex h-[320px] flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-border">
            <BarChart3 className="size-10 text-muted-foreground/40" />
            <p className="text-sm text-muted-foreground">
              Select a node to view its historical data
            </p>
          </div>
        ) : isLoading ? (
          /* Loading state */
          <div className="flex h-[320px] items-center justify-center">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <div className="size-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
              Loading history...
            </div>
          </div>
        ) : chartData.length === 0 ? (
          /* No data state */
          <div className="flex h-[320px] flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-border">
            <BarChart3 className="size-10 text-muted-foreground/40" />
            <p className="text-sm text-muted-foreground">
              No numerical data available for this node
            </p>
          </div>
        ) : (
          /* Chart display */
          <div className="h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="var(--border)"
                  opacity={0.5}
                />
                <XAxis
                  dataKey="time"
                  tick={{ fill: "var(--muted-foreground)", fontSize: 11 }}
                  stroke="var(--border)"
                  tickLine={false}
                  interval="preserveStartEnd"
                />
                <YAxis
                  tick={{ fill: "var(--muted-foreground)", fontSize: 11 }}
                  stroke="var(--border)"
                  tickLine={false}
                  axisLine={false}
                  width={60}
                  tickFormatter={(v: number) =>
                    v >= 1_000_000
                      ? `${(v / 1_000_000).toFixed(1)}M`
                      : v >= 1_000
                        ? `${(v / 1_000).toFixed(1)}K`
                        : String(v)
                  }
                />
                <Tooltip content={<CustomTooltip unit={selectedNode?.unit ?? ""} />} />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="var(--primary)"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{
                    r: 4,
                    fill: "var(--primary)",
                    stroke: "var(--card)",
                    strokeWidth: 2,
                  }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

/**
 * Custom tooltip component for the Recharts line chart.
 * Displays the full timestamp and formatted value with unit.
 */
function CustomTooltip({
  active,
  payload,
  unit,
}: TooltipProps<number, string> & { unit: string }) {
  if (!active || !payload?.length) return null

  const data = payload[0]
  const fullTime = data.payload?.fullTime

  return (
    <div className="rounded-lg border border-border bg-card px-3 py-2 shadow-lg">
      <p className="mb-1 font-mono text-xs text-muted-foreground">{fullTime}</p>
      <p className="font-mono text-sm font-semibold text-primary">
        {typeof data.value === "number" ? data.value.toLocaleString() : data.value}
        {unit ? ` ${unit}` : ""}
      </p>
    </div>
  )
}
