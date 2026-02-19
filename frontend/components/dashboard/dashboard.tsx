"use client"

import { useEffect, useState } from "react"
import useSWR from "swr"

import { DashboardHeader } from "./dashboard-header"
import { StatusCards } from "./status-cards"
import { MeasurementsTable } from "./measurements-table"
import { HistoryChart } from "./history-chart"

import { fetchNodes, fetchLatestMeasurements } from "@/lib/api"
import type { OpcNode, Measurement } from "@/lib/types"
import { Skeleton } from "@/components/ui/skeleton"

export function Dashboard() {
  // HOOKS EN PREMIER – SANS CONDITION
  const [mounted, setMounted] = useState(false)
  const [measurements, setMeasurements] = useState<Measurement[]>([])
  const [wsConnected, setWsConnected] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const { data: nodes = [] } = useSWR<OpcNode[] | null>(
    "nodes",
    fetchNodes,
    { refreshInterval: 30000, fallbackData: [] }
  )

  // Chargement initial REST
  useEffect(() => {
    async function loadInitial() {
      try {
        const initialData = await fetchLatestMeasurements(50)
        console.log("Données initiales REST :", initialData?.length || 0, "mesures")
        setMeasurements(initialData || [])
      } catch (err) {
        console.error("Erreur chargement initial REST :", err)
      }
    }
    loadInitial()
  }, [])

  // WebSocket
  useEffect(() => {
    console.log("Tentative connexion WebSocket...")
    const ws = new WebSocket("ws://127.0.0.1:8000/ws/measurements")

    ws.onopen = () => {
      console.log("✅ WebSocket connecté")
      setWsConnected(true)
    }

    ws.onmessage = (event) => {
      console.log("Message WS reçu :", event.data)
      try {
        const msg = JSON.parse(event.data)
        console.log("Message parsé :", msg.type)

        if (msg.type === "initial" && Array.isArray(msg.data)) {
          setMeasurements(msg.data)
        } else if (msg.type === "new_measurement" && msg.data) {
          setMeasurements((prev) => {
            const copy = [...prev]
            const idx = copy.findIndex(m => m.node_id === msg.data.node_id)
            if (idx >= 0) copy[idx] = msg.data
            else copy.push(msg.data)
            return copy
          })
        }
      } catch (err) {
        console.error("Erreur parsing WS :", err)
      }
    }

    ws.onerror = (err) => {
      console.error("Erreur WebSocket :", err)
      setWsConnected(false)
    }

    ws.onclose = () => {
      console.log("WebSocket fermé")
      setWsConnected(false)
    }

    return () => ws.close()
  }, [])

  // Déduplication
  const latestPerNode = measurements.reduce((acc, m) => {
    if (!m || !m.node_id) return acc
    const existing = acc[m.node_id]
    if (!existing || new Date(m.timestamp) > new Date(existing.timestamp)) {
      acc[m.node_id] = m
    }
    return acc
  }, {} as Record<string, Measurement>)

  const uniqueMeasurements = Object.values(latestPerNode)

  const isConnected = wsConnected && uniqueMeasurements.length > 0
  const lastRefresh = uniqueMeasurements[0]?.timestamp ?? null

  if (!mounted) {
    return <div className="min-h-screen bg-background" />
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-screen-2xl px-4 py-6 md:px-6 lg:px-8">
        <div className="flex flex-col gap-6">
          <DashboardHeader
            isConnected={isConnected}
            lastRefresh={lastRefresh}
          />

          {uniqueMeasurements.length > 0 ? (
            <StatusCards measurements={uniqueMeasurements} />
          ) : (
            <StatusCardsSkeleton />
          )}

          <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
            <MeasurementsTable
              measurements={uniqueMeasurements}
              category="system"
              title="System Variables"
            />
            <MeasurementsTable
              measurements={uniqueMeasurements}
              category="sensor"
              title="Sensor Variables"
            />
          </div>

          <HistoryChart nodes={nodes ?? []} />
        </div>
      </div>
    </div>
  )
}

function StatusCardsSkeleton() {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <div
          key={i}
          className="flex items-center gap-4 rounded-xl border border-border bg-card px-6 py-5"
        >
          <Skeleton className="size-11 rounded-lg" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-3 w-20" />
            <Skeleton className="h-6 w-16" />
          </div>
        </div>
      ))}
    </div>
  )
}