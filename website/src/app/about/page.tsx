// SPDX-License-Identifier: Apache-2.0
import type { Metadata } from "next";
import { ButtonLink } from "@/components/button-link";
import { PageIntro } from "@/components/page-intro";
import { Reveal } from "@/components/reveal";
import { Section } from "@/components/section";
import { about } from "@/content/about";
import { site } from "@/content/site";

export const metadata: Metadata = {
  title: "About",
  description: "Who we are, what we believe, the problems we choose, our values, and how we design and engineer.",
};

export default function AboutPage() {
  return (
    <>
      <PageIntro
        label={about.label}
        title={about.title}
        lede={
          <p>
            {site.name} {about.lede}
          </p>
        }
      />

      {/* What we believe */}
      <Section tone="stone" labelledBy="beliefs-title">
        <div className="grid gap-10 lg:grid-cols-12 lg:gap-8">
          <h2 id="beliefs-title" className="text-quiet lg:col-span-3">
            {about.beliefs.title}
          </h2>
          <ul className="space-y-10 lg:col-span-9">
            {about.beliefs.items.map((b, i) => (
              <Reveal as="li" key={b} delay={i * 0.06} className="display display-m max-w-[24ch]">
                {b}
              </Reveal>
            ))}
          </ul>
        </div>
      </Section>

      {/* The problems we choose */}
      <Section tone="night" labelledBy="problems-title">
        <div className="grid gap-8 lg:grid-cols-12">
          <h2 id="problems-title" className="display display-l lg:col-span-6">
            {about.problems.title}
          </h2>
          <p className="lede text-mist lg:col-span-5 lg:col-start-8 lg:self-end">{about.problems.lede}</p>
        </div>
        <ul className="mt-16 grid gap-x-10 gap-y-10 sm:grid-cols-2 lg:mt-20 lg:grid-cols-4">
          {about.problems.items.map((p) => (
            <li key={p.name} className="border-t border-graphite pt-6">
              <h3 className="text-lg font-semibold">{p.name}</h3>
              <p className="mt-2 text-mist">{p.text}</p>
            </li>
          ))}
        </ul>
      </Section>

      {/* Values and design philosophy */}
      <Section tone="stone" labelledBy="values-title">
        <div className="grid gap-16 lg:grid-cols-2 lg:gap-20">
          <div>
            <h2 id="values-title" className="display display-m">
              {about.values.title}
            </h2>
            <dl className="mt-10">
              {about.values.items.map((v) => (
                <div key={v.name} className="grid gap-2 border-t border-rule py-5 sm:grid-cols-[9rem_1fr] sm:gap-6">
                  <dt className="font-semibold">{v.name}</dt>
                  <dd className="text-quiet">{v.text}</dd>
                </div>
              ))}
            </dl>
          </div>
          <div>
            <h2 className="display display-m">{about.philosophy.title}</h2>
            <dl className="mt-10">
              {about.philosophy.items.map((v) => (
                <div key={v.name} className="border-t border-rule py-5">
                  <dt className="font-semibold">{v.name}</dt>
                  <dd className="mt-1 text-quiet">{v.text}</dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </Section>

      <Section tone="night" space="loose" labelledBy="about-close">
        <div className="grid gap-10 lg:grid-cols-12">
          <h2 id="about-close" className="display display-l lg:col-span-7">
            {site.signature}
          </h2>
          <div className="flex flex-wrap gap-3 lg:col-span-4 lg:col-start-9 lg:self-end">
            <ButtonLink href="/manifesto">Read the manifesto</ButtonLink>
            <ButtonLink href="/contact" variant="secondary">
              Contact us
            </ButtonLink>
          </div>
        </div>
      </Section>
    </>
  );
}
