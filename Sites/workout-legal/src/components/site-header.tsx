import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto max-w-7xl flex h-14 items-center px-4 md:px-8">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 font-bold text-primary">
            <span className="text-xl">⚽</span>
            <span>Arsenal Trophy Room</span>
          </div>
          <Separator orientation="vertical" className="mx-2 h-4" />
          <nav className="flex items-center space-x-4 text-sm font-medium">
            <span className="text-muted-foreground">V's Road to Puerto Rico 10K</span>
          </nav>
        </div>
        <div className="flex flex-1 items-center justify-end space-x-2">
          <Button variant="ghost" size="sm" asChild>
            <a
              href="https://github.com/vrijen/workout-legal"
              target="_blank"
              rel="noreferrer"
            >
              GitHub
            </a>
          </Button>
        </div>
      </div>
    </header>
  )
}

