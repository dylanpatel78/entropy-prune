export const profile = {
  name: "Dylan Patel",
  claim: "I build systems that decide what to throw away.",
  standfirst:
    "Backend and ML infrastructure, with a habit of asking what the system does not need. Currently looking for software engineering roles.",
  domains: ["Software", "Machine learning", "Computation", "Finance"],
  bio: [
    "I started in quantitative finance, where the whole job is separating signal from an enormous amount of noise. That turned out to be the same problem I keep running into everywhere else — in inference pipelines, in numerical solvers, and in deciding what a team should build next.",
    "These days I work on the infrastructure underneath machine learning systems: making them cheaper, faster, and more honest about what they actually need. I like the parts of engineering where the constraint is real and the tradeoff is measurable.",
  ],
  leadership: {
    what: "Engineering lead, campus research computing group",
    period: "2024 — 2025",
    size: 6,
    body:
      "Ran a six-person team maintaining shared GPU infrastructure for about 200 researchers. Set the scheduling policy, rewrote the allocation model, and handled the part nobody wants, which is telling people why their job is queued.",
    outcome: [
      { value: "6", label: "engineers led" },
      { value: "200+", label: "researchers served" },
      { value: "41%", label: "cut in median queue time" },
    ],
  },
  links: {
    email: "hello@example.com",
    github: "https://github.com/example",
    linkedin: "https://linkedin.com/in/example",
  },
} as const;
