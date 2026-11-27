// SPDX-License-Identifier: Apache-2.0
import { existsSync } from "node:fs";
import { join } from "node:path";
import Image from "next/image";
import { photoNote, photos, type PhotoId } from "@/content/photos";
import type { Tone } from "./section";

const EXTENSIONS = [".jpg", ".jpeg", ".png", ".webp"];

/** The saved picture for a slot (any common image type), or null if the owner has not added it yet. */
function findPhoto(name: string): string | null {
  for (const ext of EXTENSIONS) {
    if (existsSync(join(process.cwd(), "public", "photos", name + ext))) return `/photos/${name}${ext}`;
  }
  return null;
}

type Props = {
  id: PhotoId;
  sizes: string;
  /** CSS aspect ratio of the frame, e.g. "4 / 3". The picture is cropped to fill it. */
  aspect: string;
  position?: string;
  priority?: boolean;
  tone?: Tone;
  /** Show "Illustration. SenseBook is in development." under the picture. Off where a nearby line already says it. */
  caption?: boolean;
  className?: string;
};

/**
 * A picture of SenseBook in use, from public/photos/. Until the owner adds the file, a clearly
 * marked placeholder names the scene and the file name it is waiting for.
 */
export function PhotoFigure({ id, sizes, aspect, position = "50% 50%", priority, tone = "stone", caption = true, className = "" }: Props) {
  const p = photos[id];
  const src = findPhoto(p.name);

  return (
    <figure className={className}>
      <div className="relative overflow-hidden" style={{ aspectRatio: aspect }}>
        {src ? (
          <Image
            src={src}
            alt={p.alt}
            fill
            sizes={sizes}
            priority={priority}
            className="object-cover"
            style={{ objectPosition: position }}
          />
        ) : (
          <div
            role="img"
            aria-label={`Placeholder for a picture: ${p.scene}.`}
            className={`flex h-full w-full flex-col items-start justify-end gap-2 border border-dashed p-5 text-left text-sm ${
              tone === "night" ? "border-[#3a4547] bg-night-raised text-mist" : "border-[#c4c7c0] bg-stone-deep text-quiet"
            }`}
          >
            <span className={`font-medium ${tone === "night" ? "text-stone" : "text-ink"}`}>Picture to come</span>
            <span>{p.scene}.</span>
            <span className="text-xs opacity-80">photos/{p.name}.jpg</span>
          </div>
        )}
      </div>
      {src && caption && (
        <figcaption className={`mt-2 text-xs ${tone === "night" ? "text-mist" : "text-quiet"}`}>
          {photoNote}
        </figcaption>
      )}
    </figure>
  );
}
