# SenseBook: claims and assumptions register

Every claim the SenseBook plan rests on, where it comes from, and a verdict from desk research on 27 November 2026.

**Sources read:**
- `docs/SenseBook_Venture_Plan.pdf` (VP), v1.0, 26 Nov 2026
- `docs/SenseBook_Product_Spec.pdf` (PS), v1.0
- `finance/SenseBook_Financial_Model.xlsx` (FM)
- `README.md`
- `design/SenseBook_Attachment_Plan.md` (AP) and `design/cad/out/analysis_results.json`
- the hub site, https://sensebook-hub.vercel.app, which is an index of these documents and adds no claims of its own

**Verdicts**
- **Holds:** published data supports it.
- **Weak:** partly supported, optimistic, mislabelled, or resting on one soft source.
- **Unsupported:** no evidence found, or the evidence points the other way.
- **Untested:** only a real test can settle it, and the plan says so too.

Evidence and links are in the [validation report](SenseBook_Validation_Report.md); the raw notes are in [research_notes/](research_notes/).

## Who buys
| # | Claim | Where | Verdict | Why |
|---|---|---|---|---|
| C01 | Parents of Class 6–10 NCTB students pay first; they are the revenue engine | VP §1, §4 | **Holds**, narrower | Families spend Tk 27,340 a year per Class 9 student (Education Watch 2022). But the device is about 33% of an average urban monthly income, so the realistic buyer is the top 10–20% of urban households |
| C02 | Private schools buy devices (Tk 11,490, 10+ units) plus a Tk 1,990 yearly licence: 400 in Year 2, 2,000 in Year 3 | VP §6; FM | **Unsupported** | No evidence of school purchasing of study devices found; school budgets are tight and fee-capped (Tuition Fee Policy 2024) |
| C03 | Sponsors (CSR, NGOs, donors, government) fund blind readers at Tk 16,990: 40 / 300 / 1,000 | VP §6; FM | **Weak** | Indian CSR precedents exist (Dec 2025). No Bangladeshi sponsor has funded a print-reading device. Bank CSR to education about Tk 64 crore per half-year, falling in H1 2026 |
| C04 | NGOs and programmes buy accessible-content contracts: Tk 5 / 15 / 40 lakh | FM | **Weak** | YPSA with a2i and WIPO ABC already make free DAISY textbooks; demand for a paid supplier is unproven |
| C05 | Diaspora giving funds Sponsor-a-Reader | VP §5 | **Untested** | No data; ShunBoi shows the diaspora pays for Bangla content (70% of its listeners) |
| C06 | Coaching centres and libraries are a second channel from Year 2 | VP §4 | **Untested** | |

## Who uses, and why
| # | Claim | Where | Verdict | Why |
|---|---|---|---|---|
| C07 | Students get stuck alone at night; their options are a costly tutor, a guidebook, a phone or giving up | VP §2 | **Holds** | 76.5% tutored, 93% use guidebooks (Education Watch 2023); 58% of secondary students have internet at home |
| C08 | 76.5% of secondary students have a private tutor | VP §1, §2 | **Holds**, with caveats | Education Watch 2023 (CAMPE), Classes 5–9, 26 upazilas; "tutors or coaching"; not a national statistic |
| C09 | Households carry 71% of education costs | VP §2 | **Holds** | UNESCO GEM 2022 South Asia report; older underlying data |
| C10 | Bangladesh has about 750,000–1 million blind people and more than 6 million with some visual impairment | VP §2, §4 | **Weak** | About 1% of people aged 30+ are blind, and 19% of them have some impairment (2020 survey). Most are older adults with cataract, much of it treatable; blind children number about 35,000–40,000 |
| C11 | Braille textbooks arrive late and miss maths notation | VP §1, §2 | **Holds** | TBS, Apr 2025; the maths and science braille code was approved only in 2024 |
| C12 | Phone apps need a sighted setup, a steady hand and constant re-aiming | VP §2 | **Holds** | Aiming is the most repeated failure in studies from 2016 to 2025; in a 2025 study, 8 of 14 Be My AI users needed sighted help |
| C13 | A blind student reading her own textbook on the day it's handed out is the story (implies no current access) | VP §5 | **Weak** | Free DAISY talking textbooks for Classes 1–10 have been on NCTB's app and website since January 2023 |
| C14 | Load-shedding and weak Wi-Fi break cloud learning at study time | VP §2 | **Holds** | 8–10 hours a day in many areas during the April 2026 SSC exams; household internet 58.2% |
| C15 | Parents fear AI doing the homework; guide-don't-solve answers that | PS §6 | **Holds** (evidence) | An unguarded AI tutor cut unassisted exam scores by 17% (PNAS 2025) |
| C16 | Siblings share devices; a family plan adds value | PS §6 | **Untested** | |
| C17 | Madrasa students: 2.84 million Dakhil and above | VP §4 | **Weak** | 2.84 million is all madrasa levels (BANBEIS 2025) |

## Price
| # | Claim | Where | Verdict | Why |
|---|---|---|---|---|
| C18 | Device Tk 14,990 including 3 months of Learn Plus (Tk 7,990 for pilot families; Tk 10,990–12,990 on v2) | VP §6 | **Holds** as a price point | Sits at entry-tablet level; needs a deposit test |
| C19 | Tk 14,990 is below one entry tablet (Tk 14,490–16,499) | VP §6 | **Weak** | Walton Walpad 8G Pro Tk 16,499, but Redmi Pad SE about Tk 13,198 |
| C20 | It costs less than four months of one private tutor (about Tk 4,000 a month) | VP §6 | **Weak** | True in Dhaka (Tk 4,000–8,000); typical national spend is Tk 1,100–3,000 a month, so it is 5–14 months there |
| C21 | Learn Plus Tk 399 a month or Tk 3,990 a year | VP §6 | **Weak** | Same price as ShunBoi, whose listeners are 70% abroad; Gemini AI Plus Tk 600 a month, free for students for a year |
| C22 | A free tier keeps the device useful for ever (read-aloud, offline library, 3 live questions a day) | VP §6 | **Untested** | Cost of free questions is modelled at Tk 20 a month for half the devices |
| C23 | Access Tk 16,990 is one-sixth to one-quarter of imported aids ($2,500–4,250) | VP §6 | **Weak** (arithmetic) | Prices hold, but Tk 16,990 is about 1/14 of Envision Glasses' lowest price and 1/20–1/40 of OrCam; the plan understates the gap |
| C24 | Below Tk 12,990 the v1 device loses money at sale | VP §6 | **Holds** | Re-run: −Tk 229 at Tk 12,990 |

## How often, and how many stay
| # | Claim | Where | Verdict | Why |
|---|---|---|---|---|
| C25 | Median use is 45 minutes a day, 26 days a month, with 12 spoken questions an hour and 30% answered from cache | FM | **Untested** | No usage data from any comparable device |
| C26 | 45% of buyers subscribe after the included months | VP App. A; FM | **Unsupported** | No benchmark found for device-plus-subscription edtech |
| C27 | 60% of paying subscribers stay each year | VP App. A; FM | **Unsupported** | Same; exam-year churn likely (SSC moved to March–April 2027) |
| C28 | Week-6 retention ≥40% (pilot gate) | VP §9 | **Untested** | A sensible gate; the Khanmigo trial shows low engagement is common (median student used it on a third of practice days) |

## Against what
| # | Claim | Where | Verdict | Why |
|---|---|---|---|---|
| C29 | The main threat is Gemini or ChatGPT on a phone; SenseBook wins on hands-free following, the offline library, tactile controls and child safety | VP §4, §15 | **Holds**, incomplete | True, but the plan misses Shikho EduTab, 10 Minute School AI, guidebooks, Lookout and Envision (both list Bengali), DAISY books and Kibo |
| C30 | Talking pens (Tk 3,000–4,000) only play recordings | VP §4 | **Holds** | Digibook Tk 3,249 works only with its own books |
| C31 | Phone apps compete least for blind readers | VP §5 | **Weak** | Lookout and Envision are free and list Bengali; aiming is still the gap |
| C32 | The durable advantage is an indexed, reviewed Bangla textbook library plus accessibility credibility and school/NGO distribution | VP §4 | **Weak** | All 647 NCTB books are free PDFs, so anyone can index them; credibility and distribution are not built yet |

## Channel
| # | Claim | Where | Verdict | Why |
|---|---|---|---|---|
| C33 | Sell through Facebook and Instagram, bKash and Nagad, cash on delivery in Dhaka, Rokomari, schools, Access partners | VP §5 | **Untested** | Over 90% of online shoppers prefer cash on delivery; return rates of 20–30% are claimed only by vendor blogs |
| C34 | Marketing costs Tk 1,300 a device (Tk 1,100 in Year 3) | FM | **Unsupported** | No Bangladesh cost-per-sale data; one bad input here wipes out most of the profit at sale |
| C35 | Retail channel, delivery and returns cost 10% of the ex-VAT price | FM | **Weak** | Marketplace commission and COD refusals unconfirmed |
| C36 | Payment fees 1.5% | FM | **Holds** | 1–1.15% seen |

## Technology and cost
| # | Claim | Where | Verdict | Why |
|---|---|---|---|---|
| C37 | AI can read Bangla print and hold a spoken conversation for about Tk 113 a student a month | VP §1, §8; FM | **Weak** | Prices are right, but voicing unknown pages is left out; about Tk 250–390 by our estimate; TTS prices double on 1 Jan 2027 |
| C38 | NCTB publishes all 647 textbooks as PDFs in both versions | VP §1 | **Holds** | Dhaka Tribune, 28 Dec 2025 |
| C39 | Page recognition ≥95% (P0) and ≥97% (pilot) on indexed books in real homes | VP §9 | **Untested** | No benchmark on a Pi Zero 2 W found |
| C40 | Read-aloud character error ≤2% Bangla, ≤1% English | VP §9; PS §9 | **Unsupported** for unknown pages | Best published AI result on clean Bangla scans is about 4%; AI readers can invent text. Known NCTB pages avoid the problem |
| C41 | The ultra-wide camera sees the whole spread from 11 cm; pull up to 18 cm for small print | VP §3; AP | **Weak** | It covers the spread, but resolution at the reader's edge is 74 dpi (99 dpi at 18 cm), against the 200–300 dpi OCR normally uses |
| C42 | Questions go as audio straight to the AI, with no separate transcription | VP §8 | **Weak** | Independent Bangla tests: Gemini streaming 69.6% character error, batch 13.3%, specialist services about 7% |
| C43 | Time to first audio ≤2 s cached, ≤3.5 s live; resume ≤1 s after a page turn | VP §9 | **Untested** | Gemini streaming returned its result 10 s after speech ended in one Bangla test |
| C44 | 40% of answers are voiced on the device | FM | **Unsupported** | No Bangla neural voice shown running in real time on a Pi Zero 2 W |
| C45 | Battery: 5 hours on the prototype, 8 on v2; about 90 g | VP §3 | **Untested** | Our estimate is 4–6.5 hours on 2,000 mAh; no measurement |
| C46 | Pi Zero 2 W price held at $15 | VP §15 | **Holds** | Raspberry Pi, Feb 2026: no Zero price change expected (LPDDR2 stock) |
| C47 | BOM $101.50 pilot, $52.30 v1, $37.80 v2 | VP §10; FM | **Weak** | $52 is tight; $38 needs a custom board, and Year 3's 9,500 units fall below the 10k tier |
| C48 | Import charges are 20% of parts (v1) and 15% (v2) | VP §7; FM | **Weak** | 12.2% only on concessional mobile parts; general rates can pass 40%; needs an HS-code check |
| C49 | The tri-grip fits books from a booklet to 6 cm; blind users attach it alone in under 15 seconds; it holds in a shaking hand | AP; PS §9 | **Untested** | Build chat's bench test; the attachment plan lists these as open points |
| C50 | It works offline for NCTB books and through power cuts | VP §2 | **Holds** (by design) | Downloaded packs and cached audio, if built; live questions still need internet |
| C51 | No-bricking promise: core reading keeps working if the servers stop | VP §8 | **Holds** (by design) | A good practice after Moxie and Humane |
| C52 | Gemini prices: Flash-Lite $0.30 in / $2.50 out; TTS prices double in January 2027 | PS §7 | **Holds** | Official pricing page, read 27 Nov 2026; model names exist |

## Legal, privacy and safety
| # | Claim | Where | Verdict | Why |
|---|---|---|---|---|
| C53 | NCTB books are published openly; commercial derivatives need written permission; refusal is "Low" likelihood | VP §14, §15 | **Weak** | Copyright sits with the Government or NCTB for 60 years (Copyright Act 2023), and the Note-Books (Prohibition) Act 1980 also bars unauthorised explanations and answers (upheld, 48 DLR (AD) 184). Likelihood is nearer Medium |
| C54 | Personal Data Protection Ordinance 2025 governs children's data: guardian consent, no profiling of minors | VP §14; PS §6 | **Weak** (outdated) | Replaced by the Personal Data Protection Act 2026 (Act 63 of 2026): under-18s need guardian consent for *all* processing; facial images and voiceprints are sensitive biometric data; no child-profiling ban found in the Act text |
| C55 | Google Gemini is the default AI provider | VP §8; PS §7 | **Unsupported** for children | Gemini API terms (effective 23 Mar 2026) bar services "directed towards or likely to be accessed by individuals under the age of 18"; Google Cloud's generative AI terms say the same |
| C56 | BTRC importer/vendor enlistment and type approval; budget Tk 1.5 lakh | VP §10 | **Weak** | Today it's enlistment (2 years) plus a clearance before each shipment, not full type approval; a July 2026 licence notice has an unclear scope; fees not found |
| C57 | A UN38.3 report and MSDS cover the battery | VP §10 | **Weak** | Also needs IEC 62133-2 (cell) and IEC 62368-1 (product; 48 °C limit for hand contact); since Jan 2026 air shipments must be at ≤30% charge; some couriers refuse lithium to Bangladesh |
| C58 | Take-back and refurbishment comply with the E-waste Rules 2021 | VP §12 | **Holds** (by design) | An assembler is a "producer": DoE registration, take-back points, collection targets from 10% rising to 50% |
| C59 | The blind-reader impact line is helped by accessible-format rights | VP §6 | **Weak** | Copyright Act s.70(2) covers accessible copies only if entirely non-profit at production cost; Bangladesh acceded to Marrakesh in 2022 |

## Finance and funding
| # | Claim | Where | Verdict | Why |
|---|---|---|---|---|
| C60 | 8.64 million secondary students, all institution types | VP §4 | **Weak** | General secondary only; enrolment fell by about 425,000 in 2025 |
| C61 | About 1.0 million serviceable students (urban, top two quintiles, home internet ~76%) | VP §4 | **Weak** | 76% is individual urban internet use; household urban internet is about 62%. Serviceable: 0.8–1.0 million |
| C62 | Volumes 100 / 2,000 / 9,500; revenue Tk 15.5 lakh / 2.81 crore / 11.88 crore | VP §11; FM | **Untested** | No conversion data yet; the arithmetic is correct |
| C63 | Hardware margin 23.5% on the student v1 device | VP §7 | **Weak** | Consumer electronics run 33–45%; the price is 2.3× BOM |
| C64 | Break-even at about 12,400 devices a year | VP §11 | **Holds** as arithmetic | It rises to about 26,800 a year if contribution falls to Tk 1,000 a device |
| C65 | Grants of Tk 43 lakh in Year 1 (iDEA up to Tk 50 lakh) | VP §11; FM | **Unsupported** | The 2026 ICT Division policy sets Tk 3–10 lakh at prototype stage; Tk 50 lakh only "in special circumstances" |
| C66 | Pre-seed of Tk 2 crore in Year 2; seed of Tk 1.4 crore in Year 3 | VP §11 | **Weak** | All startup funding in H1 2026 was US$6 million, 100% foreign |
| C67 | Equity for Bangladeshi startups fell about 95% in H1 2026 | VP §5 | **Holds**, misleading alone | H1 2025 included a one-off US$110 million merger; H1 2026 was up 51% on H2 2025 |
| C68 | The Access line pays for itself (Tk 1,363 contribution, Tk 4,000 of service over two years) | VP §6, §12 | **Weak** | Reading unknown print through the cloud costs Tk 230–850 a month against about Tk 125 budgeted |
| C69 | 1,340 visually impaired readers and 10,000+ students reached by Year 3 | VP §1 | **Untested** | Depends on sponsors (C03) and sales (C62) |
| C70 | Team costs Tk 25,000 per FTE-month in Year 1, rising to Tk 55,000–60,000 | FM | **Untested** | Not checked against salary data |

## Consistency issues found in the documents
- **Test count:** the product spec says 38 automated tests; the README says 72; we counted 71 test functions in `prototype/software/tests/`.
- **Missing references:** the spec cites `design/SenseBook_Industrial_Design.md`, which doesn't exist. The README cites `prototype/hardware/`, which wasn't in the repo when we read it (it belongs to the build chat).
- **Voice cost:** the spec names Gemini 3.8 TTS for speech, but the cost model prices Google Cloud WaveNet voices at $16 per million characters.
- **Untested AI calls:** the spec notes that real Gemini calls haven't been run yet, so every AI quality figure is still a target.
