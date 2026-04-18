// src/app/(main)/dashboard/topologia/page.tsx
import { promises as fs } from 'fs';
import path from 'path';
import { GraficoTopologiaAPI } from "./_components/grafico-topologia";

export default async function TopologiaPage() {
  // 1. Leemos el archivo JSON (Simulando una llamada a API)
  const filePath = path.join(process.cwd(), 'src/data/umap_reduced.json');
  const fileContent = await fs.readFile(filePath, 'utf8');
  const datosPuros = JSON.parse(fileContent);

  // 2. Opcional: Filtrar o limitar si son demasiados para la primera carga
  const datosLimitados = datosPuros.slice(0, 3000); 

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <h2 className="text-3xl font-bold tracking-tight">Topología Dinámica</h2>
      
      <div className="grid gap-4 md:grid-cols-7">
        <div className="col-span-7">
          {/* Pasamos los datos del servidor al componente de cliente */}
          <GraficoTopologiaAPI datos={datosLimitados} />
        </div>
      </div>
    </div>
  );
}