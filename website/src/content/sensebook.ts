// SPDX-License-Identifier: CC-BY-4.0
// SenseBook page copy. Product facts follow the build chat’s design (sensebook/design/) and are
// described as design intent: nothing has been built or tested yet.

export const sensebook = {
  hero: {
    title: "SenseBook",
    subtitle: "A screen-free AI learning companion.",
    text: "It clips onto any printed book, sees the page, and answers your questions aloud. The book stays at the centre, and the same device serves every reader.",
    primary: { label: "See how it works", href: "#how" },
    secondary: { label: "Who it serves", href: "#lives" },
    facts: [
      { name: "Clips onto any printed book", text: "A light spring grip holds anything from a thin booklet to a thick hardcover." },
      { name: "Reads the page aloud", text: "A camera above the book sees both open pages at once." },
      { name: "Answers your questions", text: "Press the marigold Ask button and talk about what you are reading." },
      { name: "No screen. Works without sight.", text: "Physical buttons, spoken feedback and a headphone socket." },
    ],
    madeFor: "Made for every reader",
    status: "In development. Pictures of people are illustrations. Product images are renders of the prototype design.",
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
  // Who it serves (owner, 27 Nov): one product, four lives. Illustrative, not testimonials.
  // crop: where to centre each picture when the header strip shows it in a tall 4:5 frame.
  lives: {
    label: "Who it serves",
    title: "One product. Different lives.",
    lede: "The same SenseBook, with the same features and the same intelligence, in four very different lives. Nothing about it marks one reader out from another.",
    stories: [
      {
        name: "The student in a remote village",
        situation: "She is studying physics at night. Her teacher is not available, and her family cannot afford a private tutor for every subject.",
        outcome: "She does not have to skip the chapter because she cannot understand it.",
        photo: "life-village",
        crop: "55% 50%",
        short: "Students in remote villages",
      },
      {
        name: "The university student",
        situation: "He is studying a difficult engineering theory and wants to understand how it is used in the real world.",
        outcome: "Instead of switching between five different resources, he has an intellectual conversation while he keeps reading.",
        photo: "life-university",
        crop: "50% 50%",
        short: "University students",
      },
      {
        name: "The student who is blind",
        situation: "She wants to study from the same textbook as her classmates.",
        outcome: "She uses the same SenseBook, with the same features and intelligence, to pursue the same academic ambitions.",
        photo: "life-blind",
        crop: "75% 50%",
        short: "Blind and low-vision students",
      },
      {
        name: "The lifelong learner",
        situation: "He left university years ago, but he wants to understand economics, psychology, technology and business.",
        outcome: "His education does not end with his graduation.",
        photo: "life-lifelong",
        crop: "45% 50%",
        short: "Lifelong learners",
      },
    ],
    note: "These are illustrative future experiences, not existing users or testimonials. The pictures are illustrations: SenseBook is in development.",
  },
  // Six ways SenseBook could change society (owner, 27 Nov). Possibilities, stated as such.
  society: {
    title: "Six ways SenseBook could transform society",
    lede: "SenseBook is one device. Used widely, it could change how a society learns. These are the changes we are designing for. None of them has been measured yet.",
    ways: [
      {
        name: "Democratising personalised education",
        photo: "way-1",
        text: "Give students in remote villages on-demand explanations, discussion and academic guidance that would otherwise need a knowledgeable person to be there.",
        line: "Geography should not determine how deeply someone can learn.",
      },
      {
        name: "Reducing educational inequality",
        photo: "way-2",
        text: "Supplement private tutoring, and reduce families’ dependence on extra paid instruction, where SenseBook proves effective.",
        line: "A family’s financial circumstances should not determine how many questions their child can afford to ask.",
      },
      {
        name: "Normalising inclusive education",
        photo: "way-3",
        text: "A blind student and a sighted student use the same commercially desirable technology to study the same subject.",
        line: "Accessibility becomes an ordinary feature of modern education, instead of something that needs visibly separate equipment.",
      },
      {
        name: "Developing a generation of independent thinkers",
        photo: "way-4",
        text: "Move students beyond memorisation by encouraging questioning, reasoning, debating, connecting concepts and applying knowledge.",
        line: "Imagine students preparing for examinations by defending their understanding in conversation, rather than memorising model answers.",
      },
      {
        name: "Creating a lifelong learning society",
        photo: "way-5",
        text: "A farmer studying modern agricultural techniques, a technician understanding machinery, an entrepreneur studying economics and an adult learning English could all benefit.",
        line: "Education no longer has to end when someone leaves an academic institution.",
      },
      {
        name: "Building Bangladesh’s technological capabilities",
        photo: "way-6",
        text: "Develop locally engineered consumer hardware, Bangla AI learning systems, accessible digital content, electronics manufacturing expertise and, in time, intellectual capabilities Bangladesh can export.",
        line: "The technology Bangladesh learns with can also be designed, engineered and made in Bangladesh.",
      },
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
    text: "Every part of SenseBook is drawn in a full CAD model. The renders below come straight from it.",
    modelTitle: "Turn it. Pull it apart.",
    modelText: "The full CAD model of the prototype: every part of the unit and the grip. Drag to turn it, use the slider to pull it apart, and select a part to name it.",
    modelNote: "This is the CAD model, not a photograph. Bought parts are drawn at typical sizes, and nothing has been built or tested yet.",
  },
  roadmap: {
    title: "The road ahead",
    lede: "Each stage begins only when the one before it is done well. We do not publish dates we cannot keep.",
    stages: [
      { name: "Prototype design", text: "A complete CAD model, parts list and assembly guide.", now: true },
      { name: "First working units", text: "Hand-built from the parts list and tested on real books." },
      { name: "Reader trials", text: "With school students, university learners and blind and low-vision readers, measured against what we set out to change." },
      { name: "Ready to make", text: "Refined for cost, durability and manufacture." },
      { name: "In readers’ hands", text: "SenseBook available to the people it was designed for." },
    ],
  },
} as const;
