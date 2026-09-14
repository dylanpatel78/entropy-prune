import Link from "next/link";
import { Chrome } from "@/components/chrome";
import { profile } from "@/content/profile";
import { projects } from "@/content/projects";

export default function Resume() {
  return (
    <>
      <Chrome />
      <main className="px-3 pb-3 sm:px-6 sm:pb-6">
        <div className="slab mx-auto max-w-[1440px]">
          <div className="px-5 pt-32 pb-20 sm:px-10 sm:pt-44 sm:pb-28">
            <h1 className="wide text-[clamp(2.6rem,8vw,6rem)] leading-[0.95]">
              {profile.name}
            </h1>
            <p className="mt-6 max-w-[48ch] text-[clamp(1.05rem,1.8vw,1.4rem)] leading-relaxed text-fg2">
              {profile.standfirst}
            </p>

            <section className="mt-16 border-t border-line pt-10">
              <h2 className="mb-8 text-[15px] text-fg3">Selected work</h2>
              <ul className="space-y-8">
                {projects.map((p) => (
                  <li key={p.slug} className="grid gap-3 sm:grid-cols-12">
                    <div className="sm:col-span-3">
                      <Link
                        href={`/work/${p.slug}`}
                        className="text-[17px] underline decoration-from-font underline-offset-[5px]"
                      >
                        {p.name}
                      </Link>
                      <p className="mt-1 text-[13px] text-fg3">{p.period}</p>
                    </div>
                    <p className="max-w-[56ch] text-[15px] leading-relaxed text-fg2 sm:col-span-9">
                      {p.summary}{" "}
                      <span style={{ color: "var(--outcome)" }}>
                        {p.outcome.map((o) => `${o.value} ${o.label}`).join(" · ")}
                      </span>
                    </p>
                  </li>
                ))}
              </ul>
            </section>

            <section className="mt-16 border-t border-line pt-10">
              <h2 className="mb-8 text-[15px] text-fg3">Leadership</h2>
              <p className="text-[17px]">{profile.leadership.what}</p>
              <p className="mt-1 text-[13px] text-fg3">
                {profile.leadership.period}
              </p>
              <p className="mt-4 max-w-[60ch] text-[15px] leading-relaxed text-fg2">
                {profile.leadership.body}
              </p>
            </section>

            <p className="mt-16 border-t border-line pt-10 text-[14px] text-fg3">
              A downloadable PDF goes here once you have one.
            </p>
          </div>
        </div>
      </main>
    </>
  );
}
