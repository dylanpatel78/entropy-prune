"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

const PAGES = [
  ["Home", "/"],
  ["Projects", "/projects"],
  ["Resume", "/resume"],
] as const;

export function Nav() {
  const path = usePathname();
  const [dark, setDark] = useState(true);

  useEffect(() => {
    setDark(document.documentElement.dataset.theme !== "light");
  }, []);

  function toggle() {
    const next = dark ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    setDark(!dark);
    try {
      localStorage.setItem("theme", next);
    } catch {}
  }

  return (
    <nav className="shell flex items-center justify-between gap-3 py-5">
      <div className="flex items-center rounded-full border border-line bg-surface p-1 backdrop-blur-md">
        {PAGES.map(([label, href]) => {
          const on = path === href;
          return (
            <Link
              key={href}
              href={href}
              className="rounded-full px-5 py-2 text-[13.5px] font-medium tracking-[-0.01em] transition-colors"
              style={{
                background: on ? "var(--ink)" : "transparent",
                color: on ? "var(--ground)" : "var(--ink2)",
              }}
            >
              {label}
            </Link>
          );
        })}
      </div>

      <div className="flex items-center gap-2.5">
        <button
          onClick={toggle}
          aria-label={`Switch to ${dark ? "light" : "dark"} mode`}
          className="grid size-10 place-items-center rounded-full border border-line text-ink2 transition-colors hover:text-ink"
        >
          {dark ? <Sun /> : <Moon />}
        </button>
        <a
          href="mailto:hello@example.com"
          className="rounded-full px-6 py-2.5 text-[13.5px] font-medium tracking-[-0.01em]"
          style={{ background: "var(--acid)", color: "#08080a" }}
        >
          Contact me
        </a>
      </div>
    </nav>
  );
}

function Sun() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden>
      <circle cx="12" cy="12" r="4.2" />
      <path strokeLinecap="round" d="M12 2v2.4M12 19.6V22M2 12h2.4M19.6 12H22M4.9 4.9l1.7 1.7M17.4 17.4l1.7 1.7M19.1 4.9l-1.7 1.7M6.6 17.4l-1.7 1.7" />
    </svg>
  );
}

function Moon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden>
      <path strokeLinejoin="round" d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5Z" />
    </svg>
  );
}
