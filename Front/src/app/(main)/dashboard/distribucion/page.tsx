import { Metadata } from "next";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { BarChart3, ListOrdered, info } from "lucide-react";
import { GraficoHistograma } from "./_components/grafico-histograma";

export const metadata: Metadata = {
  title: "Distribución de Datos | Sistema de Monitoreo",
};

const valoresTabla = [
  { rango: "0-10", cant: 45, porcentaje: "4.5%" },
  { rango: "10-20", cant: 82, porcentaje: "8.2%" },
  { rango: "20-30", cant: 115, porcentaje: "11.5%" },
  { rango: "30-40", cant: 190, porcentaje: "19.0%" },
  { rango: "40-50", cant: 250, porcentaje: "25.0%" },
  { rango: "50-60", cant: 210, porcentaje: "21.0%" },
];

export default function DistribucionPage() {
  return (
    <div className="flex-1 space-y-6 p-8 pt-6">
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight">Distribución de Frecuencias</h2>
        <p className="text-muted-foreground">Análisis estadístico de la población de datos actual.</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        {/* Card del Histograma */}
        <Card className="lg:col-span-8 shadow-sm">
          <CardHeader>
            <div className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-primary" />
              <CardTitle>Histograma de Carga</CardTitle>
            </div>
            <CardDescription>Visualización de la densidad por rangos de operación.</CardDescription>
          </CardHeader>
          <CardContent>
            <GraficoHistograma />
          </CardContent>
        </Card>

        {/* Card de la Tabla */}
        <Card className="lg:col-span-4 shadow-sm overflow-hidden">
          <CardHeader className="bg-muted/30">
            <div className="flex items-center gap-2">
              <ListOrdered className="h-5 w-5 text-primary" />
              <CardTitle>Desglose Numérico</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead className="font-bold">Rango</TableHead>
                  <TableHead className="text-right font-bold">Cantidad</TableHead>
                  <TableHead className="text-right font-bold">%</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {valoresTabla.map((row) => (
                  <TableRow key={row.rango}>
                    <TableCell className="font-medium font-mono">{row.rango}</TableCell>
                    <TableCell className="text-right">{row.cant}</TableCell>
                    <TableCell className="text-right text-muted-foreground">{row.porcentaje}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            <div className="p-4 bg-muted/10 border-t">
              <p className="text-[10px] uppercase font-bold text-muted-foreground flex items-center gap-2">
                 Muestra total: 1,000 puntos analizados
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}