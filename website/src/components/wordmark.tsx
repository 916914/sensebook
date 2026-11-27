// SPDX-License-Identifier: Apache-2.0
import { site } from "@/content/site";

/** The institution's name with its mark: a short marigold reading line. */
export function Wordmark({ className = "" }: { className?: string }) {
  return (
    <span className={`inline-flex items-baseline gap-3 ${className}`}>
      <span aria-hidden="true" className="inline-block h-[2px] w-5 translate-y-[-0.3em] bg-marigold" />
      <span className="font-display text-[1.375rem] leading-none font-normal tracking-[-0.01em]">{site.name}</span>
    </span>
  );
}
