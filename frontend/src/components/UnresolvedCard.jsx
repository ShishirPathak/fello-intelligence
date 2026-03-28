// Warning state for visitor traffic that cannot be confidently tied to a company.
export default function UnresolvedCard({ result }) {
  return (
    <section className="w-full rounded-[32px] border border-orange-400/25 bg-slate-900/70 p-6 backdrop-blur">
      <div className="rounded-[28px] border border-orange-400/20 bg-[linear-gradient(135deg,rgba(251,146,60,0.16),rgba(15,23,42,0.9))] p-6">
        <p className="text-xs uppercase tracking-[0.28em] text-orange-200/80">
          Unresolved visitor
        </p>
        <h2 className="mt-3 text-3xl font-semibold text-white">
          {result?.unresolved_reason || "Residential ISP detected"}
        </h2>
        <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-300">
          This visit likely came through a residential or privacy network, so the
          company behind the traffic could not be resolved with confidence. The
          signal is still useful, but it is not strong enough to route to sales as
          a verified account.
        </p>
        {result?.confidence != null && (
          <p className="mt-3 text-sm text-orange-200/80">
            Confidence: {(result.confidence * 100).toFixed(0)}%
          </p>
        )}
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-3">
        {[
          "Form fills with work email create a direct account match.",
          "Email click tracking can connect anonymous sessions to known contacts.",
          "Product login or trial signup bridges anonymous traffic to CRM records.",
        ].map((item) => (
          <div
            key={item}
            className="rounded-[28px] border border-slate-800 bg-slate-950/80 p-5"
          >
            <p className="text-sm leading-7 text-slate-300">{item}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
