// SPDX-License-Identifier: Apache-2.0
import Link from "next/link";
import { nav, site } from "@/content/site";
import { Container } from "./container";
import { Wordmark } from "./wordmark";

export function SiteFooter() {
  return (
    <footer className="border-t border-graphite bg-night text-stone">
      <Container className="grid gap-14 py-16 sm:py-20 lg:grid-cols-12 lg:gap-8">
        <div className="lg:col-span-5">
          <Link href="/" className="inline-block rounded-sm" aria-label={`${site.name}, home`}>
            <Wordmark />
          </Link>
          <p className="mt-6 max-w-xs font-display text-2xl leading-snug font-light text-stone">{site.signature}</p>
        </div>

        <nav aria-label="Footer" className="lg:col-span-3">
          <ul className="grid grid-cols-2 gap-x-8 gap-y-3 text-[0.9375rem] lg:grid-cols-1">
            {nav.map((item) => (
              <li key={item.href}>
                <Link href={item.href} className="text-mist transition-colors duration-300 hover:text-stone">
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        <div className="text-[0.9375rem] leading-relaxed text-mist lg:col-span-4">
          <p>For investors, researchers, institutions, press, designers and engineers who want to work with us.</p>
          <p className="mt-4">
            <Link href="/contact" className="link-draw text-stone">
              Contact us
            </Link>
          </p>
        </div>
      </Container>
      <Container className="flex flex-col gap-2 border-t border-graphite py-8 text-sm text-dim sm:flex-row sm:justify-between">
        <p>
          &copy; 2026 {site.name}
        </p>
        <p>{site.belief}</p>
      </Container>
    </footer>
  );
}
