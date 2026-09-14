"use client";

import { useEffect, useState } from "react";

type Theme = "light" | "dark";
type Density = "full" | "pruned";

export function Chrome() {
  const [theme, setTheme] = useState<Theme>("dark");
  const [density, setDensity] = useState<Density>("full");

  useEffect(() => {
    const stored = localStorage.getItem("theme") as Theme | null;
    const initial =
      stored ??
      (window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light");
    setTheme(initial);
    document.documentElement.setAttribute("data-theme", initial);
    document.documentElement.setAttribute("data-density", "full");
  }, []);

  function flipTheme() {
    const next: Theme = theme === "dark" ? "light" : "dark";
    setTheme(next);
    document.documentElement.setAttribute("data-theme", next);
    try {
      localStorage.setItem("theme", next);
    } catch {}
  }

  function flipDensity() {
    const next: Density = density === "full" ? "pruned" : "full";
    setDensity(next);
    document.documentElement.setAttribute("data-density", next);
  }

  return (
    <header className="fixed inset-x-0 top-0 z-50 px-3 pt-3 sm:px-6 sm:pt-5">
      <div className="mx-auto flex max-w-[1400px] items-center gap-2 sm:gap-3">
        <a
          href="#top"
          aria-label="Top of page"
          className="grid size-11 shrink-0 place-items-center rounded-full bg-fg text-[13px] tracking-tight text-bg sm:size-13"
          style={{ fontStretch: "86%" }}
        >
          DP
        </a>

        <nav className="hidden items-center gap-1 rounded-full border border-line bg-surface/70 px-2 py-1.5 backdrop-blur-xl sm:flex">
          {[
            ["Work", "#work"],
            ["Range", "#range"],
            ["Leading", "#leading"],
            ["About", "#about"],
          ].map(([label, href]) => (
            <a
              key={href}
              href={href}
              className="rounded-full px-3.5 py-1.5 text-[14px] text-fg2 transition-colors hover:bg-raised hover:text-fg"
            >
              {label}
            </a>
          ))}
        </nav>

        <div className="ml-auto flex items-center gap-2">
          <button
            onClick={flipDensity}
            aria-pressed={density === "pruned"}
            className="rounded-full border border-line bg-surface/70 px-3.5 py-2.5 text-[13px] text-fg2 backdrop-blur-xl transition-colors hover:text-fg"
            title="Collapse the page to only what matters"
          >
            <span className="tnum">
              {density === "full" ? "Prune this page" : "Restore"}
            </span>
          </button>

          <button
            onClick={flipTheme}
            aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
            className="grid size-11 place-items-center rounded-full border border-line bg-surface/70 text-fg2 backdrop-blur-xl transition-colors hover:text-fg"
          >
            {theme === "dark" ? (
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden>
                <circle cx="12" cy="12" r="4.2" />
                <path d="M12 2v2.4M12 19.6V22M2 12h2.4M19.6 12H22M4.9 4.9l1.7 1.7M17.4 17.4l1.7 1.7M19.1 4.9l-1.7 1.7M6.6 17.4l-1.7 1.7" strokeLinecap="round" />
              </svg>
            ) : (
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden>
                <path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5Z" strokeLinejoin="round" />
              </svg>
            )}
          </button>

          <a
            href="/resume"
            className="rounded-full bg-fg px-5 py-2.5 text-[14px] text-bg transition-opacity hover:opacity-85 sm:px-6 sm:py-3"
          >
            Resume
          </a>
        </div>
      </div>
    </header>
  );
}
