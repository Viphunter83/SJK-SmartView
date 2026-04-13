import { AppSidebar } from "@/components/app-sidebar"
import { LocationCatalog } from "@/components/location-catalog"
import { SidebarTrigger } from "@/components/ui/sidebar"

export default function Home() {
  return (
    <div className="flex min-h-screen w-full">
      <AppSidebar />
      <main className="flex-1 overflow-auto">
        <header className="flex h-16 shrink-0 items-center justify-between border-b border-border/40 px-6 backdrop-blur-md">
          <SidebarTrigger />
          <div className="flex items-center gap-4">
            <div className="text-sm font-medium text-muted-foreground">
              Менеджер: <span className="text-foreground">Константин В.</span>
            </div>
            <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-primary to-purple-500 shadow-lg shadow-primary/20" />
          </div>
        </header>
        <LocationCatalog />
      </main>
    </div>
  )
}
