// SPDX-License-Identifier: Apache-2.0
import type { ReactNode } from "react";
import { Container } from "./container";

export type Tone = "night" | "stone";

const tones: Record<Tone, string> = {
  night: "bg-night text-stone",
  stone: "bg-stone text-ink",
};

type Props = {
  tone?: Tone;
  id?: string;
  /** Accessible name for the section, usually the id of its heading. */
  labelledBy?: string;
  className?: string;
  /** Vertical rhythm. "loose" for single statements, "normal" for content. */
  space?: "loose" | "normal" | "tight" | "none";
  contained?: boolean;
  children: ReactNode;
};

const spaces = {
  loose: "py-28 sm:py-36 lg:py-48",
  normal: "py-20 sm:py-28 lg:py-36",
  tight: "py-14 sm:py-20",
  none: "",
};

export function Section({ tone = "night", id, labelledBy, className = "", space = "normal", contained = true, children }: Props) {
  return (
    <section id={id} aria-labelledby={labelledBy} data-tone={tone} className={`${tones[tone]} ${spaces[space]} ${className}`}>
      {contained ? <Container>{children}</Container> : children}
    </section>
  );
}
