import { Metadata } from "next";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Zap, Activity, ShieldAlert, Layers } from "lucide-react";
import { Grafica3DFlujo } from "./_components/grafica-3d-flujo";

export const metadata: Metadata = {
  title: "Flujo Neutrónico 3D | Monitoreo Nuclear",
};

export default function FlujoNeutronicoPage() {
  return (
    <div className="flex-1 space-y-6 p-8 pt-6">
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-3xl font-bold tracking-tight">Análisis de Flujo Neutrónico</h2>
          <p className="text-muted-foreground">Distribución volumétrica de la densidad de flujo en el núcleo.</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-4">
        {/* Métricas rápidas */}
        <Card className="border-l-4 border-l-yellow-500">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-bold uppercase text-muted-foreground">Pico Central</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-mono">3.42e14 <span className="text-xs font-normal text-muted-foreground">n/cm²s</span></div>
          </CardContent>
        </Card>
        {/* Más métricas... */}
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        {/* Gráfica 3D */}
        <Card className="lg:col-span-8 shadow-xl border-border">
          <CardHeader className="bg-muted/30 border-b">
            <div className="flex items-center gap-2">
              <Layers className="h-5 w-5 text-primary" />
              <CardTitle>Mapeo Volumétrico</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <Grafica3DFlujo />
          </CardContent>
        </Card>

        {/* Panel de Control Lateral */}
        <Card className="lg:col-span-4 shadow-md bg-secondary/10">
          <CardHeader>
            <CardTitle className="text-sm font-bold">Zonas de Interés</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {[
              { zona: "Núcleo Central", nivel: "Alto", color: "text-red-500" },
              { zona: "Periferia Norte", nivel: "Medio", color: "text-yellow-500" },
              { zona: "Moderador", nivel: "Estable", color: "text-green-500" },
            ].map((z) => (
              <div key={z.zona} className="flex items-center justify-between p-3 border rounded-lg bg-card shadow-sm">
                <span className="text-sm font-semibold">{z.zona}</span>
                <span className={`text-[10px] font-black uppercase ${z.color}`}>{z.nivel}</span>
              </div>
            ))}
            <div className="pt-4">
              <p className="text-[10px] text-muted-foreground text-center font-bold italic">
                * Gráfica interactiva: use el mouse para rotar el núcleo.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}