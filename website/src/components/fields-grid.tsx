// SPDX-License-Identifier: Apache-2.0
import { fields, fieldsIntro } from "@/content/fields";

/**
 * The five fields of work, side by side on wide screens. Rows line up across columns
 * (name, description, programmes) with CSS subgrid. Proposed programmes are named only;
 * SenseBook carries its real status.
 */
export function FieldsGrid({ headingLevel = "h3" }: { headingLevel?: "h2" | "h3" }) {
  const Heading = headingLevel;
  const Item = headingLevel === "h2" ? "h3" : "h4";
  return (
    <div>
      <Heading className="text-mist">{fieldsIntro.title}</Heading>
      <ul className="mt-6 grid border-t border-graphite md:grid-cols-2 lg:grid-cols-5 lg:grid-rows-[auto_auto_1fr]">
        {fields.map((f) => (
          <li
            key={f.name}
            className="border-b border-graphite py-8 md:odd:pr-8 md:even:border-l md:even:pl-8 lg:row-span-3 lg:grid lg:grid-rows-subgrid lg:border-b-0 lg:px-6 lg:py-10 lg:odd:pr-6 lg:even:pl-6 lg:[&:not(:first-child)]:border-l lg:first:pl-0"
          >
            <Item className="font-display text-[1.75rem] leading-[1.1] font-light tracking-[-0.015em] text-stone">{f.name}</Item>
            <p className="mt-4 text-[0.9375rem] leading-relaxed text-mist">{f.text}</p>
            <div className="mt-8 lg:mt-10">
              <p className="text-sm text-dim">Programmes</p>
              <ul className="mt-3 space-y-2 text-[0.9375rem]">
                {f.programmes.map((p) => (
                  <li key={p.name} className="flex flex-wrap items-center gap-x-2.5">
                    {p.status ? (
                      <>
                        <span aria-hidden="true" className="h-2 w-2 rounded-full bg-marigold" />
                        <span className="font-medium text-stone">{p.name}</span>
                        <span className="text-sm text-marigold">{p.status}</span>
                      </>
                    ) : (
                      <>
                        <span aria-hidden="true" className="h-2 w-2 rounded-full ring-1 ring-dim ring-inset" />
                        <span className="text-mist">{p.name}</span>
                        <span className="sr-only">(proposed)</span>
                      </>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          </li>
        ))}
      </ul>
      <p className="mt-8 flex flex-wrap items-center gap-x-5 gap-y-2 text-sm text-dim">
        <span className="inline-flex items-center gap-2.5">
          <span aria-hidden="true" className="h-2 w-2 rounded-full bg-marigold" />
          In development
        </span>
        <span className="inline-flex items-center gap-2.5">
          <span aria-hidden="true" className="h-2 w-2 rounded-full ring-1 ring-dim ring-inset" />
          Proposed, not yet built
        </span>
      </p>
    </div>
  );
}
