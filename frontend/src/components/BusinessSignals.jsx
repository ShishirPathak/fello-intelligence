// Card component for recent hiring, funding, and growth signals.
const defaultSignals = [
  {
    type: "hiring",
    label: "Hiring revenue roles",
    description: "Sales hiring suggests active go-to-market expansion.",
  },
  {
    type: "growth",
    label: "Regional expansion",
    description: "Office footprint appears to be growing in core markets.",
  },
  {
    type: "news",
    label: "Digital investment",
    description: "Recent messaging points to workflow modernization efforts.",
  },
];

const toneClasses = {
  hiring: "border-sky-400/30 bg-sky-400/10 text-sky-300",
  funding: "border-violet-400/30 bg-violet-400/10 text-violet-300",
  growth: "border-emerald-400/30 bg-emerald-400/10 text-emerald-300",
  news: "border-orange-400/30 bg-orange-400/10 text-orange-300",
};

export default function BusinessSignals({ signals = defaultSignals }) {
  return (
    <div className="rounded-[28px] border border-slate-800 bg-slate-950/80 p-5">
      <p className="text-xs uppercase tracking-[0.28em] text-slate-500">
        Business signals
      </p>
      <div className="mt-4 flex flex-wrap gap-3">
        {signals.map((signal) => (
          <div
            key={`${signal.type}-${signal.label}`}
            className="min-w-[220px] flex-1 rounded-2xl border border-slate-800 bg-slate-900/70 p-4"
          >
            <span
              className={`inline-flex rounded-full border px-3 py-1 text-[11px] font-medium uppercase tracking-[0.2em] ${
                toneClasses[signal.type] || toneClasses.news
              }`}
            >
              {signal.type}
            </span>
            <p className="mt-3 text-sm font-medium text-white">{signal.label}</p>
            <p className="mt-2 text-sm leading-6 text-slate-400">
              {signal.description}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
