import React from 'react';
import { IconTrophy } from "@tabler/icons-react";

interface ProgressCannonProps {
  percentage: number;
}

export function ProgressCannon({ percentage }: ProgressCannonProps) {
  return (
    <div className="relative w-full py-8">
      {/* Background Track */}
      <div className="h-4 w-full rounded-full bg-muted overflow-hidden">
        <div 
          className="h-full bg-primary transition-all duration-1000 ease-out"
          style={{ width: `${percentage}%` }}
        />
      </div>

      {/* Cannon Icon positioned at the end of the progress */}
      <div 
        className="absolute top-1/2 -translate-y-1/2 transition-all duration-1000 ease-out flex flex-col items-center"
        style={{ left: `calc(${percentage}% - 20px)` }}
      >
        <div className="bg-primary text-white p-2 rounded-full border-4 border-background shadow-lg">
          <IconTrophy size={24} />
        </div>
        <span className="text-xs font-bold mt-1 text-primary">{percentage.toFixed(0)}%</span>
      </div>
      
      {/* Start/Finish Labels */}
      <div className="flex justify-between mt-2 text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
        <span>The Academy</span>
        <span>The Emirates (10K)</span>
      </div>
    </div>
  );
}

