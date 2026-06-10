import React from "react";
import {interpolate, useCurrentFrame} from "remotion";

export function TypewriterExample({text = "Build the proof, then tell the story."}: {text?: string}) {
  const frame = useCurrentFrame();
  const visibleChars = Math.floor(interpolate(frame, [0, 80], [0, text.length], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  }));
  const cursorVisible = Math.floor(frame / 12) % 2 === 0;

  return (
    <div style={{fontSize: 54, fontWeight: 700, letterSpacing: 0}}>
      {text.slice(0, visibleChars)}
      <span style={{opacity: cursorVisible ? 1 : 0}}>|</span>
    </div>
  );
}
