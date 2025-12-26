import React, { useState, useEffect } from 'react';
import CountUp from 'react-countup';

interface AnimatedCounterProps {
  end: number;
  duration?: number;
  prefix?: string;
  suffix?: string;
  className?: string;
  decimals?: number;
}

export const AnimatedCounter: React.FC<AnimatedCounterProps> = ({ 
  end, 
  duration = 2.5, 
  prefix = '', 
  suffix = '',
  className = '',
  decimals = 0
}) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    // Small delay to ensure hydration is complete
    const timer = setTimeout(() => setMounted(true), 100);
    return () => clearTimeout(timer);
  }, []);

  if (!mounted) {
    // Show the final value during SSR/initial render to avoid flash
    return <span className={className}>{prefix}{end.toLocaleString()}{suffix}</span>;
  }

  return (
    <span className={className}>
      <CountUp
        start={0}
        end={end}
        duration={duration}
        separator=","
        prefix={prefix}
        suffix={suffix}
        decimals={decimals}
      />
    </span>
  );
};

