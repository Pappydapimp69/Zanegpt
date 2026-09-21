# Put Me To Sleep

A six-movement 3D piece, adapted from the transcript of a short narrated video.

Everything is generated at runtime — no textures, models, or audio files. The
plants, the leaves (serrated, because the story turns on leaf serration), the
character, the dream photographs, the room and the node lattice are all built
procedurally with three.js and canvas-drawn textures. The score is synthesised
with the Web Audio API against the same clock.

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
  screen flicker all drop out.
- The original video's audio was never reachable, so none of it is reproduced
  here; the score is written for this piece.
- Transport: space to play/pause, arrow keys to scrub 5s, movement names to
  jump.

## Running it

Open `index.html` in a browser and press Begin. It needs network access for
three.js (`0.147.0`, UMD) and the Google Fonts faces (Newsreader, IBM Plex
Mono); the fonts degrade to fallbacks, and a failure to load three.js is
reported on the title card rather than left as a black screen.
