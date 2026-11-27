# SenseBook brand direction

Version 1, 27 November 2026. The visual guide is [guide/SenseBook_Brand_Guide.pdf](guide/SenseBook_Brand_Guide.pdf) (20 pages). Positioning, sources and the never-say list are in [POSITIONING.md](POSITIONING.md). The name check is in [NAME_CHECK.md](NAME_CHECK.md).

**Status**
- **Settled:** the story, positioning, palette, type, icon style, voice, audio and tactile identity.
- **Name:** stays SenseBook, pending a Bangladesh trademark search.
- **Logo:** a **working mark**. The founders will confirm or replace it. Every file comes from `src/`, so a new mark regenerates everything.

## 1. The story (manifesto)

> **Understanding should never be a privilege.**
>
> Two students can read the same textbook and get two different educations. One can turn to a tutor whenever something is hard. The other has to work it out alone. For someone who can't see the page, even reaching the printed words is another barrier. The knowledge is the same. The chance to understand it is not.
>
> We have built schools, printed textbooks, opened libraries and connected people to the internet. That gave people access to knowledge. Understanding it is the other half of the journey.
>
> What if every reader had someone to learn with? Someone to explain a hard equation, talk through an argument, or connect a new idea to one you already know. Someone who knows which page you're on, remembers what you've learned, and helps you find what you don't know yet. Not limited by where you live, what your family earns, or whether you can see.
>
> That is why we are building SenseBook: a small, screen-free learning companion that turns a printed book into a conversation. Open a book. Ask a question. Turn the page and carry on.
>
> We are not building separate technology for different kinds of people. We are building one better technology for everyone. Our ambition begins in Bangladesh, but the problem is everywhere.
>
> **Knowledge belongs to everyone. Understanding should too.**

The manifesto states the ambition. What the product does today is a prototype; public claims follow [POSITIONING.md §8](POSITIONING.md#8-claims-we-must-never-make).

| | English | বাংলা |
|---|---|---|
| Purpose | Democratise understanding. | বোঝার সুযোগ সবার কাছে পৌঁছে দেওয়া। |
| Promise | Never get stuck learning alone again. | পড়তে গিয়ে আর একা আটকে থাকতে হবে না। |
| Tagline | Knowledge, now conversational. | বই এখন কথা বলে। |
| Brand idea | Someone to learn with. | শেখার একজন সঙ্গী। |
| Category | Personal learning technology | ব্যক্তিগত শেখার প্রযুক্তি |

## 2. Personality
| Trait | বাংলা | Is | Is not |
|---|---|---|---|
| Patient | ধৈর্যশীল | Explains again, a different way, as often as needed | Rushed, salesy |
| Honest | সৎ | Says what the page says, and when it isn't sure | Hype, overclaiming |
| Curious | কৌতূহলী | Asks good questions back; makes you think | An answer machine |
| Calm | শান্ত | Quiet sounds, plain words, grown-up design | Gamified, cute, loud |
| Equal | সমান | Speaks to every reader the same way | Pitying, childish, charitable |

## 3. Voice
- Short sentences, one idea each, concrete words.
- Say what we know. Mark estimates as estimates. Say "in testing" when it is.
- Bangla first in Bangladesh, in standard colloquial (চলিত):
  - তুমি to students; আপনি to parents, adults and institutions;
  - Bangla numerals in Bangla text.
- Two voices on the device: the **reader voice** reads the page; a bell, then the **explainer voice** helps.
- Never use: revolutionary, magic, smart, genius, never wrong, replaces, the only.

| Where | English | বাংলা |
|---|---|---|
| Device, unsure | I'm not sure of this word. It may be 'refraction'. | এই শব্দটা নিয়ে আমি নিশ্চিত নই। সম্ভবত 'প্রতিসরণ'। |
| Device, offline | No internet. I can still read downloaded books. | ইন্টারনেট নেই। ডাউনলোড করা বই এখনো পড়তে পারি। |
| Marketing | Help on the page you're reading, any evening. | যে পাতা পড়ছ, সেখানেই সাহায্য, যেকোনো সন্ধ্যায়। |

## 4. Logo (working mark)
- **The mark:** an open book with a marigold dot at the top of the spine.
  - The dot is SenseBook, sitting where the device sits, in the colour of its Ask button.
  - It reads as a reader with a book, works at 16 px and can be embossed.
- **The wordmark:** Literata SemiBold, outlined. In Bangla, Noto Serif Bengali Bold, outlined.
- **Clear space:** one dot diameter.
- **Smallest sizes:** mark 16 px or 5 mm; lockup 96 px or 25 mm.
- **Files:** [logo/](logo/). Versions: colour, one-colour (ink or spine), reversed, reversed white; English, Bangla and stacked bilingual lockups; app icon and favicon.
- The three explored options are in [logo/options/](logo/options/).

## 5. Colour
| Token | Name | Hex | Role |
|---|---|---|---|
| spine | Spine · মলাট | #133B42 | Primary: the device colour, text, logo, dark backgrounds |
| teal | Teal · নদী | #1F5560 | Links, headings on paper |
| mist | Mist · কুয়াশা | #DCE9E8 | Panels on paper |
| marigold | Marigold · গাঁদা | #E8A317 | The dot, Ask, one key action. Never text on a light background |
| paper | Paper · কাগজ | #F7F2E8 | Background |
| ink | Ink · কালি | #161B1C | Body text, one-colour print |
| brick | Brick · ইট | #A63D2A | Errors only |
| leaf | Leaf · পাতা | #2E6B4A | Success only |

Measured contrast:
- AAA (7:1 or more): ink on paper 15.6:1, spine on paper 10.9:1, paper on spine 10.9:1, ink on marigold 8.0:1.
- AA only: marigold on spine 5.6:1, so use it for large text.
- Fails: marigold on paper 1.9:1.

Tokens: [colour/palette.css](colour/palette.css), [colour/palette.json](colour/palette.json).

## 6. Type
| Role | Latin | Bangla |
|---|---|---|
| Display and headings | Literata 600 | Noto Serif Bengali 600/700 |
| Text and interface | Atkinson Hyperlegible Next 400/700 | Noto Sans Bengali 400/700 |

- Large type is the default: web body 18 px (line height 1.5; Bangla 1.65) and print body at least 11 pt.
- Every printed guide also comes in 18 pt large print.
- All four families are SIL OFL; the files are in [type/fonts/](type/fonts/).

## 7. Icons
- 24 px grid, 2 px stroke, round caps and joins, no fills.
- The one exception is the marigold dot for "voice" and "touch".
- Icons always appear with a text label.
- 16 icons are in [icons/](icons/).

## 8. Photography and renders
**Do:**
- Shoot real Bangladeshi homes, classrooms and libraries, in evening lamp light and window light.
- Show real hands, real books and the device at true size.
- Show every kind of reader as capable, and photograph blind readers with consent and with them, not about them.
- Label renders as renders, matched to the CAD dimensions.

**Don't:**
- Use AI-generated people or scenes presented as real.
- Use holograms, neon, purple gradients or floating screens.
- Stage pity.
- Use foreign stock classrooms.
- Use readable NCTB covers as an implied endorsement.

The brand illustration is [illustration/sensebook-on-book.svg](illustration/sensebook-on-book.svg). It is an illustration, labelled as one.

## 9. Accessibility is the identity
- **Built in for everyone:** no separate edition, no proof of disability, no hidden "accessibility mode".
- **Touch:** every control can be found by touch.
- **Sound:** every state has a sound and a spoken line, plus a vibration when the speaker is off.
- **Contrast:** body text AAA; nothing important is shown by colour alone.
- **Formats:** every guide in large print, braille and audio.

## 10. Sound identity
These are first drafts in [audio/](audio/) (WAV, 22 kHz, mono), to be tested with blind and sighted listeners.

| Sound | When |
|---|---|
| Startup (sonic logo) | Power on: three rising notes, like a page opening |
| Ready | Attached and the page is in view |
| Page captured | A page has settled: a soft paper click |
| Explainer voice next | A single bell, always before AI explanation |
| Listening / stopped | Ask held / released |
| Reminder | Three gentle notes, then the spoken reminder |
| Something's wrong | A low tone, always followed by a spoken instruction |
| Battery low | Two falling notes, then the level spoken |

- **Vibration:** attached 1 short pulse; ready 2 short; mic off 1 long; error 3 short; reminder with headphones in 2 long.
- **Tuning:** sounds are never melodies or jingles, and can be turned down separately from speech.

## 11. Tactile identity
1. **Ask button:** concave, marigold, top centre, with one raised dot (Ø 2.0 mm, 0.6 mm high). It is larger than a braille dot, so it is never read as braille.
2. **Raised mark on the back face:** 14 mm wide, 0.5 mm relief; the dot points to the top.
3. **Buttons:** back, play and forward have three distinct shapes. The mic-mute slide has ridges and an orange flag.
4. **Tri-grip:** a raised dot near the hub on each blade.
5. **Box:** a notch on the opening edge, and the name in braille (English UEB and Bangla), set and proofread by braille readers.

Sizes are targets for the bench test. Drawing: [tactile/tactile-identity.svg](tactile/tactile-identity.svg).

## 12. Packaging and on-device marks
- **Box:** recycled kraft board, no plastic film, printed in one colour (Spine), with a marigold pull tab.
- **Inside:** a large-print and braille quick start, and an audio guide the device plays on first start.
- **On the device:** no logo on the front face, only the four dots and the lens. The raised mark is on the back; the name and regulatory marks are underneath.

Drawing: [packaging/packaging-direction.svg](packaging/packaging-direction.svg).

## 13. Brand architecture
One master brand: **SenseBook**. Three ways to reach a reader, set in the text typeface after the logo, never as separate logos:
- **SenseBook Personal:** owned devices.
- **SenseBook Commons:** shared devices in schools, libraries and centres.
- **SenseBook Access Fund:** funded access, covering the device, training, maintenance and service.

Every route gets the same device, software and look. We also publish the **SenseBook Impact Report** every year, independently evaluated wherever possible, reporting only what was measured.

## Rebuilding
```
python brand/src/make_options.py   # logo options, name board, palette board
python brand/src/make_brand.py     # logo files, colour tokens, icons, illustration, tactile, packaging, audio
python brand/src/make_guide.py     # the brand guide PDF and page previews (needs Microsoft Edge or Chrome)
python brand/src/make_pitch.py     # docs/pitch: the 10-slide deck and the one-page summary
python brand/src/make_og.py        # the hub site's social image
python -I tools/build_site.py      # the hub site, into site/
```
Needs Python 3 with fontTools, brotli, uharfbuzz, PyMuPDF and Pillow. On Windows, run these from PowerShell or cmd: headless Edge didn't write PDFs from Git Bash in our build.

Code: Apache-2.0. Brand assets, guide and text: CC BY 4.0. Fonts: SIL Open Font License.
