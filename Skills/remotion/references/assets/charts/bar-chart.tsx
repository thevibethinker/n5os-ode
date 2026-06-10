import React from "react";
import {interpolate, useCurrentFrame} from "remotion";

type Bar = {
  label: string;
  value: number;
  color: string;
};

const bars: Bar[] = [
  {label: "Plan", value: 72, color: "#2563eb"},
  {label: "Build", value: 91, color: "#16a34a"},
  {label: "Verify", value: 64, color: "#f97316"},
];

export function BarChartExample() {
  const frame = useCurrentFrame();
  const progress = interpolate(frame, [0, 45], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div style={{display: "grid", gap: 18, width: 760}}>
      {bars.map((bar) => (
        <div key={bar.label} style={{display: "grid", gridTemplateColumns: "120px 1fr", gap: 18}}>
          <div style={{fontSize: 28, fontWeight: 700}}>{bar.label}</div>
          <div style={{height: 34, background: "#e5e7eb", borderRadius: 6, overflow: "hidden"}}>
            <div
              style={{
                width: `${bar.value * progress}%`,
                height: "100%",
                background: bar.color,
              }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
