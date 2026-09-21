export type Triad = { c1: string; c2: string; c3: string };

/**
 * c1 is the bright bloom corner, c3 the dark anchor. The vignette sits on the
 * c3 corner, which moves with the angle — a fixed position broke every card
 * that wasn't set to 140deg.
 */
export function fishbowl(t: Triad, angle = 140, light = false) {
  const rad = (angle * Math.PI) / 180;
  const vx = Math.round(50 - Math.sin(rad) * 48);
  const vy = Math.round(50 + Math.cos(rad) * 48);

  if (light) {
    return [
      `radial-gradient(130% 110% at ${vx}% ${vy}%, rgba(0,0,0,.05) 0%, transparent 52%)`,
      `linear-gradient(${angle}deg,` +
        ` color-mix(in oklab, ${t.c3} 22%, white) 0%,` +
        ` color-mix(in oklab, ${t.c2} 52%, white) 32%,` +
        ` color-mix(in oklab, ${t.c1} 90%, white) 72%,` +
        ` color-mix(in oklab, ${t.c1} 72%, white) 100%)`,
    ].join(", ");
  }

  return [
    `radial-gradient(130% 110% at ${vx}% ${vy}%, rgba(2,2,5,.65) 0%, transparent 54%)`,
    `linear-gradient(${angle}deg,` +
      ` ${t.c3} 0%,` +
      ` color-mix(in oklab, ${t.c2} 75%, ${t.c3}) 20%,` +
      ` ${t.c2} 45%,` +
      ` color-mix(in oklab, ${t.c1} 55%, ${t.c2}) 68%,` +
      ` ${t.c1} 85%,` +
      ` color-mix(in oklab, ${t.c1} 38%, #F0D88C) 100%)`,
  ].join(", ");
}

export const TRIADS = {
  Dusk: { c1: "#C8783C", c2: "#8A4270", c3: "#2C1A58" },
  Ember: { c1: "#BE8440", c2: "#98422E", c3: "#3A1524" },
  Coral: { c1: "#CC8460", c2: "#A8462C", c3: "#42111E" },
  Bloom: { c1: "#C44E7C", c2: "#852E6C", c3: "#301346" },
  Iris: { c1: "#9474C4", c2: "#54389E", c3: "#181240" },
  Slate: { c1: "#6A82AA", c2: "#384664", c3: "#121622" },
  Umber: { c1: "#B8926A", c2: "#7E5230", c3: "#2A1810" },
  Brass: { c1: "#C0A850", c2: "#786E2E", c3: "#262A12" },
  Fern: { c1: "#84AE6E", c2: "#3E7A4C", c3: "#12301E" },
  Sage: { c1: "#98B69C", c2: "#4A7C72", c3: "#163030" },
  Lagoon: { c1: "#66B6AE", c2: "#2C7084", c3: "#0E2438" },
  Cobalt: { c1: "#6C9AD2", c2: "#32529C", c3: "#101836" },
  Garnet: { c1: "#C26E7C", c2: "#92303E", c3: "#360E18" },
  Graphite: { c1: "#98989E", c2: "#4C4C54", c3: "#131316" },
} satisfies Record<string, Triad>;

/** Derived from the official UMD palette at brand.umd.edu/colors. */
export const UMD = {
  RedBronze: { c1: "#9A1020", c2: "#6E2A0E", c3: "#080408" },
  GoldBronze: { c1: "#C0A018", c2: "#7E5010", c3: "#100C08" },
  BronzeRed: { c1: "#AD7231", c2: "#7A1E14", c3: "#080408" },
  WineGold: { c1: "#C8A020", c2: "#8A2418", c3: "#080408" },
  DeepWine: { c1: "#7A1828", c2: "#3A0A10", c3: "#060408" },
} satisfies Record<string, Triad>;
