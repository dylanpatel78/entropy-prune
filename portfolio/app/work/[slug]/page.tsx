import Link from "next/link";
import { notFound } from "next/navigation";
import { Chrome } from "@/components/chrome";
import { Spectrum } from "@/components/spectrum";
import { projects } from "@/content/projects";

export function generateStaticParams() {
  return projects.map((p) => ({ slug: p.slug }));
}

export default async function CaseStudy({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const p = projects.find((x) => x.slug === slug);
  if (!p) notFound();

  const blocks = [
    { title: "The decision", body: p.decision, tone: "var(--outcome)" },
    { title: "The build", body: p.build, tone: "var(--build)" },
  ];

  return (
    <>
      <Chrome />
      <main className="px-3 pb-3 sm:px-6 sm:pb-6">
        <div className="slab mx-auto max-w-[1440px]">
          <article className="px-5 pt-32 pb-20 sm:px-10 sm:pt-44 sm:pb-28">
            <header className="border-b border-line pb-12">
              <h1 className="wide text-[clamp(2.6rem,8vw,6rem)] leading-[0.95]">
                {p.name}
              </h1>
              <p className="mt-6 max-w-[48ch] text-[clamp(1.05rem,1.8vw,1.4rem)] leading-relaxed text-fg2">
                {p.summary}
              </p>
              <dl className="mt-10 grid gap-6 sm:grid-cols-3">
                {[
                  ["Role", p.role],
                  ["Period", p.period],
                  ["Domain", p.domainLabel],
                ].map(([k, v]) => (
                  <div key={k}>
                    <dt className="text-[13px] text-fg3">{k}</dt>
                    <dd className="mt-1 text-[15px]">{v}</dd>
                  </div>
                ))}
              </dl>
            </header>

            <div className="grid gap-x-12 gap-y-14 py-14 lg:grid-cols-12">
              {blocks.map((b) => (
                <section key={b.title} className="contents">
                  <h2
                    className="text-[15px] lg:col-span-3"
                    style={{ color: b.tone }}
                  >
                    {b.title}
                  </h2>
                  <p className="max-w-[62ch] text-[clamp(1.05rem,1.6vw,1.3rem)] leading-relaxed lg:col-span-9">
                    {b.body}
                  </p>
                </section>
              ))}

              <h2
                className="text-[15px] lg:col-span-3"
                style={{ color: "var(--outcome)" }}
              >
                The outcome
              </h2>
              <div className="lg:col-span-9">
                <dl className="flex flex-wrap gap-x-14 gap-y-8">
                  {p.outcome.map((o) => (
                    <div key={o.label}>
                      <dt className="sr-only">{o.label}</dt>
                      <dd>
                        <span
                          className="tnum wide block text-[clamp(2.6rem,6vw,4.4rem)] leading-none"
                          style={{ color: "var(--outcome)" }}
                        >
                          {o.value}
                        </span>
                        <span className="mt-2 block max-w-[18ch] text-[14px] text-fg3">
                          {o.label}
                        </span>
                      </dd>
                    </div>
                  ))}
                </dl>
                <div className="mt-12 max-w-[520px]">
                  <Spectrum values={p.spectrum} />
                  <p className="mt-3 font-mono text-[12px] text-fg3">
                    singular value spectrum
                  </p>
                </div>
              </div>

              <h2 className="text-[15px] text-fg2 lg:col-span-3">
                What I&rsquo;d change
              </h2>
              <p className="max-w-[62ch] text-[clamp(1.05rem,1.6vw,1.3rem)] leading-relaxed text-fg2 lg:col-span-9">
                Placeholder. This is where the honest self-critique goes — the
                thing you would do differently, written plainly enough that an
                interviewer believes you have thought about it.
              </p>
            </div>

            <footer className="flex flex-wrap gap-7 border-t border-line pt-10">
              <Link
                href="/#work"
                className="text-[15px] underline decoration-from-font underline-offset-[5px]"
              >
                All work
              </Link>
              {p.links?.repo && (
                <a
                  href={p.links.repo}
                  className="text-[15px] underline decoration-from-font underline-offset-[5px]"
                  style={{ color: "var(--build)" }}
                >
                  Source
                </a>
              )}
            </footer>
          </article>
        </div>
      </main>
    </>
  );
}
