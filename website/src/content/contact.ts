// SPDX-License-Identifier: CC-BY-4.0
// Contact. The address itself comes from NEXT_PUBLIC_CONTACT_EMAIL and is never committed.

export const contact = {
  label: "Contact",
  title: "Work with us.",
  lede: "We work with people and organisations who can help this institution do serious work well. If that is you, write to us and tell us plainly what you have in mind.",
  audiences: [
    { name: "Investors", subject: "Investment", text: "For those interested in backing an institution built for the long term, beginning with SenseBook." },
    { name: "Researchers", subject: "Research", text: "In learning, accessibility, computer vision, speech and human-computer interaction. We want our trials designed with people who know how to measure." },
    { name: "Institutions", subject: "Institutions", text: "Schools, universities, libraries and organisations of blind and low-vision readers who want to shape and test what we build." },
    { name: "Press", subject: "Press", text: "For interviews and accurate information about the institution and SenseBook." },
    { name: "Design collaborators", subject: "Design", text: "Industrial, interaction and type designers who care about objects that are calm, clear and lasting." },
    { name: "Engineers", subject: "Engineering", text: "Hardware, embedded and software engineers. SenseBook’s design files are public, and reading them is a good place to start." },
  ],
  reply: "We read every message, and reply where there is a clear way to work together.",
  missing: "Our contact address will be published here shortly.",
} as const;
