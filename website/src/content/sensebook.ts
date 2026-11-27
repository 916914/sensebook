// SPDX-License-Identifier: CC-BY-4.0
// SenseBook page copy. Product facts follow the build chat’s design (sensebook/design/) and are
// described as design intent: nothing has been built or tested yet.

export const sensebook = {
  hero: {
    title: "SenseBook",
    subtitle: "A screen-free AI learning companion for printed books.",
    text: "It clips onto a book, sees the page, and answers your questions aloud. The book stays at the centre.",
    status: "In development. Every image on this page is a render of the current prototype design, made from its open CAD model.",
  },
  whatItIs: {
    title: "What it is",
    paragraphs: [
      "SenseBook is a small companion that sits above an open book. A camera looks down at both pages. Press the Ask button, ask a question aloud, and it answers in speech: what a word means, how one step follows from another, what a passage is really saying. It can also read the page aloud.",
      "There is no screen and nothing to scroll. You keep reading the book you already have, and you are never on your own with a page you cannot get past.",
    ],
  },
  howItWorks: {
    title: "How it works",
    steps: [
      {
        name: "Clip it on",
        text: "Squeeze the grip, slide its two thin blades inside the covers beside the spine, and let go. A spring holds the book lightly, from a thin booklet to a thick hardcover.",
      },
      {
        name: "Open to any page",
        text: "The lens sits above the top edge of the book and looks down at both pages. Pages turn freely in front of it.",
      },
      {
        name: "Ask",
        text: "Press the raised marigold Ask button and ask your question in your own words.",
      },
      {
        name: "Listen, and ask again",
        text: "SenseBook answers in speech, through its speaker or your headphones. Simple buttons let you pause, go back and go on.",
      },
    ],
    contexts: "The same grip works on a desk, in the hands, or standing on its own over a letter or a loose sheet. For small print, the stick extends.",
    note: "These steps describe the prototype design. They have not yet been tested with readers.",
  },
  whoItServes: {
    title: "Who it serves",
    groups: [
      { name: "School students", text: "Help with the textbook in front of them, at the moment they are stuck, without waiting for the next lesson." },
      { name: "University learners", text: "A way to question dense texts, check their reading, and go further than the page." },
      { name: "Blind and low-vision readers", text: "Printed books read aloud and explained on request, with controls made for touch." },
      { name: "Lifelong learners", text: "Any book on the shelf becomes a patient conversation, at any age." },
    ],
  },
  conversational: {
    title: "Conversational learning",
    paragraphs: [
      "Reading is where most learning begins, and where much of it stalls. A reader meets a word, a step or an argument they cannot get past, and there is no one to ask.",
      "SenseBook makes the question possible at the moment it arises. It starts from the page in front of the reader, so the conversation stays with the book instead of drifting away from it. Asking is how people learn. SenseBook is designed to make asking easy, private and patient.",
    ],
  },
  accessibility: {
    title: "Accessibility by design",
    lede: "SenseBook is not a disability device with a mainstream version. It is one product, designed from the start to work fully without sight.",
    points: [
      { name: "Controls you can feel", text: "Every control is a physical button with its own shape. The Ask button is the largest, round and raised." },
      { name: "Attaches by touch", text: "Find the spine, slide the blades in, let go. There is nothing to line up by eye." },
      { name: "Tells you what it sees", text: "Spoken status and a short vibration confirm that it is attached and which pages it can see." },
      { name: "Private when you want it", text: "A headphone socket for listening alone, and a physical switch that turns the microphones off." },
    ],
  },
  physicalAi: {
    title: "Why physical AI matters",
    paragraphs: [
      "Most AI lives behind a screen, and screens compete for attention. A book does not. SenseBook brings intelligence to the object people already learn from, instead of moving learning onto another device.",
      "A dedicated object is also easier to trust and easier to use. It does one thing. It is there when you reach for it. And you can feel, with a switch under your finger, whether it is listening.",
    ],
  },
  visuals: {
    title: "The design",
    text: "SenseBook is designed in the open. The renders below come straight from its CAD model, which anyone can download, inspect and build from.",
    modelTitle: "Turn it. Pull it apart.",
    modelText: "The full CAD model of the prototype: every part of the unit and the grip. Drag to turn it, use the slider to pull it apart, and select a part to name it.",
    modelNote: "This is the CAD model, not a photograph. Bought parts are drawn at typical sizes, and nothing has been built or tested yet.",
  },
  open: {
    title: "Designed in the open",
    text: "SenseBook’s software is published under Apache-2.0, its hardware under CERN-OHL-W-2.0, and its documents and images under CC BY 4.0. Engineers, researchers and readers can check our work, repair what they own, and improve on it.",
    cta: "SenseBook’s design files on GitHub",
  },
  roadmap: {
    title: "The road ahead",
    lede: "Each stage begins only when the one before it is done well. We do not publish dates we cannot keep.",
    stages: [
      { name: "Prototype design", text: "A complete CAD model, parts list and assembly guide, published openly.", now: true },
      { name: "First working units", text: "Hand-built from the parts list and tested on real books." },
      { name: "Reader trials", text: "With school students, university learners and blind and low-vision readers, measured against what we set out to change." },
      { name: "Ready to make", text: "Refined for cost, durability and manufacture." },
      { name: "In readers’ hands", text: "SenseBook available to the people it was designed for." },
    ],
  },
} as const;
