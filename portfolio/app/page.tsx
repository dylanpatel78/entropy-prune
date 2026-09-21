import { Nav } from "@/components/nav";
import { BentoCard, Chip } from "@/components/bento-card";
import { TRIADS, UMD } from "@/lib/gradient";

const SKILLS = ["React", "TypeScript", "Python", "Figma", "SQL", "ML"];

export default function Home() {
  return (
    <>
      <Nav />
      <main className="shell flex flex-col gap-3 pb-20">
        <div className="grid gap-3 min-[860px]:grid-cols-[7fr_3fr]">
          <BentoCard
            triad={TRIADS.Dusk}
            label="Available for work"
            className="min-h-[380px]"
          >
            <h1
              className="mb-[18px] text-[clamp(52px,6vw,84px)] font-light leading-[0.9] tracking-[-0.05em]"
              style={{ color: "var(--card-heading)" }}
            >
              Dylan Patel
            </h1>
            <p
              className="max-w-[480px] text-[15px] leading-[1.65]"
              style={{ color: "var(--card-body)" }}
            >
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
              eiusmod tempor incididunt ut labore et dolore magna aliqua ut enim
              ad minim veniam.
            </p>
          </BentoCard>

          <BentoCard triad={UMD.BronzeRed} label="Education" className="min-h-[380px]">
            <h2
              className="mb-2.5 text-[22px] font-normal leading-tight tracking-[-0.025em]"
              style={{ color: "var(--card-heading)" }}
            >
              University of Maryland
            </h2>
            <div className="mb-3.5 flex gap-2">
              <Chip>B.S. CS</Chip>
              <Chip>M.S. Finance</Chip>
            </div>
            <p className="text-[14px] leading-[1.6]" style={{ color: "var(--card-body)" }}>
              Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut enim ad
              minim veniam quis nostrud.
            </p>
          </BentoCard>
        </div>

        <div className="grid gap-3 min-[860px]:grid-cols-3">
          <BentoCard triad={TRIADS.Cobalt} label="Projects" className="min-h-[260px]">
            <p
              className="figure mb-2 text-[52px]"
              style={{ color: "var(--card-heading)" }}
            >
              12
            </p>
            <p className="text-[14px] leading-[1.6]" style={{ color: "var(--card-body)" }}>
              Lorem ipsum dolor sit amet, consectetur adipiscing elit sed do
              eiusmod.
            </p>
          </BentoCard>

          <BentoCard triad={TRIADS.Iris} label="Skills" className="min-h-[260px]">
            <div className="mb-3 flex flex-wrap gap-[7px]">
              {SKILLS.map((s) => (
                <Chip key={s}>{s}</Chip>
              ))}
            </div>
            <p className="text-[14px] leading-[1.6]" style={{ color: "var(--card-body)" }}>
              Lorem ipsum dolor sit amet consectetur adipiscing elit.
            </p>
          </BentoCard>

          <BentoCard triad={TRIADS.Garnet} label="Experience" className="min-h-[260px]">
            <p
              className="figure mb-2 text-[52px]"
              style={{ color: "var(--card-heading)" }}
            >
              4+
            </p>
            <p className="text-[14px] leading-[1.6]" style={{ color: "var(--card-body)" }}>
              Lorem ipsum dolor sit amet, consectetur adipiscing elit sed do
              eiusmod tempor.
            </p>
          </BentoCard>
        </div>
      </main>
    </>
  );
}
