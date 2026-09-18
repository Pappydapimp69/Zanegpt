# Put Me To Sleep

A six-movement 3D piece, adapted from the transcript of a short narrated video.

Everything on screen is generated at runtime — no textures, models, or media
files. The plants, the leaves (serrated, because the story turns on leaf
serration), the character, the dream photographs, the room and the node
lattice are all built procedurally with three.js and canvas-drawn textures.

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
- Transport: space to play/pause, arrow keys to scrub 5s, movement names to
  jump.

## Running it

Open `index.html` in a browser. It needs network access for three.js and the
Google Fonts faces (Newsreader, IBM Plex Mono); both degrade to fallbacks.
