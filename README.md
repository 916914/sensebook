# SenseBook

**Printed books that talk back.** SenseBook is a webcam-sized, screen-free AI reading companion. It grips the top of any open book like a tiny tripod. It:

- reads the pages aloud;
- explains and discusses them in Bangla and English;
- tests the reader and reminds them what to revise.

It works on a table or in the hands, through its speaker, wired headphones or Bluetooth earbuds. It is built for secondary students in Bangladesh and, from day one, for blind and low-vision readers.

> **Status: prototype and venture plan (November 2026).** Nothing here is a finished or certified product. Prices, costs, volumes and performance figures are planning estimates from desk research, not measurements. Hardware has not yet been built or tested on real books.

## How it attaches: the tri-grip
- **Front blades:** two wafer-thin spring-steel blades slide inside the front and back covers, one on each side of the spine, under the pages.
- **Rear leg:** a third leg presses on the back of the spine.
- **Fit:** a light spring adapts to any book from a thin booklet to about 6 cm thick.
- **Pages:** nothing touches them, so they turn freely, and the device moves with the book.
- **On a table:** it stands as a tripod.
- **Folded:** a small baton about 10 × 4 × 3.5 cm.

See [design/SenseBook_Attachment_Plan.md](design/SenseBook_Attachment_Plan.md).

## What's in this repository
| Folder | Contents |
|---|---|
| [docs/](docs/) | Venture plan and product specification (PDF and Word) |
| [finance/](finance/) | Financial model (Excel, formula-driven: change the blue cells) |
| [design/](design/) | Attachment plan, industrial design, CAD source and 3D-print files, renders, image-generation prompts; earlier explored concepts in `archive_v0_lamp_and_stem/` |
| [prototype/hardware/](prototype/hardware/) | Prototype bill of materials, wiring diagram, pin map, assembly guide, test checklist |
| [prototype/software/](prototype/software/) | Device and companion-app software (Python): page following, faithful read-aloud, Ask, two-voice Chapter Talk, quizzes with spaced repetition, memory, reminders, seamless page turning |
| [tools/](tools/) | Hub-site builder and publishing scripts |

## Try the software on a laptop
```bash
cd prototype/software
python -m venv .venv && .venv/Scripts/pip install -r requirements.txt   # Windows; use .venv/bin/pip on macOS/Linux
python -m sensebook --mode dev --provider mock --fake-camera             # offline demo, no keys needed
python -m pytest -q                                                      # 72 tests
```
To use real AI, copy `.env.example` to `.env` and add your own Gemini API key. **Never commit `.env`.** Raspberry Pi set-up is in [prototype/software/README.md](prototype/software/README.md).

## Licences
- Software: **Apache-2.0**
- Hardware design: **CERN-OHL-W-2.0**
- Documents, images and data: **CC BY 4.0**

Details in [LICENSE](LICENSE); full texts in [LICENSES/](LICENSES/).

## Safety and privacy notes
- **Prototype only.** It is not certified (BTRC, CE, FCC). Li-ion batteries need protection circuits and care.
- **Privacy:**
  - The microphone records only while Ask is held, and there is a hardware mute switch.
  - Learning memory is off until a guardian enables it, and memory is stored on the device.
  - Captures are deleted after use unless you choose to keep them.
- **AI output can be wrong.** SenseBook keeps faithful reading separate from AI explanation, and says when something isn't on the page.
