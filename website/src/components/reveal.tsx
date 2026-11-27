"use client";
// SPDX-License-Identifier: Apache-2.0
import { motion } from "framer-motion";
import type { ReactNode } from "react";

type Props = {
  children: ReactNode;
  className?: string;
  delay?: number;
  as?: "div" | "p" | "li";
};

/**
 * A single, soft rise into view, once. Used for section headings and key statements only,
 * not for every block. With "reduce motion" on, content simply appears.
 */
export function Reveal({ children, className, delay = 0, as = "div" }: Props) {
  const M = motion[as];
  return (
    <M
      className={className}
      initial={{ opacity: 0, y: 18 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "0px 0px -12% 0px" }}
      transition={{ duration: 1.1, delay, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </M>
  );
}
