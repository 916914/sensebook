# Institution website

The website of the human-advancement technology institution whose first invention is SenseBook. Built from the owner's brief (`briefs/website-brief.md`, outside this repo) with Next.js, Tailwind CSS and Framer Motion.

- `docs/01-strategy.md`: strategy, site architecture and copy direction
- `docs/02-homepage-copy.md`: the full homepage copy
- `docs/03-design-build-plan.md`: design system and build plan

## Pages

Home `/`, Manifesto `/manifesto`, SenseBook `/sensebook`, Vision `/vision`, Impact `/impact`, About `/about`, Contact `/contact`.

## Where things live

| What | Where |
|---|---|
| Every word on the site | `src/content/*.ts` (one file per page) |
| The institution's name | `src/content/site.ts` (shows `[Institution]` until it is decided) |
| Layout pieces | `src/components/` |
| Pages | `src/app/*/page.tsx` |
| Colours and type | `src/app/globals.css` |

## SenseBook visuals

All product images and the 3D model come from the build chat's folder, `../design/` (renders in `design/renders/`, model `design/cad/out/sensebook.glb`). `npm run dev` and `npm run build` first run `scripts/sync-design.mjs`, which copies them into `public/design/`. The copies are not committed. If a file is missing, the page shows a marked placeholder instead. Pull the repo to get the build chat's latest renders.

## Run it

```bash
npm install
npm run dev        # http://localhost:3000
npm run build      # production build (all pages static)
npm run lint
```

Needs Node.js 20 or newer.

## Settings at publish time

| Variable | Purpose |
|---|---|
| `NEXT_PUBLIC_CONTACT_EMAIL` | The public contact address on the Contact page. Never committed. |
| `NEXT_PUBLIC_SITE_URL` | The site's public address, for links shared on social media and the sitemap. |

On Vercel, set the project's root directory to `website` and keep "Include files outside the root directory" on, so the build can read `../design/`.

## Licence

Code: Apache-2.0. Words, screenshots and docs: CC BY 4.0. SenseBook renders and model: from the SenseBook repo, under its licences.
