import { Metadata } from "next";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { BrainCircuit, TrendingUp, AlertTriangle, Clock } from "lucide-react";
import { GraficoPrediccion } from "./_components/grafico-prediccion";

export const metadata: Metadata = {
  title: "Pronósticos Predictivos | Sistema Nuclear",
};

export default function PronosticosPage() {
  return (
    <div className="flex-1 space-y-6 p-8 pt-6">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight">Análisis de Pronósticos</h2>
        <div className="flex items-center gap-2 bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-sm font-medium border border-blue-200">
          <BrainCircuit className="h-4 w-4" />
          IA Generativa Activa
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Confianza del Modelo</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">98.4%</div>
            <p className="text-xs text-muted-foreground">Basado en últimas 24h</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Próximo Evento Estimado</CardTitle>
            <Clock className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">14:45 HS</div>
            <p className="text-xs text-muted-foreground">Pico de carga térmica</p>
          </CardContent>
        </Card>

        <Card className="border-orange-200 bg-orange-50/30">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-orange-700">Desviación Detectada</CardTitle>
            <AlertTriangle className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-700">0.02%</div>
            <p className="text-xs text-orange-600">Margen de error estable</p>
          </CardContent>
        </Card>
      </div>

      <Card className="col-span-4">
        <CardHeader>
          <CardTitle>Proyección de Reactividad (Próximas 6 Horas)</CardTitle>
          <CardDescription>
            La línea discontinua representa la proyección calculada por el modelo de red neuronal.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <GraficoPrediccion />
        </CardContent>
      </Card>
    </div>
  );
}