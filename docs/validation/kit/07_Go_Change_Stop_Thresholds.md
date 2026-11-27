# Go, change or stop: thresholds set in advance

Agree these numbers **before** collecting data, and don't move them afterwards. Where the venture plan already has a pilot gate, the threshold matches it (marked *plan gate*). Thresholds marked **must-pass** decide a track on their own.

- **Go:** keep the plan for this item.
- **Change:** the idea survives, but the design, price or channel changes, then test again.
- **Stop:** drop this part of the plan, or the whole track if it is a must-pass.

## Need and behaviour
| # | Measure | Source | Go | Change | Stop |
|---|---|---|---|---|---|
| 1 | Parents reporting 1+ evenings in the last 7 days when the child was stuck with no help | Survey Q5 | ≥50% | 25–49% | <25% |
| 2 | Target families spending Tk 2,000+ a month on tutoring or coaching | Survey Q4 | ≥50% | 25–49% | <25% |
| 3 | Trial students using it on 4+ of 6 days, unprompted (median days) | Trial logs | ≥4 days | 2–3 days | ≤1 day |

## SenseBook against a phone
| # | Measure | Source | Go | Change | Stop |
|---|---|---|---|---|---|
| 4 | **Must-pass.** Students who keep SenseBook over phone-plus-free-AI on the same stand, after 3 days of each | Trial day 7 | ≥60% *plan gate* | 40–59%: lead with a phone app plus stand; keep hardware for Access | <40%: stop student hardware |
| 5 | Parents choosing the device over a Tk 199/month app at their shown price | Survey Q10 | ≥50% | 25–49% | <25% |

## Willingness to pay
| # | Measure | Source | Go | Change | Stop |
|---|---|---|---|---|---|
| 6 | **Must-pass.** Parents placing a refundable deposit at Tk 14,990 | Parent guide, Part 5 | ≥30% *plan gate* | 10–29%, or ≥30% only at Tk 9,990: change price, financing or the school channel | <10% at every price |
| 7 | Median "too expensive" price | Parent guide Q15 | ≥Tk 15,000 | Tk 8,000–14,999 | <Tk 8,000 |
| 8 | Parents willing to pay Tk 300+ a month for the service | Parent guide Q16 | ≥40% | 20–39% | <20% |

Stated willingness overstates real payment. Only deposits and, later, real subscription payments count for the pilot gate.

## Reading quality (bench tests)
| # | Measure | Source | Go | Change | Stop |
|---|---|---|---|---|---|
| 9 | **Must-pass.** Bangla character error rate on unknown printed pages at the device's real view, whole spread | T1 | ≤2% *plan gate* | 2–5%, or fine only on the near half: raise or tilt the camera, read one page at a time, or read textbooks from the library text only | >5%: drop "reads any print" from the claims |
| 10 | **Must-pass.** Invented words per 1,000 words read | T1 | ≤1 | 1–5: add confidence checks and "unclear" flags | >5: unsafe for faithful reading with this model |
| 11 | Page recognition on indexed NCTB pages in home light | T1 or trial logs | ≥97% *plan gate* | 90–96% | <90% |
| 12 | Best Bangla voice: naturalness score and "would listen 30 minutes" | T2 | ≥3.5 and ≥70% | 3.0–3.4 or 50–69% | <3.0 for every voice |
| 13 | On-device Bangla voice on the Pi Zero 2 W, compute time per second of speech | T2 | ≤1.0 | 1.0–2.0: pre-generate or use the cloud, then redo the cost model | >2.0 and no cloud budget |

## Accessibility
| # | Measure | Source | Go | Change | Stop |
|---|---|---|---|---|---|
| 14 | **Must-pass (Access).** Blind testers attaching it alone in ≤15 s | Guide 02 Task A | ≥80% of attempts | 50–79%: redesign the grip or the cues | <50% |
| 15 | **Must-pass (Access).** Blind and low-vision testers completing read and ask tasks alone | Guide 02 Tasks B–C | ≥80% *plan gate* | 50–79% | <50% |
| 16 | Blind and low-vision testers who did a real reading task alone that normally needs help | Trial day 7 | ≥60% | 30–59% | <30% |

## Buyers, funders and cost
| # | Measure | Source | Go | Change | Stop |
|---|---|---|---|---|---|
| 17 | **Must-pass (Access).** Organisations giving a written letter of intent for 20+ units at Tk 15,000+ per reader (device, training, 2 years' service) | Guide 04 | 2 or more | 1, or only at a lower price | None after 10 asks |
| 18 | Schools agreeing to host a pilot or buy a reading-corner set | Guide 04 | 2 of 5 | 1 of 5 | None |
| 19 | AI and voice cost per active student a month, median use, **including voice for unknown pages** | T3 | ≤Tk 120 *plan gate* | Tk 121–250: fair use, on-device voice or price | >Tk 250 |
| 20 | Same, per Access reader a month (budget in the model: about Tk 125, from Tk 3,000 over 2 years) | T3 | ≤Tk 125 | Tk 126–400: raise the package price or cap cloud pages | >Tk 400 |

## How to decide
- **Learn track (students):** go only if 4, 6, 9 and 10 are all go. If 4 is "change", build the phone app plus stand first and keep the hardware for Access.
- **Access track (blind and low-vision readers):** go only if 9, 10, 14, 15 and 17 are all go.
- If a must-pass is "stop", stop that track or redesign it, and don't spend pilot money on it until a retest passes.
- Everything else: fix and retest within the next stage.
