# Illustration style

Drawings for OpenRPMS.
The line is the Civic Studio ink-and-wash family, in `~/workspace/civic-studio-org/handbook/illustration-style-ink-and-wash.md`.
The subject is ours: a health system, seen the way a map is seen, from far away to up close.

## The style

- Black ink line, loose and hand-drawn.
- Two watercolour pigments only: a soft let-down sage green, and a cool grey-blue.
- Lots of white paper, no background wash, no shadows.
- No text, no letters, no numbers, no logos, no readable screens.
- People are allowed when the layer is about people.
  Draw them as staff at work, small in the frame, faces only suggested.
  Never a portrait of a real person, and never a patient who can be recognized.
- The subject is the thing that layer is about, drawn plainly.

Sage green is the project's accent, in place of the Civic Studio orange.
Everything else stays fixed, so a drawing from any layer reads as one family.

There is a second register for texture only.
It is a quiet photograph of a clinic or a hospital, with a person at the center of the frame, documentary rather than posed.
No logos, no readable text, no brand on the clothing.
Use it as atmosphere.
Do not use it to explain a workflow or a system.
Explanation stays in ink.

## Zoom

Think of the pictures as one map at five altitudes.
Farther out is place and feeling.
Closer in is the work, then the system, then the path a person walks.

| Layer | Altitude | What a drawing shows |
| --- | --- | --- |
| Place | Farthest | A clinic and a hospital, and the people who work there: front desk, scheduler, nurse, physician. One place, a few figures, lots of paper. |
| Needs | Far | What the work is for, as objects on a desk: the book of appointments, the chart, the tools of an exam, a lab tube. Scheduling, the record, a careful diagnosis. |
| Stack | Middle | The technical stack as a still life: a small server, a terminal, a database volume, a desktop window, a browser window. No labels. |
| Flow | Near | One person's path, left to right, as four stations: the desk, the exam room, the lab, the pharmacy shelf. |
| Texture | Atmosphere | A photograph. A clinician in a clinic or on a hospital floor, human, unhurried, no signage you can read. |

Place and texture both include a person.
Needs, stack, and flow are objects.
A page uses one altitude.
It does not mix a photograph and an ink drawing in the same row.

## The prompt

Every ink prompt is the fixed style block plus one subject sentence.
Change only the subject, and the aspect.

```text
Loose black ink pen drawing with watercolor washes on pure white paper, two pigments only: a soft let-down sage green and a cool grey-blue. <SUBJECT>. Lots of white paper, no background wash, no shadows. No text, no letters, no numbers, no logos.
```

Add "A few staff figures, small in the frame, faces only suggested" when the layer is Place.
Leave people out of Needs, Stack, and Flow.

Aspect: 3:2 for a half-width hero, 1:1 for a card, 2:3 for a tall margin drawing.

The texture prompt is separate:

```text
A quiet documentary photograph in a clinic, natural window light, a clinician at work and clearly the subject, unhurried and respectful. Soft sage and cool grey in the room. No logos, no readable text, no brand marks, no posed smile at the camera.
```

## Subjects

Place.
A small rural clinic and, beyond it, a low hospital wing, drawn as one loose scene: a front desk, a scheduler with an open book, a nurse in a doorway, a physician at a bedside. Figures small, faces only suggested.

Needs.
A clinic desk as a casual still life: an open appointment book with blank pages, a paper chart folder, a stethoscope, a small lab tube in a rack, a blank prescription pad.

Stack.
A casual still life of the stack: a small server box, a terminal with a dark empty screen, a squat database volume, a desktop window standing open, a browser window beside it, a short cable between them.

Flow.
Four stations in a row on one sheet of paper, left to right: a reception desk, an exam table, a lab rack with a few tubes, a pharmacy shelf. White paper between the stations. No arrows.

Texture.
A nurse standing at a clinic counter in late-afternoon window light, seen from a few paces away, the room quiet around them.

## Working drawings

Drawings stay out of the repository until one is chosen for a page.
Make the Needs still life first, and edit later drawings from that file.
For an offset background, keep a wide empty field on one side.
The useful subjects so far are the open book, the chart folders, and the stethoscope, or one small figure at a desk with a blank face and simple hands.
The keyed WebP is trimmed to the ink.
The JPEG keeps the empty field.
In dark mode, lay the keyed drawing on a paper-coloured sheet.
The white of the book pages is keyed out, and on a dark page those openings would become black gaps.

## Generate, key, and save

1. Generate the Needs drawing first.
   It is the style anchor.
   Every later ink drawing is an edit of that file, so the line and the two pigments stay put.
2. Key the white paper out, so the pigment sits on the page, and save as WebP:

   ```
   magick <name>.jpg -fuzz 8% -transparent white -trim +repage \
     -bordercolor none -border 20 -resize '1200x800>' PNG32:/tmp/<name>.png
   cwebp -q 85 -alpha_q 100 /tmp/<name>.png -o <name>.webp
   ```

   A grey box around the drawing means the white was not keyed.
   Use a lower fuzz if the sage wash starts to disappear.
3. Keep each prompt beside its image, outside the site, until a drawing is chosen.
4. The photograph is not keyed.
   It keeps its background.
   Do not lay it under body text.

## On the page

- Multiply an ink drawing onto the page, with no paper texture behind it.
- In a row of cards, give every drawing the same height.
- In dark mode, lay the drawing on a paper-coloured sheet, because black ink vanishes on a black page.
- The photograph is a full-bleed band or a single hero, never a repeating texture, and never the only way a page explains itself.
