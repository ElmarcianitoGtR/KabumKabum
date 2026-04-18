"use client";

import { Bar, BarChart, CartesianGrid, XAxis, YAxis, ResponsiveContainer } from "recharts";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";

const data = [
  { rango: "0-10", frecuencia: 45 },
  { rango: "10-20", frecuencia: 82 },
  { rango: "20-30", frecuencia: 115 },
  { rango: "30-40", frecuencia: 190 },
  { rango: "40-50", frecuencia: 250 },
  { rango: "50-60", frecuencia: 210 },
  { rango: "60-70", frecuencia: 140 },
  { rango: "70-80", frecuencia: 75 },
  { rango: "80-90", frecuencia: 30 },
  { rango: "90-100", frecuencia: 10 },
];

const config = {
  frecuencia: {
    label: "Frecuencia",
    color: "hsl(var(--primary))",
  },
};

export function GraficoHistograma() {
  return (
    <ChartContainer config={config} className="h-[400px] w-full">
      <BarChart data={data} barGap={0} margin={{ top: 20, right: 20, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-muted" />
        <XAxis 
          dataKey="rango" 
          axisLine={false} 
          tickLine={false} 
          tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }}
        />
        <YAxis 
          axisLine={false} 
          tickLine={false} 
          tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }}
        />
        <ChartTooltip content={<ChartTooltipContent />} />
        <Bar 
          dataKey="frecuencia" 
          fill="hsl(var(--primary))" 
          radius={[4, 4, 0, 0]} 
          opacity={0.8}
        />
      </BarChart>
    </ChartContainer>
  );
}