// SPDX-License-Identifier: Apache-2.0
import type { Metadata } from "next";
import { ButtonLink } from "@/components/button-link";
import { Container } from "@/components/container";
import { RenderFigure } from "@/components/render-figure";
import { Reveal } from "@/components/reveal";
import { Section } from "@/components/section";
import { ModelStage } from "@/components/sensebook/model-stage";
import { modelSrc, renderSrc } from "@/content/renders";
import { sensebook } from "@/content/sensebook";
import { site } from "@/content/site";

export const metadata: Metadata = {
  title: "SenseBook",
  description: "SenseBook is a screen-free AI learning companion that clips onto a printed book, sees the page and answers questions aloud. In development.",
};

export default function SenseBookPage() {
  const s = sensebook;
  return (
    <>
      {/* Hero: the product in its own studio light */}
      <section aria-labelledby="page-title" className="bg-stone text-ink">
        <Container className="pt-12 sm:pt-16 lg:pt-20">
          <div className="grid gap-8 lg:grid-cols-12">
            <div className="lg:col-span-7">
              <p className="text-quiet">Our first invention</p>
              <h1 id="page-title" className="display display-xl mt-4">
                {s.hero.title}
              </h1>
            </div>
            <div className="lg:col-span-5 lg:self-end">
              <p className="display display-s">{s.hero.subtitle}</p>
              <p className="mt-5 text-quiet">{s.hero.text}</p>
            </div>
          </div>
        </Container>
        <Container className="pt-12 pb-16 lg:pt-16 lg:pb-24">
          <RenderFigure id="hero" sizes="(min-width: 1344px) 1248px, 100vw" priority parallax={3} aspect="16 / 8.2" position="60% 35%" caption={false} />
          <p className="mt-5 inline-flex items-start gap-3 text-sm text-quiet">
            <span aria-hidden="true" className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-marigold" />
            {s.hero.status}
          </p>
        </Container>
      </section>

      {/* What it is */}
      <Section tone="stone" labelledBy="what-title" className="border-t border-rule">
        <div className="grid gap-12 lg:grid-cols-12 lg:gap-8">
          <div className="lg:col-span-5">
            <h2 id="what-title" className="display display-m">
              {s.whatItIs.title}
            </h2>
            <div className="mt-8 space-y-5">
              {s.whatItIs.paragraphs.map((p) => (
                <p key={p} className="measure">
                  {p}
                </p>
              ))}
            </div>
          </div>
          <RenderFigure note={false} id="top" sizes="(min-width: 1024px) 55vw, 100vw" className="lg:col-span-7" />
        </div>
      </Section>

      {/* How it works: a real sequence, so the steps are numbered */}
      <Section tone="night" labelledBy="how-title">
        <Reveal>
          <h2 id="how-title" className="display display-l">
            {s.howItWorks.title}
          </h2>
        </Reveal>
        <ol className="mt-16 grid gap-x-10 gap-y-12 sm:grid-cols-2 lg:mt-20 lg:grid-cols-4">
          {s.howItWorks.steps.map((step, i) => (
            <li key={step.name} className="border-t border-graphite pt-6">
              <span className="font-display text-5xl font-light text-marigold" aria-hidden="true">
                {i + 1}
              </span>
              <h3 className="mt-5 text-lg font-semibold">
                <span className="sr-only">Step {i + 1}: </span>
                {step.name}
              </h3>
              <p className="mt-3 text-mist">{step.text}</p>
            </li>
          ))}
        </ol>
        <div className="mt-20 grid gap-6 sm:grid-cols-2 lg:mt-28">
          <RenderFigure note={false} id="hardcover" tone="night" sizes="(min-width: 640px) 50vw, 100vw" aspect="3 / 2" />
          <RenderFigure note={false} id="paperback" tone="night" sizes="(min-width: 640px) 50vw, 100vw" aspect="3 / 2" />
          <RenderFigure note={false} id="tripod" tone="night" sizes="(min-width: 640px) 50vw, 100vw" aspect="3 / 2" />
          <RenderFigure note={false} id="extended" tone="night" sizes="(min-width: 640px) 50vw, 100vw" aspect="3 / 2" />
        </div>
        <div className="mt-12 grid lg:grid-cols-12">
          <div className="lg:col-span-7">
            <p className="lede text-stone">{s.howItWorks.contexts}</p>
            <p className="mt-4 text-sm text-dim">{s.howItWorks.note}</p>
          </div>
        </div>
      </Section>

      {/* Who it serves */}
      <Section tone="stone" labelledBy="who-title">
        <div className="grid gap-12 lg:grid-cols-12 lg:gap-8">
          <h2 id="who-title" className="display display-m lg:col-span-4">
            {s.whoItServes.title}
          </h2>
          <ul className="grid gap-x-12 gap-y-10 sm:grid-cols-2 lg:col-span-8">
            {s.whoItServes.groups.map((g) => (
              <li key={g.name} className="border-t border-ink/80 pt-5">
                <h3 className="text-lg font-semibold">{g.name}</h3>
                <p className="mt-2 text-quiet">{g.text}</p>
              </li>
            ))}
          </ul>
        </div>
      </Section>

      {/* Conversational learning */}
      <Section tone="stone" labelledBy="conv-title" space="none" className="pb-20 sm:pb-28 lg:pb-36">
        <div className="grid gap-10 border-t border-rule pt-20 sm:pt-28 lg:grid-cols-12 lg:gap-8 lg:pt-36">
          <h2 id="conv-title" className="display display-l lg:col-span-6">
            {s.conversational.title}
          </h2>
          <div className="space-y-5 lg:col-span-5 lg:col-start-8 lg:self-end">
            {s.conversational.paragraphs.map((p) => (
              <p key={p}>{p}</p>
            ))}
          </div>
        </div>
      </Section>

      {/* Accessibility by design */}
      <Section tone="night" labelledBy="access-title">
        <div className="grid gap-10 lg:grid-cols-12">
          <Reveal className="lg:col-span-7">
            <h2 id="access-title" className="display display-l">
              {s.accessibility.title}
            </h2>
          </Reveal>
          <p className="lede text-stone lg:col-span-8">{s.accessibility.lede}</p>
        </div>
        <ul className="mt-16 grid gap-x-10 gap-y-10 sm:grid-cols-2 lg:mt-20 lg:grid-cols-4">
          {s.accessibility.points.map((p) => (
            <li key={p.name} className="border-t border-graphite pt-5">
              <h3 className="text-lg font-semibold">{p.name}</h3>
              <p className="mt-2 text-mist">{p.text}</p>
            </li>
          ))}
        </ul>
      </Section>

      {/* Why physical AI matters */}
      <Section tone="night" labelledBy="physical-title" className="border-t border-graphite">
        <div className="grid gap-12 lg:grid-cols-12 lg:gap-8">
          <div className="lg:col-span-5">
            <h2 id="physical-title" className="display display-m">
              {s.physicalAi.title}
            </h2>
            <div className="mt-8 space-y-5 text-mist">
              {s.physicalAi.paragraphs.map((p) => (
                <p key={p} className="measure">
                  {p}
                </p>
              ))}
            </div>
          </div>
          <RenderFigure note={false} id="folded" tone="night" sizes="(min-width: 1024px) 55vw, 100vw" className="lg:col-span-7" aspect="3 / 2" parallax={3} />
        </div>
      </Section>

      {/* Product visuals and the 3D model */}
      <Section tone="stone" labelledBy="design-title">
        <div className="grid gap-8 lg:grid-cols-12">
          <h2 id="design-title" className="display display-l lg:col-span-6">
            {s.visuals.title}
          </h2>
          <p className="measure lg:col-span-5 lg:col-start-8 lg:self-end">{s.visuals.text}</p>
        </div>
        <RenderFigure note={false} id="exploded" sizes="(min-width: 1344px) 1248px, 100vw" className="mt-16 lg:mt-20" />
        <div className="mt-16 grid gap-10 md:grid-cols-2">
          <RenderFigure note={false} id="front" sizes="(min-width: 768px) 50vw, 100vw" />
          <RenderFigure note={false} id="side" sizes="(min-width: 768px) 50vw, 100vw" />
        </div>
        <RenderFigure note={false} id="cutaway" sizes="(min-width: 1344px) 1248px, 100vw" className="mt-16" />

        <div className="mt-24 border-t border-rule pt-16 lg:mt-32 lg:pt-20">
          <div className="grid gap-6 lg:grid-cols-12">
            <h3 className="display display-m lg:col-span-6">{s.visuals.modelTitle}</h3>
            <p className="measure lg:col-span-5 lg:col-start-8 lg:self-end">{s.visuals.modelText}</p>
          </div>
          <div className="mt-10">
            <ModelStage src={modelSrc} poster={renderSrc("exploded")} posterAlt="" />
            <p className="mt-4 text-sm text-quiet">{s.visuals.modelNote}</p>
          </div>
        </div>
      </Section>

      {/* Open design + roadmap */}
      <Section tone="night" labelledBy="roadmap-title">
        <div className="grid gap-10 lg:grid-cols-12">
          <div className="lg:col-span-5">
            <h2 id="roadmap-title" className="display display-l">
              {s.roadmap.title}
            </h2>
            <p className="mt-6 text-mist measure">{s.roadmap.lede}</p>
          </div>
          <ol className="lg:col-span-6 lg:col-start-7">
            {s.roadmap.stages.map((stage, i) => (
              <li key={stage.name} className="grid grid-cols-[2.5rem_1fr] gap-x-4 border-t border-graphite py-6 last:border-b">
                <span aria-hidden="true" className={`font-display text-2xl font-light ${"now" in stage ? "text-marigold" : "text-dim"}`}>
                  {i + 1}
                </span>
                <div>
                  <h3 className="flex flex-wrap items-baseline gap-x-3 text-lg font-semibold">
                    <span className="sr-only">Stage {i + 1}: </span>
                    {stage.name}
                    {"now" in stage && <span className="text-sm font-normal text-marigold">Where we are now</span>}
                  </h3>
                  <p className="mt-1 text-mist">{stage.text}</p>
                </div>
              </li>
            ))}
          </ol>
        </div>

        <div className="mt-24 grid gap-8 border-t border-graphite pt-16 lg:mt-32 lg:grid-cols-12 lg:pt-20">
          <h2 className="display display-m lg:col-span-5">{s.open.title}</h2>
          <div className="lg:col-span-6 lg:col-start-7">
            <p className="text-mist">{s.open.text}</p>
            <div className="mt-8 flex flex-wrap gap-3">
              <ButtonLink href={site.repoUrl} variant="secondary">
                {s.open.cta}
              </ButtonLink>
              <ButtonLink href="/contact">Work with us</ButtonLink>
            </div>
          </div>
        </div>
      </Section>
    </>
  );
}
