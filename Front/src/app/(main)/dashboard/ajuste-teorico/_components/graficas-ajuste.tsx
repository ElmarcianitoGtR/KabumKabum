"use client";

import { Bar, BarChart, Area, AreaChart, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from "recharts";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";

const dataAnual = [
  { año: "2021", excedente: 450, maximo: 890 },
  { año: "2022", excedente: 520, maximo: 920 },
  { año: "2023", excedente: 380, maximo: 850 },
  { año: "2024", excedente: 610, maximo: 980 },
  { año: "2025", excedente: 490, maximo: 910 },
];

const config = {
  excedente: { label: "Excedente Anual", color: "hsl(var(--primary))" },
  maximo: { label: "Máximo Histórico", color: "hsl(var(--destructive))" },
};

export function GraficaExcedentes() {
  return (
    <ChartContainer config={config} className="h-[300px] w-full">
      <BarChart data={dataAnual}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-muted" />
        <XAxis dataKey="año" axisLine={false} tickLine={false} />
        <YAxis axisLine={false} tickLine={false} />
        <ChartTooltip content={<ChartTooltipContent />} />
        <Bar dataKey="excedente" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ChartContainer>
  );
}

export function GraficaMaximos() {
  return (
    <ChartContainer config={config} className="h-[300px] w-full">
      <AreaChart data={dataAnual}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} className="stroke-muted" />
        <XAxis dataKey="año" axisLine={false} tickLine={false} />
        <YAxis axisLine={false} tickLine={false} />
        <ChartTooltip content={<ChartTooltipContent />} />
        <Area 
          type="monotone" 
          dataKey="maximo" 
          stroke="hsl(var(--destructive))" 
          fill="hsl(var(--destructive))" 
          fillOpacity={0.2} 
          strokeWidth={3}
        />
      </AreaChart>
    </ChartContainer>
  );
}