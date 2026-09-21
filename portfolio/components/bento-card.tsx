import type { CSSProperties, ReactNode } from "react";
import { fishbowl, type Triad } from "@/lib/gradient";

export function BentoCard({
  triad,
  angle = 140,
  label,
  className = "",
  children,
}: {
  triad: Triad;
  angle?: number;
  label: string;
  className?: string;
  children: ReactNode;
}) {
  const vars = {
    "--bg-dark": fishbowl(triad, angle),
    "--bg-light": fishbowl(triad, angle, true),
  } as CSSProperties;

  return (
    <div
      className={`bento flex flex-col justify-between rounded-[26px] p-[26px] ${className}`}
      style={vars}
    >
      <p className="label text-card-label">{label}</p>
      <div>{children}</div>
    </div>
  );
}

export function Chip({ children }: { children: ReactNode }) {
  return (
    <span className="label rounded-full border border-card-border px-[11px] py-[5px] text-card-chip">
      {children}
    </span>
  );
}
