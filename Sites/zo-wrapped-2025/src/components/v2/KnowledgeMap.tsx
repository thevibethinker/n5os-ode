import React from 'react';
import { Treemap, ResponsiveContainer, Tooltip } from 'recharts';

interface KnowledgeMapProps {
  data: Record<string, number>;
}

// Custom content renderer for treemap cells
const CustomizedContent: React.FC<any> = (props) => {
  const { x, y, width, height, name, value } = props;
  
  if (width < 40 || height < 30) return null;
  
  return (
    <g>
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        style={{
          fill: '#a855f7',
          fillOpacity: 0.15 + (value / 300) * 0.6,
          stroke: '#27272a',
          strokeWidth: 2,
        }}
        rx={4}
      />
      <text
        x={x + width / 2}
        y={y + height / 2 - 6}
        textAnchor="middle"
        fill="#d4d4d8"
        fontSize={width < 80 ? 10 : 12}
        fontWeight="500"
      >
        {name?.length > 12 ? name.slice(0, 10) + '...' : name}
      </text>
      <text
        x={x + width / 2}
        y={y + height / 2 + 10}
        textAnchor="middle"
        fill="#a855f7"
        fontSize={width < 80 ? 11 : 14}
        fontWeight="bold"
      >
        {value}
      </text>
    </g>
  );
};

export const KnowledgeMap: React.FC<KnowledgeMapProps> = ({ data }) => {
  // Transform data into treemap format with children array
  const chartData = [
    {
      name: 'Knowledge',
      children: Object.entries(data)
        .filter(([_, size]) => size > 0)
        .map(([name, size]) => ({
          name: name.charAt(0).toUpperCase() + name.slice(1).replace(/-/g, ' '),
          size,
          value: size,
        }))
        .sort((a, b) => b.size - a.size),
    },
  ];

  const totalFiles = Object.values(data).reduce((sum, val) => sum + val, 0);

  return (
    <div className="w-full h-[350px] flex flex-col bg-zinc-900/50 rounded-2xl p-6 border border-zinc-800">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-zinc-400 text-sm font-medium uppercase tracking-widest">Neural Knowledge Density</h3>
          <p className="text-xs text-zinc-600 mt-1">Semantic clusters across your /Knowledge directory</p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-purple-400">{totalFiles}</p>
          <p className="text-[10px] text-zinc-600 uppercase">Total Files</p>
        </div>
      </div>
      
      <ResponsiveContainer width="100%" height="100%">
        <Treemap
          data={chartData}
          dataKey="size"
          aspectRatio={4 / 3}
          stroke="#18181b"
          content={<CustomizedContent />}
        >
          <Tooltip
            contentStyle={{ 
              backgroundColor: '#18181b', 
              border: '1px solid #27272a', 
              borderRadius: '8px',
              fontSize: '12px'
            }}
            formatter={(value: number) => [`${value} files`, 'Count']}
          />
        </Treemap>
      </ResponsiveContainer>
    </div>
  );
};

