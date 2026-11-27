// SPDX-License-Identifier: Apache-2.0
import Link from "next/link";
import type { ReactNode } from "react";
import type { Tone } from "./section";

type Props = {
  href: string;
  children: ReactNode;
  variant?: "primary" | "secondary";
  /** The background the button sits on. */
  tone?: Tone;
  className?: string;
};

const styles: Record<Tone, Record<"primary" | "secondary", string>> = {
  night: {
    primary: "bg-marigold text-night hover:bg-[#ecb45a]",
    secondary: "text-stone ring-1 ring-inset ring-[#45514f] hover:ring-stone",
  },
  stone: {
    primary: "bg-ink text-stone hover:bg-[#2c3739]",
    secondary: "text-ink ring-1 ring-inset ring-[#b9bcb5] hover:ring-ink",
  },
};

export function ButtonLink({ href, children, variant = "primary", tone = "night", className = "" }: Props) {
  const external = /^(https?:|mailto:)/.test(href);
  const cls = `inline-flex min-h-12 items-center justify-center rounded-full px-6 text-[0.9375rem] font-medium tracking-[-0.005em] transition-[background-color,box-shadow,color] duration-300 ${styles[tone][variant]} ${className}`;
  return external ? (
    <a href={href} className={cls} rel={href.startsWith("http") ? "noopener" : undefined}>
      {children}
    </a>
  ) : (
    <Link href={href} className={cls}>
      {children}
    </Link>
  );
}

/** A plain text link with a drawn underline, for inline "read more" moments. */
export function TextLink({ href, children, className = "" }: { href: string; children: ReactNode; className?: string }) {
  return (
    <Link href={href} className={`link-draw inline-block text-[1.0625rem] font-medium ${className}`}>
      {children}
    </Link>
  );
}
