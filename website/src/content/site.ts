// SPDX-License-Identifier: Apache-2.0
// One place for the institution’s identity. Change the name here and every page follows.

export const site = {
  /** The institution’s name. "[Institution]" until the owner decides it. */
  name: "[Institution]",
  belief: "Greatness should not be a privilege.",
  purpose: "Advance human potential.",
  signature: "Born in Bangladesh. Built for humanity.",
  description:
    "A human-advancement technology institution, born in Bangladesh and built for humanity. Our first invention is SenseBook, a screen-free AI learning companion for printed books.",
  /** Public repository of SenseBook’s open design files. */
  repoUrl: "https://github.com/916914/sensebook",
  /** Set NEXT_PUBLIC_CONTACT_EMAIL at build time (for example in Vercel). It is never committed to the repo. */
  contactEmail: process.env.NEXT_PUBLIC_CONTACT_EMAIL?.trim() || "",
  /** Public URL of the site once published, used for metadata. */
  url: process.env.NEXT_PUBLIC_SITE_URL?.trim() || "http://localhost:3000",
} as const;

export const nav = [
  { href: "/manifesto", label: "Manifesto" },
  { href: "/sensebook", label: "SenseBook" },
  { href: "/vision", label: "Vision" },
  { href: "/impact", label: "Impact" },
  { href: "/about", label: "About" },
  { href: "/contact", label: "Contact" },
] as const;
