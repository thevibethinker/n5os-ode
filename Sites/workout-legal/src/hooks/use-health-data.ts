import { useState, useEffect } from "react";

export interface HealthSummary {
  avgRhr: number;
  avgDistance: number;
  maxDistance: number;
  best10kTime: number | null;
  integrity: number;
  squadStatus: string;
  legendName: string;
  readinessPercent: number;
}

export function useHealthSummary() {
  const [data, setData] = useState<HealthSummary>({
    avgRhr: 0,
    avgDistance: 0,
    maxDistance: 0,
    best10kTime: null,
    integrity: 0,
    squadStatus: "Transfer List",
    legendName: "Lord Bendtner",
    readinessPercent: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/health/summary")
      .then((res) => res.json())
      .then((json) => {
        const maxDist = json.maxDistance || 0;
        const bestTime = json.best10kTime;
        
        let squadStatus = "Transfer List";
        let legendName = "Lord Bendtner";
        
        if (maxDist >= 10) {
          if (bestTime && bestTime <= 60) {
            squadStatus = "Legend";
            legendName = "Dennis Bergkamp";
          } else {
            squadStatus = "First Team";
            legendName = "Thierry Henry / Patrick Vieira";
          }
        } else if (maxDist >= 5) {
          squadStatus = "Reserves";
          legendName = "Bukayo Saka";
        } else if (maxDist > 0) {
          squadStatus = "Academy";
          legendName = "Jack Wilshere";
        }

        const readinessPercent = Math.min(100, (maxDist / 10) * 100);

        setData({
          ...json,
          squadStatus,
          legendName,
          readinessPercent,
        });
        setLoading(false);
      });
  }, []);

  return { data, loading };
}

export function useHealthChart() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/health/chart")
      .then((res) => res.json())
      .then((json) => {
        setData(json);
        setLoading(false);
      });
  }, []);

  return { data, loading };
}

export function useHealthRuns() {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/health/runs")
      .then((res) => res.json())
      .then((json) => {
        setData(json);
        setLoading(false);
      });
  }, []);

  return { data, loading };
}

// Bio-Log: Today's mood
export function useBioToday() {
  const [data, setData] = useState<{
    emoji: string | null;
    note: string | null;
    date: string;
    hasData: boolean;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/bio/today")
      .then((res) => res.json())
      .then((json) => {
        setData(json);
        setLoading(false);
      });
  }, []);

  return { data, loading };
}

// Bio-Log: Last 7 days
export function useBioWeek() {
  const [data, setData] = useState<{ date: string; emoji: string }[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/bio/week")
      .then((res) => res.json())
      .then((json) => {
        setData(json);
        setLoading(false);
      });
  }, []);

  return { data, loading };
}

// 10K Readiness
export function use10KReadiness() {
  const [data, setData] = useState<{
    percentage: number;
    longestRun: number;
    weeklyVolume: number;
    streak: number;
    rhrBaseline: number | null;
    rhrCurrent: number | null;
    rhrDrop: number;
    weeksRemaining: number;
    nextMilestone: string;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/goals/10k-readiness")
      .then((res) => res.json())
      .then((json) => {
        setData(json);
        setLoading(false);
      });
  }, []);

  return { data, loading };
}


