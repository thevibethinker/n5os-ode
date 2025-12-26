import { ChartAreaInteractive } from "@/components/chart-area-interactive";
import { DataTable } from "@/components/data-table";
import { SectionCards } from "@/components/section-cards";

import data from "@/app/dashboard/data.json";

/**
 * Data dashboard demo - demonstrates charts, tables, and data visualization.
 *
 * This demo shows how to:
 * - Display data with Recharts (line, bar, area charts)
 * - Build interactive data tables with sorting and filtering
 * - Create sidebar navigation
 * - Load data from JSON files or APIs
 *
 * All dependencies (recharts, shadcn/ui components) are pre-installed.
 * The sample data is in src/app/dashboard/data.json.
 * See docs/shadcncharts.md for comprehensive chart examples and patterns.
 *
 * Customize this by:
 * - Connecting to a SQLite database for dynamic data
 * - Adding real-time data updates via WebSocket
 * - Creating custom chart types
 * - Adding data export (CSV, PDF)
 * - Implementing advanced filters and search
 */

export default function DataDemo() {
  return (
    <div className="flex flex-col min-h-screen">
      <header className="flex h-12 shrink-0 items-center gap-2 border-b px-4 lg:px-6">
        <h1 className="text-base font-medium">Data Dashboard</h1>
      </header>
      <div className="flex flex-1 flex-col">
        <div className="@container/main flex flex-1 flex-col gap-2">
          <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
            <SectionCards />
            <div className="px-4 lg:px-6">
              <ChartAreaInteractive />
            </div>
            <DataTable data={data} />
          </div>
        </div>
      </div>
    </div>
  );
}
