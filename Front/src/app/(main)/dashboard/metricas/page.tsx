
import { Metadata } from "next";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card"; // La ruta correcta suele ser /ui/card
import { Activity, Thermometer, Zap, ShieldAlert, Grab } from "lucide-react";
import { GraficoReactividad } from "./_components/grafico";



export const metadata: Metadata = {
  title: "Métricas de Rendimiento | Monitoreo Nuclear",
};

export default function MetricasPage() {
  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Métricas de Rendimiento</h2>
      </div>

      {/* Cartas de Resumen Rápido (KPIs) */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Potencia Térmica</CardTitle>
            <Zap className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1,250 MWt</div>
            <p className="text-xs text-muted-foreground">+0.2% desde el último ciclo</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Temperatura del Refrigerante</CardTitle>
            <Thermometer className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">295°C</div>
            <p className="text-xs text-muted-foreground">Margen de seguridad: 15°C</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Flujo de Neutrones</CardTitle>
            <Activity className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">3.2e13 n/cm²s</div>
            <p className="text-xs text-muted-foreground">Estado: Estable</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Alertas de Contención</CardTitle>
            <ShieldAlert className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">0</div>
            <p className="text-xs text-muted-foreground">Sin incidencias detectadas</p>
          </CardContent>
        </Card>
      </div>

      {/* Espacio para Gráficas Principales */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Historial de Reactividad</CardTitle>
            <CardDescription>Simulación de la evolución de reactividad en las últimas 24 horas.</CardDescription>
          </CardHeader>
          <CardContent className="pl-2">
            <GraficoReactividad/>



          </CardContent>
        </Card>

        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Estado de las Barras de Control</CardTitle>
            <CardDescription>Posicionamiento actual por zona del núcleo.</CardDescription>
          </CardHeader>
          <CardContent>
             <div className="space-y-4">
               {/* Simulación de barras de progreso para el estado físico */}
               {[1, 2, 3, 4].map((id) => (
                 <div key={id} className="flex items-center">
                    <div className="ml-4 space-y-1 w-full">
                      <p className="text-sm font-medium leading-none">Grupo de Control {id}</p>
                      <div className="h-2 w-full bg-secondary rounded-full overflow-hidden">
                        <div className="h-full bg-primary" style={{ width: `${75 + id * 5}%` }}></div>
                      </div>
                    </div>
                 </div>
               ))}
             </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}