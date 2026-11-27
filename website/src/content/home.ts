// SPDX-License-Identifier: CC-BY-4.0
// Homepage copy. Approved structure and lines from the owner’s brief; see docs/02-homepage-copy.md.

export const home = {
  hero: {
    headline: ["Greatness should", "not be a privilege."],
    text: "Humanity’s greatest untapped resource is human potential. We are building an institution dedicated to advancing it through meaningful technology.",
    secondary: "Our first invention, SenseBook, transforms books into conversational learning experiences.",
    primary: { label: "Discover our mission", href: "/manifesto" },
    secondaryCta: { label: "Explore SenseBook", href: "/sensebook" },
  },
  core: {
    lines: [
      "A child’s future should not be limited by circumstance.",
      "A person’s potential should not be diminished by disability.",
      "A nation’s ambition should not be confined to consuming technologies created elsewhere.",
    ],
    close: "We exist to remove barriers between people and what they are capable of becoming.",
  },
  firstChapter: {
    title: "SenseBook",
    subtitle: "The first invention in our mission to expand human potential.",
    text: "SenseBook transforms physical books into conversational learning experiences, helping people understand, question and explore knowledge more deeply.",
    detail: "It clips onto a printed book, reads the page, and answers questions aloud. There is no screen to look at, only the book.",
    status: "In development. Images are renders of the current prototype design.",
    cta: { label: "Explore SenseBook", href: "/sensebook" },
  },
  why: {
    title: "Understanding should not depend on who is in the room.",
    people: [
      {
        name: "The student seeking understanding",
        text: "A lesson moves on before an idea has landed. With SenseBook, a student can ask about the paragraph in front of them and hear it explained again, another way, for as long as it takes.",
      },
      {
        name: "The university learner exploring complex ideas",
        text: "Difficult texts reward questions. A reader can stop at a hard passage, test their reading of it, and follow a thought further than the page goes.",
      },
      {
        name: "The blind reader pursuing independence",
        text: "Print should not require a second pair of eyes. SenseBook reads the page aloud and answers questions about it, with physical controls made to be used by touch.",
      },
      {
        name: "The lifelong learner expanding capability",
        text: "Curiosity does not end with school. For someone learning a new field or a new trade, any book on the shelf can become a patient conversation.",
      },
    ],
  },
  institution: {
    title: "One invention. A much larger purpose.",
    text: "SenseBook is our first step. Our ambition extends further: to build technologies that expand learning, independence and opportunity.",
    pillars: [
      { name: "Human Intelligence", text: "Technologies that deepen how people learn, reason and understand." },
      {
        name: "Human Independence",
        text: "Technologies that let people do for themselves what circumstance or disability has made them depend on others to do.",
      },
      {
        name: "Human Opportunity",
        text: "Technologies that widen access to the skills, tools and work through which people shape their own lives.",
      },
    ],
    cta: { label: "See our vision", href: "/vision" },
  },
  bangladesh: {
    title: ["Born in Bangladesh.", "Built for humanity."],
    text: "We believe Bangladesh can become a birthplace of globally meaningful technological innovation. Our journey begins here, but our ambition is for the world.",
  },
  manifesto: {
    paragraphs: [
      "Every generation leaves talent unused. Not because the talent was absent, but because the conditions to develop it were: a teacher who was not there, a page that could not be read, a tool designed for someone else.",
      "We do not treat these as misfortunes. We treat them as design problems. And design problems can be solved.",
    ],
    cta: { label: "Read the manifesto", href: "/manifesto" },
  },
  close: {
    title: "We are building for what humanity can become.",
    text: "If you believe technology should expand human possibility, not merely accelerate convenience, we invite you to follow our journey.",
    primary: { label: "Explore SenseBook", href: "/sensebook" },
    secondary: { label: "Contact us", href: "/contact" },
  },
} as const;
