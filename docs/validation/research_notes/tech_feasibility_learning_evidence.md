# Technical feasibility and learning evidence: AI read-aloud and voice tutor for printed Bangla/English textbooks

Research date: 27 November 2026. Every fact below has a source link, with publisher or authors and a date where the page gave one. "Vendor" means the number comes from the company selling the product. "Independent" means a third party measured it. Inferences are kept in their own sub-sections. A few studies are older than 2023, and each is flagged.

## 1. Bangla printed-text OCR accuracy (Google, Tesseract, multimodal LLMs, Bangla-specific OCR) and LLM hallucination

### Takeaway
No published benchmark tests Gemini Flash-Lite class models on phone photos of NCTB textbook spreads, so the targets (Bangla CER ≤2%, English ≤1%) have no evidence behind them yet. The best published LLM figure for Bangla document pages is about 4% CER, for Gemini 2.5 on scanned Wikisource pages, which are easier than phone photos. Tesseract Bangla sits around 8–12% CER. Independent 2026 studies show vision-language OCR has a specific risk: rare but serious failures, where the model adds plausible words, "corrects" spellings and invents text in unclear regions, while average CER still looks good.

### Cited Findings
**LLM / VLM OCR on Bangla**
- IndicVisionBench (Faraz, Akash, Khan, Kolla, Patidar, Goswami, Ravi, Khatri, Agarwal; arXiv preprint 2511.04727, 6 Nov 2025, no peer-reviewed venue). Bengali OCR on Wikisource scanned pages (printed and handwritten, community-proofread "Level-4" pages). Word and character error scores, lower is better: **Gemini-2.5: 11.30 word / 4.04 char**; GPT-4o 55.51 / 32.68; LLaMA-4 31.52 / 13.21; Gemma-3 42.15 / 24.41; Chitrapathak 17.14 / 7.03. The paper's text calls these ANLS scores, but the column headers say "↓" and the values behave like error rates, so the labelling is inconsistent. GPT-4o's OCR was "far below expectations". LLaMA-4's long, repetitive outputs inflated its errors — [arXiv 2511.04727](https://arxiv.org/html/2511.04727)
- BanglaWild (arXiv 2608.03884, 2026) compares Tesseract, EasyOCR, Surya, Gemini-2.5-Flash and Claude Sonnet 4.6 on Bengali **scene text**, not printed pages. Numbers not retrieved — [arXiv 2608.03884](https://arxiv.org/html/2608.03884)
- GlotOCR Bench (arXiv 2604.12978, 2026) is titled "OCR Models Still Struggle Beyond a Handful of Unicode Scripts". Bangla-specific numbers not retrieved — [arXiv 2604.12978](https://arxiv.org/pdf/2604.12978)

**Traditional and Bangla-specific OCR**
- BornoDrishti (Islam, Hasan, Ovi, Rabby, Rahman; Apurba Technologies; EACL 2026 Industry Track, pp. 278–286, March 2026). The metric is word-level Top-1 accuracy on word images, not CER. **Printed-only: Tesseract 73.49%, Apurba "Bengali OCR" (Rabby et al. 2024) 90.06%, BornoDrishti 94.7%.** Mixed printed and handwritten: Tesseract 57.56%, Rabby 2024 87.20%, BornoDrishti 83.77%. The paper names "conjunct forms" and visual variability as core Bangla difficulties. The model has about 86M parameters and runs at about 15 ms per word image on a T4 GPU, so it needs a GPU server. It states "The Government of Bangladesh will soon open-source the code". Demo at kagoj.ai. These are vendor-authored results — [ACL Anthology 2026.eacl-industry.20](https://aclanthology.org/2026.eacl-industry.20.pdf)
- The same paper cites earlier Bangla OCR results: a ViT+RoBERTa model (Hasan et al. 2024) at CER 0.07 / WER 0.12, and Apurba's 2021 CNN models with over 95% character recognition rate "across all document types" — [ACL Anthology 2026.eacl-industry.20](https://aclanthology.org/2026.eacl-industry.20.pdf)
- BRAC University study, "Benchmarking and enhancing Bengali OCR: a hybrid OCR system with AHP-based evaluation", on 216 real-world Bengali document images: **Tesseract CER 11.46%, EasyOCR CER 9.02%, best hybrid (including Google Vision API) CER 3.37%.** Taken from a search snippet only, because the repository page returned an error, so the date and authors are unverified — [BRAC University DSpace](https://dspace.bracu.ac.bd/items/e6d24067-9f43-4ef7-a3ed-55780048ed66)
- **Older (2019), flagged.** A BLSTM printed Bengali OCR paper tested 20 fonts: Tesseract 4.0 91.79% character accuracy (about 8.2% CER), Google Drive OCR 98.54% (about 1.5% CER), the authors' own method 99.32%. These were clean rendered fonts, not photos — [arXiv 1908.08674](https://arxiv.org/pdf/1908.08674)
- Google Cloud Vision on **handwritten** Bangla words: average CER 0.1389, against 0.1037 for the authors' hybrid model (Springer Discover AI, 2025) — [Springer s44163-025-00251-7](https://link.springer.com/article/10.1007/s44163-025-00251-7)
- bbOCR (Zulkarnain et al.; Bengali.AI / BRACU; arXiv 2308.10647, Aug 2023) is an open-source multi-domain Bengali document OCR pipeline with a new evaluation set. The abstract gives no figures — [arXiv 2308.10647](https://arxiv.org/abs/2308.10647)

**NCTB textbooks specifically**
- NCTB-SchoolText (Mendeley Data) is a Bangla/English corpus for Classes 1–10, built by running Tesseract on scans. The authors say direct text extraction from the NCTB PDFs was unreliable, and they hand-transcribed the Class 1–5 chapter boundaries because the tables of contents could not be OCR'd reliably. They publish only text, because of copyright — [Mendeley f3882ccczp](https://data.mendeley.com/datasets/f3882ccczp/1)
- NCTB-SchoolText-EN: 13,042 English-version pages with a residual "OCR garbage rate" of 0.7% — [Mendeley xwr5vy66nb](https://data.mendeley.com/datasets/xwr5vy66nb/1)
- BnMMLU (arXiv 2505.18951, 2025) OCR'd NCTB pages with EasyOCR Bengali and then cleaned them with gpt-3.5-turbo. No OCR accuracy figure is reported — [arXiv 2505.18951](https://arxiv.org/pdf/2505.18951)

**Hallucination in LLM/VLM OCR (independent, 2026)**
- Gardella, Mariño, Belzarena, Ramírez, Randall, Morel, "When Low CER is Not Enough" (arXiv 2607.24077, v1 27 Jul 2026, v3 17 Sep 2026), on historical Spanish documents from Uruguay:
  - VLMs beat traditional OCR on CER, but their **mean and median diverge**. Qwen 3.6 (reasoning mode) has a median CER of 1.72% and a mean of 11.17%, meaning occasional catastrophic pages. For comparison, Tesseract's mean CER was 10.87% (median 11.86%), and Surya-OCR had the lowest mean CER at 8.87%.
  - Failure modes: "spurious additions" (plausible text generated for unreadable regions, **even when the prompt says to output [illegible]**), extra names inserted into lists, inconsistent spelling "correction", and fluent semantic substitutions that change meaning while barely moving CER. Surya leaned towards English words when the image was ambiguous.
  - The authors call for metrics beyond CER.
  - [arXiv 2607.24077](https://arxiv.org/abs/2607.24077v3)
- Karamolegkou, Angleraud, Sagot, Clérice (Inria), "Reading or Guessing?" (arXiv 2605.27750v2, 7 Sep 2026). Five open VLMs, with Tesseract and Kraken as baselines, on Greek and Arabic editions:
  - VLM-only errors: repetition collapse (0.1–1.5% of pages) and off-script characters (Latin letters inside Arabic lines).
  - VLM substitutions were more often real words (Arabic: 44.5% for VLMs vs 21.9–34.3% for traditional systems), "consistent with prior-driven repair".
  - When the page text was deliberately perturbed, **VLM CER rose by +10.55 to +42.45 points, against +2.53 to +6.05 for traditional OCR**. The models type what language makes likely, not what is printed.
  - Recommendations: scan outputs for repetition, markup and off-script characters; run perturbation tests; keep human review where transcription matters.
  - [arXiv 2605.27750](https://arxiv.org/html/2605.27750v2)

### Inferences
- About 4% CER for Gemini 2.5 on scanned Bengali pages suggests ≤2% is reachable only with help: clean, flat, well-lit captures; a newer model; and post-checks. Treat ≤2% as an **untested target** until it is measured on real NCTB spreads photographed by the device.
- The "recognise known pages offline" design is the strongest defence against hallucination. For known pages, the device reads verified text, so the LLM is never asked to read the page. The LLM-OCR path for unknown pages needs guardrails, for example: run a second pass and compare the two; flag repetition or off-script output; and tell the student "I may have misread this page" when confidence is low.
- Perturbation results imply spelling and grammar exercises (deliberately wrong words, "find the mistake" tasks) are at high risk of being silently "corrected" by an LLM.
- Tesseract `ben` (about 8–12% CER, and about 73% word accuracy in BornoDrishti) is too weak to be the main OCR. It might still work as an on-device cross-check, but that is untested.
- Juktakkhor (conjuncts) are named as a core difficulty in recent work (BornoDrishti), but no study above gives a conjunct-specific error rate.

### Gaps
- No benchmark of any Gemini 3.x Flash-Lite model, or of GPT-4o-class models, on **phone or ultra-wide-camera photos of printed Bangla textbooks**, including curved pages, glare, low-quality newsprint paper and mixed Bangla-English pages.
- No published numbers on maths notation (Bangla numerals, fractions, equations) or on page-level mixed-script errors.
- No quantified hallucination rate for Bangla specifically.
- The full BRACU hybrid study could not be retrieved (HTTP 468), and the IndicVisionBench Table 10 (median CER/WER) was not read.
- The Bengali.AI OCR leaderboard and apurba/kagoj.ai accuracy on book pages were not found.

## 2. Bangla text-to-speech: cloud voices, open-source models, MOS scores, on-device feasibility

### Takeaway
Cloud Bangla TTS exists from Google (Gemini TTS, bn-BD listed as GA; Chirp 3 HD in bn-IN) and Microsoft (bn-BD Nabanita and Pradeep). The best open-source VITS Bangla models score MOS about 4.4–4.5 in academic tests, and Meta MMS-TTS scores much lower (3.66). No source shows any good Bangla neural voice running in real time on a Pi Zero 2 W. Piper reaches only about real time on a Pi 4, which is a much faster board.

### Cited Findings
**Gemini TTS**
- The Gemini API speech-generation docs (aistudio.google.com, read 27 Nov 2026) name `gemini-3.8-flash-tts` ("over 130 languages"), `gemini-3.8-flash-lite-tts` ("over 100 languages"), `gemini-3.1-flash-tts-preview` and `gemini-2.5-pro-preview-tts`.
  - The language table marks **Bangla supported (✔) for both 3.8 models**.
  - Input is text only and output is audio only. Streaming is supported (headerless 16-bit PCM, 24 kHz). Unary calls return WAV.
  - Up to 2 speakers per request.
  - No latency figure is published.
  - [Google AI Studio docs: speech generation](https://aistudio.google.com/docs/speech-generation)
- The Google Cloud Gemini-TTS docs list **Bangla (Bangladesh) bn-BD as GA**, with no bn-IN entry. Models listed: `gemini-3.1-flash-tts-preview`, `gemini-2.5-flash-tts`, `gemini-2.5-flash-lite-preview-tts`, `gemini-2.5-pro-tts`. Limits: 8,192 input tokens, about 655 s of audio per request, 4,000 bytes per text field. Other language versions of the page label bn-BD as "Preview", so the docs are inconsistent — [Google Cloud Gemini-TTS](https://docs.cloud.google.com/text-to-speech/docs/gemini-tts)
- One developer forum post reports a "No audio generated" error for Bangla with 2.5 Pro preview TTS in AI Studio. This is a single user report, not a confirmed bug — [Google AI Developers Forum](https://discuss.ai.google.dev/t/bug-no-audio-generated-error-when-using-bangla-bengali-in-speech-generation/138122)

**Google Cloud and Azure voices**
- Google Cloud Chirp 3: HD supports **Bengali (India) bn-IN**, with about 30 named voices (pattern `bn-IN-Chirp3-HD-<Name>`, e.g. Achernar, Kore, Puck), alongside older bn-IN WaveNet and Standard voices. GA in global, us, eu and several Asian regions — [Google Cloud Chirp 3 HD](https://docs.cloud.google.com/text-to-speech/docs/chirp3-hd)
- Microsoft Azure Neural TTS has **bn-BD-NabanitaNeural (female) and bn-BD-PradeepNeural (male)**, added in a batch of 49 new languages/variants (older announcement, not dated in the snippet) — [Microsoft Learn language support](https://learn.microsoft.com/en-my/AZURE/ai-services/speech-service/language-support); [Microsoft Tech Community](https://techcommunity.microsoft.com/t5/azure-ai/azure-speech-s-neural-tts-empowers-organizations-to-serve-users/ba-p/2920882)

**Open-source and academic MOS results (independent academic; different raters and test sets, so not directly comparable)**
- BanglaTalk (arXiv 2510.06188; ACL BanglaLP 2025): **VITS-Bengali male MOS 4.49, female 4.40; MMS-TTS-Ben 3.66** (about 22.7% lower). MMS outputs 16 kHz and VITS-Bengali 22.05 kHz — [ACL Anthology 2025.banglalp-1.4](https://aclanthology.org/2025.banglalp-1.4.pdf); [arXiv 2510.06188](https://arxiv.org/html/2510.06188v2)
- Custom VITS Bangla model (Springer, Discover Computing / Information Retrieval Journal, 2025): **MOS 4.01, against Google TTS 3.71 and Narakeet 3.65**, rated by 15 native speakers. This is one of the few head-to-heads against Google's Bangla voice. It is not clear which Google voice generation was tested — [Springer s10791-025-09701-3](https://link.springer.com/article/10.1007/s10791-025-09701-3)
- BanglaKontho (arXiv 2609.29146, 2026), a long-form VITS-based model: naturalness MOS 4.46 ± 0.06, against 4.90 for natural speech (ITU-T P.800, 50 utterances) — [arXiv 2609.29146](https://arxiv.org/pdf/2609.29146)
- Dhaka University Journal of Science benchmark (Tacotron2, FastSpeech2, VITS, Grad-TTS): VITS was best on quality but had the **slowest synthesis** — [Bangla JOL DUJS](https://www.banglajol.info/index.php/DUJS/article/view/84122/56752)
- BanglaBox (arXiv 2610.09211, 2026) is a phonetically balanced Bangla TTS corpus with zero-shot voice cloning. Numbers not retrieved — [arXiv 2610.09211](https://arxiv.org/pdf/2610.09211)

**On-device (Piper / espeak-ng) and Pi performance**
- Piper on a Pi 4 runs at "around 95% realtime" (RTF about 0.95) — [Snapcraft piper-tts](https://snapcraft.io/install/piper-tts/arch). Picovoice's benchmark puts Piper at RTF about 0.19 on a **Pi 5** — [Picovoice TTS benchmark](https://picovoice.ai/docs/benchmark/tts-piper-tts/)
- A Piper GitHub issue: on a Pi Zero 2 W the prebuilt binary worked, but the pip Python package crashed with an illegal instruction (SIGILL) — [rhasspy/piper issue #773](https://github.com/rhasspy/piper/issues/773)
- A community listing shows a Bengali Piper voice, "bn_BD-google-medium". No quality ratings were found, and the official piper-voices listing was not verified — [tts.ai Piper voices (bn)](https://tts.ai/voices/piper/?lang=bn)
- espeak-ng includes a Bengali dictionary (`bn_dict`), which Piper uses for phonemes. No published quality rating of espeak-ng Bangla was found — [Hugging Face espeak-ng-data bn_dict](https://huggingface.co/csukuangfj/vits-piper-en_US-glados/blob/main/espeak-ng-data/bn_dict)

### Inferences
- The Pi Zero 2 W uses the same Cortex-A53 core type as the Pi 3, at a lower clock, and it is slower than a Pi 4. If Piper medium is only about real time on a Pi 4, a VITS/Piper medium Bangla voice on the Zero 2 W is very likely **slower than real time**. That would break the 2–3.5 s time-to-first-audio target for anything but short sentences or a "low" quality voice. This needs a test on the device.
- A realistic on-device fallback is espeak-ng Bangla (robotic but tiny) or a Piper "low" voice. Natural-sounding Bangla probably needs the cloud, or audio pre-generated per known page and cached. Pre-generating audio once per known NCTB page means every student who reads that page reuses it, which spreads the cost.
- Chirp 3 HD covers bn-IN (Indian Bengali), not bn-BD. Accent and vocabulary fit for Bangladeshi students is untested. Gemini TTS bn-BD and Azure bn-BD are the Bangladesh-accent cloud options.

### Gaps
- No MOS study of Gemini 3.x TTS or Azure bn-BD voices for Bangla.
- No time-to-first-audio measurement for Gemini TTS in Bangla.
- No Pi Zero 2 W real-time factor for any Bangla neural voice.
- No listening test of Piper bn_BD.
- No study of TTS pronunciation of conjuncts, numerals or mixed Bangla-English text.

## 3. Bangla speech recognition: WER for Whisper, Google Chirp, Gemini audio, Bengali.AI; children, noise, code-mixing

### Takeaway
Bangla ASR differs widely between products. In a September 2026 independent benchmark that includes children's voices, Gemini 2.5 Flash batch reached 13.3% CER / 27.0% WER, while **Gemini's Live native-audio model streaming scored 69.6% CER**. Off-the-shelf Whisper large-v3 is poor (WER about 72–75%). Specialist APIs (Sarvam, Soniox) lead at about 7% CER. Sending student audio straight to a low-cost LLM is therefore a real accuracy risk and needs testing.

### Cited Findings
- **Riverborn Bangla speech-to-text benchmark v1.0** (Riverborn Limited, tested September 2026; prices checked 24 Sep 2026). 1,001 BanSpeech clips (SUST), about 50 min, 13 domains including **kids' voices and kids' cartoons**. It does not cover phone calls, heavy noise or code-switching. The authors build voice AI products but say they have no relationship with the tested providers.
  - Batch, CER / WER:
    - Sarvam saarika:v2.5: 6.9% / 18.2%
    - Soniox: 8.1% / 21.5%
    - Deepgram nova-3: 10.1% / 23.9%
    - **gemini-2.5-flash: 13.3% / 27.0%** (3.85 s mean latency)
    - ElevenLabs scribe_v1: 14.7% / 26.0%
    - **Google chirp_2: 21.9% / 41.4%**
    - **gpt-4o-transcribe: 28.7% / 45.1%**
    - **Groq whisper-large-v3: 30.7% / 71.7%**
  - Streaming:
    - Soniox: 7.4% CER
    - Sarvam: 9.0%
    - **gemini-2.5-flash-native-audio-preview-12-2025 (Live): 69.6% CER / 79.2% WER, final result 10.44 s after speech ended.** Gemini Live gave no interim results, and the adapter set no language hint.
  - Latency was measured from Bangladesh.
  - [GitHub riverbornai/bangla-speech-to-text-benchmark](https://github.com/riverbornai/bangla-speech-to-text-benchmark/tree/main)
- ShobdoSetu (arXiv 2603.19256, 2026), long-form Bengali: **Whisper large-v3 zero-shot WER 75.0**; a community whisper-medium Bengali fine-tune scored 34.8; full fine-tuning on the competition data reached 16.75%. The same base scored 44.68% on a small out-of-distribution set — [arXiv 2603.19256](https://arxiv.org/html/2603.19256)
- BuzzASR Bengali (Hugging Face model card; vendor): a fine-tuned Whisper-large-v3 reached combined WER 25.6% (FLEURS 31.97%, Common Voice 25: 19.42%). Zero-shot Whisper-large-v3 had a combined CER of 34.04% — [Hugging Face BuzzASR/bengali](https://huggingface.co/BuzzASR/bengali)
- Bengali.AI Speech Recognition (Kaggle, July–October 2023, US$53,000 prizes, out-of-distribution audio): the 3rd-place public WER was 0.405 — [Kaggle discussion](https://kaggle.com/c/bengaliai-speech/discussion/447961). The OOD-Speech test set has 23.03 h from 17 sources (TV drama, audiobooks, sermons and more) — [arXiv 2305.09688](https://arxiv.org/pdf/2305.09688)
- Gemini 3.5 Transcribe (reported by Gigazine, 27 Aug 2026): Google claims an average WER of 4.0% streaming and 2.6% batch across languages. This is a vendor claim with no Bengali breakdown — [Gigazine](https://gigazine.net/gsc_news/en/20260827-gemini-3-5-transcribe/)
- The Gemini Live API (Firebase AI Logic docs) lists **"Bengali (Bangladesh) bn-BD" among languages supported by all audio-generating models**. Live models "automatically choose" the response language, and they "do not support explicitly setting a response language". Use system instructions instead — [Firebase Live API configuration](https://firebase.google.com/docs/ai-logic/live-api/configuration)
- **Older (2023), flagged.** The Gemini 1.0 technical report gives an aggregate FLEURS WER across 62 languages: Gemini Pro 7.6% (15.8% without FLEURS training data), USM 11.8%, Whisper v3 17.6%. There is no per-language Bengali figure — [arXiv 2312.11805](https://arxiv.org/html/2312.11805v5)

### Inferences
- "Audio straight to the LLM" for spoken questions should be tested first. The cheapest path (Live native audio) was the worst performer for Bangla in the only independent benchmark found. The batch gemini-2.5-flash route was much better, but 27% WER is still high. One option is a 2-step path: a Bangla-strong ASR, then the LLM. Another is to judge LLM understanding directly by answer quality rather than transcript WER, since the LLM may understand intent despite a wrong transcript (untested).
- Spoken quiz answers are short and often a single word, and that suits a closed-vocabulary match (expected answer vs heard answer) better than open transcription. This is untested.

### Gaps
- No Bangla WER data for children in noisy homes, for Bangla-English code-mixing, or for regional dialects. The Riverborn benchmark excluded dialects, noise and code-switching.
- No Bengali-specific WER for Google Chirp 3 or Gemini 3.x audio.
- The winning Bengali.AI 2023 Kaggle WER was not found.
- One search snippet said a Bengali ASR paper found Chirp emitting Hindi, Arabic, Malayalam and Telugu tokens inside Bengali transcripts. The paper could not be identified, so this is unverified.

## 4. Gemini API: model names, Flash-Lite and TTS pricing (Nov 2026), Bengali in Live / native audio, announced 2027 changes

### Takeaway
The official pricing page, read on 27 Nov 2026, lists three Flash-Lite models and two GA 3.8 TTS models. **Both 3.8 TTS models double in price on 1 Jan 2027** (Flash-Lite TTS audio output goes from $6 to $12 per 1M tokens). TTS, not OCR or chat, is the main threat to a ~US$0.92 per student per month AI budget.

### Cited Findings (all from the official Google AI Studio / Gemini API pricing page, read 27 Nov 2026, no "last updated" date shown — [Gemini API pricing](https://aistudio.google.com/docs/pricing). Note: ai.google.dev/gemini-api/docs/pricing now redirects there.)

**Flash-Lite models, standard paid tier, per 1M tokens**

| Model ID | Input | Output | Batch (in / out) |
|---|---|---|---|
| `gemini-3.5-flash-lite` | $0.30 (text, image, video, audio) | $2.50 | $0.15 / $1.25 |
| `gemini-3.1-flash-lite` | $0.25 (text, image, video); $0.50 audio | $1.50 | $0.125 / $0.75 |
| `gemini-2.5-flash-lite` | $0.10 (text, image, video); $0.30 audio | $0.40 | $0.05 / $0.20 |

All three have a free tier.

**TTS models, per 1M tokens**

| Model ID | Text input | Audio output | From 1 Jan 2027 (in / out) | Batch now (in / out) |
|---|---|---|---|---|
| `gemini-3.8-flash-tts` | $0.50 | $9.00 (≈$0.00225 per 10 s of audio) | $1.00 / $18.00 | not noted |
| `gemini-3.8-flash-lite-tts` | $0.50 | $6.00 | $1.00 / $12.00 | $0.25 / $3.00 |
| `gemini-3.1-flash-tts-preview` | $1.00 | $20.00 | not noted | not noted |
| 2.5 Pro Preview TTS | $1.00 | $20.00 | not noted | not noted |

- 2.5 Flash Preview TTS: $10.00 audio output.
- The free tier covers the 3.8 TTS models. The truncated part of the page suggests no free tier for the 2.5 preview TTS models.

**Live / native audio, per 1M tokens**

| Model ID | Audio in | Audio out | Text in / out |
|---|---|---|---|
| `gemini-3.8-live`, `gemini-3.8-live-extended-thinking`, `gemini-3.1-flash-live-preview` | $3.00 ($0.005/min) | $12.00 ($0.018/min) | $0.75 / $4.50 |
| `gemini-2.5-flash-native-audio-preview-12-2025` | $3.00 | $12.00 | $0.50 / $2.00 |

- `gemini-3.5-transcribe-live`: audio input $3.50 ($0.005/min).

**Other changes announced on the page**
- From 1 Dec 2026, `gemini-2.5-flash` requests auto-route to `gemini-3.5-flash-lite`, and `gemini-2.5-pro` requests to `gemini-3.8-flash`.
- Gemini 4 Carbon and Argon prices roughly double on 1 Dec 2026.
- Gemini 3.8 Flash ($0.75 / $3.75) doubles on 1 Jan 2027.
- `gemini-2.5-flash-image` shuts down 15 Mar 2027.
- In the portion read, **no price change was announced for the Flash-Lite text/vision models**.

**Bengali support and third-party pricing sources**
- The Gemini 3.8 TTS models list Bangla as supported — [Google AI Studio speech generation](https://aistudio.google.com/docs/speech-generation). The Live API lists bn-BD for all audio-generating models — [Firebase Live API configuration](https://firebase.google.com/docs/ai-logic/live-api/configuration)
- Third-party write-ups agree on the 3.8 TTS doubling (e.g., Flash-Lite TTS about $0.54 per hour of audio now, about $1.08 per hour from 2027). These are secondary sources — [Neomanex](https://neomanex.com/news/gemini-3-8-flash-tts-flash-lite-tts-api-pricing); [OpenRouter](https://openrouter.ai/google/gemini-3.8-flash-lite-tts)

### Inferences (worked estimates; all are estimates)
- **Audio token rate.** Google's own "$0.00225 per 10 s at $9/M" implies 25 audio tokens per second. On that basis, 3.8 Flash-Lite TTS costs about **$0.54 per hour of speech now and $1.08 per hour from 1 Jan 2027** (Batch: $0.27 now, $0.54 from 2027).
- **TTS budget.** At about US$0.92 per student per month, and if the whole budget went to TTS at 2027 rates, that buys about **51 minutes of freshly generated speech per student per month**. Reading unknown pages and tutoring answers aloud would quickly use this up. Ways to stretch it:
  - Cache audio per known page and share it across students.
  - Use on-device TTS where quality allows.
  - Keep spoken answers short.
- **Spoken question via Live** (15 s in, 30 s out): about $0.00125 + $0.009, or **about $0.01 per question**. That means about 90 questions per month fills the whole budget.
- **Same question via a Flash-Lite call plus Flash-Lite TTS:**
  - Audio in to 3.1 Flash-Lite: about $0.0002.
  - Text out: about $0.0002.
  - 30 s of TTS: about $0.0045 now, $0.009 from 2027.
  - TTS again dominates.
- **OCR of an unknown page** with Flash-Lite is probably a fraction of a cent per page, but the image-token count for Gemini 3.x at the resolution needed for Bangla is not confirmed (see Gaps).
- **Model stability.** Model IDs change and old ones are auto-routed to new ones (e.g., 2.5 Flash routes to 3.5 Flash-Lite from 1 Dec 2026). The Bangla accuracy measured on one model may not carry over after an auto-route, so the device should pin model IDs and re-test after changes.

### Gaps
- Image-token counts per photo for Gemini 3.x Flash-Lite, and Bangla text tokenisation efficiency (tokens per Bangla word), were not found. Both are needed for an exact OCR cost.
- No published time-to-first-audio or latency figures for Gemini TTS or Live from Bangladesh.
- Free-tier rate limits were not retrieved.
- The rest of the pricing page after the visible sections, and any Flash-Lite price change announced elsewhere, were not checked.

## 5. Raspberry Pi Zero 2 W and Camera Module 3: prices, memory-driven price rises, on-device compute, battery life

### Takeaway
The Pi Zero 2 W is still US$15 list, and Raspberry Pi said in February 2026 that it does not expect Zero prices to change, because it holds years of LPDDR2 stock. The memory-driven rises hit Pi 4 and Pi 5 boards with 2GB or more. The Camera Module 3 Wide launched at $35 and stays in production until at least January 2030. The board draws about 0.5–0.6 W idle and up to about 2.5 W at full load. No source measures page detection or Bangla TTS on it.

### Cited Findings
**Prices and memory costs**
- Raspberry Pi, "More memory-driven price rises" (Eben Upton, 2 Feb 2026):
  - Increases apply to Pi 4/5 and CM4/CM5 with 2GB or more: +$10 for 2GB, +$15 for 4GB, +$30 for 8GB, +$60 for 16GB. The 1GB Pi 4 ($35) and 1GB Pi 5 ($45) are unchanged.
  - "We don't anticipate any changes to the price of Raspberry Pi Zero, Raspberry Pi 3, and other older products, as we currently hold several years' inventory of the LPDDR2 memory that they use."
  - The post does not mention the Zero 2 W by name or the Camera Module 3.
  - [Raspberry Pi News](https://www.raspberrypi.com/news/more-memory-driven-price-rises/)
- The official Pi Zero 2 W page describes a "$15 computer" (no price in the buy box): quad-core 64-bit Cortex-A53 at 1 GHz, 512 MB SDRAM, 2.4 GHz 802.11n Wi-Fi, BT 4.2, CSI-2 camera connector, micro-USB power, in production until at least January 2030 — [Raspberry Pi Zero 2 W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/)
- Third-party claims, unverified:
  - Six rounds of price rises on other boards between October 2025 and November 2026.
  - A Pi Hut tracker showing the Zero 2 W at £12.00 on 25 Nov 2026, unchanged.
  - "Availability is the real problem" (substrate shortage).
  - One outlier article claims $25, which contradicts the official statement.
  - [magazin Mehatronika 2026 guide](https://magazinmehatronika.com/en/the-2026-raspberry-pi-pricing-and-buying-guide/); [raspberry.tips](https://raspberry.tips/en/raspberrypi-tutorials/raspberry-pi-price-increase-ai-boom-alternatives)
- Camera Module 3 launch (Raspberry Pi News, 9 Jan 2023, older but the official price source): **standard $25, Wide $35, NoIR $25, NoIR Wide $35.** Wide field of view is 102° horizontal (120° diagonal). Minimum focus is about 5 cm for Wide and about 10 cm for standard (staff comment) — [Raspberry Pi News](https://www.raspberrypi.com/news/new-autofocus-camera-modules/)
- The current official Camera Module 3 page says "from $25": Sony IMX708, 11.9 MP (4608×2592), phase-detection autofocus, in production until at least January 2030 — [Raspberry Pi Camera Module 3](https://www.raspberrypi.com/products/camera-module-3/)
- Retail examples: Hackster lists the CM3 Wide at $37.95, and Elektor at €39.95 (out of stock) — [Hackster](https://hackster.io/products/buy/102464); [Elektor](https://www.elektor.com/products/raspberry-pi-camera-module-3-wide)

**Power draw**
- Idle: about 120 mA at 5 V (600 mW) on stock Pi OS Lite, and 92.7 mA with services disabled — [CNX Software, 9 Dec 2021](https://www.cnx-software.com/2021/12/09/raspberry-pi-zero-2-w-power-consumption/) (older)
- Idle about 100 mA, up to about 500 mA with all four cores maxed (stress-ng 370–460 mA). Disabling cores roughly halves draw — [Jeff Geerling, 2021](https://www.jeffgeerling.com/blog/2021/disabling-cores-reduce-pi-zero-2-ws-power-consumption-half/) (older)
- Hackster measured a peak of nearly 3 W under its test load — [Hackster review](https://www.hackster.io/news/raspberry-pi-zero-2-w-review-hands-on-with-the-fastest-zero-ever-b85b155905a5) (older)
- No measured Camera Module 3 draw was found — [CNX Software](https://www.cnx-software.com/2021/12/09/raspberry-pi-zero-2-w-power-consumption/)

### Inferences (estimates, untested)
- **Battery life.** A 2,000 mAh Li-ion cell at 3.7 V holds about 7.4 Wh, or about 6.3–6.7 Wh after a 5 V boost converter at 85–90% efficiency. With an average draw of about 1.0–1.5 W (Pi mostly idle with Wi-Fi on, short camera bursts, a small speaker amp), that gives roughly **4–6.5 hours of active use**. At sustained full load (about 2.5 W or more, e.g. on-device neural TTS) it drops to about 2.5 hours. The camera and amplifier draws are assumptions, not measurements.
- **Memory.** 512 MB RAM is tight for a VITS model plus a camera pipeline. Classical page recognition (downscaled image, perceptual hash or ORB features, matched against a local index of known pages) is plausible on a Cortex-A53, but no benchmark was found. Treat it as an engineering test item.
- **Price risk.** The Zero 2 W price risk looks low for now (official LPDDR2 stock statement, Feb 2026). Supply availability is the stated risk in third-party sources.
- **Focus at 11 cm.** The Wide module's ~5 cm minimum focus covers the planned ~11 cm distance. A 102° horizontal view across a full spread at 11 cm means low pixels per character at the page edges, plus lens distortion. Whether that resolves small Bangla text and matras well enough is untested.

### Gaps
- No published benchmark of page detection, OCR or TTS on a Pi Zero 2 W.
- No measured power for Camera Module 3 or a full device.
- No 2026 primary source on Zero 2 W stock levels in Bangladesh or local (Tk) prices.

## 6. Learning evidence: AI tutors (RCTs 2023–2026), spaced repetition and retrieval practice, read-aloud/TTS, over-reliance harms

### Takeaway
Rigorous evidence for structured AI tutoring is positive but varied:
- Nigeria: about 0.23–0.3 SD in 6 weeks.
- Ghana (Rori, WhatsApp maths): about 0.36 SD.
- Harvard physics: about 0.63 SD (short-term).
- Khanmigo in Tennessee: only about 0.06–0.08 SD per year, with low student engagement.

Unguarded "answer-giving" AI can harm learning: −17% on an unassisted exam in a Turkish RCT. Retrieval practice and spacing are among the best-supported classroom techniques (g ≈ 0.3–0.5). TTS/read-aloud helps students with reading difficulties modestly (d ≈ 0.35). No rigorous AI-tutor learning RCT from Bangladesh, India or Pakistan was found.

### Cited Findings
**AI tutor trials**
- **World Bank Nigeria** ("From Chalkboards to Chatbots", De Simone, Tiberti, Barron Rodriguez, Manolio, Mosuro, Dikoru; Policy Research Working Paper 11125, 2025):
  - Design: 6-week after-school programme (June–July 2024) in Benin City, Edo State, using Microsoft Copilot (GPT-4), with teacher guidance, randomised.
  - **English effect 0.23 SD.** About 0.031 SD per extra day attended (LATE).
  - Outperformed about 80% of interventions in a database of developing-world education RCTs.
  - The authors cannot separate the chatbot from the whole package (prompts, teachers, peers).
  - [World Bank Open Knowledge](https://openknowledge.worldbank.org/entities/publication/15e1ff08-15ae-4f7a-b2a8-d146e6c113ee/full); [EconPapers](https://econpapers.repec.org/RePEc:wbk:wbrwps:11125)
  - The World Bank blog (9 Jan 2025) gives an overall gain of about 0.3 SD ("nearly two years of typical learning"). Girls, who started behind, appeared to gain more, and the benefits reached all students, not only the highest achievers. Long-term effects are unknown — [World Bank Blogs](https://blogs.worldbank.org/en/education/From-chalkboards-to-chatbots-Transforming-learning-in-Nigeria)
  - The sample size and cost per student were not retrieved.
- **Rori, Ghana** (Henkel et al.; arXiv 2402.09809, 2024; WhatsApp maths tutor, grades 3–9):
  - Effect 0.37 SD (v1, about 1,000 students, 11 schools); 0.36 SD in the later version (about 500 students).
  - Year 1 only.
  - The authors say results "should be interpreted judiciously".
  - [arXiv 2402.09809](https://arxiv.org/abs/2402.09809?); [Stanford SCALE](https://scale.stanford.edu/publications/effective-and-scalable-math-support-experimental-evidence-impact-ai-math-tutor-ghana)
  - A follow-up RCT is registered (AEARCTR-0014476) — [AEA registry](https://www.socialscienceregistry.org/trials/14476)
- **Harvard physics** (Kestin, Miller et al., "AI tutoring outperforms in-class active learning", Scientific Reports, 3 Jun 2025):
  - Design: crossover RCT, 194 undergraduates.
  - Results: linear-regression effect 0.63 SD (the authors say a ceiling effect means this underestimates it), p < 10⁻⁸; median learning gain more than double; 49 vs 60 minutes.
  - Limits: short-term, 2 topics, 1 institution, college students.
  - [PMC12179260](https://pmc.ncbi.nlm.nih.gov/articles/PMC12179260/); [Harvard Gazette, Sep 2024](https://news.harvard.edu/gazette/story/2024/09/professor-tailored-ai-tutor-to-physics-course-engagement-doubled/)
  - The quantile-regression effect size was not verified.
- **Khanmigo** (Oreopoulos and Low, "One Click Away", NBER Working Paper w35620; 2-year cluster RCT in 18 Tennessee middle schools, 2024–26, remedial maths):
  - **+1.3 percentile ranks per term, about 0.06–0.08 SD per year**; implied 0.14 SD for a full year of active use. Similar to Khan Academy practice without AI.
  - 96% of students tried it, but the median student messaged it on a third of practice days and in 17% of sessions where they made a mistake.
  - Not peer-reviewed.
  - [NBER w35620](https://www.nber.org/papers/w35620); [Hechinger Report](https://hechingerreport.org/proof-points-khanmigo-math-ai-tutor/)
- **Turkey high school maths, harm without guardrails** (Bastani et al., "Generative AI without guardrails can harm learning", PNAS 122(26) e2422633122, 2025):
  - About 1,000 students in grades 9–11.
  - GPT-4 access raised practice scores by 48% (GPT Base) and 127% (GPT Tutor).
  - **GPT Base students scored 17% lower on the unassisted exam**. The guardrailed GPT Tutor largely avoided the harm.
  - [IDEAS/RePEc](https://ideas.repec.org/a/nas/journl/v122y2025pe2422633122.html); [Knowledge at Wharton](https://knowledge.wharton.upenn.edu/article/without-guardrails-generative-ai-can-harm-education)
- **19-university trial** (arXiv 2611.19099, 2026): a pre-registered RCT across 19 universities, spring 2025 to spring 2026, reports that instructor-designed AI improved learning. Only the abstract-level claim was seen and the numbers were not verified — [arXiv 2611.19099](https://arxiv.org/html/2611.19099)

**Over-reliance (mostly preprints or observational)**
- Oregon State preprint "Why Johnny Can't Think" (arXiv 2601.22430, Jan 2026): students who trusted and routinely used genAI reported lower cognitive engagement — [arXiv 2601.22430](https://arxiv.org/html/2601.22430v1)
- UTS report (March 2026): unstructured AI use is especially risky for school students who are still building foundations — [UTS](https://www.uts.edu.au/news/2026/03/experts-warn-unstructured-ai-use-in-schools-risks-cognitive-atrophy/contentassets/ai-cognitive-offloading-and-implications-for-education.pdf)
- Hechinger coverage of a June 2026 working paper: speed gains appeared only on problems that could be handed to AI, and they disappeared under supervision. Causality is unconfirmed — [Hechinger Report](https://hechingerreport.org/?p=117043)

**Retrieval practice and spacing (meta-analyses)**
- Classroom quizzing as retrieval practice: **Hedges' g = 0.50** (Yang et al. 2021, Psychological Bulletin; cited in reviews) — [Springer Educational Psychology Review](https://link.springer.com/10.1007/s10648-021-09595-9)
- Classroom spacing meta-analysis (Mawson and Kang, 2025): 22 reports, 31 effect sizes, N > 3,000, **d = 0.54** for distributed over massed practice — [White Rose eprints](https://eprints.whiterose.ac.uk/id/eprint/229807)
- Mathematics: spaced vs massed practice, **g = 0.28** (27 studies, 53 effect sizes) — [PMC10950551](https://pmc.ncbi.nlm.nih.gov/articles/PMC10950551)
- Spaced vs massed retrieval, mostly lab studies: g = 0.74 — [search result; Springer s10648-020-09572-8](https://link.springer.com/10.1007/s10648-020-09572-8)
- Bego and Lyle (2024): spaced retrieval across nine introductory STEM courses; effects depend on format and feedback — [International Journal of STEM Education](https://link.springer.com/article/10.1186/s40594-024-00468-5)

**Read-aloud / TTS**
- Wood, Moxley, Tighe, Wagner (Journal of Learning Disabilities, online 2017 / print 2018; **older**): TTS and read-aloud for students with reading disabilities, 22 studies, **d = 0.35** (95% CI 0.14–0.56) — [PMC5494021](https://pmc.ncbi.nlm.nih.gov/articles/PMC5494021); [ASHA Evidence Map](https://apps.asha.org/EvidenceMaps/Articles/ArticleSummary/8f7b9dd3-41fb-48c6-86a5-3e25ad47bc7b)
- Clinton-Lisell (2023): reading while listening vs reading alone, 30 studies, **trivial overall benefit** — [ERIC EJ1403866](https://files.eric.ed.gov/fulltext/EJ1403866.pdf)
- A 2023 primary study (ages 8–12) in Annals of Dyslexia found TTS improved comprehension. Students with dyslexia benefited more than students with reading and language impairment — [PubMed 37119436](https://pubmed.ncbi.nlm.nih.gov/37119436/)
- **Older (2014).** Buzick and Stone meta-analysis of the read-aloud test accommodation: larger effects for reading than maths, and larger for students with disabilities — [British Library catalogue](https://eld.bl.uk/catalog/100025055220_0x000001)

**South Asia**
- The only South Asian AI-tutor-adjacent RCT found is a registered Bangalore trial (about 430 students, grades 6–8) whose outcomes are anxiety, depression and growth mindset, not achievement — [ClinicalTrials.gov NCT07316647](https://clinicaltrials.gov/study/NCT07316647)

### Inferences
- The positive trials (Nigeria, Ghana, Harvard) share **structure**: curriculum-tied prompts, teacher or programme scaffolding, and tutors designed not to hand out answers. The disappointing or harmful ones (Khanmigo engagement, GPT Base in Turkey) show what happens when students can skip effort or simply opt out. A book-tied device that quizzes from the page and gives hints before answers matches the evidence-backed design pattern. This alignment is an inference and does not show the device will work.
- The effect sizes above come from different ages, subjects, durations and comparisons. They should not be quoted as an expected SenseBook effect.
- Read-aloud evidence is strongest for weak or struggling readers and weak for typical readers. Positioning read-aloud as support, not a substitute for reading, fits the evidence.
- Spaced spoken quizzes are the most evidence-backed feature. The classroom effect sizes come from teacher-run quizzing, though, not voice devices at home.

### Gaps
- No RCT of an AI voice tutor, or any LLM tutor, measuring learning in Bangladesh or India.
- No evidence on screen-free or voice-only AI tutoring for children.
- Nigeria sample size and cost per student not retrieved (PDF too large; blog gave neither).
- Harvard quantile-regression effect size not verified (PMC page blocked).
- No evidence on Bangla-medium read-aloud effects.

## 7. Can a phone app do the same? Phone capture quality and existing phone AI tutors (Gemini Live camera, ChatGPT voice/vision, Google Lens/Socratic) for Bangla

### Takeaway
Gemini Live on phones supports Bengali, and camera sharing exists (launched April 2025). The only independent Bangla test of Gemini's Live native-audio model found very poor Bangla transcription (69.6% CER). gpt-4o-transcribe was also weak on Bangla (45% WER), and GPT-4o was the weakest of the big models on Bengali document OCR in IndicVisionBench. No source evaluates Bangla textbook page capture or tutoring through these phone apps.

### Cited Findings
- Beebom (undated India launch report): Gemini and Gemini Live launched in nine Indian languages, including Bengali — [Beebom](https://beebom.com/gemini-live-supports-indian-languages)
- Gemini Live camera and screen sharing rolled out in April 2025, at first for paid subscribers on compatible Android devices and for all users on Pixel 9 and Galaxy S25. Gemini Live conversations were reported in over 45 languages, but whether Bengali is included in camera mode was not confirmed — [Android Authority](https://androidauthority.com/gemini-live-camera-screen-sharing-features-rolling-out-3542168); [Google Blog](https://blog.google/products/gemini/gemini-live-android-tips/)
- Gemini Live live captions are reported to support 30+ languages, including Bengali — [Beebom Gadgets](https://gadgets.beebom.com/news/google-gemini-live-adds-real-time-captions-android-ios)
- Gemini Live native-audio model on Bangla, streaming: **69.6% CER / 79.2% WER** (Riverborn, Sep 2026; no language hint set) — [GitHub riverbornai benchmark](https://github.com/riverbornai/bangla-speech-to-text-benchmark/tree/main)
- OpenAI gpt-4o-transcribe on Bangla: 28.7% CER / 45.1% WER batch, 24.6% / 42.4% Realtime — [GitHub riverbornai benchmark](https://github.com/riverbornai/bangla-speech-to-text-benchmark/tree/main)
- GPT-4o Bengali document OCR: 55.51 word / 32.68 char error scores, compared with Gemini-2.5's 11.30 / 4.04 (IndicVisionBench, Nov 2025) — [arXiv 2511.04727](https://arxiv.org/html/2511.04727)

### Inferences
- A phone app could use the same cloud models, so model quality alone gives a dedicated device no edge. The device's possible advantages lie elsewhere, and all are untested assumptions:
  - Fixed camera geometry over the book.
  - No screen distraction.
  - A shared family device instead of a personal smartphone.
  - Curriculum-indexed known pages with verified text and cached audio, which removes OCR errors and TTS cost for known pages.
  - Guardrailed tutoring, given the Bastani harms.
- Without those, general phone assistants inherit the weak Bangla voice-recognition results above.
- Handheld phone photos of a spread vary in angle, blur and shadow. A clip-on fixed camera should give more consistent input, but no study compares them.

### Gaps
- No evaluation of Google Lens Bangla OCR, Socratic, ChatGPT vision or Gemini Live camera on printed Bangla textbook pages.
- No data on Bangla support in ChatGPT Advanced Voice.
- No current status of Google's Socratic app was retrieved.
- No study comparing phone-captured with fixed-mount document photos for Bangla OCR accuracy.
- No data on smartphone access or ownership among Bangladeshi students; that falls to another research track.
