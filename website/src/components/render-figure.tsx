// SPDX-License-Identifier: Apache-2.0
import { existsSync } from "node:fs";
import { join } from "node:path";
import Image from "next/image";
import { renderNote, renderSrc, renders, type RenderId } from "@/content/renders";
import { Parallax } from "./parallax";
import type { Tone } from "./section";

type Props = {
  id: RenderId;
  sizes: string;
  priority?: boolean;
  /** Crop to this aspect ratio (CSS value, e.g. "16 / 9"). Defaults to the render's own. */
  aspect?: string;
  /** Where in the image to anchor a crop. */
  position?: string;
  parallax?: number;
  tone?: Tone;
  caption?: boolean | string;
  /** Add "Render of the prototype design…" to the caption. Off where the page already says so once. */
  note?: boolean;
  className?: string;
  imageClassName?: string;
};

/** True when the build chat's render has been copied into public/design (see scripts/sync-design.mjs). */
export function renderExists(id: RenderId) {
  return existsSync(join(process.cwd(), "public", "design", "renders", renders[id].file));
}

export function RenderFigure({
  id,
  sizes,
  priority,
  aspect,
  position = "50% 50%",
  parallax,
  tone = "stone",
  caption = true,
  note = true,
  className = "",
  imageClassName = "",
}: Props) {
  const r = renders[id];
  /** "fill" makes the picture fill its parent's height instead of keeping a ratio. */
  const fill = aspect === "fill";
  const ratio = fill ? undefined : (aspect ?? `${r.width} / ${r.height}`);
  const present = renderExists(id);
  const captionText = typeof caption === "string" ? caption : r.caption;

  const image = present ? (
    <Image
      src={renderSrc(id)}
      alt={r.alt}
      width={r.width}
      height={r.height}
      sizes={sizes}
      priority={priority}
      className={`h-full w-full object-cover ${imageClassName}`}
      style={{ objectPosition: position }}
    />
  ) : (
    <Placeholder label={r.file} tone={tone} />
  );

  return (
    <figure className={className}>
      <div className={`relative overflow-hidden ${fill ? "h-full" : ""}`} style={ratio ? { aspectRatio: ratio } : undefined}>
        {parallax && present ? <Parallax strength={parallax} className="h-full w-full">{image}</Parallax> : image}
      </div>
      {caption !== false && (
        <figcaption className={`mt-4 max-w-2xl text-sm leading-relaxed ${tone === "night" ? "text-dim" : "text-quiet"}`}>
          {captionText}
          {note && <> {renderNote}</>}
        </figcaption>
      )}
    </figure>
  );
}

/** Shown, clearly marked, when a build-chat render is not available yet. */
function Placeholder({ label, tone }: { label: string; tone: Tone }) {
  return (
    <div
      role="img"
      aria-label={`Placeholder: SenseBook render ${label} is not available yet.`}
      className={`flex h-full w-full items-center justify-center border border-dashed p-6 text-center text-sm ${
        tone === "night" ? "border-graphite bg-night-raised text-mist" : "border-rule bg-stone-deep text-quiet"
      }`}
    >
      <span>
        Placeholder. Render <code className="font-sans font-medium">{label}</code> from the build chat goes here.
      </span>
    </div>
  );
}
