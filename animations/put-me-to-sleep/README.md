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

It is scored like everything else rather than applied flat. The balcony only
shimmers and its hue *oscillates* so the designed palette survives; from the
dreams onward the hue *cycles* fully. The room folds into wedges — a room of
people mirrored into itself — and the network opens into a zoom tunnel. The
shudder at 1:47 spikes every parameter at once.

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

## Movements

| # | Title | Runs |
|---|-------|------|
| i | The Balcony | 0:00 |
| ii | Noted | 0:34 |
| iii | Put Me To Sleep | 1:02 |
| iv | The Dreams | 1:36 |
| v | The Room | 2:22 |
| vi | One Node | 2:56 |

Total runtime 3:42.

## Notes

- Captions are a curated selection of lines from the transcript, not the
  whole of it. The piece is an adaptation.
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
