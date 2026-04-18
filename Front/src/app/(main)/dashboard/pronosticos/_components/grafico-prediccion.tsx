"use client";

import { Area, AreaChart, CartesianGrid, XAxis, YAxis, ResponsiveContainer } from "recharts";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";

// Datos simulados: histórico + predicción
const data = [
  { tiempo: "10:00", actual: 400, pronostico: 400 },
  { tiempo: "11:00", actual: 450, pronostico: 450 },
  { tiempo: "12:00", actual: 420, pronostico: 420 },
  { tiempo: "13:00", actual: null, pronostico: 460 },
  { tiempo: "14:00", actual: null, pronostico: 510 },
  { tiempo: "15:00", actual: null, pronostico: 490 },
];

const config = {
  actual: { label: "Valor Real", color: "hsl(var(--primary))" },
  pronostico: { label: "Tendencia IA", color: "hsl(var(--muted-foreground))" },
};

export function GraficoPrediccion() {
  return (
    <ChartContainer config={config} className="h-[350px] w-full">
      <AreaChart data={data}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="tiempo" axisLine={false} tickLine={false} />
        <YAxis axisLine={false} tickLine={false} hide />
        <ChartTooltip content={<ChartTooltipContent />} />
        {/* Área para el pronóstico (sombreado) */}
        <Area
          type="monotone"
          dataKey="pronostico"
          stroke="#94a3b8"
          fillOpacity={0.1}
          fill="#94a3b8"
          strokeDasharray="5 5"
        />
        {/* Línea para el valor actual */}
        <Area
          type="monotone"
          dataKey="actual"
          stroke="hsl(var(--primary))"
          fillOpacity={0.3}
          fill="hsl(var(--primary))"
          strokeWidth={3}
        />
      </AreaChart>
    </ChartContainer>
  );
}