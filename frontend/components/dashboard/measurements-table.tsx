"use client"

import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import type { Measurement } from "@/lib/types"
import { Cpu, Gauge } from "lucide-react"

interface MeasurementsTableProps {
  measurements: Measurement[]
  category: "system" | "sensor"
  title: string
}

export function MeasurementsTable({
  measurements,
  category,
  title,
}: MeasurementsTableProps) {
  // Filtrer par catégorie
  const filtered =
    category === "system"
      ? measurements.filter((m) => m.category === "system")
      : measurements.filter((m) => m.category !== "system")

  const Icon = category === "system" ? Cpu : Gauge

  /**
   * Formatage propre et intelligent de la valeur
   * - Priorité à numeric_value si présent
   * - Nettoyage de text_value (enlève guillemets, simplifie objets complexes)
   * - Gestion des cas spéciaux (ServerStatus, BuildInfo, timestamps)
   */
  function formatValue(
    numeric: number | null,
    text: string | null,
    unit: string
  ): string {
    if (numeric !== null) {
      return unit ? `${numeric.toLocaleString()} ${unit}` : numeric.toLocaleString()
    }

    if (text === null || text === undefined) return "N/A"

    // Nettoyage du texte JSON
    let cleaned = text.replace(/^"|"$/g, '')

    // Simplification des objets complexes
    if (cleaned.includes("ServerStatusDataType")) {
      cleaned = "Server Status Data"
    } else if (cleaned.includes("BuildInfo")) {
      cleaned = "Build Info"
    } else if (cleaned.includes(":{self.")) {
      // Pour les timestamps ou autres : on garde la valeur brute
      cleaned = cleaned.replace(/\{self\.[^}]+\}/g, "").trim()
    }

    // Tronquer si trop long (évite débordement)
    if (cleaned.length > 60) {
      cleaned = cleaned.substring(0, 57) + "..."
    }

    return unit ? `${cleaned} ${unit}` : cleaned
  }

  /**
   * Formatage du timestamp (priorité à readable_time, fallback sur timestamp)
   */
  function formatTimestamp(ts: string | null): string {
    if (!ts) return "N/A"
    try {
      return new Date(ts).toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      })
    } catch {
      return ts
    }
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <Icon className="size-4 text-primary" />
          {title}
          <Badge variant="secondary" className="ml-auto font-mono text-xs">
            {filtered.length} nodes
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {filtered.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">
            No {category} data available
          </p>
        ) : (
          <div className="rounded-md border border-border overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="bg-secondary/50 hover:bg-secondary/50">
                  <TableHead className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Name
                  </TableHead>
                  <TableHead className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Node ID
                  </TableHead>
                  <TableHead className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Value
                  </TableHead>
                  <TableHead className="text-right text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Last Update
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filtered.map((m, index) => (
                  <TableRow 
                    key={`${m.node_id}-${m.timestamp || index}`} // clé unique et sûre
                    className="hover:bg-muted/50 transition-colors"
                  >
                    <TableCell className="font-medium text-foreground">
                      {m.name}
                    </TableCell>
                    <TableCell>
                      <code className="rounded bg-secondary px-1.5 py-0.5 font-mono text-xs text-muted-foreground">
                        {m.node_id}
                      </code>
                    </TableCell>
                    <TableCell className="font-mono text-sm text-primary max-w-md truncate">
                      {formatValue(m.numeric_value, m.text_value, m.unit)}
                    </TableCell>
                    <TableCell className="text-right font-mono text-xs text-muted-foreground whitespace-nowrap">
                      {formatTimestamp(m.readable_time || m.timestamp)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </CardContent>
    </Card>
  )
}