# 4. Image prompts: people using SenseBook (exact version)

For the owner to run in an image generator (ChatGPT, Gemini, Midjourney or similar). Every rule about the device comes from the build chat's CAD model and renders in `sensebook/design/`.

Save each chosen image under its file name in `website/public/photos/` (.jpg, .png or .webp), or send it in the website chat.

---

## Step 1. Attach these four reference images to every prompt

From `sensebook/design/renders/`:

1. `01_hero.jpg`: the device over an open book, seen from the reader's front-left
2. `02_front.png`: the front face, from the reader's side
3. `03_side.png`: the side view, showing how the unit leans forward over the book
4. `04_top.png`: the buttons from above

Then start the prompt with this sentence:

> Use the attached images as the exact design of the device called SenseBook. Copy its shape, proportions, colours, buttons and the way it attaches to the book exactly. Do not redesign it.

## Step 2. Paste blocks A, B, C and D, then the scene, then block E

### A. The device, exactly

> SENSEBOOK, THE DEVICE:
> - One small unit: a rounded rectangular box, matte slate-teal (dark blue-green grey, close to #46595C), 9 cm long, 4 cm deep, 3.5 cm tall, with softly rounded corners. Same colour all over; the lower part of the front face is a sloped band in a slightly darker shade.
> - Front face (the long side that faces the reader): four tiny white dots in a row at the left, a small square grid of speaker holes at the right, nothing else. No screen, no display, no logo, no text.
> - Lens: one small round black camera lens with a thin white ring around it, centred on the sloped lower front edge, pointing down and towards the pages at about 55 degrees.
> - Top face: one large round marigold-yellow button (close to #E9A33C), slightly raised, in the centre and nearest the reader. Just behind it, a small slate pill-shaped button. On the left of the top face a small round slate button marked with a left-pointing triangle; on the right, one marked with a right-pointing triangle.
> - Left end of the unit: two small oval slate buttons and a tiny slide switch with an orange mark. Right end: a small USB-C port and a round headphone socket.
> - The unit sits on a small slate tilt joint on top of a slim brushed-aluminium stick, about 1 cm thick, with one slate collar halfway up.
> - The stick rises from a small slate block (the clamp). From the clamp, two thin flat brushed-steel blades, 8 mm wide, reach forward into the book. A short slate rear leg reaches backwards and ends in a flat T-shaped pad with a black rubber underside.
> - It looks like a finished, well-made consumer product, about the size of a deck of cards on its side.

### B. Where it sits on the book (do not change)

> PLACEMENT, EXACTLY:
> 1. The book lies open in front of the reader with its spine running straight away from the reader. The reader is at the bottom edge of the pages (the near edge).
> 2. SenseBook stands at the FAR edge of the book (the top edge, opposite the reader), exactly in line with the spine. It is never at the near edge, never at a side edge, never standing on the pages.
> 3. The clamp sits just beyond the top edge of the book. The two steel blades slide into the book inside the front and back covers, one each side of the spine; only about 2 cm of each blade shows at the top edge. The rear leg points away from the reader and its T-shaped pad lies flat behind the book.
> 4. The stick stands straight up from the clamp. The unit sits on top, about 12 cm (one hand-width) above the pages, its long side parallel to the top edge of the book and centred over the spine, leaning slightly forward over the pages.
> 5. The front face (four dots, speaker holes, lens) faces the reader. The marigold button is on top, on the side nearest the reader.
> 6. Scale: the unit is about half the width of one page. The whole device is only a little taller than a standing paperback. One device per book.
> 7. No cables unless the scene says so. If there is an earphone, its thin cable runs from the right end of the unit to the reader's ear.

### C. Camera, so the device is always visible

> CAMERA: a candid photo taken from the reader's front-right, about 45 degrees to the side, at the reader's seated eye height, 1 to 1.5 metres away. From this angle we see the reader's face in three-quarter view, both open pages, and the front face and top of SenseBook (the four dots, the lens ring and the marigold button). The whole device is inside the frame, uncropped and in sharp focus. Keep the person, book and device near the centre so the image can also be cropped to a tall 4:5 frame.

### D. Style

> STYLE: documentary photograph, 35 mm lens, natural available light, real skin texture, unretouched, slight film grain, true-to-life colours, gentle background blur. Real places in Bangladesh, real clothes, real objects, a little everyday mess. Not glossy, not CGI, not an advertisement. The person is absorbed in what they are doing and does not look at the camera. Text on the pages is soft and not readable.

### E. Do not (paste at the end, or use as a negative prompt)

> DO NOT: put a screen or display on the device; turn it into a phone, tablet, lamp, webcam or robot; add glowing beams, holograms or sci-fi lighting (the only light is the small soft white ring round the lens); add logos or writing on the device; add extra buttons; move the device to the near edge, a side edge or onto the pages; make it float; turn its front away from the reader; make it large; show more than one device on one book; close the book; add cables other than one earphone cable where asked; give anyone extra or missing fingers; make skin look plastic; make anyone look at the camera.

## Step 3. Check before you keep an image

- [ ] Device at the far (top) edge, in line with the spine, front facing the reader
- [ ] Stick straight up, unit leaning slightly forward, lens on the lower front edge looking down
- [ ] Round marigold button on top, nearest the reader; arrow buttons left and right of it
- [ ] Four white dots at the left of the front, speaker holes at the right, no screen, no logo
- [ ] Slate-teal colour, small size, one device per book
- [ ] Hands with five fingers, faces natural, nobody looking at the camera

If only the device is wrong, keep the picture and use the tool's edit or inpaint feature on the device alone, again with the reference images attached.

---

## The scenes

Each scene goes between blocks D and E.

### SenseBook page header

**File:** `header.jpg`. Landscape 16:9. The site shows it as a wide 2:1 strip, so keep the girl, the book and the device in the middle band of the picture, with nothing important near the top or bottom edge.
> SCENE: Dusk, a modest home in Dhaka. A 16-year-old Bangladeshi girl in a simple cotton kameez sits at a wooden desk by a window. Her physics textbook lies open on the desk in front of her, spine pointing away from her, with SenseBook at its far edge as described. Her right index finger rests on the marigold button on top of the unit (she reaches forward over the book to press it); her left hand holds a pencil on the left-hand page. She is listening, eyes on the page, focused. Soft blue dusk light from the window on her left, a warm desk lamp on the right. The soft white ring round the lens glows faintly. Framing: wide shot; girl on the left half of the frame, book and device in the centre and right; the device sharp and clearly visible in the middle band of the frame, not near the top edge.

### One product. Different lives.

All four: landscape 4:3.

**1. The student in a remote village.** File: `life-village.jpg`.
> SCENE: Night in a rural tin-roofed home in Bangladesh. A 15-year-old girl in a simple cotton salwar kameez sits cross-legged on a woven mat on the floor. A physics textbook lies open on a low wooden stool in front of her, spine pointing away from her, with SenseBook at its far edge as described. She has just pressed the marigold button with her right index finger and is listening, pencil in her left hand above the page, concentrating. One small rechargeable LED lamp on the floor to her right lights the scene; a bamboo wall and a steel water jug behind her in soft darkness. The lens ring glows softly on the page. Camera at her front-right at her eye height, low to the floor.

**2. The university student.** File: `life-university.jpg`.
> SCENE: Daytime in a busy university library in Dhaka, tall shelves behind. A 21-year-old Bangladeshi engineering student, short dark hair, checked shirt, sits at a long wooden table. A thick engineering textbook with diagrams lies open in front of him, spine pointing away from him, with SenseBook at its far edge as described. A thin white earphone cable runs from the right end of the unit to his right ear. He looks at a diagram on the page with a focused, questioning expression, listening. An open notebook with handwritten notes lies to the right of the book. Daylight from tall windows on his left. Other students softly blurred in the background.

**3. The student who is blind.** File: `life-blind.jpg`.
> SCENE: Daytime in an ordinary Bangladeshi school classroom. A 16-year-old girl who is blind, in school uniform (white kameez, navy scarf), sits at her desk among sighted classmates. The same printed textbook as her classmates lies open on her desk, spine pointing away from her, with SenseBook at its far edge as described. Her right hand reaches forward over the book and her fingertips rest on the marigold button; her left hand rests flat on the left-hand page. Her head is tilted slightly as she listens, with a small smile; her eyes are relaxed and looking down, not at the device. A folded white cane leans against the side of her desk. Classmates in the softly blurred background read the same book. Natural daylight from windows on her left. Ordinary and respectful, not sentimental.

**4. The lifelong learner.** File: `life-lifelong.jpg`.
> SCENE: Early morning in a home in Dhaka. A Bangladeshi man in his late forties with greying hair and reading glasses, in a light cotton shirt, sits at a small wooden table by a window, a cup of tea to the right of the book. A book on economics lies open on the table in front of him, spine pointing away from him, with SenseBook at its far edge as described. He is asking it a question: mouth slightly open mid-sentence, eyebrows raised with curiosity, left hand lifted slightly, eyes on the page. Plants and a bookshelf softly blurred behind, warm morning light from the window on his left.

### Six ways SenseBook could transform society

All six: landscape 3:2.

**1. Democratising personalised education.** File: `way-1-villages.jpg`.
> SCENE: Late afternoon in a village in rural Bangladesh. A 13-year-old girl sits on the concrete steps of a small house holding a schoolbook open on her knees, spine pointing away from her, with SenseBook at its far edge as described (the stick rises straight up from the top edge of the book she holds). She is listening and looking at a diagram on the page. Rice fields and palm trees softly blurred behind her, a goat at the edge of the frame. Golden light.

**2. Reducing educational inequality.** File: `way-2-inequality.jpg`.
> SCENE: Evening in a small, modest apartment in Dhaka. A 12-year-old boy sits at the family's only table doing maths homework. His maths textbook lies open in front of him, spine pointing away from him, with SenseBook at its far edge as described. He is pressing the marigold button and asking it a question, pencil in his other hand. Behind him, softly blurred, his mother cooks at a small gas stove and glances over. No tutor in the room. Warm, everyday, real.

**3. Normalising inclusive education.** File: `way-3-inclusive.jpg`.
> SCENE: Daytime in a Bangladeshi school classroom. Two 14-year-old girls sit side by side at the same bench, sharing a laugh while they study the same textbook. The girl on the left is blind, with a folded white cane beside her; the girl on the right is sighted. Each has her own copy of the book open in front of her, spine pointing away from her, and each book has its own SenseBook at its far edge as described (two devices, one per book). Camera in front of them and to the right, at their eye height, so both devices show their front faces. Other students softly blurred.

**4. Developing a generation of independent thinkers.** File: `way-4-thinkers.jpg`.
> SCENE: Daytime in a university library. Three Bangladeshi students around a table in a lively discussion. The young woman in the middle has a book open in front of her, spine pointing away from her, with SenseBook at its far edge as described, and points at a passage on the page. The young man on the left counts points on his fingers; the young woman on the right listens with a sceptical smile. Only one book, with one device. Shelves and daylight behind. Camera at the front-right of the woman with the book.

**5. Creating a lifelong learning society.** File: `way-5-lifelong.jpg`.
> SCENE: Soft morning light on the veranda of a village house beside a green rice paddy in Bangladesh. A farmer in his fifties in a lungi and cotton shirt sits on a low wooden bench with a printed manual on modern rice farming open on his lap, spine pointing away from him, with SenseBook at its far edge as described (stick straight up from the top edge of the manual). He listens closely, one hand flat on the page. A bicycle leans against the veranda post; the paddy is softly blurred behind.

**6. Building Bangladesh's technological capabilities.** File: `way-6-capability.jpg`.
> SCENE: A small, bright electronics lab in Dhaka. Two young Bangladeshi women and one young man work at a long workbench assembling SenseBook units. On the bench: several open slate-teal shells, small green circuit boards, a soldering iron in its stand, tweezers, a magnifying lamp. At the right of the bench, one finished SenseBook stands assembled on its stick, clipped to the far edge of an open book exactly as described, its front face towards the camera. The engineers are focused on their hands, not looking at the camera. Camera at the front-right of the bench, at standing chest height.
