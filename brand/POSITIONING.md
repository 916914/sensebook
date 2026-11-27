# SenseBook positioning

Version 1, 27 November 2026. Built from the venture plan, the product spec and their cited desk research. Nothing here comes from customer interviews yet: the product validation work in `docs/validation/` will replace the hypotheses below with real findings, and this page will be updated to match.

## 1. Target customer

**Who uses it**

| User | Situation |
|---|---|
| **Class 6–10 students** studying NCTB textbooks (Bangla and English versions) | Study alone at home in the evening, often after a full day of school and coaching. |
| **Blind and low-vision readers**: students in integrated schools first, then adults | Need to read the same printed books as everyone else, on the same day, without a sighted helper. |

**Who buys it**

| Buyer | Why they pay | Plan estimate |
|---|---|---|
| **Parents** in urban, connected homes who already pay for private tuition | Help every evening, in every subject, for less than a few months of one tutor | About 1.0 million serviceable students (estimate from public statistics; the pilot must replace it) |
| **Sponsors**: CSR teams, NGOs, donors, disability programmes | Independent reading for blind students, with an impact they can report | 40 sponsored readers in the pilot, 1,340 by Year 3 (plan target) |
| **Private schools and coaching centres** (from Year 2) | Reading corners and inclusive classrooms | Second channel |

The first buyer the plan goes after is the sponsor (Access track); the revenue engine is the parent (Learn track). Every device is accessible, so one brand serves both.

## 2. The problem, as we expect to hear it

These are our hypotheses in plain words. They are **not quotes**. Real words from interviews will replace them.

- **Student:** stuck on one paragraph or diagram late at night, with nobody to ask; the textbook gives one explanation and that is all.
- **Parent:** spends a lot on tutors and guidebooks and still can't tell whether the child understands; worries that a phone means Facebook and games, and that AI will do the homework.
- **Blind or low-vision reader:** classmates get their books in January, accessible copies arrive late and often without the maths and science notation; phone apps need someone sighted to set them up and a steady hand to aim.
- **Everyone:** power cuts and weak Wi-Fi hit exactly when students study.

What the plan's sources already show (see section 6):
- 76.5% of secondary students have a private tutor.
- Braille textbooks are delayed every year.
- Bangladesh has roughly 750,000 to 1 million blind people and more than 6 million with some visual impairment.

## 3. The category we compete in

**A reading companion for printed books** (বই পড়ার সঙ্গী).

Not an edtech app, not a gadget, not a talking pen, not a general chatbot. The book stays the interface: the reader turns real pages and SenseBook follows.

We choose this category because it lets us win where we are strong (the printed page, hands-free, touch and sound, offline textbooks) and avoid a fight we would lose (a free AI app on a phone the family already owns).

How each buyer will file us:
- **Parents:** next to the private tutor. That is the budget we draw from.
- **Sponsors:** next to imported reading aids for blind people, at one-sixth to one-quarter of their price.

## 4. The main alternative

**A smartphone with a free AI app** (Gemini Live, ChatGPT with the camera) is what we must beat. It is free, already owned and very capable. The plan rates "families decide a free phone app is good enough" as its top risk (high likelihood, high impact).

Where SenseBook wins against it:
- no aiming or holding: it rides on the book and follows the pages;
- no screen, so no feeds or games;
- textbooks recognised offline and read through power cuts;
- buttons a blind reader can find by touch;
- faithful reading kept apart from AI explanation;
- child-safe, with no open web and no ads.

Where the phone wins: price, ownership and breadth. We don't claim otherwise.

The budget alternative is the **private tutor** (about Tk 4,000 a month per tutor, anecdotal): human judgement and motivation, but not every evening, not every subject.

## 5. The one promise

> **Open any printed book. SenseBook reads the page exactly as printed, then helps you understand it.**
>
> **যেকোনো ছাপা বই খুলুন। সেন্সবুক পাতাটা হুবহু পড়ে শোনায়, তারপর বুঝতে সাহায্য করে।**

Public headline (from the venture plan): **বই এখন কথা বলে** · *Printed books that talk back.*

## 6. Reasons to believe (sources only)

| Reason | Source |
|---|---|
| Families already pay for help: 76.5% of secondary students have a private tutor | The Daily Star, 2023: https://www.thedailystar.net/node/3578376 |
| Blind students wait: braille textbooks are delayed and often miss notation | The Business Standard, 2025: https://www.tbsnews.net/node/1124151 |
| The need is large: roughly 750,000 to 1 million blind people, 6 million+ with some visual impairment | IAPB, national survey 2020: https://www.iapb.org/fr/blog/bangladesh-fresh-evidence-on-blindness-and-visual-impairment/ |
| Every textbook page can be prepared in advance: NCTB publishes its textbooks online in Bangla and English versions | Dhaka Tribune, 2026: https://www.dhakatribune.com/bangladesh/399732/online-versions-of-2026-textbooks-published-on |
| Reading aids for blind people cost $2,500–4,250 abroad; Access is planned at Tk 16,990 | OrCam MyEye price: https://www.maxiaids.com/product/myeye-pro; Access price is a plan hypothesis |
| AI is now affordable for a family product: about Tk 113 per student per month at median use (**estimate**) | Gemini API pricing, Nov 2026: https://aistudio.google.com/docs/pricing; finance/SenseBook_Financial_Model.xlsx |
| Cloud-only devices die with their company; SenseBook publishes a no-bricking promise and an offline core | The Register, 2024: https://theregister.com/2024/12/16/moxie_cloud_services_lessons/; venture plan section 8 |
| Anyone can check how it works: software, hardware and documents are open source | This repository (Apache-2.0, CERN-OHL-W-2.0, CC BY 4.0) |
| The prototype software exists and its automated tests pass on a laptop with a mock AI | prototype/software (real AI calls and real hardware not yet tested) |

## 7. Proof we still need

None of these is proven yet. The plan sets the targets before the pilot.

| Proof | Target | When |
|---|---|---|
| Students prefer it to a phone set-up after two weeks of each | ≥60% | P1 home trials |
| Blind and low-vision users finish tasks on their own | ≥80% | P1 and pilot |
| Blind testers attach it alone | under 15 seconds | Tri-grip bench test |
| The tri-grip holds real books without slipping | all 30 test books | Bench test |
| Page recognition on indexed textbooks in real homes | ≥97% | Pilot |
| Read-aloud accuracy (character error) | ≤2% Bangla, ≤1% English | Pilot |
| Students keep using it (3+ days a week at week 6) | ≥40% | Pilot |
| Understanding improves against a comparison group | effect size ≥0.2 | Independent study |
| Families pay at the target price | ≥30% | Pilot deposits |
| AI cost per active student | ≤Tk 120 a month | Pilot |

## 8. Claims we must never make

Until a pilot measures it, and even then only as measured:

1. **Grades:** no "improves grades" or "boosts exam results".
2. **People:** no "replaces your tutor" or "replaces your teacher". Say: "help every evening, between lessons".
3. **Accuracy:** no "100% accurate" and no "never makes mistakes". Say: "AI can make mistakes. Check important facts with your teacher."
4. **Every book:** no "fits every book". Say: "designed for books from a thin booklet to about 6 cm thick".
5. **Offline:** no "works fully offline". Say: "downloaded textbooks, read-aloud, bookmarks and reminders work without Wi-Fi".
6. **Privacy:** no "nothing leaves the device". Say: "the microphone records only while you hold Ask".
7. **Endorsements:** no NCTB, BTRC, government, school or NGO approval or partnership until it is signed.
8. **Co-design:** no "built with blind students" until co-design has happened. Say: "designed from day one for blind and low-vision readers".
9. **Origin:** no "Made in Bangladesh" until it is. "Assembled in Dhaka" only once it is.
10. **Invented evidence:** no invented users, testimonials, quotes, ratings or user counts; no AI-generated people presented as real users.
11. **Comparisons:** no "better than OrCam" or any untested comparison.
12. **Health:** no medical or vision claims. SenseBook does not treat anything.
13. **Pity:** no portraying blind readers as helpless or as charity cases.

## 9. Positioning statements

**One line**

> SenseBook is a screen-free reading companion that sits at the top of any printed book, reads the page aloud exactly as printed and helps you understand it, in Bangla and English.

> সেন্সবুক এক পর্দাহীন পড়ার সঙ্গী, যা যেকোনো ছাপা বইয়ের মাথায় বসে পাতা হুবহু পড়ে শোনায় আর বাংলা ও ইংরেজিতে বুঝিয়ে দেয়।

**One paragraph**

> For secondary students in Bangladesh who study alone from printed textbooks, and for blind and low-vision readers who wait months for accessible books, SenseBook is a reading companion that clips onto the top of any open book. A phone app must be aimed and held, and most families can afford a tutor only a few evenings a week. SenseBook needs neither: it follows the pages as they turn, reads exactly what is printed, and explains what is hard in Bangla or English, through its speaker or the reader's own earphones. The book's words and the AI's explanation always sound different, so the reader knows which is which. It is designed so a blind reader can use every function by touch and sound, it keeps reading downloaded textbooks without Wi-Fi, and it is open source.

> বাংলাদেশের যে মাধ্যমিক শিক্ষার্থীরা ছাপা পাঠ্যবই নিয়ে একা পড়ে, আর যে দৃষ্টিপ্রতিবন্ধী ও স্বল্পদৃষ্টির পাঠকেরা প্রবেশযোগ্য বইয়ের জন্য মাসের পর মাস অপেক্ষা করেন, তাঁদের জন্য সেন্সবুক এক পড়ার সঙ্গী, যা যেকোনো খোলা বইয়ের মাথায় আঁকড়ে বসে। ফোনের অ্যাপকে তাক করে ধরে রাখতে হয়, আর বেশির ভাগ পরিবার সপ্তাহে কয়েক সন্ধ্যার বেশি গৃহশিক্ষক রাখতে পারে না। সেন্সবুকে এর কোনোটাই লাগে না: পাতা ওল্টালে সে-ও সঙ্গে চলে, যা ছাপা আছে ঠিক তা-ই পড়ে শোনায়, আর কঠিন জায়গাটা বাংলা বা ইংরেজিতে বুঝিয়ে দেয়, নিজের স্পিকারে বা পাঠকের ইয়ারফোনে। বইয়ের কথা আর এআই-এর ব্যাখ্যা সবসময় আলাদা কণ্ঠে শোনায়, তাই পাঠক বোঝেন কোনটা বইয়ের, কোনটা ব্যাখ্যা। এমনভাবে নকশা করা যে একজন দৃষ্টিহীন পাঠক স্পর্শ আর শব্দ দিয়েই সব কাজ করতে পারেন; ডাউনলোড করা পাঠ্যবই ওয়াই-ফাই ছাড়াও পড়ে চলে; আর পুরোটাই ওপেন সোর্স।

## 10. How to use this page
- Every public sentence about SenseBook should trace back to the promise (section 5) and survive the never-say list (section 8).
- A number is used only with its source, and an estimate is labelled as an estimate.
- When validation findings arrive, update sections 2, 6 and 7 first.

Text licensed CC BY 4.0.
