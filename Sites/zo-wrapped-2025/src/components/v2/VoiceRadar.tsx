import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts';

interface VoiceRadarProps {
  data: Record<string, number>;
}

export const VoiceRadar: React.FC<VoiceRadarProps> = ({ data }) => {
  const chartData = [
    { subject: 'Warmth', value: data.warmth ?? 80, fullMark: 100 },
    { subject: 'Precision', value: data.precision ?? 90, fullMark: 100 },
    { subject: 'Authority', value: data.authority ?? 70, fullMark: 100 },
    { subject: 'Conciseness', value: data.conciseness ?? 85, fullMark: 100 },
    { subject: 'Empathy', value: data.empathy ?? 75, fullMark: 100 },
  ];

  return (
    <div className="w-full h-[400px] flex flex-col bg-zinc-900/50 rounded-2xl p-6 border border-zinc-800">
      <h3 className="text-zinc-400 text-sm font-medium mb-2 uppercase tracking-widest">Voice Transformation Profile</h3>
      <p className="text-xs text-zinc-600 mb-4">Semantic alignment of outbound communications</p>
      
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={chartData}>
          <PolarGrid stroke="#27272a" strokeDasharray="3 3" />
          <PolarAngleAxis 
            dataKey="subject" 
            tick={{ fill: '#71717a', fontSize: 11 }} 
          />
          <PolarRadiusAxis 
            angle={90} 
            domain={[0, 100]} 
            tick={false} 
            axisLine={false}
          />
          <Radar
            name="V's Voice"
            dataKey="value"
            stroke="#a855f7"
            fill="#a855f7"
            fillOpacity={0.4}
            strokeWidth={2}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#18181b', 
              border: '1px solid #27272a', 
              borderRadius: '8px',
              fontSize: '12px'
            }}
            formatter={(value: number) => [`${value}/100`, 'Score']}
          />
        </RadarChart>
      </ResponsiveContainer>
      
      <div className="flex justify-center gap-6 mt-2">
        {chartData.slice(0, 3).map((item) => (
          <div key={item.subject} className="text-center">
            <p className="text-[10px] text-zinc-600 uppercase">{item.subject}</p>
            <p className="text-sm font-bold text-purple-400">{item.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

