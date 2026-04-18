"use client";

import { Line, LineChart, XAxis } from "recharts";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { revenueChartConfig, revenueChartData } from "./metricas.config";

export function GraficoReactividad() {
  return (
    <ChartContainer config={revenueChartConfig} className="h-48 w-full">
      <LineChart
        data={revenueChartData}
        margin={{ top: 5, right: 10, left: 10, bottom: 0 }}
      >
        <XAxis dataKey="month" tickLine={false} tickMargin={10} axisLine={false} hide />
        <ChartTooltip content={<ChartTooltipContent />} />
        <Line
          type="monotone"
          strokeWidth={3}
          dataKey="revenue"
          stroke="var(--color-revenue)"
          dot={false}
          activeDot={{ r: 6 }}
        />
      </LineChart>
    </ChartContainer>
  );
}