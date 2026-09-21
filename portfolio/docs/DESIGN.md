# Design system

Dylan Patel's personal site. Last updated 20 September 2026. Implemented in `Desktop/Project 1/portfolio`.

Live references:
- Gradient gallery — https://claude.ai/artifact/6kZZuQsQBdUVgscQsKFBA6
- Type specimen — https://claude.ai/artifact/TNkgb4fdn2c6e4GUDJY8jw
- Home page mock — https://claude.ai/artifact/4MvLPsEbsMvdPYfZTP7fq1
- System sheet (partly stale) — https://claude.ai/artifact/XyS692ETneRoXL7g65XVwK

Reference material: Rondesignlab case studies and card work, plus a Figma-authored token spec.
Where they disagree, the decisions recorded here win.

## Type

**Outfit, and nothing else.** Same family Rondesignlab set. Four weights earn a place.

| Role | Weight | Size | Tracking | Leading |
| --- | --- | --- | --- | --- |
| Display | 300 | 50–90px | −0.05em | 0.88 |
| Figures | **500** | 36–124px | −0.05em | 0.9 |
| Heading | 400 | 20–28px | −0.025em | 1.15 |
| Body | 300 | 15–16px | 0 | 1.65 |
| Label | 500 | 10.5–12px | 0.17em, uppercase | 1.5 |
| Button | 500 | 13.5px | −0.01em | 1 |

Figures carry `font-variant-numeric: tabular-nums` everywhere except running prose.
Tracking does real work — Outfit reads generic at default spacing and designed at −0.05em.

## Colour

| Token | Hex | Use |
| --- | --- | --- |
| Ground | `#08080A` | page |
| Card | `#141417` | every dark card |
| Ink | `#F2ECE8` | primary text (warm white, never pure white) |
| Ink 2 | `#A7A29E` | body and supporting text |
| Ink 3 | `#76716E` | labels and metadata |
| Line | `rgba(242,236,232,.12)` | hairlines and chip borders |
| Acid | `#E7FE55` | the only accent |

Acid appears at most twice per page. Currently: the Contact me button in the nav, and the
contact bar. It is never a card surface.

## Gradient identities

Fourteen analogous triads. Each is three hexes travelling one direction around the wheel across
roughly 60–90°, so no colour ever meets its complement and there is no grey seam.

| Name | c1 | c2 | c3 |
| --- | --- | --- | --- |
| Dusk | `#C8783C` | `#8A4270` | `#2C1A58` |
| Ember | `#BE8440` | `#98422E` | `#3A1524` |
| Coral | `#CC8460` | `#A8462C` | `#42111E` |
| Bloom | `#C44E7C` | `#852E6C` | `#301346` |
| Iris | `#9474C4` | `#54389E` | `#181240` |
| Slate | `#6A82AA` | `#384664` | `#121622` |
| Umber | `#B8926A` | `#7E5230` | `#2A1810` |
| Brass | `#C0A850` | `#786E2E` | `#262A12` |
| Fern | `#84AE6E` | `#3E7A4C` | `#12301E` |
| Sage | `#98B69C` | `#4A7C72` | `#163030` |
| Lagoon | `#66B6AE` | `#2C7084` | `#0E2438` |
| Cobalt | `#6C9AD2` | `#32529C` | `#101836` |
| Garnet | `#C26E7C` | `#92303E` | `#360E18` |
| Graphite | `#98989E` | `#4C4C54` | `#131316` |

Cards stay dark in both themes. No more than two identities visible at once.

### Fishbowl recipe

Implemented as `fishbowl(triad, angle, light)` in `lib/gradient.ts`. Two things it does that a
static CSS block cannot:

- **The vignette tracks the angle.** It sits on the `c3` anchor corner, whose position is derived
  from the angle rather than hardcoded. A fixed position broke every card not set to 140deg.
- **It emits a light variant.** Light mode pushes maximum contrast between the poles — the `c3`
  anchor goes to 22% colour against white while `c1` stays at 90% — so the gradient survives on
  small cards where the travel distance is short.

Dark: `c3 → c2 → c1 → a warm #F0D88C bloom at the far corner`, mixed in oklab throughout.

Both variants are emitted as `--bg-dark` and `--bg-light` custom properties on each card, so the
theme swap is pure CSS with no re-render.

## UMD triads

Education uses the same fishbowl recipe as everything else, with triads derived from the official
palette. Five options exist; `BronzeRed` is currently in use.

| Name | c1 | c2 | c3 |
| --- | --- | --- | --- |
| RedBronze | `#9A1020` | `#6E2A0E` | `#080408` |
| GoldBronze | `#C0A018` | `#7E5010` | `#100C08` |
| BronzeRed | `#AD7231` | `#7A1E14` | `#080408` |
| WineGold | `#C8A020` | `#8A2418` | `#080408` |
| DeepWine | `#7A1828` | `#3A0A10` | `#060408` |

### Official UMD colours

From https://brand.umd.edu/colors

| | Hex | Pantone |
| --- | --- | --- |
| Maryland Red | `#E21833` | 186 |
| Maryland Gold | `#FFD200` | 116 |
| White | `#FFFFFF` | — |
| Black | `#000000` | Black 6 |
| Dark Gray | `#454545` | Cool Gray 11 |
| Medium Gray | `#7F7F7F` | Cool Gray 8 |
| Light Gray | `#E6E6E6` | Cool Gray 1 |
| Bronze Testudo | `#AD7231` | 4645 |

The card currently uses hand-picked deepened values rather than exact shades of the official
pair. Open question: rebuild it from `#E21833` and `#FFD200` at a fixed darkening, optionally
with Bronze Testudo `#AD7231` as the middle stop so the whole gradient is official-palette only.

The M is a block stand-in I drew. Replace it with the official mark.

## Card anatomy

Every card is built the same way. Only the contents change.

- Radius `26px`, padding `26px`
- Small uppercase label, top left
- Content anchored to the bottom, gap between doing the spacing
- `flex-direction: column; justify-content: space-between`

**Every card is a gradient.** The dark `#141417` card is retired — it survives only as the nav
pill background. Text colour inside cards comes from `--card-heading`, `--card-body`,
`--card-label`, `--card-border` and `--card-chip`, which flip with the theme.

## Layout

Twelve-column bento, 12px gap, max width 1160px.

Spans in use: 12, 8/4, 7/5, 4/4/4. Every row resolves to twelve — mixing 3s against 5s and 7s
with no discipline is what made an earlier version read as a mess.

Breakpoints: wide spans collapse to 12 at 920px, 4s collapse to 12 at 600px.

### Pages

Nav is **Home · Projects · About**, a theme toggle, and **Contact me** in acid.

**Home** — five cards over two rows. Row one is 2fr/1fr: the name card (Dusk, 380px) and
Education (UMD BronzeRed, 380px). Row two is three equal cards at 260px: Projects (Cobalt),
Skills (Iris), Experience (Garnet).

**Projects** — full-width list cards, each with an oversized decorative number, title,
description, tags and a corner arrow. Fern, Sage, Slate, Lagoon at 140/160/140/120deg.

**About** — single card, Umber.

Dark is the default and light is opt-in via the toggle, persisted to localStorage. This is not a
`prefers-color-scheme` site; the palette is built for dark.

## Rejected, and why

Recorded so we do not relitigate.

- **Liquid glass** — colourless cards over blurred colour blobs. Cut on 19 Sept.
- **Dot-matrix numerals** — mush below 24px, and the hard edges were the problem with the
  figures. Replaced by Outfit 500.
- **Pattern fills** — halftone dots and diagonal stripes read as noise. They work in the
  reference because they encode stock levels against a legend; ours decorated a number.
- **Seven card treatments at once** — flat acid, flat orange, flat blue, paper, dark,
  dark-with-dots, gradient. The reference is consistent *within* a view; one or two colour
  worlds per screen, not seven.
- **Light-mode gradient cards** — mixing each hue toward white gave pastels that lost all
  depth. Cards stay dark in both themes.
- **Complementary triads** — an accent 180° from the edge colour puts mud in the middle.
- **Space Mono for figures and labels** — blunt terminals, squared bowls, fixed advance.
- **Manrope and Archivo** — superseded by Outfit.

## Content status

Everything on the mock is placeholder. Figures came out of a partly garbled PDF text extraction
and need confirming before anything goes public: 30 staff led, 700+ organisations, 40% system
performance, 200+ students, 25% click-through lift, 50% turnaround cut, ~$10K forecast savings.

The tagline and the availability line are mine, not Dylan's.

No personal projects exist yet — the Projects page would currently be built from employment,
which is why "Work" is still under consideration as its name.
