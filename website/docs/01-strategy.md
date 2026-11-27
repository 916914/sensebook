# 1. Strategy, architecture and copy direction

Source: the owner's brief, `briefs/website-brief.md` (27 Nov 2026). This file turns it into decisions. Where the brief gives exact words, the site uses them as written.

## What the site is

The website of a human-advancement technology institution. SenseBook is its first invention, shown as proof of the institution's philosophy, not as the subject of the site.

- Core belief: Greatness should not be a privilege.
- Purpose: Advance human potential.
- Signature: Born in Bangladesh. Built for humanity.
- Name: not decided yet. Every page reads it from one setting (`src/content/site.ts`) and shows **[Institution]** until the owner gives it.

## The five jobs, and where each is done

| Job | Done mainly by |
|---|---|
| Establish authority | Calm, exact writing; restrained design; honest status of SenseBook (in development, renders of the prototype design) |
| Create emotional gravity | Home sections 1, 2 and 6; the Manifesto page |
| Explain the vision clearly | Vision page: three pillars, each with the kinds of invention it leads to |
| Introduce SenseBook as proof | Home section 3 and 4; the SenseBook page |
| Open future possibility | Home section 5; Vision page |

## Pages

| Page | Path | Purpose (from the brief) |
|---|---|---|
| Home | `/` | Wonder, philosophy, authority, SenseBook, curiosity. Eight sections in the brief's order. |
| Manifesto | `/manifesto` | The philosophical heart: the gap between what people can become and what circumstance allows; Bangladesh and global ambition; the kind of institution this is. |
| SenseBook | `/sensebook` | What it is, how it works, who it serves, conversational learning, accessibility by design, why physical AI matters, product visuals (renders and the 3D model), roadmap. |
| Vision | `/vision` | Three pillars: Human Intelligence, Human Independence, Human Opportunity. Categories of future invention, never invented products. |
| Impact | `/impact` | Barriers to remove and outcomes we intend to measure, across education, accessibility, intellectual independence, Bangladeshi capability and global impact. Intentions, not claims. |
| About | `/about` | Who we are, what we believe, problems we choose, values, design and engineering philosophy. |
| Contact | `/contact` | For investors, researchers, institutions, press, design collaborators and engineers. Selective, not eager. |

Navigation: the wordmark (home) and the six pages. Footer repeats them with the signature line and the open-source licences.

## Honesty rules the site follows

- SenseBook is in development. Product images are labelled as renders of the prototype design from the build chat's CAD model. No photos are faked.
- No invented people, partners, users, quotes, numbers, dates or results. The Impact page says what we intend to measure, not what we have measured.
- No team names until the owner gives them.
- The contact address is not committed to the public repo; it is set as a Vercel environment variable at publish time.

## Copy direction

Voice: an institution speaking plainly about serious work. Calm, exact, unhurried. Short sentences carry the weight; long ones explain.

Do:
- Say what a thing does, in plain verbs ("reads the page aloud", "answers questions about it").
- Use the brief's own lines where it gives them.
- Speak about disability as access and independence, never as tragedy.
- State intent as intent ("we intend to", "we will measure") and status as status ("in development").

Don't:
- disrupt, revolutionize, empower, cutting-edge, game-changing, unlock, seamless, next-generation
- exclamation marks
- donation or charity language; fundraising talk in the brand story
- pity; "suffering from"; "the less fortunate"
- futurist filler ("the future is here")
- long blocks of vague text; listing every ambition on every page

Test for every line: would a serious reader find it precise, and would it still be true in five years?
