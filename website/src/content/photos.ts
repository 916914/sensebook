// SPDX-License-Identifier: Apache-2.0
// Pictures of people using SenseBook. The owner generates them from docs/04-image-prompts.md and
// saves them in public/photos/ under these names (.jpg, .png or .webp). Until a file exists, the site shows a
// clearly marked placeholder in its place.

export type PhotoId =
  | "header"
  | "life-village"
  | "life-university"
  | "life-blind"
  | "life-lifelong"
  | "way-1"
  | "way-2"
  | "way-3"
  | "way-4"
  | "way-5"
  | "way-6";

export type Photo = { name: string; alt: string; scene: string };

export const photos: Record<PhotoId, Photo> = {
  header: {
    name: "header",
    scene: "A student at her desk at dusk, pressing the Ask button on SenseBook",
    alt: "A teenage girl at a desk by a window at dusk, her physics textbook open with SenseBook clipped to its top edge. She has just pressed its marigold button and is listening, pencil in hand.",
  },
  "life-village": {
    name: "life-village",
    scene: "A girl in a rural home at night, studying physics with SenseBook",
    alt: "A teenage girl sitting on a woven mat in a rural home at night, studying a physics textbook with SenseBook clipped to it, lit by one small lamp.",
  },
  "life-university": {
    name: "life-university",
    scene: "An engineering student in a university library, listening to SenseBook",
    alt: "A university student in a library with a thick engineering textbook open and SenseBook clipped to it, one earphone in, listening as he reads.",
  },
  "life-blind": {
    name: "life-blind",
    scene: "A blind student in her classroom, using SenseBook with the same textbook as her classmates",
    alt: "A blind schoolgirl at her desk in an ordinary classroom, fingertips on SenseBook's marigold button, listening, a folded white cane beside her desk.",
  },
  "life-lifelong": {
    name: "life-lifelong",
    scene: "A man at home in the morning, asking SenseBook about an economics book",
    alt: "A man in his forties with reading glasses at home in the morning, a cup of tea beside him, asking SenseBook a question about the economics book in front of him.",
  },
  "way-1": {
    name: "way-1-villages",
    scene: "A girl on the steps of a village house, studying with SenseBook",
    alt: "A girl sitting on the steps of a village house with a schoolbook on her knees and SenseBook clipped to it, rice fields behind her.",
  },
  "way-2": {
    name: "way-2-inequality",
    scene: "A boy doing homework with SenseBook at the family table while his mother cooks",
    alt: "A boy doing maths homework at the family table with SenseBook clipped to his textbook, his mother cooking in the background.",
  },
  "way-3": {
    name: "way-3-inclusive",
    scene: "A blind student and a sighted student studying side by side, each with SenseBook",
    alt: "Two classmates laughing together at a school bench, one blind and one sighted, each with SenseBook clipped to her own copy of the same textbook.",
  },
  "way-4": {
    name: "way-4-thinkers",
    scene: "Three university students debating a passage, SenseBook on the open book",
    alt: "Three university students in a lively discussion around a library table, one pointing at a passage in a book with SenseBook clipped to it.",
  },
  "way-5": {
    name: "way-5-lifelong",
    scene: "A farmer on his veranda, studying a rice-farming manual with SenseBook",
    alt: "A farmer on the veranda of his house beside a rice field, listening to SenseBook clipped to a farming manual on his lap.",
  },
  "way-6": {
    name: "way-6-capability",
    scene: "Young engineers in a Dhaka electronics lab assembling SenseBook units",
    alt: "Young engineers at a workbench in a small electronics lab assembling SenseBook units, with open shells, circuit boards and a soldering iron.",
  },
};

export const photoNote = "Illustration. SenseBook is in development.";
