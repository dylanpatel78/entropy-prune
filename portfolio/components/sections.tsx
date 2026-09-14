import { profile } from "@/content/profile";
import { projects, domainLabels, type Domain } from "@/content/projects";
import { PruneDemo } from "./prune-demo";
import { StatBars } from "./stat-bars";

export function Hero() {
  return (
    <section className="px-5 pt-36 pb-24 sm:px-10 sm:pt-52 sm:pb-32">
      <h1 className="wide max-w-[16ch] text-[clamp(3.2rem,10.5vw,9rem)] leading-[0.86]">
        {profile.claim}
      </h1>

      <div className="mt-16 grid gap-12 lg:grid-cols-12 lg:gap-10">
        <div className="prunable lg:col-span-5">
          <p className="max-w-[40ch] text-[clamp(1.05rem,1.6vw,1.35rem)] leading-relaxed text-fg2">
            {profile.standfirst}
          </p>
          <ul className="mt-9 flex flex-wrap gap-2">
            {profile.domains.map((d) => (
              <li
                key={d}
                className="rounded-full border border-line px-5 py-2.5 text-[14px] text-fg2"
              >
                {d}
              </li>
            ))}
          </ul>
        </div>
        <div className="prunable lg:col-span-7">
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
      className="prunable panel-invert scroll-mt-28 rounded-[28px] px-5 py-24 sm:px-10 sm:py-32"
    >
      <h2 className="wide text-[clamp(3rem,9vw,7rem)] leading-[0.88]">Range</h2>

      <p className="mt-10 max-w-[24ch] text-[clamp(1.6rem,4.2vw,3.2rem)] leading-[1.06]">
        Four areas, one habit.
      </p>
      <p className="mt-7 max-w-[56ch] text-[clamp(1rem,1.6vw,1.3rem)] leading-relaxed opacity-70">
        Pruning a context window, cutting a guarantee nobody can observe, and
        killing a feature before it ships are the same operation performed on
        different material.
      </p>

      <div className="mt-20 grid gap-x-10 gap-y-14 sm:grid-cols-2 lg:grid-cols-4">
        {order.map((d, i) => (
          <div key={d}>
            <span className="font-mono text-[12px] opacity-45">
              {String(i + 1).padStart(2, "0")}
            </span>
            <h3 className="mt-4 text-[clamp(1.2rem,2.4vw,1.7rem)] leading-snug">
              {domainLabels[d]}
            </h3>
            <p className="mt-4 max-w-[28ch] text-[15px] leading-relaxed opacity-70">
              {notes[d]}
            </p>
            <ul className="mt-6 flex flex-wrap gap-2">
              {byDomain(d).map((p) => (
                <li
                  key={p.slug}
                  className="rounded-full px-3.5 py-1.5 font-mono text-[11px]"
                  style={{ background: "rgba(128,128,128,0.22)" }}
                >
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
      className="panel-blue scroll-mt-28 rounded-[28px] px-5 py-24 text-white sm:px-10 sm:py-32"
    >
      <h2 className="wide text-[clamp(3rem,9vw,7rem)] leading-[0.88]">
        Leading
      </h2>

      <div className="mt-12 max-w-[52ch]">
        <h3 className="text-[clamp(1.3rem,2.8vw,2.1rem)] leading-snug">
          {leadership.what}
        </h3>
        <p className="mt-3 font-mono text-[13px] text-white/60">
          {leadership.period}
        </p>
        <p className="prunable mt-7 text-[clamp(1rem,1.5vw,1.2rem)] leading-relaxed text-white/75">
          {leadership.body}
        </p>
      </div>

      <div className="mt-20">
        <StatBars
          onDark
          dimColor="rgba(0,0,0,0.22)"
          stats={[
            { fill: 55, display: "6", label: "engineers led" },
            { fill: 82, display: "200+", label: "researchers served" },
            { fill: 41, display: "41%", label: "cut in median queue time" },
          ]}
        />
      </div>
    </section>
  );
}

export function About() {
  return (
    <section
      id="about"
      className="prunable scroll-mt-28 px-5 py-24 sm:px-10 sm:py-32"
    >
      <h2 className="wide text-[clamp(3rem,9vw,7rem)] leading-[0.88]">About</h2>
      <div className="mt-12 max-w-[54ch] space-y-7">
        {profile.bio.map((para) => (
          <p
            key={para.slice(0, 24)}
            className="text-[clamp(1.05rem,1.7vw,1.45rem)] leading-relaxed text-fg2"
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
    <section className="px-5 pt-16 pb-14 sm:px-10 sm:pt-24 sm:pb-16">
      <div className="border-t border-line pt-14">
        <a
          href={`mailto:${links.email}`}
          className="wide block break-all text-[clamp(2rem,8.5vw,6.5rem)] leading-[0.9] transition-opacity hover:opacity-60"
        >
          {links.email}
        </a>

        <div className="mt-16 flex flex-wrap items-end justify-between gap-8">
          <ul className="flex flex-wrap gap-2">
            {[
              ["GitHub", links.github],
              ["LinkedIn", links.linkedin],
              ["Resume", "/resume"],
            ].map(([label, href]) => (
              <li key={label}>
                <a
                  href={href}
                  className="inline-block rounded-full border border-line px-6 py-3 text-[15px] text-fg2 transition-colors hover:bg-raised hover:text-fg"
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
