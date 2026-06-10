import React from "react";
import {interpolate, useCurrentFrame} from "remotion";

export function WordHighlightExample() {
  const frame = useCurrentFrame();
  const highlight = interpolate(frame, [18, 42], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div style={{fontSize: 58, fontWeight: 700, lineHeight: 1.15}}>
      Make the system{" "}
      <span style={{position: "relative", display: "inline-block"}}>
        <span
          style={{
            position: "absolute",
            left: 0,
            bottom: 4,
            height: 18,
            width: `${highlight * 100}%`,
            background: "#fde047",
            zIndex: -1,
          }}
        />
        legible
      </span>
      .
    </div>
  );
}
