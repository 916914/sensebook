// SPDX-License-Identifier: Apache-2.0
import { ButtonLink, TextLink } from "@/components/button-link";
import { Container } from "@/components/container";
import { HeroHeadline } from "@/components/home/hero-headline";
import { HeroStage } from "@/components/home/hero-stage";
import { HorizonLine } from "@/components/home/horizon-line";
import { RenderFigure } from "@/components/render-figure";
import { Reveal } from "@/components/reveal";
import { Section } from "@/components/section";
import { home } from "@/content/home";

export default function Home() {
  const { hero, core, firstChapter, why, institution, bangladesh, manifesto, close } = home;

  return (
    <>
      {/* 1. Hero */}
      <section aria-labelledby="hero-title" className="bg-night text-stone">
        <Container className="pt-8 pb-12 sm:pt-12 lg:pt-10 lg:pb-14">
          <HeroHeadline id="hero-title" lines={hero.headline} />
          <div className="mt-10 grid gap-10 lg:mt-8 lg:grid-cols-12">
            <div className="lg:col-span-6 lg:col-start-7">
              <p className="lede text-stone">{hero.text}</p>
              <p className="mt-5 text-mist">{hero.secondary}</p>
              <div className="mt-9 flex flex-wrap gap-3">
                <ButtonLink href={hero.primary.href}>{hero.primary.label}</ButtonLink>
                <ButtonLink href={hero.secondaryCta.href} variant="secondary">
                  {hero.secondaryCta.label}
                </ButtonLink>
              </div>
            </div>
          </div>
        </Container>
        <HeroStage className="h-[62vh] min-h-[22rem] sm:h-[78vh] lg:max-h-[56rem]">
          <RenderFigure id="hardcover" sizes="100vw" priority caption={false} aspect="fill" className="h-full" position="50% 22%" tone="night" />
        </HeroStage>
        <Container>
          <p className="py-4 text-sm text-dim">SenseBook on an open hardcover. Render of the prototype design, not a photograph.</p>
        </Container>
      </section>

      {/* 2. The core idea */}
      <Section tone="night" space="loose" labelledBy="core-title">
        <h2 id="core-title" className="sr-only">
          Why we exist
        </h2>
        <div className="grid gap-y-10 lg:grid-cols-12">
          <ul className="space-y-8 lg:col-span-9 lg:space-y-10">
            {core.lines.map((line, i) => (
              <Reveal as="li" key={line} delay={i * 0.12} className="display display-s max-w-[30ch] text-mist">
                {line}
              </Reveal>
            ))}
          </ul>
          <Reveal className="lg:col-span-10 lg:col-start-3 lg:mt-16">
            <span aria-hidden="true" className="mb-8 block h-[2px] w-12 bg-marigold" />
            <p className="display display-m max-w-[22ch] text-stone">{core.close}</p>
          </Reveal>
        </div>
      </Section>

      {/* 3. Our first chapter */}
      <Section tone="stone" labelledBy="sensebook-title" className="overflow-hidden">
        <div className="grid items-end gap-12 lg:grid-cols-12 lg:gap-8">
          <div className="lg:col-span-5">
            <p className="text-quiet">Our first chapter</p>
            <h2 id="sensebook-title" className="display display-l mt-3">
              {firstChapter.title}
            </h2>
            <p className="display display-s mt-6 max-w-[22ch]">{firstChapter.subtitle}</p>
            <p className="mt-8 measure">{firstChapter.text}</p>
            <p className="mt-4 measure">{firstChapter.detail}</p>
            <p className="mt-8 inline-flex items-center gap-3 text-sm text-quiet">
              <span aria-hidden="true" className="h-2 w-2 rounded-full bg-marigold" />
              {firstChapter.status}
            </p>
            <div className="mt-8">
              <ButtonLink href={firstChapter.cta.href} tone="stone">
                {firstChapter.cta.label}
              </ButtonLink>
            </div>
          </div>
          <RenderFigure
            id="hero"
            sizes="(min-width: 1024px) 58vw, 100vw"
            parallax={4}
            caption={false}
            aspect="4 / 3.4"
            position="62% 40%"
            className="lg:col-span-7"
          />
        </div>
      </Section>

      {/* 4. Why it matters */}
      <Section tone="stone" space="none" labelledBy="why-title" className="pb-20 sm:pb-28 lg:pb-36">
        <div className="border-t border-rule pt-20 sm:pt-28 lg:pt-36">
          <Reveal>
            <h2 id="why-title" className="display display-m max-w-[20ch]">
              {why.title}
            </h2>
          </Reveal>
          <ul className="mt-16 grid gap-x-12 gap-y-14 sm:grid-cols-2 lg:mt-24 lg:gap-x-20">
            {why.people.map((p) => (
              <li key={p.name} className="border-t border-ink/80 pt-6">
                <h3 className="text-lg font-semibold tracking-[-0.01em]">{p.name}</h3>
                <p className="mt-3 max-w-[34rem] text-quiet">{p.text}</p>
              </li>
            ))}
          </ul>
        </div>
      </Section>

      {/* 5. The bigger institution */}
      <Section tone="night" labelledBy="institution-title">
        <div className="grid gap-10 lg:grid-cols-12">
          <Reveal className="lg:col-span-7">
            <h2 id="institution-title" className="display display-l max-w-[14ch]">
              {institution.title}
            </h2>
          </Reveal>
          <p className="lede text-mist lg:col-span-4 lg:col-start-9 lg:self-end">{institution.text}</p>
        </div>
        <ol className="mt-20 grid gap-px overflow-hidden bg-graphite lg:mt-28 lg:grid-cols-3">
          {institution.pillars.map((p) => (
            <li key={p.name} className="bg-night py-10 lg:px-10 lg:py-12 lg:first:pl-0">
              <h3 className="display display-s">
                {p.name.split(" ").map((w) => (
                  <span key={w} className="block">
                    {w}
                  </span>
                ))}
              </h3>
              <p className="mt-5 max-w-[30ch] text-mist">{p.text}</p>
            </li>
          ))}
        </ol>
        <div className="mt-14">
          <TextLink href={institution.cta.href} className="text-stone">
            {institution.cta.label}
          </TextLink>
        </div>
      </Section>

      {/* 6. Bangladesh to humanity */}
      <Section tone="night" space="loose" labelledBy="bangladesh-title" className="border-t border-graphite">
        <h2 id="bangladesh-title" className="display display-xl">
          {bangladesh.title.map((l) => (
            <span key={l} className="block">
              {l}
            </span>
          ))}
        </h2>
        <div className="mt-14 lg:mt-20">
          <HorizonLine />
        </div>
        <div className="mt-10 grid lg:grid-cols-12">
          <p className="lede text-mist lg:col-span-6 lg:col-start-7">{bangladesh.text}</p>
        </div>
      </Section>

      {/* 7. Manifesto preview */}
      <Section tone="stone" labelledBy="manifesto-title">
        <div className="grid gap-10 lg:grid-cols-12">
          <h2 id="manifesto-title" className="text-quiet lg:col-span-3">
            From the manifesto
          </h2>
          <div className="lg:col-span-8">
            <blockquote>
              {manifesto.paragraphs.map((p) => (
                <p key={p} className="display display-s mb-8 max-w-[34ch] last:mb-0">
                  {p}
                </p>
              ))}
            </blockquote>
            <div className="mt-12">
              <ButtonLink href={manifesto.cta.href} tone="stone" variant="secondary">
                {manifesto.cta.label}
              </ButtonLink>
            </div>
          </div>
        </div>
      </Section>

      {/* 8. Final close */}
      <Section tone="night" space="loose" labelledBy="close-title">
        <div className="mx-auto max-w-4xl text-center">
          <Reveal>
            <h2 id="close-title" className="display display-l">
              {close.title}
            </h2>
          </Reveal>
          <p className="lede mx-auto mt-8 max-w-2xl text-mist">{close.text}</p>
          <div className="mt-12 flex flex-wrap justify-center gap-3">
            <ButtonLink href={close.primary.href}>{close.primary.label}</ButtonLink>
            <ButtonLink href={close.secondary.href} variant="secondary">
              {close.secondary.label}
            </ButtonLink>
          </div>
        </div>
      </Section>
    </>
  );
}
