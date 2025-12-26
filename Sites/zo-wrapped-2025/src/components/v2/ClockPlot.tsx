import React from 'react';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell } from 'recharts';

interface ClockPlotProps {
  data: Record<string, number>;
}

export const ClockPlot: React.FC<ClockPlotProps> = ({ data }) => {
  // Transform data for bar chart (00 to 23)
  const chartData = Array.from({ length: 24 }, (_, i) => {
    const hour = i.toString().padStart(2, '0');
    const value = data[hour] || 0;
    return {
      hour: `${i}`,
      value,
      label: `${hour}:00`,
    };
  });

  const maxValue = Math.max(...chartData.map(d => d.value));
  
  // Find peak hour
  const peakHour = chartData.reduce((max, curr) => curr.value > max.value ? curr : max, chartData[0]);

  return (
    <div className="w-full h-[400px] flex flex-col bg-zinc-900/50 rounded-2xl p-6 border border-zinc-800">
      <h3 className="text-zinc-400 text-sm font-medium mb-2 uppercase tracking-widest">Peak Velocity Clock</h3>
      <p className="text-xs text-zinc-600 mb-4">Your peak hour: <span className="text-purple-400 font-bold">{peakHour.label}</span> ({peakHour.value.toLocaleString()} conversations)</p>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <XAxis 
            dataKey="hour" 
            tick={{ fill: '#52525b', fontSize: 10 }}
            axisLine={{ stroke: '#27272a' }}
            tickLine={false}
          />
          <YAxis 
            hide 
          />
          <Tooltip
            contentStyle={{ 
              backgroundColor: '#18181b', 
              border: '1px solid #27272a', 
              borderRadius: '8px',
              fontSize: '12px'
            }}
            labelFormatter={(label) => `${label.toString().padStart(2, '0')}:00`}
            formatter={(value: number) => [value.toLocaleString(), 'Conversations']}
          />
          <Bar dataKey="value" radius={[4, 4, 0, 0]}>
            {chartData.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={entry.value === peakHour.value ? '#a855f7' : `rgba(168, 85, 247, ${0.2 + (entry.value / maxValue) * 0.6})`}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-zinc-600 text-[10px] mt-2 text-center uppercase tracking-wider">24-hour activity distribution</p>
    </div>
  );
};

