import type { CSSProperties } from "react";
import { Nav } from "@/components/nav";
import { Chip } from "@/components/bento-card";
import { fishbowl, TRIADS, type Triad } from "@/lib/gradient";

const PROJECTS = [
  {
    num: "01",
    triad: TRIADS.Fern,
    angle: 140,
    title: "Enterprise Data Platform",
    desc: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    tags: ["React", "TypeScript", "D3"],
  },
  {
    num: "02",
    triad: TRIADS.Sage,
    angle: 160,
    title: "Consumer Mobile App",
    desc: "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
    tags: ["Figma", "Swift", "Python"],
  },
  {
    num: "03",
    triad: TRIADS.Slate,
    angle: 140,
    title: "ML Interface Design",
    desc: "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur excepteur.",
    tags: ["Python", "TensorFlow", "React"],
  },
  {
    num: "04",
    triad: TRIADS.Lagoon,
    angle: 120,
    title: "Fintech Dashboard",
    desc: "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
    tags: ["Vue", "SQL", "Figma"],
  },
];

export default function Projects() {
  return (
    <>
      <Nav />
      <main className="shell flex flex-col gap-2.5 pb-20">
        {PROJECTS.map((p) => (
          <ProjectCard key={p.num} {...p} />
        ))}
      </main>
    </>
  );
}

function ProjectCard({
  num,
  triad,
  angle,
  title,
  desc,
  tags,
}: {
  num: string;
  triad: Triad;
  angle: number;
  title: string;
  desc: string;
  tags: string[];
}) {
  const vars = {
    "--bg-dark": fishbowl(triad, angle),
    "--bg-light": fishbowl(triad, angle, true),
  } as CSSProperties;

  return (
    <article
      className="bento relative flex items-center gap-8 overflow-hidden rounded-[26px] px-8 py-[26px]"
      style={vars}
    >
      <p
        className="figure hidden w-[120px] shrink-0 select-none text-center text-[120px] sm:block"
        style={{ color: "var(--card-label)" }}
        aria-hidden
      >
        {num}
      </p>

      <div className="min-w-0 flex-1">
        <h2
          className="mb-2.5 text-[24px] font-normal leading-tight tracking-[-0.025em]"
          style={{ color: "var(--card-heading)" }}
        >
          {title}
        </h2>
        <p
          className="mb-4 max-w-[560px] text-[14px] leading-[1.6]"
          style={{ color: "var(--card-body)" }}
        >
          {desc}
        </p>
        <div className="flex flex-wrap gap-2">
          {tags.map((t) => (
            <Chip key={t}>{t}</Chip>
          ))}
        </div>
      </div>

      <span
        className="absolute right-[26px] top-[22px] grid size-10 place-items-center rounded-full border border-card-chip text-[17px]"
        style={{ color: "var(--card-heading)" }}
        aria-hidden
      >
        ↗
      </span>
    </article>
  );
}
