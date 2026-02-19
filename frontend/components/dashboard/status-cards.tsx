"use client"

import { Server, Clock, Cpu, Database } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import type { Measurement } from "@/lib/types"

interface StatusCardsProps {
  /** Latest measurement data for all nodes */
  measurements: Measurement[]
}

/**
 * Displays key system status indicators as cards.
 * Shows ServerState with color coding and current time.
 */
export function StatusCards({ measurements }: StatusCardsProps) {
  /* Find key system measurements by name */
  const serverState = measurements.find((m) => m.name === "ServerState")
  const currentTime = measurements.find((m) => m.name === "CurrentTime")
  const serverStatus = measurements.find((m) => m.name === "ServerStatus")

  /* Determine server running state: value 0 = Running in OPC UA */
  const isRunning = serverState?.value === 0 || serverState?.value === "0"

  /* Format the current time from the OPC UA server */
  const formattedCurrentTime = currentTime?.value
    ? new Date(String(currentTime.value)).toLocaleString("en-US", {
        dateStyle: "medium",
        timeStyle: "medium",
      })
    : "N/A"

  /* Count total nodes by category */
  const systemCount = measurements.filter((m) => m.category === "system").length
  const sensorCount = measurements.filter((m) => m.category !== "system").length

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {/* Server State Card */}
      <Card className="border-l-4 py-4" style={{ borderLeftColor: isRunning ? "var(--success)" : "var(--destructive)" }}>
        <CardContent className="flex items-center gap-4">
          <div
            className="flex size-11 items-center justify-center rounded-lg"
            style={{
              backgroundColor: isRunning
                ? "oklch(0.72 0.19 155 / 0.12)"
                : "oklch(0.60 0.22 25 / 0.12)",
            }}
          >
            <Server
              className="size-5"
              style={{
                color: isRunning ? "var(--success)" : "var(--destructive)",
              }}
            />
          </div>
          <div className="flex-1">
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Server State
            </p>
            <p
              className="text-lg font-semibold"
              style={{
                color: isRunning ? "var(--success)" : "var(--destructive)",
              }}
            >
              {isRunning ? "Running" : serverState ? "Stopped" : "Unknown"}
            </p>
          </div>
          {/* Pulsing dot for running status */}
          {isRunning && (
            <span className="relative flex size-3">
              <span
                className="absolute inline-flex size-full animate-ping rounded-full opacity-75"
                style={{ backgroundColor: "var(--success)" }}
              />
              <span
                className="relative inline-flex size-3 rounded-full"
                style={{ backgroundColor: "var(--success)" }}
              />
            </span>
          )}
        </CardContent>
      </Card>

      {/* Current Time Card */}
      <Card className="border-l-4 border-l-primary py-4">
        <CardContent className="flex items-center gap-4">
          <div className="flex size-11 items-center justify-center rounded-lg bg-primary/10">
            <Clock className="size-5 text-primary" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Server Time
            </p>
            <p className="truncate font-mono text-sm font-semibold text-foreground">
              {formattedCurrentTime}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* System Nodes Count */}
      <Card className="border-l-4 py-4" style={{ borderLeftColor: "var(--chart-2)" }}>
        <CardContent className="flex items-center gap-4">
          <div
            className="flex size-11 items-center justify-center rounded-lg"
            style={{ backgroundColor: "oklch(0.65 0.18 250 / 0.12)" }}
          >
            <Cpu className="size-5" style={{ color: "var(--chart-2)" }} />
          </div>
          <div className="flex-1">
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              System Nodes
            </p>
            <p className="text-lg font-semibold text-foreground">
              {systemCount}
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Sensor Nodes Count */}
      <Card className="border-l-4 py-4" style={{ borderLeftColor: "var(--warning)" }}>
        <CardContent className="flex items-center gap-4">
          <div
            className="flex size-11 items-center justify-center rounded-lg"
            style={{ backgroundColor: "oklch(0.80 0.16 85 / 0.12)" }}
          >
            <Database className="size-5" style={{ color: "var(--warning)" }} />
          </div>
          <div className="flex-1">
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              Sensor Nodes
            </p>
            <p className="text-lg font-semibold text-foreground">
              {sensorCount}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
