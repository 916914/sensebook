# How SenseBook holds onto the book: table, in hand, while turning pages

Status: proposal for the founder's approval. Nothing is built until it is approved.

## The idea in one line
The device always rides on the book, at the top of the spine, exactly as the PDF shows, whether the book lies on a table or is held in the hands. It holds on with a small spring clip that grips only the book's **cover**, right beside the spine. The clip's inner jaw slides between the cover and the first page, so **all the pages lie on top of the clip and turning them never touches it**. Clip-on book lights work the same way.

## The three parts
1. **Unit (the PDF look).** A slate-teal rounded rectangle the size of a webcam (target 8.5 × 3.8 × 3 cm), with four status dots and one round lens on its face. It contains:
   - the wide-angle camera, 2 microphones and the speaker;
   - the Ask button and other controls, and the light ring;
   - the computer and **its own battery**, so nothing else is needed in the hand.
   Target weight is about 60 g.
2. **Stick.** Slim, about 15 cm in hand and telescoping to about 20 cm for large books on a table. It has a tilt joint under the unit and a fold joint at the clip.
3. **Spine clip** (about 4 × 3 cm):
   - **Fit:** grips the top edge of the left or right cover beside the spine. Soft silicone pads fit covers from 0.3 mm (paper) to 4 mm (hardback).
   - **Swivel:** keeps the stick upright at any opening angle.
   - **Magnetic snap:** joins the stick to the clip. A spare clip (about Tk 100) can live on every textbook, so changing books takes a second. Later, an NFC tag in each clip could tell the device which book it is on.

## Why page turning stays seamless
- **Nothing in the way:**
  - The clip is underneath the pages, so a turning page never touches it.
  - The unit sits just behind the top edge of the book, never over the pages. Even a page standing straight up mid-turn passes in front of the unit, not into it.
- **The software:**
  - Pauses when a hand enters the view.
  - Never photographs a hand over the text.
  - Carries on reading by itself once the new page settles.
  - Preloads the next page for known textbooks.
  - This is already built and tested in the prototype software.

## Every scenario
| Scenario | What happens |
|---|---|
| Book on a table | Book lies flat and the device rides at the top of the spine (the PDF picture). The stick can be extended for big books. |
| Book in the hands (chair, sofa, bus) | The device moves with the book, so the camera's view of the pages never changes. Keep the stick short for balance; total weight is about 85–90 g, less than half a phone. |
| Lying in bed, book held up | The joints hold their angle. Listen through earbuds or wired earphones. |
| Turning pages | Pages pass over the clip and in front of the unit. Reading pauses for the hand and resumes on the new page. |
| Switching books | Leave a clip on each textbook and snap the unit and stick onto the next one. |
| No book (letters, bills, loose papers) | The clip opens flat as a small foot, and the unit looks down at the paper in front of it. |
| Blind reader | Clip on by touch; the device says "page edge not visible" or "book upside down" until the view is right. |

## Camera geometry and the sharpness trade-off (design estimates, 26 Nov)
- **Coverage:**
  - A wide lens (about 102° × 67°) about 16 cm above the top edge covers a school-textbook spread (about 37 × 24.5 cm).
  - A large spread (46 × 30 cm) needs about 20 cm.
- **Sharpness at that height:**
  - About 170–240 dpi near the top edge and about 115–130 dpi at the page centre.
  - Only about **80–116 dpi at the reader-side edge**, below the 150 dpi we want for reading unfamiliar small print.
  - Raising the wide lens adds coverage, not sharpness.
- **What it means:**
  - **School textbooks are unaffected:** pages are recognised from the downloaded library, so the words don't depend on the photo's sharpness.
  - **Unfamiliar small print at the reader-side edge may be misread.**
- **Ways to fix it** (choose after the images):
  - (a) A higher-resolution camera module: cost and board support to be checked.
  - (b) The standard lens on a taller stick (about 31 cm) for table reading. That gives about 180–230 dpi, but it is too tall to hold comfortably.
  - (c) Accept it, and ask the reader to slide the book closer for small print.
- **Turning clearance:** with the lens about 6 cm behind the top edge at 21–22 cm, tilted about 29°, a page standing straight up still clears the unit.

## Unit size
- A Pi Zero 2 W fits upright inside an 85 × 38 × 30 mm unit with one small custom audio board. The bulky stacked audio board used in early dev kits does not fit.
- Putting the battery inside the unit (needed for in-hand use) adds a few millimetres, about 88 × 40 × 34 mm, until the smaller v2 board.

## Battery
- About 2,000 mAh inside the unit: about 5 hours on the prototype board and about 8 hours on the v2 board.
- A USB-C power bank can run it for long table sessions.
- This replaces the earlier "battery in the stick" idea, which only worked on a table.

## What changes if this is approved
- The design build restarts with this exact concept: CAD, a 3D-printable clip and stick, and renders of every scenario.
- The documents change from "slide-under foot" to "spine clip", and from a battery in the stick to a battery in the unit.
- The financial model changes almost nothing: the clip replaces the foot plate on the same cost line, plus optional spare clips.
- The software adds tolerance for a moving, tilting book in the hands (page tracking). Hand-pause and auto-continue already exist.

## Risks to test first, with real NCTB books
- Thin paper covers bending under the weight: wide clip pads and a short stick.
- Covers glued to the first page near the spine: place the clip 2–3 cm from the spine.
- Wrist fatigue in long in-hand sessions: keep the total under 100 g.
- Large books: use the longer stick setting.
