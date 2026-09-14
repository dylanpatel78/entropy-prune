import Link from "next/link";
import { projects } from "@/content/projects";
import { Spectrum } from "./spectrum";

export function Work() {
  return (
    <section id="work" className="scroll-mt-28 px-5 py-20 sm:px-10 sm:py-28">
      <div className="mb-12 flex items-baseline justify-between border-b border-line pb-5">
        <h2 className="wide text-[clamp(2rem,5vw,3.4rem)] leading-none">
          Work
        </h2>
        <span className="tnum font-mono text-[13px] text-fg3">
          {String(projects.length).padStart(2, "0")}
        </span>
      </div>

      <div className="flex flex-col">
        {projects.map((p) => (
          <article
            key={p.slug}
            className="grid gap-8 border-b border-line py-12 lg:grid-cols-12 lg:gap-10"
          >
            <div className="lg:col-span-5">
              <h3 className="wide text-[clamp(1.6rem,3.4vw,2.4rem)] leading-tight">
                {p.name}
              </h3>
              <p className="mt-2 text-[14px] text-fg3">
                {p.domainLabel}
                <span className="mx-2 text-line-strong">/</span>
                {p.period}
              </p>
              <div className="mt-7">
                <Spectrum values={p.spectrum} />
              </div>
            </div>

            <div className="lg:col-span-4">
              <p className="max-w-[46ch] text-[16px] leading-relaxed text-fg2">
                {p.summary}
              </p>
              <ul className="mt-5 flex flex-wrap gap-x-4 gap-y-2">
                {p.stack.map((s) => (
                  <li
                    key={s}
                    className="font-mono text-[12px]"
                    style={{ color: "var(--build)" }}
                  >
                    {s}
                  </li>
                ))}
              </ul>
              <Link
                href={`/work/${p.slug}`}
                className="prunable mt-7 inline-block text-[15px] underline decoration-from-font underline-offset-[5px] transition-opacity hover:opacity-70"
                style={{ color: "var(--outcome)" }}
              >
                Read the decision
              </Link>
            </div>

            <dl className="flex gap-8 lg:col-span-3 lg:flex-col lg:gap-6">
              {p.outcome.map((o) => (
                <div key={o.label}>
                  <dt className="sr-only">{o.label}</dt>
                  <dd>
                    <span
                      className="tnum wide block text-[clamp(2rem,4.5vw,3rem)] leading-none"
                      style={{ color: "var(--outcome)" }}
                    >
                      {o.value}
                    </span>
                    <span className="mt-1.5 block max-w-[14ch] text-[13px] leading-snug text-fg3">
                      {o.label}
                    </span>
                  </dd>
                </div>
              ))}
            </dl>
          </article>
        ))}
      </div>
    </section>
  );
}
