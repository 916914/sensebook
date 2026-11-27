"use client";
// SPDX-License-Identifier: Apache-2.0
import { motion, useScroll, useTransform } from "framer-motion";
import { useRef, type ReactNode } from "react";

/**
 * The wide hero picture: settles from a slight scale on load, then drifts gently with the scroll.
 * With "reduce motion" on, CSS removes the movement (same markup on server and client).
 */
export function HeroStage({ children, className = "" }: { children: ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });
  const y = useTransform(scrollYProgress, [0, 1], ["-5%", "5%"]);

  return (
    <div ref={ref} className={`relative overflow-hidden ${className}`}>
      <motion.div
        className="h-full w-full motion-reduce:!transform-none"
        style={{ y }}
        initial={{ scale: 1.12, opacity: 0 }}
        animate={{ scale: 1.1, opacity: 1 }}
        transition={{ duration: 2.4, delay: 0.3, ease: [0.22, 1, 0.36, 1] }}
      >
        {children}
      </motion.div>
      {/* Lets the picture rise out of the slate night above it. */}
      <div aria-hidden="true" className="pointer-events-none absolute inset-x-0 -top-px h-1/4 bg-gradient-to-b from-night via-night/40 to-transparent" />
    </div>
  );
}
