// SPDX-License-Identifier: CC-BY-4.0
// The institution's five fields of work and their programmes (owner, 27 Nov 2026).
// Only SenseBook is in development. Every other programme is proposed: named, not built,
// so the site shows names only and never describes them as products.

export type Programme = { name: string; status?: "in development" };

export type Field = {
  name: string;
  text: string;
  programmes: Programme[];
  categories: { name: string; text: string }[];
};

export const fieldsIntro = {
  title: "Five fields of work",
  note: "SenseBook is in development. The other programmes are proposed and not yet built.",
};

export const fields: Field[] = [
  {
    name: "Intellectual advancement",
    text: "Technologies that deepen how people learn, reason and understand.",
    programmes: [{ name: "SenseBook", status: "in development" }, { name: "LabAnywhere" }, { name: "SkillSense" }],
    categories: [
      { name: "Instruments of understanding", text: "Tools that explain rather than only retrieve, so people grasp why something is true and not just what to remember." },
      { name: "Learning that meets the learner", text: "Guidance that adapts to a person’s pace, level and language, in the places they already learn." },
      { name: "Tools for thinking", text: "Aids that help people test an argument, check a step or weigh evidence, without doing the thinking for them." },
    ],
  },
  {
    name: "Physical independence",
    text: "Technologies that let people move, act and live on their own terms, whatever their body or circumstance.",
    programmes: [{ name: "MotionSense" }, { name: "CareLift" }, { name: "HumanBridge" }],
    categories: [
      { name: "Access to the printed and visual world", text: "Books, documents, signs and labels that today require sight, or someone else’s." },
      { name: "Everyday autonomy", text: "Tools that help people move, find their way and manage daily life without waiting for help." },
      { name: "Assistive technology people want to own", text: "Products designed as desirable objects for everyone, so independence never comes with a stigma." },
    ],
  },
  {
    name: "Economic opportunity",
    text: "Technologies that widen access to the skills, tools and markets through which people earn and build.",
    programmes: [{ name: "MicroFactory" }, { name: "FarmGate" }, { name: "FreshBank" }, { name: "MaterialBank" }],
    categories: [
      { name: "Skills at the point of work", text: "Guidance that helps people learn a trade or a technique while they practise it." },
      { name: "Making and selling closer to home", text: "Tools that let small producers make, keep and sell more of what they produce." },
      { name: "Capability that stays", text: "Designing, engineering and making advanced technology in Bangladesh, so the skills to build it grow where they are needed." },
    ],
  },
  {
    name: "Health and wellbeing",
    text: "Technologies that make good health easier to reach and to keep.",
    programmes: [{ name: "ClinicOne" }, { name: "AirWorks" }, { name: "AquaTrust" }],
    categories: [
      { name: "Care within reach", text: "Dependable tools for checking and caring for health in places that lack them." },
      { name: "Healthy surroundings", text: "Technologies for cleaner air and safer water at home and at work." },
    ],
  },
  {
    name: "Societal infrastructure",
    text: "Technologies that make the systems communities depend on more resilient and dependable.",
    programmes: [{ name: "FloodCore" }, { name: "DrainWorks" }, { name: "RoadSense" }, { name: "PowerBrick" }],
    categories: [
      { name: "Resilience to climate", text: "Systems that help communities prepare for floods and recover from them." },
      { name: "Infrastructure that holds", text: "Drainage, roads and power that are watched, maintained and dependable." },
    ],
  },
];
