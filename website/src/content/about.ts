// SPDX-License-Identifier: CC-BY-4.0
// About the institution. New text for the owner’s review. No people are named until the owner decides.

export const about = {
  label: "About",
  title: "An institution for human potential.",
  lede: "is a technology institution, born in Bangladesh, dedicated to advancing human potential. We invent, design and engineer the technologies that do it. SenseBook is our first invention.",
  beliefs: {
    title: "What we believe",
    items: [
      "Greatness should not be a privilege.",
      "Most unrealised potential is lost to circumstance, not to a lack of ability.",
      "Technology should add to what people can do, not only to how quickly they can consume.",
      "Where something is invented shapes who it is invented for.",
    ],
  },
  problems: {
    title: "The problems we choose",
    lede: "We will say no to most good ideas. A problem becomes ours when it meets all four tests.",
    items: [
      { name: "Real and widely shared", text: "A barrier that limits the learning, independence or opportunity of many people, in Bangladesh and far beyond it." },
      { name: "Answerable with technology", text: "A problem where a well-made tool, and not only policy or money, can change the outcome." },
      { name: "Worth owning", text: "The answer must be something people want, not only something they need. Desirable things get used." },
      { name: "Ours to do well", text: "A problem where our knowledge, our place and our way of working give us a real advantage." },
    ],
  },
  values: {
    title: "Values",
    items: [
      { name: "Rigour", text: "We say what we know, mark what we estimate, and test what we claim." },
      { name: "Dignity", text: "We design for people as capable adults and curious children, never as cases." },
      { name: "Openness", text: "Our designs are published under open licences, so others can check, repair and improve them." },
      { name: "Craft", text: "A tool for learning deserves the care of a well-made book." },
      { name: "Patience", text: "We choose problems worth decades, and we do not rush what should be done properly." },
    ],
  },
  philosophy: {
    title: "How we design and engineer",
    items: [
      { name: "Start from the person", text: "We begin with what someone is trying to do, and only then choose the technology." },
      { name: "Let the object disappear into the task", text: "The best tool is the one you stop noticing. SenseBook has no screen because the book is the point." },
      { name: "Physical where it matters", text: "Controls you can feel, switches you can trust, objects that are calm to live with." },
      { name: "Design for the hardest case first", text: "A product that works fully without sight works better for everyone." },
      { name: "Make it to last", text: "Parts that can be replaced, files that can be read, and designs that others can repair." },
    ],
  },
} as const;
