// Reusable stage badge for account intent classification.
const badgeStyles = {
  decision: "border-emerald-400/30 bg-emerald-400/15 text-emerald-300",
  evaluation: "border-orange-400/30 bg-orange-400/15 text-orange-300",
  awareness: "border-slate-500/30 bg-slate-500/15 text-slate-300",
};

export default function IntentBadge({ stage = "awareness" }) {
  const normalizedStage = stage.toLowerCase();
  const classes = badgeStyles[normalizedStage] || badgeStyles.awareness;

  return (
    <span
      className={`inline-flex rounded-full border px-3 py-1 text-xs font-medium uppercase tracking-[0.24em] ${classes}`}
    >
      {normalizedStage}
    </span>
  );
}
