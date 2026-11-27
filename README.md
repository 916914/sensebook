# SenseBook

**Knowledge, now conversational.** · **বই এখন কথা বলে**

SenseBook is personal learning technology: a small, screen-free companion that clips onto a printed book. Turn the page of your own textbook: it reads it aloud, explains the hard parts and quizzes you on it, in Bangla and English, hands-free. A blind student and a university student use exactly the same SenseBook: every function works by touch and sound.

> **Why it exists: understanding should never be a privilege.** Two students can read the same textbook and get two different educations: one can ask a tutor, the other is alone with the page. In Bangladesh, 49.8% of children aged 7–14 could not show foundational reading skills (MICS 2025), and 76.5% of secondary students rely on tutors or coaching (Education Watch 2023). We want every reader to have someone to learn with.

> **Status: prototype and plan (November 2026).** Nothing here is a finished or certified product.
> - **Evidence:** our own desk validation concluded *"Change, then test. Don't tool hardware yet."*
> - **Testing:** nobody has been interviewed, and no hardware has been built or tested on real books.
> - **Figures:** prices, costs and performance figures are planning estimates unless a source is given.

**Hub site:** https://sensebook-hub.vercel.app · **Brand guide:** [brand/guide/SenseBook_Brand_Guide.pdf](brand/guide/SenseBook_Brand_Guide.pdf)

## What it does
- **Follows the page:** it notices a page turn, waits for the page to settle, and carries on. No buttons.
- **Reads aloud:** the reader voice reads your textbook from verified text, and says when it isn't sure. Reading other print is still in testing.
- **Explains:** hold Ask. After a bell, a different voice, the explainer, helps in Bangla or English. AI help never sounds like the book.
- **Quizzes and reminds:** spoken quizzes on what you just read, with spaced revision reminders.
- **Works in the hands or on a table:** through its speaker, wired headphones or Bluetooth earbuds. Downloaded textbooks are read without internet; questions need internet.

## One product, three ways to reach a reader
| | What | Who pays |
|---|---|---|
| **SenseBook Personal** | Your own SenseBook | Readers and families |
| **SenseBook Commons** | Shared SenseBooks in schools, libraries and learning centres | Institutions |
| **SenseBook Access Fund** | Funded access, covering the device, training, maintenance and service, starting with blind and low-vision students | CSR teams, foundations, NGOs, donors |

Every route gets the same device, software and design. There is no separate or "charity" edition.

## How it attaches: the tri-grip
- **Front blades:** two wafer-thin spring-steel blades slide inside the front and back covers, one on each side of the spine, under the pages.
- **Rear leg:** a third leg presses on the back of the spine.
- **Fit:** a light spring is designed to grip books from a thin booklet to about 6 cm thick. This is still to be bench-tested.
- **Pages:** nothing touches them, so they turn freely, and the device moves with the book.
- **On a table:** it stands as a tripod.
- **Folded:** a small baton about 10 × 4 × 3.5 cm.

See [design/SenseBook_Attachment_Plan.md](design/SenseBook_Attachment_Plan.md).

## What's in this repository
| Folder | Contents |
|---|---|
| [docs/](docs/) | Venture plan and product specification (PDF and Word) |
| [docs/validation/](docs/validation/) | Independent desk validation: report, claims register, evidence and a field-test kit |
| [docs/pitch/](docs/pitch/) | Pitch deck and one-page summary (PDF) |
| [brand/](brand/) | Positioning, name check, brand guide, logo, colour, type, icons, sound and tactile identity |
| [finance/](finance/) | Financial model (Excel, formula-driven: change the blue cells) |
| [design/](design/) | Attachment plan, industrial design, CAD source and 3D-print files, renders, 3D viewer; earlier concepts in `archive_v0_lamp_and_stem/` |
| [prototype/hardware/](prototype/hardware/) | Prototype bill of materials, wiring, pin map, assembly guide, test checklist |
| [prototype/software/](prototype/software/) | Device and companion-app software (Python): page following, faithful read-aloud, Ask, two-voice Chapter Talk, quizzes with spaced repetition, memory, reminders |
| [tools/](tools/) | Hub-site builder and publishing scripts |

## Try the software on a laptop
```bash
cd prototype/software
python -m venv .venv && .venv/Scripts/pip install -r requirements.txt   # Windows; use .venv/bin/pip on macOS/Linux
python -m sensebook --mode dev --provider mock --fake-camera             # offline demo, no keys needed
python -m pytest -q                                                      # the automated tests
```
To try a real AI provider, copy `.env.example` to `.env` and add your own key. **Never commit `.env`.** Before any child uses SenseBook, the AI provider's terms must allow use by under-18s (see the validation report). Raspberry Pi set-up is in [prototype/software/README.md](prototype/software/README.md).

## Licences
- Software: **Apache-2.0**
- Hardware design: **CERN-OHL-W-2.0**
- Documents, images, brand and data: **CC BY 4.0**
- Fonts in `brand/type/fonts`: **SIL Open Font License**

Details in [LICENSE](LICENSE); full texts in [LICENSES/](LICENSES/).

## Safety, privacy and honesty
- **Prototype only:** not certified (BTRC, battery safety, CE, FCC). Li-ion batteries need protection circuits and care.
- **Privacy:**
  - The microphone records only while Ask is held, and there is a hardware mute switch.
  - Page images and question audio are sent to a cloud AI provider to answer questions, and a light shows when anything is sent.
  - Learning memory is off until a guardian turns it on, and is stored on the device.
- **AI can be wrong:** SenseBook keeps faithful reading separate from AI explanation and says when something isn't on the page. Check important facts with your teacher.
- **What we never claim:** see [brand/POSITIONING.md](brand/POSITIONING.md#8-claims-we-must-never-make).
