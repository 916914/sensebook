# 3. Design and build plan

## Design idea

Two lights. The institution speaks in a deep slate night; the invention lives in the pale studio light of its own renders. Dark sections carry belief and purpose. Light sections carry SenseBook, set on exactly the background colour of the build chat's technical renders (`#F4F4F1`), so the product sits on the page with no frame around it.

The one memorable moment: in the hero, a thin marigold line passes under the headline as it appears, the way a reader's eye (and SenseBook's camera) moves along a line of print. Everything else stays still and quiet.

## Tokens

| Name | Hex | Use |
|---|---|---|
| Slate night | `#131A1B` | Dark base. A deep version of SenseBook's own slate body colour. |
| Graphite | `#263032` | Rules, raised surfaces and quiet borders on dark |
| Mist | `#A9B3B2` | Secondary text on dark (AA on slate night) |
| Stone | `#F4F4F1` | Light base, same as the render plates |
| Ink | `#1A2224` | Text on light |
| Marigold | `#E3A33F` | The one accent, taken from SenseBook's Ask button. Lines, focus rings, small marks, buttons on dark. Never body text on light. |

Type
- Display: **Newsreader** (variable, optical sizes), light weights at large sizes, for statements. Editorial and serious, close in spirit to the brief's Canela suggestion and free to use.
- Text and interface: **Inter**, the brief's own body choice.
- Scale (1.25 ratio, fluid with `clamp`): 15 / 17 / 21 / 27 / 34 / 48 / 68 / up to 120 px for the hero.
- Body text 17–18 px, line length under 68 characters, line height 1.6. Display line height 1.02–1.1.
- Sentence case everywhere. No all-caps labels, no eyebrow tags over headings, no italic or coloured single words in headlines.

Layout
- 12-column grid, 1280 px content width, wide margins. Everything left-aligned; nothing centred except the final close.
- Section rhythm: generous vertical space (12–20 rem on desktop) so each idea stands alone.
- Numbers appear only where content is a sequence (the four steps of "How it works").

```
HOME
┌──────────────────────────────────────────────┐ slate night
│ Human Advancement      Manifesto SenseBook … │
│                                              │
│ Greatness should                             │
│ not be a privilege.                          │
│ ───────── (marigold reading line)            │
│ Humanity's greatest…        [Discover] [Explore]
│ ┌──────────────────────────────────────────┐ │
│ │ render 10, wide, slow drift               │ │
│ └──────────────────────────────────────────┘ │
├──────────────────────────────────────────────┤ slate night
│ A child's future…  (three lines, serif)      │
│ We exist to remove barriers…                 │
├──────────────────────────────────────────────┤ stone
│ SenseBook                     [render 01]    │
│ The first invention…                         │
├──────────────────────────────────────────────┤ stone
│ Understanding should not depend on…          │
│ student | university | blind reader | lifelong (2×2, rules)
├──────────────────────────────────────────────┤ slate night
│ One invention. A much larger purpose.        │
│ Intelligence | Independence | Opportunity    │
├──────────────────────────────────────────────┤ slate night
│ Born in Bangladesh.                          │
│ Built for humanity.   (largest type on page) │
├──────────────────────────────────────────────┤ stone
│ Manifesto excerpt (serif)   Read the manifesto│
├──────────────────────────────────────────────┤ slate night
│ We are building for what humanity can become.│
└──────────────────────────────────────────────┘
```

## Motion (Framer Motion)

- Hero: headline lines rise in sequence, the marigold reading line draws under them, the render settles from a slight scale. Once, on load.
- Scroll: slow parallax on large renders (a few percent), and a soft fade-up on section headings only.
- Hover: underline draws on links; buttons shift tone. No bouncing, no glows.
- `prefers-reduced-motion`: all of the above are switched off; content shows at once.

## SenseBook visuals (build chat only)

From `sensebook/design/`:
- Renders: 01 hero, 02 front, 03 side, 04 top, 05 exploded unit, 07 cutaway, 10 on open hardcover, 11 on thin paperback, 12 table tripod, 14 folded, 15 stick extended.
- Model: `cad/out/sensebook.glb`, shown in an interactive model stage on the SenseBook page (turn, pull apart, name a part), built on the same logic as the build chat's viewer (`design/viewer/index.html`) and loaded only when the visitor opens it (the file is about 4 MB).
- `npm run sync-design` copies these into `public/design/` on every `dev` and `build`. The copies are not committed, so the build chat's files stay the only source. Pull the repo to get its latest renders.
- If a file is missing, the page shows a clearly marked placeholder instead.

Not used: anything from `brand/` or `docs/validation/` (owner's instruction).

## Build

- Next.js (App Router, TypeScript, static pages), Tailwind CSS, Framer Motion, three.js for the model stage only.
- Structure: `src/content/` holds all words (one file per page) so copy can change without touching layout; `src/components/` holds layout pieces (Section, Display, Reveal, Button, Figure, ModelStage, Nav, Footer).
- Fonts self-hosted through `next/font` (no requests to font servers at runtime).
- Images through `next/image` with explicit sizes and `alt` text describing what is shown.
- Accessibility: semantic landmarks, skip link, visible marigold focus ring, AA contrast checked for every text colour pair, keyboard-operable navigation and model stage, reduced motion respected.
- Contact address read from `NEXT_PUBLIC_CONTACT_EMAIL` at build time; never committed.
- Checks before showing each page: `npm run build` and `npm run lint` clean, no console errors, screenshots at 390 px and 1440 px.

## Licence

Code Apache-2.0. Words and images CC BY 4.0. SenseBook renders and model come from the build chat under the repo's licences.
