// SPDX-License-Identifier: Apache-2.0
import type { Metadata } from "next";
import { ButtonLink } from "@/components/button-link";
import { PageIntro } from "@/components/page-intro";
import { Reveal } from "@/components/reveal";
import { Section } from "@/components/section";
import { vision } from "@/content/vision";

export const metadata: Metadata = {
  title: "Vision",
  description: "Three pillars of human potential: Human Intelligence, Human Independence and Human Opportunity, and the kinds of invention each leads to.",
};

export default function VisionPage() {
  return (
    <>
      <PageIntro label={vision.label} title={vision.title} lede={<p>{vision.lede}</p>} />

      {vision.pillars.map((p, i) => {
        const tone = i % 2 === 0 ? "stone" : "night";
        const id = `pillar-${i}`;
        return (
          <Section key={p.name} tone={tone} labelledBy={id}>
            <div className="grid gap-10 lg:grid-cols-12 lg:gap-8">
              <div className="lg:col-span-5">
                <Reveal>
                  <h2 id={id} className="display display-l">
                    {p.name.split(" ").map((w) => (
                      <span key={w} className="block">
                        {w}
                      </span>
                    ))}
                  </h2>
                </Reveal>
                <p className="display display-s mt-8 max-w-[24ch]">{p.statement}</p>
              </div>
              <div className="lg:col-span-6 lg:col-start-7 lg:pt-4">
                <h3 className={`text-sm ${tone === "night" ? "text-mist" : "text-quiet"}`}>Kinds of invention</h3>
                <ul className="mt-4">
                  {p.categories.map((c) => (
                    <li key={c.name} className={`border-t py-6 ${tone === "night" ? "border-graphite" : "border-rule"}`}>
                      <h4 className="text-lg font-semibold">{c.name}</h4>
                      <p className={`mt-2 ${tone === "night" ? "text-mist" : "text-quiet"}`}>{c.text}</p>
                    </li>
                  ))}
                </ul>
                <p className={`mt-2 flex gap-3 border-t pt-6 text-sm ${tone === "night" ? "border-graphite text-mist" : "border-rule text-quiet"}`}>
                  <span aria-hidden="true" className="mt-2 h-[2px] w-5 shrink-0 bg-marigold" />
                  <span>
                    <span className={`font-semibold ${tone === "night" ? "text-stone" : "text-ink"}`}>Where SenseBook fits. </span>
                    {p.sensebook}
                  </span>
                </p>
              </div>
            </div>
          </Section>
        );
      })}

      <Section tone="night" space="loose" labelledBy="vision-close" className="border-t border-graphite">
        <div className="grid gap-10 lg:grid-cols-12">
          <h2 id="vision-close" className="display display-l lg:col-span-7">
            {vision.close.title}
          </h2>
          <div className="lg:col-span-4 lg:col-start-9 lg:self-end">
            <p className="text-mist">{vision.close.text}</p>
            <div className="mt-8 flex flex-wrap gap-3">
              <ButtonLink href="/impact">How we intend to matter</ButtonLink>
            </div>
          </div>
        </div>
      </Section>
    </>
  );
}
