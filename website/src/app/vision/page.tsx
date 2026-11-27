// SPDX-License-Identifier: Apache-2.0
import type { Metadata } from "next";
import { ButtonLink } from "@/components/button-link";
import { PageIntro } from "@/components/page-intro";
import { Reveal } from "@/components/reveal";
import { Section } from "@/components/section";
import { fields } from "@/content/fields";
import { vision } from "@/content/vision";

export const metadata: Metadata = {
  title: "Vision",
  description:
    "Five fields of work: intellectual advancement, physical independence, economic opportunity, health and wellbeing, and societal infrastructure.",
};

export default function VisionPage() {
  return (
    <>
      <PageIntro label={vision.label} title={vision.title} lede={<p>{vision.lede}</p>} />

      {fields.map((f, i) => {
        const night = i % 2 === 1;
        const id = `field-${i}`;
        const muted = night ? "text-mist" : "text-quiet";
        const rule = night ? "border-graphite" : "border-rule";
        return (
          <Section key={f.name} tone={night ? "night" : "stone"} labelledBy={id}>
            <div className="grid gap-10 lg:grid-cols-12 lg:gap-8">
              <div className="lg:col-span-5">
                <Reveal>
                  <h2 id={id} className="display display-l max-w-[12ch]">
                    {f.name}
                  </h2>
                </Reveal>
                <p className="display display-s mt-8 max-w-[24ch]">{f.text}</p>
                <div className="mt-10">
                  <h3 className={`text-sm ${muted}`}>Programmes</h3>
                  <ul className="mt-3 flex flex-wrap gap-2">
                    {f.programmes.map((p) => (
                      <li
                        key={p.name}
                        className={`inline-flex items-center gap-2 rounded-full px-4 py-1.5 text-[0.9375rem] ring-1 ring-inset ${
                          p.status ? "ring-marigold" : night ? "ring-graphite" : "ring-rule"
                        }`}
                      >
                        {p.status && <span aria-hidden="true" className="h-2 w-2 rounded-full bg-marigold" />}
                        <span className={p.status ? "font-medium" : muted}>{p.name}</span>
                        <span className={p.status ? `text-sm ${night ? "text-marigold" : "text-marigold-deep"}` : "sr-only"}>
                          {p.status ?? "(proposed)"}
                        </span>
                      </li>
                    ))}
                  </ul>
                  <p className={`mt-3 text-sm ${muted}`}>
                    {f.programmes.some((p) => p.status) ? "Others proposed, not yet built." : "Proposed, not yet built."}
                  </p>
                </div>
              </div>
              <div className="lg:col-span-6 lg:col-start-7 lg:pt-4">
                <h3 className={`text-sm ${muted}`}>Kinds of invention</h3>
                <ul className="mt-4">
                  {f.categories.map((c) => (
                    <li key={c.name} className={`border-t py-6 ${rule}`}>
                      <h4 className="text-lg font-semibold">{c.name}</h4>
                      <p className={`mt-2 ${muted}`}>{c.text}</p>
                    </li>
                  ))}
                </ul>
                {i === 0 && (
                  <p className={`flex gap-3 border-t pt-6 text-sm ${rule} ${muted}`}>
                    <span aria-hidden="true" className="mt-2 h-[2px] w-5 shrink-0 bg-marigold" />
                    <span>
                      <span className="font-semibold text-ink">Where SenseBook fits. </span>
                      {vision.sensebookNote}
                    </span>
                  </p>
                )}
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
