import { IconHeart, IconShieldCheck, IconTrophy, IconActivity } from "@tabler/icons-react"
import { useHealthSummary } from "@/hooks/use-health-data"
import { ProgressCannon } from "@/components/progress-cannon"

import { Badge } from "@/components/ui/badge"
import {
  Card,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export function SectionCards() {
  const { data, loading } = useHealthSummary()

  if (loading) {
    return (
      <div className="grid grid-cols-1 gap-4 px-4 lg:px-6 @xl/main:grid-cols-2 @5xl/main:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i} className="animate-pulse h-32 bg-muted/50" />
        ))}
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-8">
      {/* 10K READINESS CANNON TRACK */}
      <Card className="overflow-hidden border-2 border-primary/20">
        <CardHeader className="bg-primary/5 pb-2">
          <CardTitle className="flex items-center gap-2 text-primary uppercase tracking-tighter italic">
            <IconTrophy className="size-5" /> 10K Readiness Cannon
          </CardTitle>
          <CardDescription>Target: Puerto Rico 10K — Path to Invincibility</CardDescription>
        </CardHeader>
        <div className="px-8 pb-4">
          <ProgressCannon percentage={data.readinessPercent} />
        </div>
      </Card>

      <div className="grid grid-cols-1 gap-4 @xl/main:grid-cols-2 @5xl/main:grid-cols-4">
        {/* SQUAD STATUS */}
        <Card className="@container/card border-2 border-secondary/20">
          <CardHeader>
            <CardDescription>Squad Status</CardDescription>
            <CardTitle className="text-2xl font-bold uppercase tracking-tight text-primary">
              {data.squadStatus}
            </CardTitle>
            <div className="mt-2">
              <Badge variant="outline" className="border-secondary text-secondary-foreground font-bold">
                Achievement: {data.legendName}
              </Badge>
            </div>
          </CardHeader>
          <CardFooter className="text-sm">
            <div className="text-muted-foreground italic">
              Based on longest run: {data.maxDistance.toFixed(2)}km
            </div>
          </CardFooter>
        </Card>

        {/* RESTING HEART RATE (MEDICAL BASELINE) */}
        <Card className="@container/card border-2 border-primary/10">
          <CardHeader>
            <CardDescription>Medical Baseline (RHR)</CardDescription>
            <CardTitle className="text-2xl font-semibold tabular-nums">
              {data.avgRhr.toFixed(1)} <span className="text-sm font-normal">bpm</span>
            </CardTitle>
            <div className="mt-2">
              <Badge variant="outline" className="border-green-500 text-green-600">
                <IconHeart className="size-4 mr-1" /> Recovered
              </Badge>
            </div>
          </CardHeader>
          <CardFooter className="flex-col items-start gap-1 text-sm">
            <div className="font-medium text-muted-foreground flex items-center gap-1">
              Family Doctor Check <IconShieldCheck className="size-4 text-green-600" />
            </div>
          </CardFooter>
        </Card>

        {/* RECENT EFFORT */}
        <Card className="@container/card">
          <CardHeader>
            <CardDescription>Avg Run Dist (30d)</CardDescription>
            <CardTitle className="text-2xl font-semibold tabular-nums">
              {data.avgDistance.toFixed(2)} <span className="text-sm font-normal">km</span>
            </CardTitle>
          </CardHeader>
          <CardFooter className="text-sm text-muted-foreground">
            Maintaining aerobic base
          </CardFooter>
        </Card>

        {/* INTEGRITY */}
        <Card className="@container/card">
          <CardHeader>
            <CardDescription>Commitment Score</CardDescription>
            <CardTitle className="text-2xl font-semibold tabular-nums">
              {(data.integrity * 100).toFixed(0)}%
            </CardTitle>
          </CardHeader>
          <CardFooter className="text-sm text-muted-foreground">
            Workouts vs. Plan
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}


