"use client"

import { Activity, Wifi, WifiOff, RefreshCw } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface DashboardHeaderProps {
  /** Whether the API connection is active */
  isConnected: boolean
  /** ISO timestamp of the last successful data refresh */
  lastRefresh: string | null
}

/**
 * Dashboard header with title, connection status, and last refresh time.
 * Displays a pulsing indicator when connected to the OPC UA backend.
 */
export function DashboardHeader({ isConnected, lastRefresh }: DashboardHeaderProps) {
  const formattedTime = lastRefresh
    ? new Date(lastRefresh).toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      })
    : "--:--:--"

  return (
    <header className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
      <div className="flex items-center gap-3">
        <div className="flex items-center justify-center rounded-lg bg-primary/10 p-2.5">
          <Activity className="size-6 text-primary" />
        </div>
        <div>
          <h1 className="text-xl font-semibold tracking-tight text-foreground">
            OPC UA Industrial Monitor
          </h1>
          <p className="text-sm text-muted-foreground">
            Real-time system and sensor monitoring
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Last refresh indicator */}
        <div className="flex items-center gap-2 rounded-md border border-border bg-secondary px-3 py-1.5">
          <RefreshCw className="size-3.5 text-muted-foreground" />
          <span className="font-mono text-xs text-muted-foreground">
            {formattedTime}
          </span>
        </div>

        {/* Connection status badge */}
        <Badge
          className={
            isConnected
              ? "bg-success/15 text-success border-success/30"
              : "bg-destructive/15 text-destructive border-destructive/30"
          }
          variant="outline"
        >
          {isConnected ? (
            <>
              <span className="relative mr-1.5 flex size-2">
                <span className="absolute inline-flex size-full animate-ping rounded-full bg-success opacity-75" />
                <span className="relative inline-flex size-2 rounded-full bg-success" />
              </span>
              <Wifi className="mr-1 size-3.5" />
              Connected
            </>
          ) : (
            <>
              <WifiOff className="mr-1 size-3.5" />
              Disconnected
            </>
          )}
        </Badge>
      </div>
    </header>
  )
}
