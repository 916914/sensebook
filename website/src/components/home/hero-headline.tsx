"use client";
// SPDX-License-Identifier: Apache-2.0
import { motion } from "framer-motion";

const ease = [0.22, 1, 0.36, 1] as const;

/**
 * The site's one orchestrated moment. The headline rises line by line, then a thin marigold
 * line passes under each line in turn, the way an eye (or SenseBook's camera) moves along
 * printed text, and settles as a short mark under the last line.
 *
 * Markup is identical on server and client. With "reduce motion" on, MotionConfig skips the
 * movement and CSS hides the travelling lines, so only the short mark remains.
 */
export function HeroHeadline({ lines, id }: { lines: readonly string[]; id?: string }) {
  const drawStart = 1.0;
  const drawTime = 0.85;

  return (
    <h1 id={id} className="display display-xl">
      {lines.map((line, i) => {
        const last = i === lines.length - 1;
        const start = drawStart + i * drawTime;
        return (
          <span key={line} className="block">
            <motion.span
              className="relative inline-block pb-[0.08em]"
              initial={{ opacity: 0, y: "0.35em" }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1.2, delay: 0.15 + i * 0.16, ease }}
            >
              {line}
              <motion.span
                aria-hidden="true"
                className="absolute bottom-0 left-0 h-[2px] w-full origin-left bg-marigold motion-reduce:hidden"
                initial={{ scaleX: 0, opacity: 1 }}
                animate={{ scaleX: [0, 1, 1], opacity: [1, 1, 0] }}
                transition={{ duration: drawTime + 0.5, delay: start, times: [0, 0.62, 1], ease: "easeInOut" }}
              />
              {last && (
                <motion.span
                  aria-hidden="true"
                  className="absolute bottom-0 left-0 h-[2px] w-12 origin-left bg-marigold motion-reduce:!transform-none"
                  initial={{ scaleX: 0 }}
                  animate={{ scaleX: 1 }}
                  transition={{ duration: 0.5, delay: start, ease }}
                />
              )}
            </motion.span>
          </span>
        );
      })}
    </h1>
  );
}
