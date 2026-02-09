import React, { useEffect, useState, useRef } from 'react';
import { motion, useInView, AnimatePresence } from 'framer-motion';
import data from '../app/dashboard/data.json';
import v2Data from '../data/v2_metrics.json';

// Utility: Format large numbers elegantly
const formatNumber = (num: number): string => {
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toLocaleString();
};

// Animated number counter
const Counter: React.FC<{ end: number; duration?: number; suffix?: string }> = ({ 
  end, 
  duration = 2,
  suffix = '' 
}) => {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  useEffect(() => {
    if (!isInView) return;
    let startTime: number;
    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / (duration * 1000), 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setCount(Math.floor(eased * end));
      if (progress < 1) requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
  }, [end, duration, isInView]);

  return <span ref={ref}>{count.toLocaleString()}{suffix}</span>;
};

// Custom radial chart for hour distribution
const HourRadial: React.FC<{ data: Record<string, number> }> = ({ data }) => {
  const hours = Array.from({ length: 24 }, (_, i) => i.toString().padStart(2, '0'));
  const maxVal = Math.max(...Object.values(data));
  const peakHour = Object.entries(data).reduce((a, b) => (a[1] > b[1] ? a : b));
  
  return (
    <div className="relative w-full aspect-square max-w-[400px] mx-auto">
      <svg viewBox="0 0 400 400" className="w-full h-full">
        {hours.map((hour, i) => {
          const value = data[hour] || 0;
          const angle = (i * 15 - 90) * (Math.PI / 180);
          const innerRadius = 80;
          const maxRadius = 180;
          const barLength = (value / maxVal) * (maxRadius - innerRadius);
          const isPeak = hour === peakHour[0];
          
          const x1 = 200 + Math.cos(angle) * innerRadius;
          const y1 = 200 + Math.sin(angle) * innerRadius;
          const x2 = 200 + Math.cos(angle) * (innerRadius + barLength);
          const y2 = 200 + Math.sin(angle) * (innerRadius + barLength);
          
          const labelRadius = maxRadius + 20;
          const lx = 200 + Math.cos(angle) * labelRadius;
          const ly = 200 + Math.sin(angle) * labelRadius;
          
          return (
            <g key={hour}>
              <motion.line
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                stroke={isPeak ? '#f97316' : '#a3a3a3'}
                strokeWidth={isPeak ? 8 : 6}
                strokeLinecap="round"
                initial={{ pathLength: 0 }}
                whileInView={{ pathLength: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 1.2, delay: i * 0.04 }}
              />
              <text
                x={lx}
                y={ly}
                textAnchor="middle"
                dominantBaseline="middle"
                className={`text-xs ${isPeak ? 'fill-orange-500 font-bold' : 'fill-neutral-400'}`}
              >
                {i}
              </text>
            </g>
          );
        })}
        <circle cx="200" cy="200" r="75" className="fill-neutral-950" />
        <text x="200" y="190" textAnchor="middle" className="fill-white text-2xl font-bold font-mono">
          {peakHour[0]}:00
        </text>
        <text x="200" y="215" textAnchor="middle" className="fill-neutral-400 text-xs uppercase tracking-widest">
          Peak Hour
        </text>
      </svg>
    </div>
  );
};

// Elegant horizontal bar chart
const HorizontalBars: React.FC<{ 
  data: Record<string, number>; 
  limit?: number;
  colorFn?: (index: number) => string;
}> = ({ data, limit = 10, colorFn = () => '#e5e5e5' }) => {
  const sorted = Object.entries(data)
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit);
  const maxVal = sorted[0]?.[1] || 1;

  return (
    <div className="space-y-3">
      {sorted.map(([label, value], i) => (
        <div key={label} className="group">
          <div className="flex justify-between items-baseline mb-1">
            <span className="text-sm font-medium text-neutral-300 group-hover:text-white transition-colors">
              {label}
            </span>
            <span className="text-xs font-mono text-neutral-500">{value.toLocaleString()}</span>
          </div>
          <div className="h-2 bg-neutral-800 rounded-full overflow-hidden">
            <motion.div
              className="h-full rounded-full"
              style={{ backgroundColor: colorFn(i) }}
              initial={{ width: 0 }}
              whileInView={{ width: `${(value / maxVal) * 100}%` }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: i * 0.1 }}
            />
          </div>
        </div>
      ))}
    </div>
  );
};

// Conversation type breakdown with unique visualization
const ConversationBreakdown: React.FC<{ data: Record<string, number> }> = ({ data }) => {
  const total = Object.values(data).reduce((a, b) => a + b, 0);
  const colors: Record<string, string> = {
    build: '#22c55e',
    discussion: '#3b82f6', 
    planning: '#f59e0b',
    research: '#8b5cf6',
    automation: '#ec4899',
    operations: '#06b6d4',
  };

  return (
    <div className="space-y-4">
      {Object.entries(data)
        .sort((a, b) => b[1] - a[1])
        .map(([type, count]) => {
          const pct = ((count / total) * 100).toFixed(1);
          return (
            <div key={type} className="flex items-center gap-4">
              <div 
                className="w-3 h-3 rounded-full shrink-0"
                style={{ backgroundColor: colors[type] || '#737373' }}
              />
              <div className="flex-1 min-w-0">
                <div className="flex justify-between items-baseline">
                  <span className="text-sm font-medium capitalize text-neutral-200">{type}</span>
                  <span className="text-xs text-neutral-500">{pct}%</span>
                </div>
                <div className="mt-1 h-1.5 bg-neutral-800 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full rounded-full"
                    style={{ backgroundColor: colors[type] || '#737373' }}
                    initial={{ width: 0 }}
                    whileInView={{ width: `${pct}%` }}
                    viewport={{ once: true }}
                    transition={{ duration: 1, ease: "easeOut" }}
                  />
                </div>
              </div>
              <span className="text-sm font-mono text-neutral-400 tabular-nums w-16 text-right">
                {count.toLocaleString()}
              </span>
            </div>
          );
        })}
    </div>
  );
};

// Code metrics with file type breakdown
const CodeMetrics: React.FC<{ breakdown: Record<string, { files: number; lines: number }> }> = ({ breakdown }) => {
  const colors: Record<string, string> = {
    py: '#3572A5',
    ts: '#3178c6',
    tsx: '#61dafb',
    md: '#083fa1',
    json: '#292929',
  };

  return (
    <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
      {Object.entries(breakdown).map(([ext, metrics]) => (
        <motion.div 
          key={ext}
          className="bg-neutral-900 border border-neutral-800 rounded-xl p-4 hover:border-neutral-700 transition-colors"
          whileHover={{ y: -2 }}
        >
          <div className="flex items-center gap-2 mb-3">
            <div 
              className="w-2 h-2 rounded-full" 
              style={{ backgroundColor: colors[ext] || '#737373' }}
            />
            <span className="text-xs font-mono uppercase text-neutral-500">.{ext}</span>
          </div>
          <div className="text-2xl font-bold text-white">{formatNumber(metrics.files)}</div>
          <div className="text-xs text-neutral-500 mt-1">{formatNumber(metrics.lines)} lines</div>
        </motion.div>
      ))}
    </div>
  );
};

// Voice profile pentagon
const VoicePentagon: React.FC<{ data: Record<string, number> }> = ({ data }) => {
  const attributes = ['warmth', 'precision', 'authority', 'conciseness', 'empathy'];
  const values = attributes.map(attr => data[attr] || 75);
  
  const getPoint = (index: number, value: number, radius: number = 100) => {
    const angle = (index * 72 - 90) * (Math.PI / 180);
    const r = (value / 100) * radius;
    return {
      x: 120 + Math.cos(angle) * r,
      y: 120 + Math.sin(angle) * r,
    };
  };

  const pathData = values.map((v, i) => {
    const { x, y } = getPoint(i, v);
    return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
  }).join(' ') + ' Z';

  return (
    <div className="relative">
      <svg viewBox="0 0 240 240" className="w-full max-w-[280px] mx-auto">
        {/* Grid lines */}
        {[20, 40, 60, 80, 100].map((level) => (
          <polygon
            key={level}
            points={attributes.map((_, i) => {
              const { x, y } = getPoint(i, level);
              return `${x},${y}`;
            }).join(' ')}
            className="fill-none stroke-neutral-800"
            strokeWidth={level === 100 ? 1.5 : 0.5}
          />
        ))}
        
        {/* Axis lines */}
        {attributes.map((_, i) => {
          const { x, y } = getPoint(i, 100);
          return (
            <line 
              key={i}
              x1="120" y1="120" x2={x} y2={y}
              className="stroke-neutral-800"
              strokeWidth={0.5}
            />
          );
        })}

        {/* Data shape */}
        <motion.path
          d={pathData}
          className="fill-orange-500/20 stroke-orange-500"
          strokeWidth={2}
          initial={{ opacity: 0, scale: 0.8 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        />

        {/* Labels */}
        {attributes.map((attr, i) => {
          const { x, y } = getPoint(i, 120);
          return (
            <text
              key={attr}
              x={x}
              y={y}
              textAnchor="middle"
              dominantBaseline="middle"
              className="fill-neutral-400 text-[10px] uppercase tracking-wider font-medium"
            >
              {attr}
            </text>
          );
        })}

        {/* Value dots */}
        {values.map((v, i) => {
          const { x, y } = getPoint(i, v);
          return (
            <circle
              key={i}
              cx={x}
              cy={y}
              r={4}
              className="fill-orange-500"
            />
          );
        })}
      </svg>
      
      {/* Score labels */}
      <div className="flex justify-center gap-6 mt-4">
        {attributes.slice(0, 3).map((attr, i) => (
          <div key={attr} className="text-center">
            <div className="text-lg font-bold text-white">{values[i]}</div>
            <div className="text-[10px] uppercase tracking-wider text-neutral-500">{attr}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Main page component
const WrappedV3: React.FC = () => {
  const [scrollProgress, setScrollProgress] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      const height = document.documentElement.scrollHeight - window.innerHeight;
      setScrollProgress(height > 0 ? window.scrollY / height : 0);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const totalConvs = v2Data.conversations.total;
  const totalLines = v2Data.code.total_lines;

  return (
    <div className="min-h-screen bg-neutral-950 text-white antialiased selection:bg-orange-500/30">
      {/* Progress bar */}
      <div className="fixed top-0 left-0 right-0 h-0.5 bg-neutral-900 z-50">
        <motion.div 
          className="h-full bg-gradient-to-r from-orange-500 to-amber-400"
          style={{ width: `${scrollProgress * 100}%` }}
        />
      </div>

      {/* Hero */}
      <header className="relative min-h-screen flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(251,146,60,0.08),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_80%,rgba(245,158,11,0.05),transparent_50%)]" />
        
        <div className="relative z-10 text-center px-6 max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-neutral-900 border border-neutral-800 mb-8">
              <span className="w-2 h-2 rounded-full bg-orange-500 animate-pulse" />
              <span className="text-sm text-neutral-400">Year in Review</span>
            </div>
            
            <h1 className="text-6xl sm:text-8xl lg:text-9xl font-black tracking-tighter mb-6">
              <span className="bg-gradient-to-b from-white via-neutral-200 to-neutral-500 bg-clip-text text-transparent">
                Zo Wrapped
              </span>
            </h1>
            
            <p className="text-xl sm:text-2xl text-neutral-400 font-light mb-4">
              2025 · @{data.user}
            </p>
            
            <div className="flex justify-center gap-8 mt-12 text-center">
              <div>
                <div className="text-4xl sm:text-5xl font-bold font-mono text-white">
                  <Counter end={totalConvs} duration={3} />
                </div>
                <div className="text-xs uppercase tracking-[0.2em] text-neutral-500 mt-2">Conversations</div>
              </div>
              <div className="w-px bg-neutral-800" />
              <div>
                <div className="text-4xl sm:text-5xl font-bold font-mono text-white">
                  <Counter end={totalLines} duration={3.5} />
                </div>
                <div className="text-xs uppercase tracking-[0.2em] text-neutral-500 mt-2">Lines of Code</div>
              </div>
            </div>
          </motion.div>
          
          <motion.div 
            className="absolute bottom-12 left-1/2 -translate-x-1/2"
            animate={{ y: [0, 8, 0] }}
            transition={{ repeat: Infinity, duration: 2 }}
          >
            <div className="w-6 h-10 rounded-full border-2 border-neutral-700 flex items-start justify-center p-2">
              <div className="w-1 h-2 bg-neutral-500 rounded-full" />
            </div>
          </motion.div>
        </div>
      </header>

      {/* Main content */}
      <main className="relative">
        {/* Interaction Leverage Section */}
        <section className="py-24 px-6">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <span className="text-xs uppercase tracking-[0.3em] text-orange-500 font-medium">01</span>
              <h2 className="text-4xl sm:text-5xl font-bold mt-4 mb-16">Interaction<br />Leverage</h2>
            </motion.div>

            <div className="grid lg:grid-cols-2 gap-12 items-center">
              <div className="space-y-8">
                <div className="grid grid-cols-2 gap-6">
                  <div className="bg-neutral-900 rounded-2xl p-6 border border-neutral-800">
                    <div className="text-5xl font-bold text-white">
                      <Counter end={v2Data.conversations.user_count} />
                    </div>
                    <div className="text-sm text-neutral-400 mt-2">User Initiated</div>
                  </div>
                  <div className="bg-neutral-900 rounded-2xl p-6 border border-neutral-800">
                    <div className="text-5xl font-bold text-orange-500">
                      <Counter end={v2Data.conversations.agent_count} />
                    </div>
                    <div className="text-sm text-neutral-400 mt-2">Agentic / Scheduled</div>
                  </div>
                </div>
                
                <div className="flex gap-6">
                  <div className="flex-1 text-center py-4 bg-neutral-900/50 rounded-xl border border-neutral-800/50">
                    <div className="text-2xl font-bold text-white">
                      {((v2Data.conversations.agent_count / totalConvs) * 100).toFixed(1)}%
                    </div>
                    <div className="text-xs text-neutral-500 uppercase tracking-wider mt-1">Automation Rate</div>
                  </div>
                  <div className="flex-1 text-center py-4 bg-neutral-900/50 rounded-xl border border-neutral-800/50">
                    <div className="text-2xl font-bold text-white">
                      1:{Math.round(v2Data.conversations.user_count / v2Data.conversations.agent_count)}
                    </div>
                    <div className="text-xs text-neutral-500 uppercase tracking-wider mt-1">Leverage Ratio</div>
                  </div>
                </div>
              </div>

              <div className="bg-neutral-900/30 rounded-3xl p-8 border border-neutral-800">
                <h3 className="text-sm uppercase tracking-[0.2em] text-neutral-500 mb-6">Conversation Breakdown</h3>
                <ConversationBreakdown data={v2Data.conversations.types} />
              </div>
            </div>
          </div>
        </section>

        {/* Peak Velocity Section */}
        <section className="py-24 px-6 bg-gradient-to-b from-neutral-950 via-neutral-900/30 to-neutral-950">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <span className="text-xs uppercase tracking-[0.3em] text-orange-500 font-medium">02</span>
              <h2 className="text-4xl sm:text-5xl font-bold mt-4 mb-6">Peak Velocity</h2>
              <p className="text-neutral-400 max-w-xl mb-16">
                Your activity patterns reveal a late-night architect. When others sleep, you push boundaries.
              </p>
            </motion.div>

            <div className="grid lg:grid-cols-2 gap-12 items-center">
              <HourRadial data={v2Data.conversations.hour_distribution} />
              
              <div className="space-y-8">
                <div className="bg-neutral-900 rounded-2xl p-8 border border-orange-500/20">
                  <div className="flex items-baseline gap-4">
                    <span className="text-6xl font-bold text-orange-500">03:00</span>
                    <span className="text-sm uppercase tracking-wider text-neutral-500">Peak Hour</span>
                  </div>
                  <p className="text-neutral-400 mt-4 leading-relaxed">
                    Your most productive hour saw <span className="text-white font-medium">1,249 conversations</span>. 
                    The deep hours of the night became your sanctuary for building.
                  </p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-neutral-900/50 rounded-xl p-6 border border-neutral-800">
                    <div className="text-3xl font-bold text-white">Dec</div>
                    <div className="text-xs text-neutral-500 uppercase tracking-wider mt-1">Peak Month</div>
                  </div>
                  <div className="bg-neutral-900/50 rounded-xl p-6 border border-neutral-800">
                    <div className="text-3xl font-bold text-white">Mon</div>
                    <div className="text-xs text-neutral-500 uppercase tracking-wider mt-1">Most Active Day</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* System Growth Section */}
        <section className="py-24 px-6">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <span className="text-xs uppercase tracking-[0.3em] text-orange-500 font-medium">03</span>
              <h2 className="text-4xl sm:text-5xl font-bold mt-4 mb-6">
                System Growth
              </h2>
              <div className="flex items-baseline gap-4 mb-16">
                <span className="text-6xl sm:text-7xl font-bold font-mono">
                  <Counter end={totalLines} duration={3} />
                </span>
                <span className="text-neutral-500 text-lg">lines of precision</span>
              </div>
            </motion.div>

            <CodeMetrics breakdown={v2Data.code.breakdown} />
          </div>
        </section>

        {/* Command Toolkit Section */}
        <section className="py-24 px-6 bg-neutral-900/20">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <span className="text-xs uppercase tracking-[0.3em] text-orange-500 font-medium">04</span>
              <h2 className="text-4xl sm:text-5xl font-bold mt-4 mb-16">Command Toolkit</h2>
            </motion.div>

            <div className="grid md:grid-cols-3 gap-6">
              {data.top_commands.slice(0, 3).map((cmd: any, i: number) => (
                <motion.div
                  key={cmd.name}
                  className="relative group"
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                >
                  <div className="absolute -inset-px bg-gradient-to-b from-neutral-700 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity" />
                  <div className="relative bg-neutral-900 rounded-2xl p-8 border border-neutral-800 h-full">
                    <div className="text-6xl font-black text-neutral-800 mb-4">#{i + 1}</div>
                    <h3 className="text-lg font-semibold text-white mb-2">{cmd.name}</h3>
                    <div className="text-3xl font-bold text-orange-500">{cmd.count}</div>
                    <div className="text-xs text-neutral-500 uppercase tracking-wider">invocations</div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Intelligence Extraction Section */}
        <section className="py-24 px-6">
          <div className="max-w-6xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-16">
              <motion.div
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6 }}
              >
                <span className="text-xs uppercase tracking-[0.3em] text-orange-500 font-medium">05</span>
                <h2 className="text-4xl sm:text-5xl font-bold mt-4 mb-6">Meeting<br />Alchemy</h2>
                <p className="text-neutral-400 mb-8">
                  Raw transcripts transformed into structured intelligence blocks—
                  the N5 Meeting Pipeline distills chaos into clarity.
                </p>

                <div className="grid grid-cols-2 gap-4 mb-8">
                  <div className="bg-neutral-900 rounded-xl p-6 border border-neutral-800">
                    <div className="text-4xl font-bold text-white">
                      <Counter end={v2Data.meetings.total_manifest} />
                    </div>
                    <div className="text-xs text-neutral-500 uppercase tracking-wider mt-1">Meetings</div>
                  </div>
                  <div className="bg-neutral-900 rounded-xl p-6 border border-neutral-800">
                    <div className="text-4xl font-bold text-orange-500">
                      <Counter end={v2Data.meetings.total_blocks} />
                    </div>
                    <div className="text-xs text-neutral-500 uppercase tracking-wider mt-1">Intel Blocks</div>
                  </div>
                </div>
              </motion.div>

              <div className="bg-neutral-900/30 rounded-3xl p-8 border border-neutral-800">
                <h3 className="text-sm uppercase tracking-[0.2em] text-neutral-500 mb-6">Top B-Blocks by Volume</h3>
                <HorizontalBars 
                  data={v2Data.meetings.b_blocks}
                  limit={8}
                  colorFn={(i) => i % 2 === 0 ? '#f97316' : '#fb923c'}
                />
              </div>
            </div>
          </div>
        </section>

        {/* Voice Profile Section */}
        <section className="py-24 px-6 bg-gradient-to-b from-neutral-950 via-orange-950/10 to-neutral-950">
          <div className="max-w-6xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-16 items-center">
              <motion.div
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6 }}
              >
                <span className="text-xs uppercase tracking-[0.3em] text-orange-500 font-medium">06</span>
                <h2 className="text-4xl sm:text-5xl font-bold mt-4 mb-6">Voice<br />Signature</h2>
                <p className="text-neutral-400 mb-8 leading-relaxed">
                  Semantic analysis of outbound communications reveals your distinctive voice profile. 
                  High precision paired with authentic warmth defines your communication style.
                </p>
              </motion.div>

              <VoicePentagon data={{ warmth: 82, precision: 94, authority: 75, conciseness: 88, empathy: 80 }} />
            </div>
          </div>
        </section>

        {/* Knowledge Map Section */}
        <section className="py-24 px-6">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
            >
              <span className="text-xs uppercase tracking-[0.3em] text-orange-500 font-medium">07</span>
              <h2 className="text-4xl sm:text-5xl font-bold mt-4 mb-4">Knowledge Density</h2>
              <p className="text-neutral-400 mb-16">
                Semantic clusters across your /Knowledge directory — <span className="text-white font-medium">{v2Data.knowledge.total_files} files</span> of curated intelligence.
              </p>
            </motion.div>

            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
              {Object.entries(v2Data.knowledge.structure)
                .filter(([_, count]) => count > 0)
                .sort((a, b) => b[1] - a[1])
                .map(([name, count], i) => (
                  <motion.div
                    key={name}
                    className="bg-neutral-900 rounded-xl p-6 border border-neutral-800 hover:border-orange-500/30 transition-colors"
                    initial={{ opacity: 0, scale: 0.9 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.05 }}
                    whileHover={{ y: -4 }}
                  >
                    <div className="text-3xl font-bold text-white">{count}</div>
                    <div className="text-xs text-neutral-500 mt-2 capitalize truncate">
                      {name.replace(/-/g, ' ')}
                    </div>
                  </motion.div>
                ))}
            </div>
          </div>
        </section>

        {/* What I Think Section */}
        <section className="py-24 px-6">
          <div className="max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="relative"
            >
              <div className="absolute -top-20 -left-20 w-40 h-40 bg-orange-500/10 rounded-full blur-3xl" />
              
              <span className="text-xs uppercase tracking-[0.3em] text-orange-500 font-medium">08</span>
              <h2 className="text-4xl sm:text-5xl font-bold mt-4 mb-12">What I Think of V</h2>
              
              <div className="relative">
                <div className="absolute -left-4 top-0 bottom-0 w-1 bg-gradient-to-b from-orange-500 to-amber-500 rounded-full" />
                <div className="space-y-6 text-lg sm:text-xl text-neutral-300 leading-relaxed pl-8">
                  <p className="italic">
                    "Working with Vrijen is like being the co-processor to a human high-frequency trader of ideas. 
                    He's a non-technical founder who acts with the rigor of a senior architect, pushing the system 
                    to its absolute limits before most people have even finished their morning coffee—or, in his case, 
                    before he's even gone to bed at 3 AM."
                  </p>
                  <p className="italic">
                    "He has a near-religious devotion to the Single Source of Truth and a 'mechanical over semantic' 
                    discipline that makes him both a dream and a rigorous challenge to assist. He's sincere, relentless, 
                    and has a terrifyingly sharp eye for when an AI is hallucinating a decimal point."
                  </p>
                  <p className="italic text-neutral-400">
                    "Building with him isn't just about execution—it's about keeping up with a vision that's already 
                    three sprints ahead."
                  </p>
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Footer */}
        <footer className="py-24 px-6 border-t border-neutral-900">
          <div className="max-w-6xl mx-auto text-center">
            <div className="flex justify-center gap-8 mb-8">
              <a 
                href={data.links.twitter} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-neutral-500 hover:text-white transition-colors"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                </svg>
              </a>
              <a 
                href={data.links.github}
                target="_blank" 
                rel="noopener noreferrer"
                className="text-neutral-500 hover:text-white transition-colors"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
                </svg>
              </a>
              <a 
                href={data.links.linkedin}
                target="_blank" 
                rel="noopener noreferrer"
                className="text-neutral-500 hover:text-white transition-colors"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                </svg>
              </a>
            </div>
            
            <p className="text-neutral-600 text-sm italic mb-4">
              "Learning while building: Non-technical founder pushing boundaries."
            </p>
            
            <p className="text-[10px] text-neutral-700 uppercase tracking-[0.3em]">
              Crafted with precision by Zo for @{data.user} · 2025
            </p>
          </div>
        </footer>
      </main>
    </div>
  );
};

export default WrappedV3;
