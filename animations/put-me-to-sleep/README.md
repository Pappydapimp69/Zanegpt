# Put Me To Sleep

A six-movement 3D piece, adapted from the transcript of a short narrated video.

Everything is generated at runtime — no textures, models, or audio files. The
plants, the leaves (serrated, because the story turns on leaf serration), the
character, the dream photographs, the room and the node lattice are all built
procedurally with three.js and canvas-drawn textures. The score is synthesised
with the Web Audio API against the same clock.

## The trip

A hand-rolled post chain — two full-screen passes and a ping-pong pair of
render targets, no addons: frame feedback (zoomed, spun and hue-rotated),
a kaleidoscopic fold, two domain warps, chromatic split and hue cycling.

**It belongs to the dreams and nothing else.** Movements I-III render straight
— the chain is bypassed outright, not set to zero — and the effects arrive
with the shudder at 1:47, the moment the app breaks. They peak through the
dreams and phase back out from 2:16, so the room and the network are clean
again.

The window is `TRIP_ONSET`/`TRIP_FULL` and `TRIP_OUT`/`TRIP_CLEAR`.

The **Trip** slider in the transport runs 0-100 and is remembered per viewer;
at 0 the chain is bypassed entirely and the picture renders straight.
`prefers-reduced-motion` caps it at 30 and slows the cycling.

## The score

Original, generated, no samples. A six-voice detuned pad through a lowpass
filter and a procedurally built convolution reverb, plus a motif on a slow
grid, a brown-noise bed, and one-shot cues tied to the picture.

It walks A major (the balcony) down to F# minor as the app goes to sleep,
pulls apart into a detuned tritone for the dreams, settles on D minor for the
room — where the percussion is dozens of irregular keystrokes — and opens into
bare fifths on D for the network, bringing the opening motif back transposed.

Audio needs a user gesture, so the piece opens on a title card with a Begin
button. `Sound on/off` is in the transport. `Narration on/off` reads the
captions with the browser's own speech synthesis; it is off by default and
disables itself where unsupported.

**With narration on, the film waits for the voice.** Rather than letting the
next caption cancel the line still being spoken, the clock creeps toward the
next cue at a twelfth speed and stops just short until the utterance ends,
plus a short beat. A line cut off mid-sentence is worse than a slower film, so
the runtime stretches to fit the reading. An 18-second cap per line means a
voice that never reports finishing cannot stall the piece, and where no voice
exists at all the gate never engages.

## Movements

| # | Title | Runs |
|---|-------|------|
| i | The Balcony | 0:00 |
| ii | Noted | 0:34 |
| iii | Put Me To Sleep | 1:02 |
| iv | The Dreams | 1:36 |
| v | The Room | 2:22 |
| vi | One Node | 2:56 |

Total runtime 4:12.

## Holds

`HOLDS` stops the clock, the picture and the narration together. There is one,
after the narrator answers the dream: the AI's "thank you, that's useful too"
has to land on a silence rather than on the heels of the answer, because the
silence is where the answer goes somewhere.

## Notes

- Captions are a selection from the transcript, not the whole of it, but they
  carry the argument rather than only the imagery: the app being reliably
  right, the questions ceasing to be about the narrator's garden, the lessons
  always saying "I learned" and never "another user told me". An earlier cut
  dropped those and the ending stopped following from anything.
- The home-screen character is an original design. The source deliberately
  declines to describe it.
- `three.js` is the only dependency, loaded from a CDN as an ES module.
- Honours `prefers-reduced-motion`: camera float, shake, the glitch and the
  screen flicker all drop out, and the trip is capped.
- No hard strobing: the psychedelic effects are continuous (hue rotation,
  feedback, warp) rather than flashing, and the one glitch burst is brief and
  low-contrast.
- Captions sit on a frosted plate rather than relying on a text-shadow. Over a
  picture this busy a shadow either fails to protect the type or unions into a
  slab; the plate does both jobs and matches the app chrome.
- The original video's audio was never reachable, so none of it is reproduced
  here; the score is written for this piece.
- Transport: space to play/pause, arrow keys to scrub 5s, movement names to
  jump.

## Running it

Open `index.html` in a browser and press Begin. It needs network access for
three.js (`0.147.0`, UMD) and the Google Fonts faces (Newsreader, IBM Plex
Mono); the fonts degrade to fallbacks, and a failure to load three.js is
reported on the title card rather than left as a black screen.
