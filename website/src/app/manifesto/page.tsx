// SPDX-License-Identifier: Apache-2.0
import type { Metadata } from "next";
import { ButtonLink } from "@/components/button-link";
import { PageIntro } from "@/components/page-intro";
import { Section } from "@/components/section";
import { manifesto } from "@/content/manifesto";
import { site } from "@/content/site";

export const metadata: Metadata = {
  title: "Manifesto",
  description: "Why we exist: the gap between what people can become and what circumstance allows, and the institution we are building to close it.",
};

export default function ManifestoPage() {
  return (
    <>
      <PageIntro label={manifesto.label} title={manifesto.title} lede={<p>{manifesto.lede}</p>} />

      <Section tone="stone" labelledBy="manifesto-body">
        <h2 id="manifesto-body" className="sr-only">
          The manifesto
        </h2>
        <div className="space-y-20 sm:space-y-28">
          {manifesto.sections.map((s) => (
            <article key={s.heading} className="grid gap-6 lg:grid-cols-12 lg:gap-8">
              <h3 className="display display-s lg:sticky lg:top-10 lg:col-span-4 lg:self-start">{s.heading}</h3>
              <div className="prose-serif max-w-[38rem] space-y-6 text-ink lg:col-span-7 lg:col-start-6">
                {s.paragraphs.map((p) => (
                  <p key={p}>{p}</p>
                ))}
              </div>
            </article>
          ))}
        </div>
      </Section>

      <Section tone="night" space="loose" labelledBy="manifesto-close">
        <span aria-hidden="true" className="mb-10 block h-[2px] w-12 bg-marigold" />
        <h2 id="manifesto-close" className="display display-l max-w-[14ch]">
          {manifesto.closing}
        </h2>
        <p className="mt-6 text-mist">{site.name}</p>
        <div className="mt-12 flex flex-wrap gap-3">
          <ButtonLink href="/sensebook">Explore SenseBook</ButtonLink>
          <ButtonLink href="/vision" variant="secondary">
            See our vision
          </ButtonLink>
        </div>
      </Section>
    </>
  );
}
