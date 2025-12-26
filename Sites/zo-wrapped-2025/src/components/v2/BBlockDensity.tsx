import React from 'react';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell } from 'recharts';

interface BBlockDensityProps {
  data: Record<string, number>;
}

export const BBlockDensity: React.FC<BBlockDensityProps> = ({ data }) => {
  const chartData = Object.entries(data || {})
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 10);

  return (
    <div className="bg-zinc-900/50 p-6 rounded-2xl border border-zinc-800 h-80 flex flex-col">
      <h3 className="text-zinc-400 text-sm font-medium mb-4 uppercase tracking-widest">Intelligence Extraction Map</h3>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart 
          data={chartData} 
          layout="vertical"
          margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
        >
          <XAxis type="number" hide />
          <YAxis 
            type="category" 
            dataKey="name" 
            stroke="#71717a" 
            fontSize={12}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip 
            cursor={{ fill: 'transparent' }}
            contentStyle={{ 
              backgroundColor: '#18181b', 
              border: '1px solid #27272a', 
              borderRadius: '8px',
              fontSize: '12px'
            }}
          />
          <Bar dataKey="value" radius={[0, 4, 4, 0]}>
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={index % 2 === 0 ? '#6366f1' : '#4f46e5'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <p className="text-zinc-500 text-[10px] mt-4 uppercase tracking-wider text-center">Top 10 B-Block Types by Volume</p>
    </div>
  );
};

