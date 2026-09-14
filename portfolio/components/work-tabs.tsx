"use client";

import Link from "next/link";
import { useState } from "react";
import { projects } from "@/content/projects";
import { Spectrum } from "./spectrum";

export function WorkTabs() {
  const [active, setActive] = useState(0);
  const p = projects[active];

  return (
    <section id="work" className="scroll-mt-28 px-5 py-24 sm:px-10 sm:py-32">
      <div className="mb-10 flex items-end justify-between gap-6">
        <h2 className="wide text-[clamp(3rem,9vw,7rem)] leading-[0.88]">
          Work
        </h2>
        <span className="grid size-11 shrink-0 place-items-center rounded-full border border-line font-mono text-[13px] text-fg3">
          {projects.length}
        </span>
      </div>

      <div
        role="tablist"
        aria-label="Projects"
        className="mb-12 flex flex-wrap gap-2"
      >
        {projects.map((x, i) => {
          const on = i === active;
          return (
            <button
              key={x.slug}
              role="tab"
              aria-selected={on}
              onClick={() => setActive(i)}
              className="rounded-full px-6 py-3.5 text-[15px] transition-colors duration-200"
              style={{
                background: on ? "var(--fg)" : "var(--raised)",
                color: on ? "var(--bg)" : "var(--fg-2)",
              }}
            >
              {x.name}
            </button>
          );
        })}
      </div>

      <div key={p.slug} className="panel-in">
        <div className="grid gap-12 lg:grid-cols-12 lg:gap-10">
          <div className="lg:col-span-7">
            <h3 className="wide text-[clamp(2.6rem,7.5vw,5.5rem)] leading-[0.92]">
              {p.name}
            </h3>
            <p className="mt-5 text-[15px] text-fg3">
              {p.domainLabel}
              <span className="mx-3 text-line-strong">/</span>
              {p.period}
              <span className="mx-3 text-line-strong">/</span>
              {p.role}
            </p>
            <p className="mt-8 max-w-[44ch] text-[clamp(1.15rem,2vw,1.6rem)] leading-snug">
              {p.summary}
            </p>
            <ul className="mt-8 flex flex-wrap gap-2">
              {p.stack.map((s) => (
                <li
                  key={s}
                  className="rounded-full px-4 py-2 font-mono text-[12px]"
                  style={{
                    background: "var(--raised)",
                    color: "var(--build)",
                  }}
                >
                  {s}
                </li>
              ))}
            </ul>
            <Link
              href={`/work/${p.slug}`}
              className="mt-10 inline-block rounded-full px-7 py-4 text-[15px] transition-opacity hover:opacity-85"
              style={{
                background: "var(--outcome-fill)",
                color: "var(--on-fill)",
              }}
            >
              Read the decision
            </Link>
          </div>

          <div className="lg:col-span-5">
            <div
              className="rounded-3xl p-7 sm:p-9"
              style={{ background: "var(--raised)" }}
            >
              <dl className="flex flex-col gap-8">
                {p.outcome.map((o) => (
                  <div key={o.label}>
                    <dt className="sr-only">{o.label}</dt>
                    <dd>
                      <span
                        className="tnum wide block text-[clamp(2.8rem,6vw,4.2rem)] leading-none"
                        style={{ color: "var(--outcome)" }}
                      >
                        {o.value}
                      </span>
                      <span className="mt-2 block text-[14px] text-fg3">
                        {o.label}
                      </span>
                    </dd>
                  </div>
                ))}
              </dl>
              <div className="mt-10 border-t border-line pt-7">
                <Spectrum values={p.spectrum} />
                <p className="mt-3 font-mono text-[11px] text-fg3">
                  singular value spectrum
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
