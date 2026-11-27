// SPDX-License-Identifier: Apache-2.0
import type { Metadata } from "next";
import { ButtonLink } from "@/components/button-link";
import { PageIntro } from "@/components/page-intro";
import { Section } from "@/components/section";
import { impact } from "@/content/impact";

export const metadata: Metadata = {
  title: "Impact",
  description: "The barriers we intend to remove and the outcomes we intend to measure, in education, accessibility, intellectual independence, Bangladeshi capability and global human impact.",
};

export default function ImpactPage() {
  return (
    <>
      <PageIntro label={impact.label} title={impact.title} lede={<p>{impact.lede}</p>} />

      <Section tone="stone" labelledBy="areas-title">
        <h2 id="areas-title" className="sr-only">
          Barriers and measures
        </h2>
        {/* Column headings for the two things said about each area */}
        <div aria-hidden="true" className="hidden grid-cols-12 gap-8 pb-4 text-sm text-quiet lg:grid">
          <span className="col-span-4" />
          <span className="col-span-4">The barrier</span>
          <span className="col-span-4">What we intend to measure</span>
        </div>
        <ul>
          {impact.areas.map((a) => (
            <li key={a.name} className="grid gap-4 border-t border-rule py-10 lg:grid-cols-12 lg:gap-8 lg:py-12">
              <h3 className="display display-s lg:col-span-4">{a.name}</h3>
              <div className="lg:col-span-4">
                <p className="text-sm text-quiet lg:sr-only">The barrier</p>
                <p className="mt-1 lg:mt-0">{a.barrier}</p>
              </div>
              <div className="lg:col-span-4">
                <p className="text-sm text-quiet lg:sr-only">What we intend to measure</p>
                <p className="mt-1 text-quiet lg:mt-0">{a.measure}</p>
              </div>
            </li>
          ))}
        </ul>
      </Section>

      <Section tone="night" labelledBy="principles-title">
        <h2 id="principles-title" className="display display-l max-w-[16ch]">
          {impact.principles.title}
        </h2>
        <ul className="mt-16 grid gap-x-10 gap-y-10 md:grid-cols-3 lg:mt-20">
          {impact.principles.items.map((p) => (
            <li key={p.name} className="border-t border-graphite pt-6">
              <h3 className="text-lg font-semibold">{p.name}</h3>
              <p className="mt-2 text-mist">{p.text}</p>
            </li>
          ))}
        </ul>
        <div className="mt-16 flex flex-wrap gap-3">
          <ButtonLink href="/contact">Research with us</ButtonLink>
          <ButtonLink href="/sensebook" variant="secondary">
            Explore SenseBook
          </ButtonLink>
        </div>
      </Section>
    </>
  );
}
