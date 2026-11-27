"use client";
// SPDX-License-Identifier: Apache-2.0
import { motion, useScroll, useTransform } from "framer-motion";
import { useRef, type ReactNode } from "react";

/**
 * Restrained parallax: the content drifts a few percent against the scroll while its
 * frame stays put. With "reduce motion" on, CSS removes the movement.
 */
export function Parallax({ children, className = "", strength = 6 }: { children: ReactNode; className?: string; strength?: number }) {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] });
  const y = useTransform(scrollYProgress, [0, 1], [`-${strength}%`, `${strength}%`]);

  return (
    <div ref={ref} className={`overflow-hidden ${className}`}>
      <motion.div style={{ y, scale: 1 + (strength * 2.2) / 100 }} className="h-full w-full motion-reduce:!transform-none">
        {children}
      </motion.div>
    </div>
  );
}
