"use client";
// SPDX-License-Identifier: Apache-2.0
import { MotionConfig } from "framer-motion";
import type { ReactNode } from "react";

/** Every animation on the site honours the visitor's "reduce motion" setting. */
export function MotionProvider({ children }: { children: ReactNode }) {
  return (
    <MotionConfig reducedMotion="user" transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}>
      {children}
    </MotionConfig>
  );
}
