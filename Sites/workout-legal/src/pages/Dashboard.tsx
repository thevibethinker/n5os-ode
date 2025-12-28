import { ChartAreaInteractive } from "@/components/chart-area-interactive";
import { DataTable } from "@/components/data-table";
import { SiteHeader } from "@/components/site-header";
import { SectionCards } from "@/components/section-cards";

export default function DashboardPage() {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <SiteHeader />
      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-7xl space-y-8 p-4 md:p-8">
          <div className="flex flex-col gap-8">
            <SectionCards />
            
            <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
              <div className="space-y-8">
                <ChartAreaInteractive />
              </div>
              
              <div className="space-y-8">
                <DataTable />
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}








