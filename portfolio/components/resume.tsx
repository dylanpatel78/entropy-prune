import type { ReactNode } from "react";

export function Section({
  id,
  title,
  count,
  children,
}: {
  id: string;
  title: string;
  count: string;
  children: ReactNode;
}) {
  return (
    <section id={id} className="scroll-mt-24 border-t border-line pt-10 pb-4 first:border-0 first:pt-0">
      <div className="mb-2 flex items-baseline justify-between gap-6">
        <h2 className="text-[clamp(30px,4vw,46px)] font-light leading-none tracking-[-0.045em] text-ink">
          {title}
        </h2>
        <span className="label text-ink3">{count}</span>
      </div>
      {children}
    </section>
  );
}

export function Entry({
  role,
  org,
  when,
  bullets,
}: {
  role: string;
  org: string;
  when: string;
  bullets: string[];
}) {
  return (
    <article className="border-t border-line py-7 first:border-0">
      <div className="flex flex-wrap items-baseline justify-between gap-x-6 gap-y-1">
        <h3 className="text-[18px] font-normal tracking-[-0.015em] text-ink">{role}</h3>
        <p className="label shrink-0 text-ink3">{when}</p>
      </div>
      <p className="mt-1 text-[14.5px] text-ink2">{org}</p>
      <ul className="mt-3.5 flex flex-col gap-2">
        {bullets.map((b) => (
          <li
            key={b}
            className="relative max-w-[70ch] pl-4 text-[14.5px] leading-[1.6] text-ink2 before:absolute before:left-0 before:top-[9px] before:size-1 before:rounded-full before:bg-line-strong"
          >
            {b}
          </li>
        ))}
      </ul>
    </article>
  );
}

export function Chips({ label, items }: { label: string; items: string[] }) {
  return (
    <div className="border-t border-line py-7 first:border-0">
      <h3 className="text-[18px] font-normal tracking-[-0.015em] text-ink">{label}</h3>
      <div className="mt-3.5 flex flex-wrap gap-2">
        {items.map((i) => (
          <span
            key={i}
            className="rounded-full border border-line px-3.5 py-1.5 text-[13px] text-ink2"
          >
            {i}
          </span>
        ))}
      </div>
    </div>
  );
}
