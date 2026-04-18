"use client";

import React, { useMemo } from "react";
import { ScatterChart, Scatter, XAxis, YAxis, ZAxis, CartesianGrid, Tooltip, Cell } from "recharts";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";

// Definimos la estructura según tu JSON
interface NodoTopologia {
  UMAP1: number;
  UMAP2: number;
  operating_state_label: string;
  trip_risk_index: number;
}

export function GraficoTopologiaAPI({ datos }: { datos: NodoTopologia[] }) {
  // Procesamos los datos para Recharts
  const chartData = useMemo(() => {
    return datos.map((d, i) => ({
      x: d.UMAP1,
      y: d.UMAP2,
      z: d.trip_risk_index, // Usamos el riesgo para el tamaño del punto
      status: d.operating_state_label,
    }));
  }, [datos]);

  const config = {
    nodos: { label: "Nodos de Red", color: "hsl(var(--primary))" },
  };

  return (
    <ChartContainer config={config} className="h-[600px] w-full bg-card rounded-xl border border-border">
      <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
        <CartesianGrid stroke="currentColor" className="text-border" strokeDasharray="3 3" />
        
        {/* Ajustamos los dominios según los valores de tu JSON */}
        <XAxis type="number" dataKey="x" hide domain={['auto', 'auto']} />
        <YAxis type="number" dataKey="y" hide domain={['auto', 'auto']} />
        <ZAxis type="number" dataKey="z" range={[2, 12]} />
        
        <Tooltip 
          cursor={{ strokeDasharray: '3 3' }} 
          content={<ChartTooltipContent />} 
        />

        <Scatter name="Sensores" data={chartData}>
          {chartData.map((entry, index) => (
            <Cell 
              key={`cell-${index}`} 
              // Color basado en el estado operativo del JSON
              fill={entry.status === "steady_high_load" ? "hsl(var(--primary))" : "hsl(var(--destructive))"} 
              fillOpacity={0.4}
            />
          ))}
        </Scatter>
      </ScatterChart>
    </ChartContainer>
  );
}