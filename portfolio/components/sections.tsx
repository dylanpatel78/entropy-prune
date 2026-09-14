import { profile } from "@/content/profile";
import { projects, domainLabels, type Domain } from "@/content/projects";
import { PruneDemo } from "./prune-demo";

export function Hero() {
  return (
    <section className="px-5 pt-32 pb-20 sm:px-10 sm:pt-44 sm:pb-28">
      <div className="grid gap-14 lg:grid-cols-12 lg:gap-12">
        <div className="lg:col-span-7">
          <h1 className="wide text-[clamp(2.6rem,7.2vw,5.6rem)] leading-[0.96]">
            {profile.claim}
          </h1>
          <p className="prunable mt-8 max-w-[52ch] text-[clamp(1rem,1.5vw,1.25rem)] leading-relaxed text-fg2">
            {profile.standfirst}
          </p>
          <ul className="mt-10 flex flex-wrap gap-x-3 gap-y-2 border-t border-line pt-6">
            {profile.domains.map((d) => (
              <li key={d} className="text-[14px] text-fg3">
                {d}
                <span className="ml-3 text-line-strong">/</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="prunable lg:col-span-5">
          <PruneDemo />
        </div>
      </div>
    </section>
  );
}

export function Range() {
  const byDomain = (d: Domain) => projects.filter((p) => p.domain === d);
  const order: Domain[] = ["software", "ml", "computation", "finance"];
  const notes: Record<Domain, string> = {
    software: "Guarantees are expensive. Buy only the ones callers can tell apart.",
    ml: "Most of a context window is redundancy wearing a costume.",
    computation: "Specialise for the shape the data actually has.",
    finance: "A number without its error bars is a rumour.",
  };

  return (
    <section
      id="range"
      className="prunable scroll-mt-28 px-5 py-20 sm:px-10 sm:py-28"
    >
      <div className="mb-12 border-b border-line pb-5">
        <h2 className="wide text-[clamp(2rem,5vw,3.4rem)] leading-none">
          Range
        </h2>
      </div>

      <p className="mb-14 max-w-[62ch] text-[clamp(1.05rem,1.7vw,1.4rem)] leading-relaxed">
        Four areas, one habit. Pruning a context window, cutting a guarantee
        nobody can observe, and killing a feature before it ships are the same
        operation performed on different material.
      </p>

      <div className="grid gap-x-10 gap-y-12 sm:grid-cols-2 lg:grid-cols-4">
        {order.map((d) => (
          <div key={d} className="border-t border-line pt-5">
            <h3 className="text-[15px]">{domainLabels[d]}</h3>
            <p className="mt-3 max-w-[28ch] text-[14px] leading-relaxed text-fg2">
              {notes[d]}
            </p>
            <ul className="mt-5 space-y-1.5">
              {byDomain(d).map((p) => (
                <li key={p.slug} className="font-mono text-[12px] text-fg3">
                  {p.name}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </section>
  );
}

export function Leading() {
  const { leadership } = profile;
  return (
    <section
      id="leading"
      className="scroll-mt-28 px-5 py-20 sm:px-10 sm:py-28"
    >
      <div className="mb-12 border-b border-line pb-5">
        <h2 className="wide text-[clamp(2rem,5vw,3.4rem)] leading-none">
          Leading
        </h2>
      </div>

      <div className="grid gap-12 lg:grid-cols-12">
        <div className="lg:col-span-7">
          <h3 className="text-[clamp(1.2rem,2.2vw,1.6rem)] leading-snug">
            {leadership.what}
          </h3>
          <p className="mt-2 text-[14px] text-fg3">{leadership.period}</p>
          <p className="prunable mt-7 max-w-[54ch] text-[16px] leading-relaxed text-fg2">
            {leadership.body}
          </p>
        </div>

        <dl className="flex flex-wrap gap-x-10 gap-y-8 lg:col-span-5 lg:justify-end">
          {leadership.outcome.map((o) => (
            <div key={o.label}>
              <dt className="sr-only">{o.label}</dt>
              <dd>
                <span
                  className="tnum wide block text-[clamp(2.4rem,5vw,3.6rem)] leading-none"
                  style={{ color: "var(--outcome)" }}
                >
                  {o.value}
                </span>
                <span className="mt-2 block max-w-[16ch] text-[13px] leading-snug text-fg3">
                  {o.label}
                </span>
              </dd>
            </div>
          ))}
        </dl>
      </div>
    </section>
  );
}

export function About() {
  return (
    <section
      id="about"
      className="prunable scroll-mt-28 px-5 py-20 sm:px-10 sm:py-28"
    >
      <div className="mb-12 border-b border-line pb-5">
        <h2 className="wide text-[clamp(2rem,5vw,3.4rem)] leading-none">
          About
        </h2>
      </div>
      <div className="max-w-[58ch] space-y-6">
        {profile.bio.map((para) => (
          <p
            key={para.slice(0, 24)}
            className="text-[clamp(1rem,1.5vw,1.2rem)] leading-relaxed text-fg2"
          >
            {para}
          </p>
        ))}
      </div>
    </section>
  );
}

export function Contact() {
  const { links } = profile;
  return (
    <section className="px-5 pt-20 pb-14 sm:px-10 sm:pt-28 sm:pb-16">
      <div className="border-t border-line pt-12">
        <a
          href={`mailto:${links.email}`}
          className="wide block text-[clamp(2rem,7vw,5rem)] leading-none transition-opacity hover:opacity-65"
        >
          {links.email}
        </a>

        <div className="mt-14 flex flex-wrap items-end justify-between gap-8">
          <ul className="flex gap-7">
            {[
              ["GitHub", links.github],
              ["LinkedIn", links.linkedin],
              ["Resume", "/resume"],
            ].map(([label, href]) => (
              <li key={label}>
                <a
                  href={href}
                  className="text-[15px] text-fg2 underline decoration-from-font underline-offset-[5px] transition-colors hover:text-fg"
                >
                  {label}
                </a>
              </li>
            ))}
          </ul>
          <p className="font-mono text-[12px] text-fg3">
            {profile.name} — {new Date().getFullYear()}
          </p>
        </div>
      </div>
    </section>
  );
}
