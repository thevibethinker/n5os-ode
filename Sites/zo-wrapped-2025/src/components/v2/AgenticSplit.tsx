import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

interface AgenticSplitProps {
  agent: number;
  user: number;
}

export const AgenticSplit: React.FC<AgenticSplitProps> = ({ agent, user }) => {
  const total = agent + user;
  const leveragePercent = total > 0 ? ((agent / total) * 100).toFixed(1) : '0';
  const efficiencyRatio = agent > 0 ? Math.round(user / agent) : 0;
  
  const data = [
    { name: 'User Initiated', value: user, color: '#a855f7' },
    { name: 'Agentic / Scheduled', value: agent, color: '#3b82f6' },
  ];

  return (
    <div className="w-full h-[350px] flex flex-col bg-zinc-900/50 rounded-2xl p-6 border border-zinc-800">
      <h3 className="text-zinc-400 text-sm font-medium mb-4 uppercase tracking-widest">Interaction Leverage</h3>
      
      <div className="flex-1 flex items-center">
        <div className="w-1/2">
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={70}
                paddingAngle={5}
                dataKey="value"
                strokeWidth={0}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#18181b', 
                  border: '1px solid #27272a', 
                  borderRadius: '8px',
                  fontSize: '12px'
                }}
                formatter={(value: number) => value.toLocaleString()}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
        
        <div className="w-1/2 space-y-4 pl-4">
          <div>
            <p className="text-zinc-600 text-[10px] uppercase tracking-wider">User Initiated</p>
            <p className="text-2xl font-bold text-purple-400">{user.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-zinc-600 text-[10px] uppercase tracking-wider">Agentic / Scheduled</p>
            <p className="text-2xl font-bold text-blue-400">{agent.toLocaleString()}</p>
          </div>
        </div>
      </div>
      
      <div className="flex justify-between mt-4 pt-4 border-t border-zinc-800">
        <div className="text-center">
          <p className="text-zinc-600 text-[10px] uppercase tracking-wider">Automation Rate</p>
          <p className="text-blue-400 font-bold text-lg">{leveragePercent}%</p>
        </div>
        <div className="text-center">
          <p className="text-zinc-600 text-[10px] uppercase tracking-wider">Leverage Ratio</p>
          <p className="text-purple-400 font-bold text-lg">1:{efficiencyRatio}</p>
        </div>
        <div className="text-center">
          <p className="text-zinc-600 text-[10px] uppercase tracking-wider">Total</p>
          <p className="text-zinc-300 font-bold text-lg">{total.toLocaleString()}</p>
        </div>
      </div>
    </div>
  );
};

