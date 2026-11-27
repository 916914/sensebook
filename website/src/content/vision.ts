// SPDX-License-Identifier: CC-BY-4.0
// Vision: three pillars and the kinds of invention each leads to. Categories, not products.

export const vision = {
  label: "Vision",
  title: "Larger than one invention.",
  lede: "SenseBook is our first invention. It will not be our last. Our work is organised around three pillars, each a part of human potential that technology can widen. Under each are the kinds of invention we intend to pursue. They are directions, not products we have built.",
  pillars: [
    {
      name: "Human Intelligence",
      statement: "Technologies that deepen how people learn, reason and understand.",
      categories: [
        { name: "Instruments of understanding", text: "Tools that explain rather than only retrieve, so people grasp why something is true and not just what to remember." },
        { name: "Learning that meets the learner", text: "Guidance that adapts to a person’s pace, level and language, in the places they already learn." },
        { name: "Tools for thinking", text: "Aids that help people test an argument, check a step or weigh evidence, without doing the thinking for them." },
      ],
      sensebook: "SenseBook brings explanation to the page a reader is already on.",
    },
    {
      name: "Human Independence",
      statement: "Technologies that let people do for themselves what circumstance or disability has made them depend on others to do.",
      categories: [
        { name: "Access to the printed and visual world", text: "Books, documents, signs and labels that today require sight, or someone else’s." },
        { name: "Everyday autonomy", text: "Tools that help people find their way, manage their affairs and make decisions on their own terms." },
        { name: "Assistive technology people want to own", text: "Products designed as desirable objects for everyone, so independence never comes with a stigma." },
      ],
      sensebook: "SenseBook reads print aloud and is operated entirely by touch and voice.",
    },
    {
      name: "Human Opportunity",
      statement: "Technologies that widen access to the skills, tools and work through which people shape their own lives.",
      categories: [
        { name: "Skills at the point of work", text: "Guidance that helps people learn a trade or a technique while they practise it." },
        { name: "Knowledge across languages", text: "Bringing what is written in a few languages within reach of people who read in many others." },
        { name: "Capability that stays", text: "Designing, engineering and making advanced technology in Bangladesh, so the skills to build it grow where they are needed." },
      ],
      sensebook: "SenseBook’s design is open, so others can learn from it, repair it and build on it.",
    },
  ],
  close: {
    title: "One invention at a time, done properly.",
    text: "We will not announce products we have not built. Each new invention will begin the way SenseBook did: with a real barrier, a clear idea of who it is for, and work that can be checked.",
  },
} as const;
