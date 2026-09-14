"use client";

import { useCallback, useEffect, useRef, useState } from "react";

const TOKENS: [string, 0 | 1][] = [
  ["The", 0], ["quarterly", 1], ["report", 1], ["was", 0], ["finally", 0],
  ["filed", 1], ["on", 0], ["the", 0], ["14th", 1], ["of", 0], ["March,", 1],
  ["and", 0], ["then", 0], ["the", 0], ["steering", 0], ["committee,", 1],
  ["after", 0], ["what", 0], ["I", 0], ["am", 0], ["told", 0], ["was", 0],
  ["a", 0], ["fairly", 0], ["long", 0], ["discussion,", 0], ["approved", 1],
  ["the", 0], ["revised", 1], ["budget", 1], ["for", 0], ["the", 0],
  ["infrastructure", 1], ["team", 1], ["in", 0], ["full.", 0],
];

const KEPT = TOKENS.filter(([, k]) => k === 1).length;
const RETAINED = Math.round((KEPT / TOKENS.length) * 100);

export function PruneDemo() {
  const [pruned, setPruned] = useState(false);
  const [pct, setPct] = useState(100);
  const raf = useRef<number>(0);

  const run = useCallback(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) {
      setPruned(true);
      setPct(RETAINED);
      return;
    }
    setPruned(false);
    setPct(100);
    const start = performance.now();
    const delay = 850;
    const dur = 900;
    cancelAnimationFrame(raf.current);
    const tick = (now: number) => {
      const t = now - start;
      if (t > delay) setPruned(true);
      const p = Math.min(Math.max((t - delay) / dur, 0), 1);
      const eased = 1 - Math.pow(1 - p, 3);
      setPct(Math.round(100 - (100 - RETAINED) * eased));
      if (p < 1) raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
  }, []);

  useEffect(() => {
    run();
    return () => cancelAnimationFrame(raf.current);
  }, [run]);

  return (
    <div className="rounded-2xl border border-line bg-raised p-5 sm:p-7">
      <div className="mb-4 flex items-baseline justify-between gap-4">
        <span className="font-mono text-[12px] text-fg3">entropy-prune</span>
        <button
          onClick={run}
          className="font-mono text-[12px] text-fg3 transition-colors hover:text-fg2"
        >
          run again
        </button>
      </div>

      <p className="font-mono text-[14px] leading-[2.1] sm:text-[15px]">
        {TOKENS.map(([word, keep], i) => {
          const gone = pruned && keep === 0;
          return (
            <span
              key={i}
              className="inline-grid transition-all duration-700 ease-out"
              style={{
                gridTemplateColumns: gone ? "0fr" : "1fr",
                opacity: gone ? 0 : 1,
              }}
            >
              <span
                className="overflow-hidden whitespace-nowrap transition-colors duration-500"
                style={{
                  color: pruned && keep === 1 ? "var(--fg)" : "var(--fg-2)",
                }}
              >
                {word}&nbsp;
              </span>
            </span>
          );
        })}
      </p>

      <div className="mt-6 flex items-baseline gap-3 border-t border-line pt-5">
        <span
          className="tnum wide text-[34px] leading-none"
          style={{ color: "var(--outcome)" }}
        >
          {pct}%
        </span>
        <span className="text-[14px] text-fg2">of tokens retained</span>
      </div>
    </div>
  );
}
