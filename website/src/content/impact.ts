// SPDX-License-Identifier: CC-BY-4.0
// Impact: intentions, not results. Nothing here has been measured yet.

export const impact = {
  label: "Impact",
  title: "Here is how we intend to matter.",
  lede: "We will judge our work by the barriers it removes, not by the attention it receives. This page sets out the barriers we have chosen and what we intend to measure. None of it has been measured yet: SenseBook is still in development.",
  areas: [
    {
      name: "Education",
      barrier: "Whether a student understands a text often depends on whether someone is there to explain it.",
      measure: "Understanding of the same material with and without SenseBook, and how often learners keep reading on their own.",
    },
    {
      name: "Accessibility",
      barrier: "Most printed material still needs sight, or a sighted helper, to be read.",
      measure: "How much of their daily reading blind and low-vision readers can do alone, and how long it takes to go from a closed book to the right page.",
    },
    {
      name: "Intellectual independence",
      barrier: "Questions go unasked when asking is slow, public or embarrassing.",
      measure: "How many questions readers ask, of what kind, and whether their confidence with difficult material grows over time.",
    },
    {
      name: "Bangladeshi capability",
      barrier: "Advanced hardware is mostly designed and made elsewhere, so the skills to build it gather elsewhere too.",
      measure: "The share of design, engineering and assembly done in Bangladesh, and the number of people who gain those skills through our work.",
    },
    {
      name: "Global human impact",
      barrier: "Learning and assistive technologies are usually built first for the richest markets, and priced for them.",
      measure: "Where our inventions are used, in which languages, and what they cost compared with local incomes.",
    },
  ],
  principles: {
    title: "How we will hold ourselves to it",
    items: [
      { name: "Reach is not impact", text: "A device that is owned but not used has changed nothing. We will count use and outcomes, not units." },
      { name: "Publish the method", text: "We intend to publish how we measure and what we find, including what does not work." },
      { name: "Ask the people it is for", text: "Students, teachers and blind and low-vision readers will shape the trials, not only take part in them." },
    ],
  },
} as const;
