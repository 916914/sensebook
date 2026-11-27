// SPDX-License-Identifier: Apache-2.0
import type { ReactNode } from "react";
import { Container } from "./container";
import { Reveal } from "./reveal";

type Props = {
  /** The page's name, shown small above the statement. */
  label: string;
  title: string;
  lede?: ReactNode;
  children?: ReactNode;
};

/** The opening of every inner page: the page's name, one statement, and a short lede. */
export function PageIntro({ label, title, lede, children }: Props) {
  return (
    <section aria-labelledby="page-title" className="bg-night text-stone">
      <Container className="pt-12 pb-20 sm:pt-16 sm:pb-28 lg:pt-20 lg:pb-36">
        <p className="text-mist">{label}</p>
        <Reveal>
          <h1 id="page-title" className="display display-xl mt-5 max-w-[16ch]">
            {title}
          </h1>
        </Reveal>
        <span aria-hidden="true" className="mt-10 block h-[2px] w-12 bg-marigold" />
        {lede && (
          <div className="mt-10 grid lg:grid-cols-12">
            <div className="lede text-mist lg:col-span-7 lg:col-start-6">{lede}</div>
          </div>
        )}
        {children}
      </Container>
    </section>
  );
}
