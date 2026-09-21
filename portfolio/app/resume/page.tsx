import { Nav } from "@/components/nav";
import { Section, Entry, Chips } from "@/components/resume";

const L1 =
  "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.";
const L2 =
  "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.";

const NAV = [
  ["Experience", "experience"],
  ["Leadership", "leadership"],
  ["Education", "education"],
  ["Skills", "skills"],
] as const;

export default function Resume() {
  return (
    <>
      <Nav />
      <main className="shell pb-28">
        <header className="max-w-[54ch] pt-4 pb-14">
          <h1 className="text-[clamp(46px,7vw,88px)] font-light leading-[0.92] tracking-[-0.05em] text-ink">
            Resume.
          </h1>
          <p className="mt-7 text-[clamp(16px,1.8vw,19px)] leading-[1.65] text-ink2">
            {L1} {L2}
          </p>
          <a
            href="#"
            className="mt-9 inline-block rounded-full px-7 py-3 text-[13.5px] font-medium"
            style={{ background: "var(--acid)", color: "#08080a" }}
          >
            Download PDF
          </a>
        </header>

        <div className="grid gap-x-16 gap-y-10 lg:grid-cols-[170px_minmax(0,1fr)]">
          <nav className="hidden lg:block">
            <ul className="sticky top-8 flex flex-col gap-3 border-l border-line pl-5">
              {NAV.map(([label, id]) => (
                <li key={id}>
                  <a href={`#${id}`} className="text-[14px] text-ink2 transition-colors hover:text-ink">
                    {label}
                  </a>
                </li>
              ))}
            </ul>
          </nav>

          <div>
            <Section id="experience" title="Experience" count="04">
              <Entry
                role="Technical Product Intern"
                org="Pinnacle Infotech · Sugar Land, TX"
                when="Jun — Jul 2026"
                bullets={[L1, L2]}
              />
              <Entry
                role="Co-author, HCI technical contributor"
                org="Embodied Dynamics Lab, University of Maryland"
                when="May 2026 —"
                bullets={[L2, L1]}
              />
              <Entry
                role="Undergraduate teaching assistant"
                org="Department of Computer Science, University of Maryland"
                when="Feb 2026 —"
                bullets={[L1]}
              />
              <Entry
                role="Student manager"
                org="Student Organization Resource Center, University of Maryland"
                when="Jan 2025 —"
                bullets={[L2, L1]}
              />
            </Section>

            <Section id="leadership" title="Leadership" count="03">
              <Entry
                role="Vice president and treasurer"
                org="Product Space @ UMD"
                when="Aug 2025 —"
                bullets={[L1, L2]}
              />
              <Entry
                role="Student senator"
                org="University Senate, Student Affairs Committee"
                when="May 2025 —"
                bullets={[L2]}
              />
              <Entry
                role="Council member"
                org="CMNS Dean’s Student Advisory Council"
                when="Jan 2026 —"
                bullets={[L1]}
              />
            </Section>

            <Section id="education" title="Education" count="02">
              <Entry
                role="BS, Computer Science"
                org="University of Maryland · College of Computer, Mathematical and Natural Sciences"
                when="College Park, MD"
                bullets={[L1]}
              />
              <Entry
                role="Master of Finance"
                org="Robert H. Smith School of Business · combined BS/MS"
                when="College Park, MD"
                bullets={[L2]}
              />
            </Section>

            <Section id="skills" title="Skills" count="03">
              <Chips
                label="Engineering"
                items={["React.js", "Flask", "Node.js", "TensorFlow", "Gemini APIs", "AWS", "Azure", "GitHub", "Agile / Scrum"]}
              />
              <Chips
                label="Research and data"
                items={["Python", "Pandas", "NumPy", "SQL", "Power BI", "Qualtrics", "Predictive modelling"]}
              />
              <Chips
                label="Programme management"
                items={["Program evaluation", "Survey design", "Assessment", "Workshop facilitation", "Smartsheet", "TerpLink"]}
              />
            </Section>
          </div>
        </div>
      </main>
    </>
  );
}
