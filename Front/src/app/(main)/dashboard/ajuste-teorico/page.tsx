import { Metadata } from "next";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Settings2, TrendingUp, AlertTriangle, History } from "lucide-react";
import { GraficaExcedentes, GraficaMaximos } from "./_components/graficas-ajuste";

export const metadata: Metadata = {
  title: "Ajuste Técnico | Histórico Anual",
};

export default function AjusteTecnicoPage() {
  return (
    <div className="flex-1 space-y-6 p-8 pt-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Ajuste Técnico</h2>
          <p className="text-muted-foreground">Auditoría de excedentes y picos máximos por ciclo operativo.</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Gráfica de Excedentes */}
        <Card className="shadow-md border-border bg-card">
          <CardHeader>
            <div className="flex items-center gap-2 text-primary">
              <TrendingUp className="h-5 w-5" />
              <CardTitle>Excedentes Acumulados</CardTitle>
            </div>
            <CardDescription>Volumen total de energía/datos por encima del umbral nominal.</CardDescription>
          </CardHeader>
          <CardContent>
            <GraficaExcedentes />
          </CardContent>
        </Card>

        {/* Gráfica de Máximos */}
        <Card className="shadow-md border-border bg-card">
          <CardHeader>
            <div className="flex items-center gap-2 text-destructive">
              <AlertTriangle className="h-5 w-5" />
              <CardTitle>Máximos Anuales</CardTitle>
            </div>
            <CardDescription>Puntos críticos de estrés detectados en cada periodo fiscal.</CardDescription>
          </CardHeader>
          <CardContent>
            <GraficaMaximos />
          </CardContent>
        </Card>
      </div>

      {/* Resumen de Auditoría */}
      <Card className="border-border bg-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <History className="h-5 w-5 text-muted-foreground" />
            Registro de Calibración
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            <div className="p-4 rounded-lg border bg-muted/20">
              <p className="text-xs font-bold text-muted-foreground uppercase">Promedio Ajustado</p>
              <p className="text-2xl font-black">482.5 Units</p>
            </div>
            <div className="p-4 rounded-lg border bg-muted/20">
              <p className="text-xs font-bold text-muted-foreground uppercase">Desviación Típica</p>
              <p className="text-2xl font-black text-primary">± 4.2%</p>
            </div>
            <div className="p-4 rounded-lg border bg-muted/20">
              <p className="text-xs font-bold text-muted-foreground uppercase">Estado del Sensor</p>
              <p className="text-2xl font-black text-emerald-500">CALIBRADO</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}