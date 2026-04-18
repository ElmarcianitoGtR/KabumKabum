"use client";

import dynamic from "next/dynamic";
import { useTheme } from "next-themes"; // Si usas next-themes para el dark mode

// Importación dinámica para evitar errores de SSR con Plotly
const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

export function Grafica3DFlujo() {
  const { theme } = useTheme();

  // Generamos una campana de Gauss 2D para simular el flujo en el núcleo
  const size = 20;
  const zData = Array.from({ length: size }, (_, y) =>
    Array.from({ length: size }, (_, x) => {
      const distance = Math.sqrt((x - size / 2) ** 2 + (y - size / 2) ** 2);
      return Math.exp((-distance) ** 2 / 50) * 100; // Flujo máximo al centro
    })
  );

  return (
    <div className="w-full h-[500px] flex justify-center items-center bg-card rounded-xl border border-border overflow-hidden">
      <Plot
        data={[
          {
            z: zData,
            type: "surface",
            colorscale: "Viridis",
            showscale: false,
          },
        ]}
        layout={{
          autosize: true,
          height: 500,
          margin: { l: 0, r: 0, b: 0, t: 0 },
          paper_bgcolor: "transparent",
          plot_bgcolor: "transparent",
          scene: {
            xaxis: { visible: false },
            yaxis: { visible: false },
            zaxis: { 
              title: "Flujo",
              gridcolor: theme === "dark" ? "#334155" : "#e2e8f0",
              zerolinecolor: theme === "dark" ? "#334155" : "#e2e8f0"
            },
            camera: {
              eye: { x: 1.5, y: 1.5, z: 1.2 }
            }
          },
        }}
        config={{ responsive: true, displayModeBar: false }}
        className="w-full h-full"
      />
    </div>
  );
}