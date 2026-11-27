"use client";
// SPDX-License-Identifier: Apache-2.0
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useId, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { nav, site } from "@/content/site";
import { Container } from "./container";
import { Wordmark } from "./wordmark";

export function SiteHeader() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const menuId = useId();

  // Close the menu on Escape (links close it themselves when chosen).
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  const isActive = (href: string) => pathname === href || pathname.startsWith(`${href}/`);

  return (
    <header className="relative z-40 bg-night text-stone">
      <Container className="flex h-20 items-center justify-between gap-6 lg:h-24">
        <Link href="/" className="rounded-sm py-2" aria-label={`${site.name}, home`}>
          <Wordmark />
        </Link>

        <nav aria-label="Main" className="hidden md:block">
          <ul className="flex items-center gap-7 text-[0.9375rem] lg:gap-9">
            {nav.map((item) => (
              <li key={item.href}>
                <Link
                  href={item.href}
                  aria-current={isActive(item.href) ? "page" : undefined}
                  className="relative py-2 text-mist transition-colors duration-300 hover:text-stone aria-[current=page]:text-stone"
                >
                  {item.label}
                  {isActive(item.href) && (
                    <span aria-hidden="true" className="absolute -bottom-0.5 left-0 h-[2px] w-full bg-marigold" />
                  )}
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        <button
          type="button"
          className="-mr-2 flex h-11 items-center gap-3 rounded-sm px-2 text-[0.9375rem] text-stone md:hidden"
          aria-expanded={open}
          aria-controls={menuId}
          onClick={() => setOpen((v) => !v)}
        >
          <span>{open ? "Close" : "Menu"}</span>
          <span aria-hidden="true" className="relative block h-3 w-6">
            <span
              className={`absolute left-0 h-[1.5px] w-6 bg-current transition-transform duration-300 ${open ? "top-1.5 rotate-45" : "top-0"}`}
            />
            <span
              className={`absolute left-0 h-[1.5px] w-6 bg-current transition-transform duration-300 ${open ? "top-1.5 -rotate-45" : "top-3"}`}
            />
          </span>
        </button>
      </Container>

      <AnimatePresence>
        {open && (
          <motion.nav
            id={menuId}
            aria-label="Main"
            className="absolute inset-x-0 top-full border-t border-graphite bg-night md:hidden"
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.35 }}
          >
            <Container className="pt-6 pb-10">
              <ul className="flex flex-col">
                <li>
                  <Link
                    href="/"
                    onClick={() => setOpen(false)}
                    className="block border-b border-graphite py-4 font-display text-3xl font-light"
                    aria-current={pathname === "/" ? "page" : undefined}
                  >
                    Home
                  </Link>
                </li>
                {nav.map((item) => (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      onClick={() => setOpen(false)}
                      aria-current={isActive(item.href) ? "page" : undefined}
                      className="flex items-center justify-between border-b border-graphite py-4 font-display text-3xl font-light"
                    >
                      {item.label}
                      {isActive(item.href) && <span aria-hidden="true" className="h-[2px] w-6 bg-marigold" />}
                    </Link>
                  </li>
                ))}
              </ul>
            </Container>
          </motion.nav>
        )}
      </AnimatePresence>
    </header>
  );
}
