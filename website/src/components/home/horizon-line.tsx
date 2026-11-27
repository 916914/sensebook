"use client";
// SPDX-License-Identifier: Apache-2.0
import { motion, useScroll, useSpring, useTransform } from "framer-motion";
import { useRef } from "react";

/**
 * A single line across the page that fills from left to right as the section passes:
 * from here, outward. Shown full and still when "reduce motion" is on.
 */
export function HorizonLine() {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start 90%", "start 35%"] });
  const scaleX = useSpring(useTransform(scrollYProgress, [0, 1], [0.04, 1]), { stiffness: 80, damping: 30 });

  return (
    <div ref={ref} aria-hidden="true" className="relative h-px w-full bg-graphite">
      <motion.div className="absolute inset-y-0 left-0 w-full origin-left bg-marigold motion-reduce:!transform-none" style={{ scaleX }} />
    </div>
  );
}
