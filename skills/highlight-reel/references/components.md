# Highlight Reel — Component Reference

## Poster

Static poster frame visible from frame 0. Shows the Quasar logo, title, and subtitle immediately with no animation delay, ensuring Slack/social thumbnails look great. Holds fully visible then fades out to let the LogoReveal scene take over. Includes decorative floating particles and a central glow effect.

```tsx
import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";

const COLORS = {
  cyan: "#8AD5FF",
  indigo: "#7A6AFD",
  fuchsia: "#EC69FF",
  dark: "#0A0A12",
  darkBlue: "#0D0F2B",
};

const GRADIENT = `linear-gradient(135deg, ${COLORS.cyan} 0%, ${COLORS.indigo} 50%, ${COLORS.fuchsia} 100%)`;

/**
 * Static poster frame visible from frame 0.
 * Shows the logo, title, and subtitle immediately — no animation delay.
 * This ensures Slack/social thumbnails look great.
 */
export const Poster: React.FC<{
  holdFrames?: number;
  fadeOutFrames?: number;
}> = ({ holdFrames = 10, fadeOutFrames = 15 }) => {
  const frame = useCurrentFrame();

  // Hold fully visible, then fade out to let LogoReveal take over
  const opacity = interpolate(
    frame,
    [0, holdFrames, holdFrames + fadeOutFrames],
    [1, 1, 0],
    { extrapolateRight: "clamp" }
  );

  const bgAngle = interpolate(frame, [0, 120], [0, 30]);

  // Floating particles for visual interest at frame 0
  const particles = Array.from({ length: 16 }, (_, i) => {
    const angle = (i / 16) * Math.PI * 2;
    const radius = 200 + (i % 3) * 60;
    return {
      x: Math.cos(angle) * radius,
      y: Math.sin(angle) * radius,
      size: 3 + (i % 4) * 2,
      color: [COLORS.cyan, COLORS.indigo, COLORS.fuchsia][i % 3],
    };
  });

  return (
    <AbsoluteFill
      style={{
        opacity,
        zIndex: 10,
        background: `conic-gradient(from ${bgAngle}deg, ${COLORS.dark}, ${COLORS.darkBlue}, ${COLORS.dark})`,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      {/* Particles */}
      {particles.map((p, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            width: p.size,
            height: p.size,
            borderRadius: "50%",
            background: p.color,
            opacity: 0.6,
            transform: `translate(${p.x}px, ${p.y}px)`,
            boxShadow: `0 0 12px ${p.color}66`,
          }}
        />
      ))}

      {/* Central glow */}
      <div
        style={{
          position: "absolute",
          width: 400,
          height: 400,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${COLORS.indigo}55, transparent 70%)`,
          filter: "blur(40px)",
        }}
      />

      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 24 }}>
        {/* Logo icon */}
        <div
          style={{
            width: 140,
            height: 140,
            borderRadius: 28,
            background: GRADIENT,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            boxShadow: `0 0 80px ${COLORS.indigo}66, 0 0 160px ${COLORS.fuchsia}33`,
          }}
        >
          <svg width="80" height="80" viewBox="0 0 24 24" fill="none">
            <path
              d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z"
              fill="white"
            />
          </svg>
        </div>

        {/* Title */}
        <div
          style={{
            fontSize: 72,
            fontWeight: 800,
            fontFamily: "SF Pro Display, -apple-system, sans-serif",
            background: GRADIENT,
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            letterSpacing: "-0.02em",
          }}
        >
          QUASAR
        </div>

        {/* Subtitle */}
        <div
          style={{
            fontSize: 28,
            fontWeight: 500,
            color: "rgba(255,255,255,0.7)",
            fontFamily: "SF Pro Display, -apple-system, sans-serif",
          }}
        >
          AI Website Generator
        </div>
      </div>
    </AbsoluteFill>
  );
};
```

## SectionTitle

Full-screen section title card displayed between demo sections. Shows a section number (monospace, gradient text), large white title, and muted subtitle. Each element animates in with a staggered spring entrance and vertical slide. Background uses a slowly rotating conic gradient.

```tsx
import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

const COLORS = {
  cyan: "#8AD5FF",
  indigo: "#7A6AFD",
  fuchsia: "#EC69FF",
  dark: "#0A0A12",
};

const GRADIENT = `linear-gradient(135deg, ${COLORS.cyan} 0%, ${COLORS.indigo} 50%, ${COLORS.fuchsia} 100%)`;

export const SectionTitle: React.FC<{
  number: string;
  title: string;
  subtitle: string;
}> = ({ number, title, subtitle }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const numS = spring({ frame, fps, config: { damping: 12 }, durationInFrames: 15 });
  const titleS = spring({ frame: frame - 5, fps, config: { damping: 14 }, durationInFrames: 18 });
  const subS = spring({ frame: frame - 12, fps, config: { damping: 15 }, durationInFrames: 18 });

  const bgAngle = interpolate(frame, [0, 45], [0, 40]);

  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        background: `conic-gradient(from ${bgAngle}deg, ${COLORS.dark}, #0D0F2B, ${COLORS.dark})`,
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        gap: 16,
      }}
    >
      {/* Section number */}
      <div
        style={{
          fontSize: 20,
          fontWeight: 700,
          fontFamily: "SF Mono, Menlo, monospace",
          background: GRADIENT,
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          opacity: numS,
          transform: `translateY(${interpolate(numS, [0, 1], [15, 0])}px)`,
          letterSpacing: "0.15em",
          textTransform: "uppercase",
        }}
      >
        {number}
      </div>

      {/* Title */}
      <div
        style={{
          fontSize: 72,
          fontWeight: 800,
          fontFamily: "SF Pro Display, -apple-system, sans-serif",
          color: "#FFFFFF",
          letterSpacing: "-0.03em",
          opacity: titleS,
          transform: `translateY(${interpolate(titleS, [0, 1], [30, 0])}px)`,
        }}
      >
        {title}
      </div>

      {/* Subtitle */}
      <div
        style={{
          fontSize: 26,
          fontWeight: 400,
          fontFamily: "SF Pro Text, -apple-system, sans-serif",
          color: "rgba(255,255,255,0.5)",
          opacity: subS,
          transform: `translateY(${interpolate(subS, [0, 1], [15, 0])}px)`,
        }}
      >
        {subtitle}
      </div>
    </div>
  );
};
```

## SectionBadge

Persistent section badge shown in the top-left corner during demo clips (e.g. "01 -- Prompt to Website"). Contains a gradient-filled number chip and a semi-transparent title label. Slides in from the left with a spring animation after an optional delay.

```tsx
import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

const GRADIENT = "linear-gradient(135deg, #8AD5FF 0%, #7A6AFD 50%, #EC69FF 100%)";

/**
 * Persistent section badge shown in the top-left corner during clips.
 * e.g. "01 — Prompt to Website"
 */
export const SectionBadge: React.FC<{
  number: string;
  title: string;
  delay?: number;
}> = ({ number, title, delay = 4 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const s = spring({
    frame: frame - delay,
    fps,
    config: { damping: 14, mass: 0.6 },
    durationInFrames: 16,
  });
  const x = interpolate(s, [0, 1], [-30, 0]);

  return (
    <div
      style={{
        position: "absolute",
        top: 36,
        left: 40,
        zIndex: 50,
        opacity: s,
        transform: `translateX(${x}px)`,
        display: "flex",
        alignItems: "center",
        gap: 12,
      }}
    >
      {/* Number chip */}
      <div
        style={{
          padding: "6px 14px",
          borderRadius: 8,
          background: GRADIENT,
          fontSize: 16,
          fontWeight: 800,
          fontFamily: "SF Mono, Menlo, monospace",
          color: "#FFFFFF",
          letterSpacing: "0.05em",
        }}
      >
        {number}
      </div>

      {/* Title */}
      <span
        style={{
          fontSize: 18,
          fontWeight: 600,
          fontFamily: "SF Pro Display, -apple-system, sans-serif",
          color: "rgba(255,255,255,0.75)",
          letterSpacing: "-0.01em",
        }}
      >
        {title}
      </span>
    </div>
  );
};
```

## InsightLabel

Animated insight label that appears over video clips, positioned at the bottom of the frame. Has two visual modes: V1 (`bold=false`) renders smaller gradient-colored text, while V2 (`bold=true`) renders larger white text on a strong dark backdrop with a subtle indigo border glow for improved readability. Supports `bottom-left` and `bottom-center` positioning.

```tsx
import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

/**
 * Animated insight label that appears over video clips.
 * V1 (bold=false): gradient text, smaller.
 * V2 (bold=true): white text on strong dark bg, much more readable.
 */
export const InsightLabel: React.FC<{
  text: string;
  delay?: number;
  position?: "bottom-left" | "bottom-center";
  bold?: boolean;
}> = ({ text, delay = 8, position = "bottom-center", bold = false }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const s = spring({
    frame: frame - delay,
    fps,
    config: { damping: 14, mass: 0.7 },
    durationInFrames: 18,
  });
  const y = interpolate(s, [0, 1], [30, 0]);

  const positionStyles: React.CSSProperties =
    position === "bottom-center"
      ? { bottom: bold ? 44 : 60, left: "50%", transform: `translateX(-50%) translateY(${y}px)` }
      : { bottom: bold ? 44 : 60, left: 60, transform: `translateY(${y}px)` };

  if (bold) {
    return (
      <div
        style={{
          position: "absolute",
          ...positionStyles,
          zIndex: 50,
          opacity: s,
        }}
      >
        <div
          style={{
            padding: "16px 44px",
            borderRadius: 999,
            background: "rgba(10, 10, 18, 0.94)",
            backdropFilter: "blur(24px)",
            border: "1.5px solid rgba(122, 106, 253, 0.45)",
            boxShadow:
              "0 16px 56px rgba(0,0,0,0.7), 0 0 28px rgba(122,106,253,0.15)",
          }}
        >
          <span
            style={{
              fontSize: 28,
              fontWeight: 700,
              fontFamily: "SF Pro Display, -apple-system, sans-serif",
              color: "#FFFFFF",
              letterSpacing: "-0.01em",
              textShadow: "0 0 20px rgba(122,106,253,0.4)",
            }}
          >
            {text}
          </span>
        </div>
      </div>
    );
  }

  // V1 style (gradient text)
  return (
    <div
      style={{
        position: "absolute",
        ...positionStyles,
        zIndex: 50,
        opacity: s,
      }}
    >
      <div
        style={{
          padding: "14px 32px",
          borderRadius: 999,
          background: "rgba(10, 10, 18, 0.88)",
          backdropFilter: "blur(24px)",
          border: "1px solid rgba(122, 106, 253, 0.35)",
          boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
        }}
      >
        <span
          style={{
            fontSize: 22,
            fontWeight: 600,
            fontFamily: "SF Pro Display, -apple-system, sans-serif",
            background:
              "linear-gradient(135deg, #8AD5FF 0%, #7A6AFD 50%, #EC69FF 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            letterSpacing: "-0.01em",
          }}
        >
          {text}
        </span>
      </div>
    </div>
  );
};
```

## PromptCaption

Typewriter-style prompt caption shown at the bottom of the screen. Types out the prompt text character by character at a configurable rate, with a blinking cursor that persists after typing completes. Includes a small gradient icon and "Prompt" label header. The entire container slides up with a spring entrance animation.

```tsx
import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

const GRADIENT = "linear-gradient(135deg, #8AD5FF 0%, #7A6AFD 50%, #EC69FF 100%)";

/**
 * Typewriter-style prompt caption shown at the bottom of the screen.
 * Types out the prompt text character by character with a blinking cursor.
 */
export const PromptCaption: React.FC<{
  text: string;
  charsPerFrame?: number;
  delay?: number;
}> = ({ text, charsPerFrame = 3, delay = 8 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Entrance spring
  const enterS = spring({
    frame: frame - delay,
    fps,
    config: { damping: 14, mass: 0.6 },
    durationInFrames: 16,
  });
  const y = interpolate(enterS, [0, 1], [40, 0]);

  // Typewriter: how many characters to show
  const typingFrame = Math.max(0, frame - delay - 5);
  const charsVisible = Math.min(text.length, Math.floor(typingFrame * charsPerFrame));
  const displayText = text.slice(0, charsVisible);
  const isDone = charsVisible >= text.length;

  // Blinking cursor
  const cursorVisible = !isDone || Math.floor(frame / 8) % 2 === 0;

  return (
    <div
      style={{
        position: "absolute",
        bottom: 40,
        left: "50%",
        transform: `translateX(-50%) translateY(${y}px)`,
        zIndex: 55,
        opacity: enterS,
        maxWidth: 1200,
        width: "70%",
      }}
    >
      <div
        style={{
          padding: "18px 28px",
          borderRadius: 16,
          background: "rgba(10, 10, 18, 0.94)",
          backdropFilter: "blur(24px)",
          border: "1.5px solid rgba(122, 106, 253, 0.4)",
          boxShadow:
            "0 16px 56px rgba(0,0,0,0.7), 0 0 32px rgba(122,106,253,0.12)",
        }}
      >
        {/* Prompt icon + label */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            marginBottom: 10,
          }}
        >
          <div
            style={{
              width: 20,
              height: 20,
              borderRadius: 6,
              background: GRADIENT,
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              flexShrink: 0,
            }}
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none">
              <path
                d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z"
                fill="white"
              />
            </svg>
          </div>
          <span
            style={{
              fontSize: 13,
              fontWeight: 600,
              fontFamily: "SF Pro Display, -apple-system, sans-serif",
              color: "rgba(255,255,255,0.4)",
              letterSpacing: "0.06em",
              textTransform: "uppercase",
            }}
          >
            Prompt
          </span>
        </div>

        {/* Typed text */}
        <div
          style={{
            fontSize: 20,
            fontWeight: 500,
            fontFamily: "SF Pro Text, -apple-system, sans-serif",
            color: "rgba(255,255,255,0.92)",
            lineHeight: 1.5,
            letterSpacing: "-0.01em",
          }}
        >
          {displayText}
          {cursorVisible && (
            <span
              style={{
                display: "inline-block",
                width: 2,
                height: 22,
                background: "rgba(255,255,255,0.7)",
                marginLeft: 1,
                verticalAlign: "text-bottom",
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
};
```

## VideoFrame

Rounded video frame container with a gradient border glow. Does not include browser chrome -- used when source recordings already contain their own browser UI. Animates in with a spring-driven slide-up and scale entrance. Fixed dimensions of 1520x855.

```tsx
import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

const GRADIENT = "linear-gradient(135deg, #8AD5FF 0%, #7A6AFD 50%, #EC69FF 100%)";

/**
 * Rounded video frame with gradient border glow — no browser chrome.
 * Used when source recordings already contain their own browser UI.
 */
export const VideoFrame: React.FC<{
  children: React.ReactNode;
  delay?: number;
}> = ({ children, delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const s = spring({ frame: frame - delay, fps, config: { damping: 14 }, durationInFrames: 20 });
  const y = interpolate(s, [0, 1], [50, 0]);
  const scale = interpolate(s, [0, 1], [0.95, 1]);

  return (
    <div
      style={{
        width: 1520,
        height: 855,
        borderRadius: 16,
        overflow: "hidden",
        transform: `translateY(${y}px) scale(${scale})`,
        opacity: s,
        position: "relative",
        boxShadow: `
          0 0 0 2px rgba(122, 106, 253, 0.35),
          0 30px 100px rgba(0, 0, 0, 0.7),
          0 0 60px rgba(122, 106, 253, 0.12)
        `,
      }}
    >
      {/* Gradient border glow */}
      <div
        style={{
          position: "absolute",
          inset: -2,
          borderRadius: 18,
          background: GRADIENT,
          opacity: 0.25,
          zIndex: -1,
        }}
      />
      {children}
    </div>
  );
};
```

## ClipCrossfade

Brief crossfade overlay placed between non-contiguous clips. Fades to a near-opaque dark color and back, suggesting a time skip. Uses eased interpolation over a configurable duration (default 12 frames). Renders as a full-screen dark overlay at z-index 80.

```tsx
import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, Easing } from "remotion";

/**
 * Brief crossfade overlay between non-contiguous clips.
 * Fades to dark then back — suggests a time skip.
 */
export const ClipCrossfade: React.FC<{ durationInFrames?: number }> = ({
  durationInFrames = 12,
}) => {
  const frame = useCurrentFrame();
  const mid = durationInFrames / 2;

  const opacity = interpolate(
    frame,
    [0, mid, durationInFrames],
    [0, 0.85, 0],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.inOut(Easing.ease),
    }
  );

  return (
    <AbsoluteFill
      style={{
        background: "#0A0A12",
        opacity,
        zIndex: 80,
      }}
    />
  );
};
```

## SceneTransition

Full-screen gradient wipe transition between major sections. A gradient-filled panel slides across the screen from one side and exits to the other, creating a clean directional wipe effect. Supports `left` and `right` directions. Uses cubic easing over 30 frames total (15 in, 15 out). Renders at z-index 100 to cover all content.

```tsx
import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, Easing } from "remotion";

const GRADIENT = "linear-gradient(135deg, #8AD5FF 0%, #7A6AFD 50%, #EC69FF 100%)";

export const SceneTransition: React.FC<{ direction?: "left" | "right" }> = ({
  direction = "left",
}) => {
  const frame = useCurrentFrame();

  const progress = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });
  const exit = interpolate(frame, [15, 30], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });

  const x =
    direction === "left"
      ? interpolate(progress - exit, [-1, 0, 1], [-1920, 0, 1920])
      : interpolate(progress - exit, [-1, 0, 1], [1920, 0, -1920]);

  return (
    <AbsoluteFill
      style={{
        background: GRADIENT,
        transform: `translateX(${x}px)`,
        zIndex: 100,
      }}
    />
  );
};
```

## BrowserFrame

Decorative macOS-style browser frame wrapper with traffic light buttons (red/yellow/green), a monospace URL bar, and a gradient border glow. Content is rendered inside a dark content area below the chrome bar. The entire frame animates in with a spring-driven slide-up and scale. Fixed width of 1440px.

```tsx
import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

const GRADIENT = "linear-gradient(135deg, #8AD5FF 0%, #7A6AFD 50%, #EC69FF 100%)";

export const BrowserFrame: React.FC<{
  children: React.ReactNode;
  url?: string;
  delay?: number;
}> = ({ children, url = "quasar.app", delay = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const s = spring({ frame: frame - delay, fps, config: { damping: 14 }, durationInFrames: 25 });
  const y = interpolate(s, [0, 1], [80, 0]);
  const scale = interpolate(s, [0, 1], [0.92, 1]);

  return (
    <div
      style={{
        width: 1440,
        borderRadius: 20,
        overflow: "hidden",
        transform: `translateY(${y}px) scale(${scale})`,
        opacity: s,
        // Gradient border via box shadow trick
        boxShadow: `
          0 0 0 2px rgba(122, 106, 253, 0.4),
          0 40px 120px rgba(10, 10, 18, 0.8),
          0 0 80px rgba(122, 106, 253, 0.15)
        `,
        position: "relative",
      }}
    >
      {/* Gradient border overlay */}
      <div
        style={{
          position: "absolute",
          inset: -2,
          borderRadius: 22,
          background: GRADIENT,
          opacity: 0.3,
          zIndex: -1,
        }}
      />

      {/* macOS browser chrome */}
      <div
        style={{
          height: 52,
          background: "#1A1A2E",
          display: "flex",
          alignItems: "center",
          padding: "0 20px",
          gap: 8,
          borderBottom: "1px solid rgba(255,255,255,0.06)",
        }}
      >
        {/* Traffic lights */}
        <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#FF5F56" }} />
        <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#FFBD2E" }} />
        <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#27CA3F" }} />

        {/* URL bar */}
        <div
          style={{
            marginLeft: 24,
            flex: 1,
            maxWidth: 480,
            height: 30,
            borderRadius: 8,
            background: "rgba(13, 13, 32, 0.8)",
            display: "flex",
            alignItems: "center",
            padding: "0 14px",
            fontSize: 13,
            color: "#6E6E6E",
            fontFamily: "SF Mono, Menlo, monospace",
          }}
        >
          {url}
        </div>
      </div>

      {/* Content area */}
      <div
        style={{
          background: "#0A0A12",
          overflow: "hidden",
        }}
      >
        {children}
      </div>
    </div>
  );
};
```

## KineticText

Word-by-word kinetic text animation. Each word springs in with a staggered delay, translating up from below with rotation and scale. Supports gradient text mode (cyan-indigo-fuchsia) or plain white text. Configurable font size, stagger timing, and start delay. Words are rendered in a flex-wrap layout centered horizontally.

```tsx
import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig, Easing } from "remotion";

const COLORS = {
  cyan: "#8AD5FF",
  indigo: "#7A6AFD",
  fuchsia: "#EC69FF",
  white: "#FFFFFF",
};

const GRADIENT = `linear-gradient(135deg, ${COLORS.cyan} 0%, ${COLORS.indigo} 50%, ${COLORS.fuchsia} 100%)`;

export const KineticText: React.FC<{
  words: string[];
  staggerFrames?: number;
  startDelay?: number;
  fontSize?: number;
  gradient?: boolean;
}> = ({ words, staggerFrames = 8, startDelay = 0, fontSize = 80, gradient = true }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <div
      style={{
        display: "flex",
        flexWrap: "wrap",
        justifyContent: "center",
        gap: "16px 28px",
      }}
    >
      {words.map((word, i) => {
        const delay = startDelay + i * staggerFrames;
        const s = spring({
          frame: frame - delay,
          fps,
          config: { damping: 10, mass: 0.6 },
          durationInFrames: 18,
        });

        const y = interpolate(s, [0, 1], [120, 0]);
        const rotation = interpolate(s, [0, 1], [-8, 0]);
        const scale = interpolate(s, [0, 1], [0.3, 1]);

        return (
          <span
            key={i}
            style={{
              display: "inline-block",
              fontSize,
              fontWeight: 800,
              fontFamily: "SF Pro Display, -apple-system, sans-serif",
              letterSpacing: "-0.03em",
              transform: `translateY(${y}px) rotate(${rotation}deg) scale(${scale})`,
              opacity: s,
              ...(gradient
                ? {
                    background: GRADIENT,
                    WebkitBackgroundClip: "text",
                    WebkitTextFillColor: "transparent",
                  }
                : {
                    color: COLORS.white,
                  }),
            }}
          >
            {word}
          </span>
        );
      })}
    </div>
  );
};
```

## DemoLabel

Floating label pill positioned at a configurable corner of the frame (top-left, top-right, bottom-left, bottom-right). Displays gradient-colored text inside a dark blurred pill with an indigo border accent. Animates in with a spring-driven vertical slide after an optional delay. Used to annotate specific moments in demo clips.

```tsx
import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

const GRADIENT = "linear-gradient(135deg, #8AD5FF 0%, #7A6AFD 50%, #EC69FF 100%)";

export const DemoLabel: React.FC<{
  text: string;
  delay?: number;
  position?: "top-left" | "top-right" | "bottom-left" | "bottom-right";
}> = ({ text, delay = 10, position = "bottom-left" }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const s = spring({ frame: frame - delay, fps, config: { damping: 14 }, durationInFrames: 20 });
  const y = interpolate(s, [0, 1], [20, 0]);

  const positionStyles: React.CSSProperties = {
    "top-left": { top: 80, left: 40 },
    "top-right": { top: 80, right: 40 },
    "bottom-left": { bottom: 40, left: 40 },
    "bottom-right": { bottom: 40, right: 40 },
  }[position] as React.CSSProperties;

  return (
    <div
      style={{
        position: "absolute",
        ...positionStyles,
        zIndex: 50,
        transform: `translateY(${y}px)`,
        opacity: s,
      }}
    >
      <div
        style={{
          padding: "10px 24px",
          borderRadius: 999,
          background: "rgba(10, 10, 18, 0.85)",
          backdropFilter: "blur(20px)",
          border: "1px solid rgba(122, 106, 253, 0.3)",
        }}
      >
        <span
          style={{
            fontSize: 18,
            fontWeight: 600,
            fontFamily: "SF Pro Display, -apple-system, sans-serif",
            background: GRADIENT,
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            letterSpacing: "-0.01em",
          }}
        >
          {text}
        </span>
      </div>
    </div>
  );
};
```

## LogoReveal

Opening scene that reveals the Quasar logo with a dramatic particle burst, glow effect, and animated conic gradient background. The logo icon scales in with a spring, followed by a staggered letter-by-letter "QUASAR" title slam, and finally a subtitle fade-in. Particles radiate outward from the center and fade. Designed for approximately 105 frames (~3.5s at 30fps).

```tsx
import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const COLORS = {
  cyan: "#8AD5FF",
  indigo: "#7A6AFD",
  fuchsia: "#EC69FF",
  dark: "#0A0A12",
};

const GRADIENT = `linear-gradient(135deg, ${COLORS.cyan} 0%, ${COLORS.indigo} 50%, ${COLORS.fuchsia} 100%)`;

export const LogoReveal: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = spring({ frame, fps, config: { damping: 12, mass: 0.6 }, durationInFrames: 25 });
  const glowOpacity = interpolate(frame, [0, 20, 70, 105], [0, 0.8, 0.8, 0], {
    extrapolateRight: "clamp",
  });
  const bgRotation = interpolate(frame, [0, 105], [0, 50]);
  const sparkleScale = spring({
    frame: frame - 15,
    fps,
    config: { damping: 10, mass: 0.5 },
    durationInFrames: 20,
  });

  // Particle burst
  const particles = Array.from({ length: 24 }, (_, i) => {
    const angle = (i / 24) * Math.PI * 2;
    const distance = interpolate(frame, [10, 60], [0, 350 + (i % 3) * 80], {
      extrapolateRight: "clamp",
    });
    const opacity = interpolate(frame, [10, 30, 70, 105], [0, 1, 1, 0], {
      extrapolateRight: "clamp",
    });
    return {
      x: Math.cos(angle) * distance,
      y: Math.sin(angle) * distance,
      opacity,
      size: 3 + (i % 4) * 2,
    };
  });

  // "QUASAR" title slam after logo
  const titleDelay = 45;
  const letters = "QUASAR".split("");
  const letterElements = letters.map((letter, i) => {
    const delay = titleDelay + i * 3;
    const s = spring({ frame: frame - delay, fps, config: { damping: 12, mass: 0.5 }, durationInFrames: 15 });
    const y = interpolate(s, [0, 1], [-100, 0]);
    return (
      <span
        key={i}
        style={{
          display: "inline-block",
          transform: `translateY(${y}px)`,
          opacity: s,
          fontSize: 72,
          fontWeight: 800,
          fontFamily: "SF Pro Display, -apple-system, sans-serif",
          background: GRADIENT,
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          letterSpacing: "-0.02em",
        }}
      >
        {letter}
      </span>
    );
  });

  // Subtitle
  const subS = spring({ frame: frame - 70, fps, config: { damping: 15 }, durationInFrames: 20 });

  return (
    <AbsoluteFill
      style={{ background: COLORS.dark, justifyContent: "center", alignItems: "center" }}
    >
      {/* Animated gradient background */}
      <div
        style={{
          position: "absolute",
          width: "200%",
          height: "200%",
          background: `conic-gradient(from ${bgRotation}deg, ${COLORS.dark}, ${COLORS.indigo}22, ${COLORS.dark}, ${COLORS.fuchsia}22, ${COLORS.dark})`,
          transform: "translate(-25%, -25%)",
        }}
      />

      {/* Particle burst */}
      {particles.map((p, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            width: p.size,
            height: p.size,
            borderRadius: "50%",
            background:
              i % 3 === 0 ? COLORS.cyan : i % 3 === 1 ? COLORS.indigo : COLORS.fuchsia,
            opacity: p.opacity,
            transform: `translate(${p.x}px, ${p.y}px)`,
          }}
        />
      ))}

      {/* Glow */}
      <div
        style={{
          position: "absolute",
          width: 400,
          height: 400,
          borderRadius: "50%",
          background: `radial-gradient(circle, ${COLORS.indigo}88, transparent 70%)`,
          opacity: glowOpacity,
          filter: "blur(40px)",
        }}
      />

      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 24 }}>
        {/* Logo icon */}
        <div
          style={{
            width: 140,
            height: 140,
            borderRadius: 28,
            background: GRADIENT,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            transform: `scale(${scale})`,
            boxShadow: `0 0 80px ${COLORS.indigo}66, 0 0 160px ${COLORS.fuchsia}33`,
          }}
        >
          <svg
            width="80"
            height="80"
            viewBox="0 0 24 24"
            fill="none"
            style={{ transform: `scale(${Math.max(0, sparkleScale)})` }}
          >
            <path
              d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z"
              fill="white"
            />
          </svg>
        </div>

        {/* Title */}
        <div style={{ display: "flex" }}>{letterElements}</div>

        {/* Subtitle */}
        <div
          style={{
            fontSize: 28,
            fontWeight: 500,
            color: "rgba(255,255,255,0.7)",
            fontFamily: "SF Pro Display, -apple-system, sans-serif",
            opacity: subS,
            transform: `translateY(${interpolate(subS, [0, 1], [20, 0])}px)`,
          }}
        >
          AI Website Generator
        </div>
      </div>
    </AbsoluteFill>
  );
};
```

## CTAFinale

Closing call-to-action scene with a word-by-word "Build your website with AI" headline slam where "Build" and "AI" are rendered in gradient while other words are white. Followed by a subtitle, a gradient pill CTA button, and a small logo lockup at the bottom. Background features a rotating conic gradient and orbiting particles. Each element enters with staggered spring animations.

```tsx
import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const COLORS = {
  cyan: "#8AD5FF",
  indigo: "#7A6AFD",
  fuchsia: "#EC69FF",
  dark: "#0A0A12",
  darkBlue: "#0D0F2B",
  white: "#FFFFFF",
};

const GRADIENT = `linear-gradient(135deg, ${COLORS.cyan} 0%, ${COLORS.indigo} 50%, ${COLORS.fuchsia} 100%)`;

export const CTAFinale: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const bgAngle = interpolate(frame, [0, 180], [0, 360]);

  // Word slam
  const words = ["Build", "your", "website", "with", "AI"];
  const wordElements = words.map((word, i) => {
    const delay = 10 + i * 6;
    const s = spring({
      frame: frame - delay,
      fps,
      config: { damping: 12, mass: 0.6 },
      durationInFrames: 18,
    });
    const y = interpolate(s, [0, 1], [60, 0]);
    const isHighlight = word === "Build" || word === "AI";

    return (
      <span
        key={i}
        style={{
          display: "inline-block",
          transform: `translateY(${y}px)`,
          opacity: s,
          marginRight: 24,
          ...(isHighlight
            ? {
                background: GRADIENT,
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }
            : {
                color: COLORS.white,
              }),
        }}
      >
        {word}
      </span>
    );
  });

  // Subtitle
  const subS = spring({ frame: frame - 50, fps, config: { damping: 15 }, durationInFrames: 20 });

  // CTA button
  const btnS = spring({ frame: frame - 65, fps, config: { damping: 14 }, durationInFrames: 20 });

  // Logo
  const logoS = spring({ frame: frame - 80, fps, config: { damping: 15 }, durationInFrames: 20 });

  // Orbiting particles
  const orbs = Array.from({ length: 6 }, (_, i) => {
    const angle = (i / 6) * Math.PI * 2 + frame * 0.02;
    const radius = 350 + (i % 2) * 80;
    return {
      x: Math.cos(angle) * radius,
      y: Math.sin(angle) * radius * 0.4,
      color: [COLORS.cyan, COLORS.indigo, COLORS.fuchsia][i % 3],
    };
  });

  return (
    <AbsoluteFill
      style={{
        background: `conic-gradient(from ${bgAngle}deg at 50% 50%, ${COLORS.dark} 0deg, ${COLORS.darkBlue} 90deg, ${COLORS.dark} 180deg, ${COLORS.darkBlue} 270deg, ${COLORS.dark} 360deg)`,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      {/* Orbiting particles */}
      {orbs.map((orb, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            width: 8,
            height: 8,
            borderRadius: "50%",
            background: orb.color,
            transform: `translate(${orb.x}px, ${orb.y}px)`,
            boxShadow: `0 0 20px ${orb.color}88`,
            opacity: 0.8,
          }}
        />
      ))}

      <div style={{ textAlign: "center" }}>
        {/* Main headline */}
        <div
          style={{
            fontSize: 92,
            fontWeight: 800,
            fontFamily: "SF Pro Display, -apple-system, sans-serif",
            lineHeight: 1.1,
            letterSpacing: "-0.03em",
          }}
        >
          {wordElements}
        </div>

        {/* Subtitle */}
        <div
          style={{
            marginTop: 32,
            fontSize: 28,
            color: `${COLORS.white}88`,
            fontFamily: "SF Pro Text, -apple-system, sans-serif",
            opacity: subS,
            transform: `translateY(${interpolate(subS, [0, 1], [20, 0])}px)`,
          }}
        >
          Powered by AI. Published in seconds.
        </div>

        {/* CTA Button */}
        <div
          style={{
            marginTop: 48,
            display: "inline-flex",
            padding: "20px 56px",
            borderRadius: 999,
            background: GRADIENT,
            fontSize: 24,
            fontWeight: 700,
            color: COLORS.white,
            fontFamily: "SF Pro Display, -apple-system, sans-serif",
            transform: `scale(${btnS})`,
            opacity: btnS,
            boxShadow: `0 8px 40px ${COLORS.indigo}44`,
            letterSpacing: "-0.01em",
          }}
        >
          Get Started →
        </div>

        {/* Logo at bottom */}
        <div
          style={{
            marginTop: 48,
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            gap: 12,
            opacity: logoS,
          }}
        >
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: 8,
              background: GRADIENT,
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
            }}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
              <path
                d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z"
                fill="white"
              />
            </svg>
          </div>
          <span
            style={{
              fontSize: 28,
              fontWeight: 700,
              color: COLORS.white,
              fontFamily: "SF Pro Display, -apple-system, sans-serif",
            }}
          >
            Quasar
          </span>
        </div>
      </div>
    </AbsoluteFill>
  );
};
```

## Main Composition Template (HighlightReelV2)

The top-level Remotion composition that orchestrates the entire highlight reel. Defines a data-driven timeline built from a `SECTIONS` array, where each section has a title card, video clips with time ranges and playback speeds, and optional prompt/label overlays. The timeline builder calculates frame positions for all elements. The composition layers: Poster (frame 0 thumbnail) -> LogoReveal intro -> section title cards -> video clips inside VideoFrames with PromptCaption or InsightLabel overlays -> ClipCrossfade between clips -> SceneTransition between sections -> CTAFinale closing scene. Includes background music with fade-in/fade-out volume envelope.

```tsx
import React from "react";
import {
  AbsoluteFill,
  Sequence,
  Audio,
  OffthreadVideo,
  staticFile,
  interpolate,
  useCurrentFrame,
} from "remotion";
import { VideoFrame } from "./components/VideoFrame";
import { InsightLabel } from "./components/InsightLabel";
import { PromptCaption } from "./components/PromptCaption";
import { SectionTitle } from "./components/SectionTitle";
import { SectionBadge } from "./components/SectionBadge";
import { SceneTransition } from "./components/SceneTransition";
import { ClipCrossfade } from "./components/ClipCrossfade";
import { LogoReveal } from "./scenes/LogoReveal";
import { CTAFinale } from "./scenes/CTAFinale";
import { Poster } from "./components/Poster";

// ─── Configuration ──────────────────────────────────────────────

const FPS = 30;
const SOURCE_FPS = 60;

interface Clip {
  startSec: number;
  endSec: number;
  speed: number;
  /** Insight label shown for result clips */
  label?: string;
  /** Prompt text shown as typewriter caption (replaces label) */
  prompt?: string;
}

interface Section {
  number: string;
  title: string;
  subtitle: string;
  video: string;
  clips: Clip[];
}

const TITLE_DURATION = 56;
const TRANSITION_DURATION = 24;
const TRANSITION_OVERLAP = 20;
const CROSSFADE_DURATION = 12;

// Extra frames appended after prompt clips so the full text can be read
const PROMPT_HOLD_FRAMES = 40; // ~1.3s hold

const SECTIONS: Section[] = [
  {
    number: "01",
    title: "Prompt to Website",
    subtitle: "Full AEM EDS site from a single prompt",
    video: "uc1.mov",
    clips: [
      {
        startSec: 0, endSec: 17, speed: 2.5,
        prompt: "Generate a microsite for the launch of our new running shoe, the AirPulse Pro. Target audience is urban runners aged 25-40. Tone should be energetic but premium.",
      },
      {
        startSec: 43, endSec: 52, speed: 2.5,
        label: "Standard AEM Edge Delivery site",
      },
    ],
  },
  {
    number: "02",
    title: "Brand Guidelines",
    subtitle: "AI-powered brand identity in seconds",
    video: "uc2.mov",
    clips: [
      {
        startSec: 0, endSec: 4, speed: 1.2,
        prompt: "Define the Brand Guidelines for Vitamix",
      },
      {
        startSec: 12, endSec: 16, speed: 1.5,
        label: "Brand profile defined",
      },
      {
        startSec: 24, endSec: 32, speed: 2,
        label: "Complete brand guidelines ready",
      },
    ],
  },
  {
    number: "03",
    title: "Custom Design",
    subtitle: "New EDS blocks aligned with your brand",
    video: "uc3.mov",
    clips: [
      {
        startSec: 0, endSec: 8, speed: 2,
        prompt: "Create a new custom design for Vitamix",
      },
      {
        startSec: 38, endSec: 44, speed: 2,
        prompt: "Build a new microsite for the Vitamix AeroBlend A9 — the world's first AI-adaptive blender. MSRP $799.95. Campaign tagline: \"Every blend, perfected.\"",
      },
      {
        startSec: 54, endSec: 58, speed: 2,
        label: "Brand-aligned website ready",
      },
    ],
  },
  {
    number: "04",
    title: "Pages & Translation",
    subtitle: "New pages, edits, and full-site translation",
    video: "uc4.mov",
    clips: [
      {
        startSec: 0, endSec: 3, speed: 1.2,
        prompt: "Create a premium contact page with FAQ accordion, newsletter signup, and customer support phone number.",
      },
      {
        startSec: 22, endSec: 25, speed: 1.5,
        label: "New page ready",
      },
      {
        startSec: 35, endSec: 37, speed: 1.2,
        prompt: "Generate a dramatic, dark-lit hero image of fresh ingredients mid-blend with subtle red light accents.",
      },
      {
        startSec: 55, endSec: 58, speed: 1.5,
        label: "Hero image placed",
      },
      {
        startSec: 70, endSec: 73, speed: 1.2,
        prompt: "Create a complete French translation of the AeroBlend A9 microsite under /fr. Translate all UI elements, CTAs, and legal copy.",
      },
      {
        startSec: 110, endSec: 114, speed: 1.5,
        label: "French website ready",
      },
    ],
  },
];

// ─── Timeline Builder ───────────────────────────────────────────

function clipDisplayFrames(clip: Clip): number {
  const base = Math.ceil(((clip.endSec - clip.startSec) / clip.speed) * FPS);
  // Prompt clips get extra hold time
  return clip.prompt ? base + PROMPT_HOLD_FRAMES : base;
}

// How many frames of actual video playback (without hold)
function clipVideoFrames(clip: Clip): number {
  return Math.ceil(((clip.endSec - clip.startSec) / clip.speed) * FPS);
}

interface ClipEntry {
  from: number;
  durationInFrames: number;
  videoFrames: number; // frames of actual video playback
  clip: Clip;
}

interface CrossfadeEntry {
  from: number;
}

interface SectionEntry {
  titleFrom: number;
  clipsStart: number;
  clipsEnd: number;
  clips: ClipEntry[];
  crossfades: CrossfadeEntry[];
  transitionFrom: number;
  section: Section;
}

function buildTimeline() {
  const INTRO_FRAMES = 84;
  let cursor = INTRO_FRAMES;
  const sections: SectionEntry[] = [];

  SECTIONS.forEach((section) => {
    const titleFrom = cursor;
    cursor += TITLE_DURATION;

    const clipsStart = cursor;
    const clips: ClipEntry[] = [];
    const crossfades: CrossfadeEntry[] = [];

    section.clips.forEach((clip, ci) => {
      const frames = clipDisplayFrames(clip);
      const videoFrames = clipVideoFrames(clip);

      if (ci > 0) {
        crossfades.push({ from: cursor - 6 });
      }

      clips.push({ from: cursor, durationInFrames: frames, videoFrames, clip });
      cursor += frames;
    });

    const clipsEnd = cursor;
    const transitionFrom = cursor - TRANSITION_OVERLAP;

    sections.push({
      titleFrom, clipsStart, clipsEnd, clips, crossfades, transitionFrom, section,
    });
  });

  const ctaFrom = cursor;
  const ctaFrames = 150;
  const totalFrames = ctaFrom + ctaFrames;

  return { introFrames: INTRO_FRAMES, sections, ctaFrom, ctaFrames, totalFrames };
}

const TIMELINE = buildTimeline();

// ─── Composition ────────────────────────────────────────────────

export const HighlightReelV2: React.FC = () => {
  const frame = useCurrentFrame();
  const totalFrames = TIMELINE.totalFrames;

  const audioVolume = interpolate(
    frame,
    [0, 30, totalFrames - 60, totalFrames],
    [0, 0.6, 0.6, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill style={{ background: "#0A0A12" }}>
      <Audio src={staticFile("music.mp3")} volume={audioVolume} />

      {/* ─── Intro ──────────────────────────────────────────── */}
      <Sequence from={0} durationInFrames={TIMELINE.introFrames}>
        <LogoReveal />
      </Sequence>

      {/* Static poster on top — visible at frame 0, fades into LogoReveal */}
      <Sequence from={0} durationInFrames={30}>
        <Poster holdFrames={8} fadeOutFrames={18} />
      </Sequence>

      <Sequence
        from={TIMELINE.introFrames - TRANSITION_OVERLAP}
        durationInFrames={TRANSITION_DURATION}
      >
        <SceneTransition direction="left" />
      </Sequence>

      {/* ─── Sections ───────────────────────────────────────── */}
      {TIMELINE.sections.map((st, si) => (
        <React.Fragment key={si}>
          {/* Section title card */}
          <Sequence from={st.titleFrom} durationInFrames={TITLE_DURATION}>
            <SectionTitle
              number={st.section.number}
              title={st.section.title}
              subtitle={st.section.subtitle}
            />
          </Sequence>

          {/* Persistent section badge */}
          <Sequence
            from={st.clipsStart}
            durationInFrames={st.clipsEnd - st.clipsStart}
          >
            <AbsoluteFill style={{ zIndex: 60 }}>
              <SectionBadge
                number={st.section.number}
                title={st.section.title}
              />
            </AbsoluteFill>
          </Sequence>

          {/* Video clips */}
          {st.clips.map((c, ci) => (
            <Sequence key={ci} from={c.from} durationInFrames={c.durationInFrames}>
              <AbsoluteFill
                style={{
                  background: "#0A0A12",
                  justifyContent: "center",
                  alignItems: "center",
                }}
              >
                {/* Ambient glow */}
                <div
                  style={{
                    position: "absolute",
                    bottom: -80,
                    width: 1000,
                    height: 400,
                    background:
                      "radial-gradient(ellipse, rgba(122,106,253,0.1), transparent 70%)",
                    filter: "blur(60px)",
                  }}
                />

                {/* Video — freeze on last frame during prompt hold */}
                <VideoFrame delay={0}>
                  <OffthreadVideo
                    src={staticFile(st.section.video)}
                    startFrom={Math.round(c.clip.startSec * SOURCE_FPS)}
                    playbackRate={c.clip.speed}
                    endAt={Math.round(c.clip.startSec * SOURCE_FPS) + Math.round(c.videoFrames * c.clip.speed)}
                    style={{
                      width: 1520,
                      height: 855,
                      objectFit: "cover",
                    }}
                  />
                </VideoFrame>

                {/* Caption: prompt (typewriter) or insight label */}
                {c.clip.prompt ? (
                  <PromptCaption text={c.clip.prompt} delay={4} charsPerFrame={3} />
                ) : c.clip.label ? (
                  <InsightLabel text={c.clip.label} delay={5} position="bottom-center" bold />
                ) : null}
              </AbsoluteFill>
            </Sequence>
          ))}

          {/* Crossfades between clips */}
          {st.crossfades.map((cf, cfi) => (
            <Sequence key={`cf-${cfi}`} from={cf.from} durationInFrames={CROSSFADE_DURATION}>
              <ClipCrossfade durationInFrames={CROSSFADE_DURATION} />
            </Sequence>
          ))}

          {/* Section transition */}
          {si < SECTIONS.length - 1 && (
            <Sequence from={st.transitionFrom} durationInFrames={TRANSITION_DURATION}>
              <SceneTransition direction={si % 2 === 0 ? "right" : "left"} />
            </Sequence>
          )}
        </React.Fragment>
      ))}

      {/* ─── CTA Finale ─────────────────────────────────────── */}
      <Sequence
        from={TIMELINE.ctaFrom - TRANSITION_OVERLAP}
        durationInFrames={TRANSITION_DURATION}
      >
        <SceneTransition direction="left" />
      </Sequence>

      <Sequence from={TIMELINE.ctaFrom} durationInFrames={TIMELINE.ctaFrames}>
        <CTAFinale />
      </Sequence>
    </AbsoluteFill>
  );
};

export const HIGHLIGHT_REEL_V2_DURATION = TIMELINE.totalFrames;
export const HIGHLIGHT_REEL_V2_FPS = FPS;
```
