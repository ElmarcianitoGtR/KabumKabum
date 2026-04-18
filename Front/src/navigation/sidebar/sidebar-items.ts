import {
  Activity,       // Para Flujo Neutrónico
  DatabaseBackup, // Para Carga de Datos
  Dna,            // Para Distribución (referencia a núcleos/partículas)
  GitGraph,       // Para Topología
  LineChart,      // Para Pronósticos
  Network,        // Alternativa para Topología
  Settings2,      // Para Ajuste Teórico
  TableProperties,// Para Métricas de Rendimiento
  Zap,            // Para Flujo Neutrónico (energía)
  LayoutDashboard,
  FileUp,         // Carga de datos
  Boxes,
  LucideIcon          // Distribución
} from "lucide-react";

export interface NavSubItem {
  title: string;
  url: string;
  icon?: LucideIcon;
  comingSoon?: boolean;
  newTab?: boolean;
  isNew?: boolean;
}

export interface NavMainItem {
  title: string;
  url: string;
  icon?: LucideIcon;
  subItems?: NavSubItem[];
  comingSoon?: boolean;
  newTab?: boolean;
  isNew?: boolean;
}

export interface NavGroup {
  id: number;
  label?: string;
  items: NavMainItem[];
}

export const sidebarItems: NavGroup[] = [
  {
    id: 1,
    label: "Monitoreo del Reactor",
    items: [
      {
        title: "Topología",
        url: "/dashboard/topologia",
        icon: GitGraph,
      },
      {
        title: "Distribución",
        url: "/dashboard/distribucion",
        icon: Boxes,
      },
      {
        title: "Flujo Neutrónico",
        url: "/dashboard/flujo-neutronico",
        icon: Activity,
      },
    ],
  },
  {
    id: 2,
    label: "Análisis y Modelado",
    items: [
      {
        title: "Ajuste Teórico",
        url: "/dashboard/ajuste-teorico",
        icon: Settings2,
      },
      {
        title: "Pronósticos",
        url: "/dashboard/pronosticos",
        icon: LineChart,
      },
      {
        title: "Métricas de Rendimiento",
        url: "/dashboard/metricas",
        icon: TableProperties,
      },
    ],
  },
  {
    id: 3,
    label: "Administración",
    items: [
      {
        title: "Carga de Datos",
        url: "/dashboard/carga-datos",
        icon: FileUp,
      },
    ],
  },
];