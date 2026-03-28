// Card component for the inferred buyer persona and confidence signal.
export default function PersonaCard({
  title = "Regional sales leader",
  confidence = 78,
  reasoning = "Confidence is based on pricing, product, and case-study review.",
}) {
  return (
    <div className="rounded-[28px] border border-slate-800 bg-slate-950/80 p-5">
      <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Persona</p>
      <h3 className="mt-3 text-xl font-semibold text-white">{title}</h3>
      <div className="mt-4 h-2 rounded-full bg-slate-800">
        <div
          className="h-2 rounded-full bg-emerald-400"
          style={{ width: `${Math.max(0, Math.min(100, confidence))}%` }}
        />
      </div>
      <p className="mt-3 text-sm text-slate-400">
        {Math.round(confidence)}% confidence. {reasoning}
      </p>
    </div>
  );
}
