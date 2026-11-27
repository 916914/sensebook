# One-week trial plan

**Goal:** in one week, with about 15 households, measure the five things that decide the venture: whether students come back without being pushed, whether they prefer SenseBook to a phone, whether parents will pay, whether Bangla reading is good enough, and whether blind readers can use it alone. **Cost:** about Tk 45,000 plus the bench tests (estimate). **Status:** not yet run.

## What to test with
Use whatever is ready, and say which in the results:
1. **Dev-kit SenseBook** (Pi Zero 2 W, camera, audio, tri-grip), if built; or
2. **Phone-on-stand SenseBook:** a phone or webcam on a stand at the device's height and angle, running the prototype software from `prototype/software/`.

The comparison arm uses the **same stand** with a phone running a free AI assistant with camera and voice (for example Gemini Live or ChatGPT voice), set up by the team. The comparison must be fair: same stand, same earphones, same help on day 1.

## Three bench tests first (no participants, 1–2 weeks, about Tk 5,000)
Run these before the trial. If T1 fails, the trial still runs, but read-any-print is not shown to participants.

**T1. Bangla reading at the device's real view.**
- Pages: 10 NCTB Bangla-version pages (with a table, a diagram, an equation and a conjunct-heavy paragraph), 10 English-version pages, 5 non-NCTB Bangla books, 3 newspaper pages, 2 handwritten-address letters.
- Capture at the device geometry: lens about 11–12 cm above the spine at the top edge, looking down at about 55°, ultra-wide lens (or the closest phone lens). Repeat at 18 cm. Light: daylight, a ceiling tube light, and a single lamp during a power cut.
- Ground truth: the NCTB PDFs for textbook pages; type the others by hand.
- Measure: character error rate (CER) for the near half and the far half of the spread separately; **invented words** (text that isn't on the page) per 1,000 words, counted separately from missed words; numbers and units read wrong.
- Why: the design analysis puts resolution at the reader's edge of the spread at about **74 dpi** at 9 cm and **99 dpi** at 18 cm for a textbook spread, and 77 dpi at 18 cm for a large 46 × 30 cm spread (`design/cad/out/analysis_results.json`). OCR is usually run at 200–300 dpi. This is the riskiest number in the product.

**T2. Bangla voice listening test.**
- 10 listeners (at least 5 blind or low-vision, mixed ages) hear the same 2-minute NCTB passage in 5–6 voices: two cloud voices, the planned Gemini TTS voice, one open-source neural voice running on a Pi Zero 2 W, and espeak-ng.
- Measure: naturalness score 1–5 (mean opinion score); 5 comprehension questions; "Could you listen to this for 30 minutes?" (yes or no); for the on-device voice, seconds of compute per second of speech on the Pi (real-time factor).

**T3. Cost meter.**
- Run 20 hours of scripted, realistic use (reading known and unknown pages, questions, quizzes, one chapter talk) through the real AI provider. Log every request.
- Measure: taka per hour of use, **including speech for unknown pages read aloud** (the current cost model leaves this out), and the share of answers voiced on the device.

## The one-week home trial
**Participants:** 10 sighted students (Class 6–10, both versions, at least 4 without a tutor) and 5 blind or low-vision readers (at least 3 students). Guardian consent for all minors.

**Design, sighted students:** a crossover. Each student uses one set-up on days 1–3 and the other on days 4–6, in random order (toss a coin). Day 7 is the exit visit.

**Design, blind and low-vision readers:** SenseBook for all 6 days, compared with their own current method on the same reading tasks on day 1 and day 7.

| Day | What happens | Who | Time |
|---|---|---|---|
| 0 | Home visit: consent, baseline interview (guide 01 or 02), set-up, 10-minute training, baseline 10-question quiz on a chapter the student will study this week | Team | 60 min |
| 1–6 | Normal studying. No reminders from the team. The software logs sessions automatically. Each evening a 3-question voice note or SMS: "Used it today? How long? One thing that helped or annoyed you." | Student | 2 min a day |
| 3 | Phone call: any breakage, charging or set-up problems. Switch arms for sighted students on day 4 (team visit or guided call). | Team | 10 min |
| 7 | Exit visit: delayed quiz on the same chapter (new questions, same topics); preference question; exit interview; the parent price questions and deposit test (guide 03, Parts 4–5); blind readers repeat the attach, read and ask tasks | Team | 60 min |

**What to log automatically (from the software)**
- Sessions per day; minutes; pages read; known vs unknown pages; questions asked; quizzes taken; reminders set; errors (no internet, page not seen, hand over text).
- Never log question audio or page images beyond the trial's consent. Delete captures after the trial.

**What to ask on day 7**
1. "If you could keep only one for the next month, which would you keep, and why?" (sighted students)
2. "What did you use it for that you couldn't do before?"
3. "What made you not use it on the days you didn't?"
4. Blind readers: "Which reading task this week did you do alone that you'd normally need someone for?"
5. Parents: price questions and the deposit test.

## How to judge the results
Compare every number with [07_Go_Change_Stop_Thresholds.md](07_Go_Change_Stop_Thresholds.md). Write a one-page result for the owner with the numbers, three quotes and the decision for each threshold. One week shows novelty as well as habit, so a "go" here earns the 100-unit pilot, not a launch.

## Common mistakes to avoid
- Helping participants more than a real customer would get.
- Trialling only with families who already love technology.
- Counting polite interest as demand. Only use, preference after both options, and deposits count.
- Testing reading only on clean textbook pages under good light.
