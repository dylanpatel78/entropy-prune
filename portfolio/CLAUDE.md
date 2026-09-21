@AGENTS.md

# House rules

## Code

Write what a careful engineer on this codebase would write, not what a generator produces.

- Comments explain *why*, never *what*. If a comment restates the line below it, delete it.
- No banner comments, no section dividers, no emoji.
- Short conventional names. `onSave`, not `handleSaveButtonClickEvent`. `i`, not `currentIndex`,
  in a three-line loop.
- Don't abstract on the second use. Wait for the third.
- No prop interface wider than the component needs. A one-off card does not get twelve optional props.
- No defensive `try`/`catch` around code that cannot throw, no null checks on values the types
  already guarantee.
- Prefer CSS to JavaScript: a `color-mix()` or a `:has()` beats a `useEffect`.
- Match the file you are editing — its import order, its quote style, its density.
- Delete dead code. Never comment it out.
- Don't restate a type the compiler already infers.

## Design

`docs/DESIGN.md` is the source of truth for tokens, type, gradients and spacing. Read it before
touching anything visual. Where it and a request disagree, ask.

Both card treatments, Fishbowl and Mesh, stay live until Dylan picks one. Any new card must work
in both.

## Content

Every figure currently on the site is placeholder and invented. Never present placeholder numbers
as real, and never invent a metric for a project that does not have one — design the layout
around its absence instead.
