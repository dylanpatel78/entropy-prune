"use client";

import { useEffect, useRef, useState } from "react";

const RAMP = ["#ff9a2e", "#e8552e", "#a63fc4", "#6b4be8", "#1466ff"];
const SEGMENTS = 22;

function segColor(i: number) {
  const f = i / (SEGMENTS - 1);
  const idx = Math.min(RAMP.length - 1, Math.floor(f * (RAMP.length - 1) + 0.5));
  return RAMP[idx];
}

export function StatBars({
  stats,
  onDark = true,
  dimColor,
}: {
  stats: { fill: number; display: string; label: string }[];
  onDark?: boolean;
  dimColor?: string;
}) {
  const [shown, setShown] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const io = new IntersectionObserver(
      ([e]) => {
        if (e.isIntersecting) {
          setShown(true);
          io.disconnect();
        }
      },
      { threshold: 0.25 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  const dim = dimColor ?? (onDark ? "rgba(255,255,255,0.16)" : "rgba(0,0,0,0.10)");

  return (
    <div
      ref={ref}
      className="grid gap-x-8 gap-y-14 sm:grid-cols-2 lg:grid-cols-3"
    >
      {stats.map((s, col) => {
        const filled = Math.round((s.fill / 100) * SEGMENTS);
        return (
          <div key={s.label}>
            <div className="flex flex-col-reverse gap-[4px]">
              {Array.from({ length: SEGMENTS }).map((_, i) => {
                const on = shown && i < filled;
                return (
                  <div
                    key={i}
                    className="h-[11px] w-full rounded-[3px]"
                    style={{
                      background: on ? segColor(i) : dim,
                      transition: `background 320ms ease ${col * 90 + i * 34}ms`,
                    }}
                  />
                );
              })}
            </div>
            <p
              className="tnum wide mt-7 text-[clamp(2.8rem,6vw,4.6rem)] leading-none"
              style={{ color: onDark ? "#fff" : "var(--fg)" }}
            >
              {s.display}
            </p>
            <p
              className="mt-3 max-w-[26ch] text-[15px] leading-snug"
              style={{ color: onDark ? "rgba(255,255,255,0.72)" : "var(--fg-2)" }}
            >
              {s.label}
            </p>
          </div>
        );
      })}
    </div>
  );
}
