// SPDX-License-Identifier: Apache-2.0
import type { Metadata } from "next";
import { PageIntro } from "@/components/page-intro";
import { Section } from "@/components/section";
import { contact } from "@/content/contact";
import { site } from "@/content/site";

export const metadata: Metadata = {
  title: "Contact",
  description: "For investors, researchers, institutions, press, design collaborators and engineers.",
};

const mailto = (subject: string) => `mailto:${site.contactEmail}?subject=${encodeURIComponent(`${subject}: ${site.name}`)}`;

export default function ContactPage() {
  const email = site.contactEmail;
  return (
    <>
      <PageIntro label={contact.label} title={contact.title} lede={<p>{contact.lede}</p>}>
        <div className="mt-14 grid lg:grid-cols-12">
          <div className="lg:col-span-7 lg:col-start-6">
            {email ? (
              <a href={`mailto:${email}`} className="link-draw font-display text-[clamp(1.5rem,1.1rem+1.6vw,2.5rem)] font-light break-all text-stone">
                {email}
              </a>
            ) : (
              <p className="rounded-sm border border-dashed border-graphite px-5 py-4 text-mist">{contact.missing}</p>
            )}
            <p className="mt-5 text-sm text-dim">{contact.reply}</p>
          </div>
        </div>
      </PageIntro>

      <Section tone="stone" labelledBy="who-title">
        <h2 id="who-title" className="display display-m max-w-[18ch]">
          Who we want to hear from
        </h2>
        <ul className="mt-14 grid gap-x-10 gap-y-12 sm:grid-cols-2 lg:mt-20 lg:grid-cols-3">
          {contact.audiences.map((a) => (
            <li key={a.name} className="flex flex-col border-t border-ink/80 pt-6">
              <h3 className="text-lg font-semibold">{a.name}</h3>
              <p className="mt-2 flex-1 text-quiet">{a.text}</p>
              <p className="mt-5 flex flex-wrap gap-x-6 gap-y-2">
                {email && (
                  <a href={mailto(a.subject)} className="link-draw text-[0.9375rem] font-medium">
                    Write about {a.subject.toLowerCase()}
                  </a>
                )}
              </p>
            </li>
          ))}
        </ul>
      </Section>
    </>
  );
}
