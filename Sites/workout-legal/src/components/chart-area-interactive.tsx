"use client";

import * as React from "react";
import { Area, AreaChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useHealthChart } from "@/hooks/use-health-data";

export function ChartAreaInteractive() {
  const { data: chartData, loading } = useHealthChart();

  if (loading) {
    return <Card className="h-[350px] bg-muted/50 animate-pulse" />;
  }

  // Use all data, sorted by date
  const sortedData = [...chartData].sort((a, b) => 
    new Date(a.date).getTime() - new Date(b.date).getTime()
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>Activity Trends</CardTitle>
        <CardDescription>Daily steps from Health OS</CardDescription>
      </CardHeader>
      <CardContent>
        <div style={{ width: '100%', height: 250 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={sortedData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date" 
                tickFormatter={(value) => {
                  const d = new Date(value);
                  return `${d.getMonth()+1}/${d.getDate()}`;
                }}
              />
              <YAxis />
              <Tooltip 
                labelFormatter={(value) => `Date: ${value}`}
                formatter={(value: number) => [value.toLocaleString(), 'Steps']}
              />
              <Area 
                type="monotone" 
                dataKey="steps" 
                stroke="#f97316" 
                fill="#f97316" 
                fillOpacity={0.3}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

