import { Chrome } from "@/components/chrome";
import { WorkTabs } from "@/components/work-tabs";
import { Hero, Range, Leading, About, Contact } from "@/components/sections";

export default function Home() {
  return (
    <>
      <Chrome />
      <main id="top" className="px-3 pb-3 sm:px-6 sm:pb-6">
        <div className="slab mx-auto max-w-[1440px]">
          <Hero />
          <WorkTabs />
          <Range />
          <Leading />
          <About />
          <Contact />
        </div>
      </main>
    </>
  );
}
