# Positioning inputs from validation

For whoever writes SenseBook's positioning. These are the facts and limits the positioning should rest on. They come from desk research on 27 November 2026; nobody has been interviewed and no SenseBook hardware has been tested. Sources are linked; full detail is in the [validation report](SenseBook_Validation_Report.md).

**Version:** 1.2 (27 Nov 2026). All evidence is in, including the legal points (NCTB rights, children's data, the AI provider's age terms), which are in section 5 of the report.

## 1. Who the first customer really is
| Track | Buyer (pays) | User | Evidence |
|---|---|---|---|
| **Learn** | A parent in roughly the **top 10–20% of urban households**, who already pays for tutoring or coaching | Their **Class 8–10 child** preparing for the SSC exam | The device costs about **33% of an average urban household's monthly income** (HIES 2022: Tk 45,757 urban), but about **11% of a top-decile month** (about Tk 132,600, derived from HIES 2022 income shares). Real wages are still falling: inflation 8.27% against wage growth 7.63% in Oct 2026. |
| **Access** | An **organisation** (NGO, blind-reader organisation, CSR team, school programme) | A **blind or low-vision student** in an integrated or special school | Tk 16,990 is about 17 months of the disability allowance (Tk 1,000 a month, FY2026-27 budget, [bdnews24](https://bdnews24.com/budget2026-27/4f25a62e756f)), so families can't be the buyer. Bank CSR gave Tk 64 crore to education in Jul–Dec 2025 ([Financial Express](https://thefinancialexpress.com.bd/trade/banks-csr-spending-rises-34pc-to-tk-198b)). In India, CSR teams bought AI reading glasses for blind students in Dec 2025. **No Bangladeshi sponsor has yet paid for a print-reading device**, so SenseBook would be first. |

**How big the Access user group is:** about 35,000–40,000 blind children ([WHO 2017](https://www.who.int/bangladesh/news/detail/24-04-2017-preventing-avoidable-childhood-blindness-in-bangladesh-a-pilot-intervention); [Hussain et al. 2019](https://pmc.ncbi.nlm.nih.gov/articles/PMC6555501/)). Most of Bangladesh's roughly 0.5–1 million blind people are older adults with cataract, much of it treatable ([National Blindness Survey 2020](https://www.thedailystar.net/node/2913066)). Low-vision students and adults are a larger, less-studied group. The natural channel is the government's integrated programme: 76 centres in 64 districts plus 12 special schools ([Prothom Alo, Jul 2025](https://en.prothomalo.com/bangladesh/roundtable/loscvcsh4l)).

Implication: the brand should talk to **two different buyers**. One is a status-conscious, exam-focused urban parent. The other is a programme officer who needs evidence and accountability. The user story (a student with a book) can be shared.

## 2. The main alternative they'll compare it to
- **Learn: the phone or tablet already in the house, plus the guidebook.**
  - 75.1% of households have a smartphone and 58.2% have internet (BBS ICT survey, Apr–Jun 2026, [The Daily Star](https://thedailystar.net/news/technology/news/mobile-phone-use-reaches-896-bangladesh-bbs-4278021)).
  - Gemini Live speaks Bengali, can see through the camera, and costs nothing (AI Plus is Tk 600 a month, with a free year for students). NotebookLM makes Bengali audio overviews of a chapter PDF, and every NCTB book is a free PDF.
  - **Shikho's EduTab** is a Walton tablet with Shikho lessons and "AI support", launched in Dec 2025 at an undisclosed price. It is the closest direct rival for the same parent.
  - 10 Minute School's live batch includes "AI Super Solve".
  - 93% of secondary students use commercial guidebooks ([Education Watch 2023](https://www.thedailystar.net/node/3578376)), which are the ready-made answer keys SenseBook really competes with.
  - The private tutor is the **price anchor**, not the product SenseBook replaces.
- **Access: free talking textbooks, a free phone app, and people.**
  - Free DAISY talking textbooks for Classes 1–10, made by YPSA with a2i, have been on NCTB's app and website since January 2023 ([BSS, Dec 2022](https://www.bssnews.net/news/98326); [YPSA](https://ypsa.org/accessible-reading-materials-for-the-students-with-visual-and-print-disabilities)). Whether they keep up with revised editions is unconfirmed.
  - Google Lookout (free, Android) and the Envision app (free) both list Bengali. Seeing AI and Be My Eyes don't.
  - Braille books are free but late and scarce. Sighted family members read the rest.
  - The nearest dedicated rival is India's **Kibo XS** (Trestle Labs): it reads Bengali, needs a computer and internet, and sold at a subsidised Rs 10,000 a year.

Implication: positioning must answer "why not just use the phone?" in one line. The honest answer isn't "better AI": a phone app can use the same Google models. It's **the book stays the screen**:
- no phone in the child's hands;
- hands-free page following;
- verified text and cached audio for the student's own NCTB pages.

## 3. The one need SenseBook meets best
**Hands-free, faithful read-aloud of the student's own NCTB textbook, with quizzes from that page.**

Why this, and not "an AI tutor for anything":
- On **indexed NCTB pages** the device plays verified text and pre-made audio. No AI reading errors, no made-up text, almost no running cost. This is the strongest part of the design.
- **Spaced, retrieval-style quizzes** are among the best-evidenced study methods: classroom quizzing g = 0.50, spacing d = 0.54 ([Yang et al. 2021](https://link.springer.com/10.1007/s10648-021-09595-9); [Mawson and Kang 2025](https://eprints.whiterose.ac.uk/id/eprint/229807)).
- **Read-aloud helps most the readers who struggle** (students with reading disabilities d = 0.35, [Wood et al. 2018](https://pmc.ncbi.nlm.nih.gov/articles/PMC5494021); trivial for typical readers, [Clinton-Lisell 2023](https://files.eric.ed.gov/fulltext/EJ1403866.pdf)). Low-vision and blind students, and weak readers, are the natural users of the reading feature.
- **AI help works when it is structured and doesn't hand out answers:**
  - Nigeria, after-school GPT-4 programme: +0.23 SD in English ([World Bank 2025](https://openknowledge.worldbank.org/entities/publication/15e1ff08-15ae-4f7a-b2a8-d146e6c113ee/full)).
  - Turkey, unguarded ChatGPT: students scored 17% lower on the unassisted exam ([Bastani et al., PNAS 2025](https://ideas.repec.org/a/nas/journl/v122y2025pe2422633122.html)).
  - So "guide, don't solve" is a real positioning asset, backed by evidence.

For blind and low-vision readers, the best need is a different one: **no aiming**. In study after study since 2016, the most common failure of phone camera apps is aiming and framing the page. In a CHI 2025 study of Be My AI, 8 of 14 participants had trouble aiming and 8 turned to sighted help ([arXiv 2502.16098](https://arxiv.org/html/2502.16098v1)). Free DAISY books already cover the core textbooks. So the Access value is the books that aren't converted (guidebooks, notes, revised editions, library books, Class 11 and above), plus diagrams, maths and explanation.

The weakest needs, which positioning should not lead with:
- **"Reads any print":** at the reader's edge of a spread the camera resolves about 74 dpi, against the 200–300 dpi OCR normally uses (`design/cad/out/analysis_results.json`).
- **Open spoken Bangla conversation:** in an independent September 2026 test, Gemini's streaming voice model got 69.6% of Bangla characters wrong, and the best batch Gemini result was 13.3% ([Riverborn benchmark](https://github.com/riverbornai/bangla-speech-to-text-benchmark/tree/main)).

## 4. Proof points we can use now (with sources)
| Proof point | Source | Use it as |
|---|---|---|
| 76.5% of secondary students had private tutors or coaching in 2023; families spent Tk 27,340 a year per Class 9 student in 2022 | Education Watch 2023 (CAMPE), [The Daily Star, 30 Mar 2024](https://www.thedailystar.net/node/3578376) | The size of the "help at home" need, and the price anchor |
| 8–10 hours a day of load-shedding in many areas during the April 2026 SSC exams; students studying by candle | [Dhaka Tribune, 20 Apr 2026](https://www.dhakatribune.com/bangladesh/education/408243/ssc-exams-begin-amid-severe-load-shedding) | Why battery and offline textbooks matter (the soft light needs testing) |
| Blind users struggle to aim phone cameras; 8 of 14 needed sighted help in a 2025 study | [CHI 2025, arXiv 2502.16098](https://arxiv.org/html/2502.16098v1) | Why a fixed, hands-free camera matters for blind readers |
| 75.1% of households have a smartphone; 58.2% have internet | BBS ICT survey Apr–Jun 2026, [The Daily Star, 20 Sep 2026](https://thedailystar.net/news/technology/news/mobile-phone-use-reaches-896-bangladesh-bbs-4278021) | Context: the phone is the rival, and setup can rely on it |
| Spaced quizzing is one of the best-evidenced study methods (g ≈ 0.5) | [Yang et al. 2021](https://link.springer.com/10.1007/s10648-021-09595-9), [Mawson and Kang 2025](https://eprints.whiterose.ac.uk/id/eprint/229807) | Why "Test me" and revision reminders matter |
| Unguarded AI homework help can lower exam scores; guarded tutors avoid it | [Bastani et al., PNAS 2025](https://ideas.repec.org/a/nas/journl/v122y2025pe2422633122.html) | Why "guide, don't solve" is built in |
| Structured AI tutoring raised English results by 0.23 SD in 6 weeks in Nigeria | [World Bank PRWP 11125, 2025](https://openknowledge.worldbank.org/entities/publication/15e1ff08-15ae-4f7a-b2a8-d146e6c113ee/full) | That AI tutoring *can* work, never as SenseBook's own result |
| SSC 2027 runs 14 March to 15 April 2027 | [Dhaka Tribune, Aug 2026](https://www.dhakatribune.com/bangladesh/education/418217/2027-ssc-exams-rescheduled-to-start-march-14) | Launch and message timing |

SenseBook's own proof points (preference over a phone, independence for blind readers, reading accuracy) don't exist yet. The [validation kit](kit/) is how to get them.

## 5. Claims we must not make (until tested)
| Don't say | Why | Say instead |
|---|---|---|
| "Reads any book, letter or newspaper" | Untested; camera resolution is low at the far edge; LLM reading of Bangla is about 4% character error even on clean scans ([IndicVisionBench 2025](https://arxiv.org/html/2511.04727)) | "Reads your NCTB textbooks. Other print: in testing" |
| "Never makes things up" / "Reads your textbook. Never makes things up about it." (current plan line) | AI text readers are documented to invent plausible text ([arXiv 2607.24077](https://arxiv.org/abs/2607.24077v3), [arXiv 2605.27750](https://arxiv.org/html/2605.27750v2)) | "Reads verified text for your textbook. Tells you when it isn't sure." |
| "Your tutor, every evening, every subject" / "replaces tuition" | No evidence it replaces a tutor; savings unmeasured | "Help on the page you're reading, any evening" |
| Any grade or score improvement | No SenseBook study yet; other trials' effect sizes don't transfer | Nothing, until the pilot's learning study reports |
| "Works offline" (unqualified) | Only downloaded NCTB packs, reminders and quizzes from packs work offline; questions need internet | "Reads downloaded textbooks without internet" |
| "Private: nothing leaves the device" | Page images and question audio go to a cloud AI provider (Google) | "The mic only listens while you hold Ask. A light shows when anything is sent." |
| "Understands your questions in Bangla" (as a promise) | Bangla speech recognition is weak in independent tests | Test first; then claim only what the pilot measured |
| "Built with blind students" | No co-design has happened yet | Use it only after co-design sessions have taken place |
| "Blind students can't read their textbooks" / "the only Bangla reader" | Free DAISY talking textbooks exist for Classes 1–10; Lookout and Envision list Bengali | "Reads the printed page in front of you, hands-free: guides, notes and books that aren't in audio" |
| "One-sixth to one-quarter of the price of imported reading aids" (current plan line) | The arithmetic is wrong: Tk 16,990 is about 1/20 of OrCam Read 3 ($2,790) and about 1/14 of Envision Glasses' lowest price ($1,899) | "A small fraction of the price of imported readers", with the real figures |
| "Your tutor … for less than one month of tuition" | True only for the Tk 399 subscription; the device is Tk 14,990 up front, which is 5–14 months of a typical tutor outside Dhaka (Tk 1,100–3,000 a month) | Compare the subscription with tuition, and say the device price plainly |
| "NCTB-approved" or anything implying endorsement | No NCTB permission or memorandum yet. Textbook copyright sits with the Government or NCTB, and the Note-Books (Prohibition) Act 1980 bars unauthorised textbook explanations | Don't use NCTB's name or logo as an endorsement; "works with NCTB textbooks" only after permission |
| "Powered by Google Gemini" (or any provider name) for the student product | Google's Gemini API terms (effective 23 Mar 2026) bar services likely to be used by under-18s; the provider may change | Don't name the AI provider in brand materials |
| Battery hours, "certified", "safe for children" | No device tested or certified (BTRC, battery tests) | "Prototype" until certified |

## 6. The price range the evidence supports
- **Device:** test **Tk 9,990–14,990**, with cardless instalments.
  - Tk 14,990 is entry-tablet money: Redmi Pad SE about Tk 13,198, Walton Walpad Tk 16,499 ([GizNext](https://www.giznext.com/bd/tablets/xiaomi-tablets-price-list?amp=1), [TechLand](https://www.techlandbd.com/smartphone-and-tablet/tablet-pc), 2026).
  - Above about Tk 15,000, parents are in the band where more than half of smartphones sell (Tk 15,000–20,000, a Xiaomi claim) and will compare it with a phone.
  - Below Tk 12,990 the v1 device loses money at sale in the plan's own model (FM, Unit Economics).
  - Cardless instalment plans already cover about 25% of financed phone sales ([Omdia, Aug 2026](https://omdia.tech.informa.com/blogs/2026/aug/bangladesh-smartphone-financing-moves-from-an-affordability-tool-to-a-competitive-advantage)).
- **Subscription:** Tk 399 a month is about 0.9% of average urban household income. Its margin holds only if AI cost stays near Tk 113 a month. Reading unfamiliar pages aloud through the cloud, which the model leaves out, could raise that to about Tk 250–390 (validation estimate). Position the subscription around **questions, quizzes and reports on NCTB books**, not unlimited reading of any print.
- **Access package:** Tk 16,990 per reader (device, training, two years of service) is the plan's figure. It is below every dedicated reader found: Kibo XS sold at a subsidised Rs 27,000 perpetual (about Tk 38,000, approx.), and Envision Glasses start at $1,899. Whether funders pay it is the key unknown: no Bangladeshi precedent exists. Unlimited reading of non-textbook print would cost far more than the Tk 125 a month budgeted (validation estimate: Tk 230–850 a month for 60–300 cloud-read pages).

## 7. Words and tone that fit the evidence
- Lead with **the book** and **the student's own textbook**, not with "AI".
- Name the two voices: "the reader voice reads the page; the explainer voice helps." It is a real, honest product difference.
- Keep "বই এখন কথা বলে" (books now talk back); it promises reading, which the design does best on NCTB books.
- Avoid: "revolutionary", "smart", "magic", "never wrong", "replaces".
