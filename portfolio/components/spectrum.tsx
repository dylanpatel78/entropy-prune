const RAMP = ["#1466ff", "#6b4be8", "#a63fc4", "#e8552e", "#ff9a2e"];

function stopAt(fraction: number) {
  const i = Math.min(
    RAMP.length - 1,
    Math.floor(fraction * (RAMP.length - 1) + 0.5),
  );
  return RAMP[i];
}

export function Spectrum({ values }: { values: number[] }) {
  const max = Math.max(...values);
  return (
    <div
      className="flex h-16 items-end gap-[3px]"
      role="img"
      aria-label={`Singular value spectrum, decaying from ${max} to ${values[values.length - 1]}`}
    >
      {values.map((v, i) => (
        <div
          key={i}
          className="min-w-0 flex-1 rounded-[2px]"
          style={{
            height: `${Math.max((v / max) * 100, 4)}%`,
            background: stopAt(i / (values.length - 1)),
          }}
        />
      ))}
    </div>
  );
}
