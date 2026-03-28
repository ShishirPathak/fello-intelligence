// Left-side dashboard control panel for visitor and company enrichment workflows.
export default function InputPanel({
  mode,
  setMode,
  recentVisitors,
  scoreTone,
  formState,
  companyList,
  loading,
  onChangeField,
  onChangeCompanyList,
  onAnalyze,
  onReset,
  onSelectVisitor,
}) {
  return (
    <aside className="w-full rounded-[28px] border border-slate-800/80 bg-slate-900/85 p-6 shadow-2xl shadow-black/20 backdrop-blur xl:w-[360px]">
      <div className="flex items-center gap-3">
        <span className="h-3 w-3 animate-pulse rounded-full bg-emerald-400 shadow-[0_0_18px_rgba(52,211,153,0.9)]" />
        <div>
          <p className="text-xs uppercase tracking-[0.32em] text-slate-400">
            Fello AI Builder Hackathon
          </p>
          <h1 className="text-2xl font-semibold tracking-tight text-white">
            Fello Intelligence
          </h1>
        </div>
      </div>

      <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-950/70 p-1">
        <div className="grid grid-cols-2 gap-1 text-sm">
          <button
            className={`rounded-xl px-4 py-3 transition ${
              mode === "visitor"
                ? "bg-emerald-400 text-slate-950"
                : "text-slate-300 hover:bg-slate-800"
            }`}
            onClick={() => setMode("visitor")}
            type="button"
          >
            Visitor signal
          </button>
          <button
            className={`rounded-xl px-4 py-3 transition ${
              mode === "company"
                ? "bg-emerald-400 text-slate-950"
                : "text-slate-300 hover:bg-slate-800"
            }`}
            onClick={() => setMode("company")}
            type="button"
          >
            Company list
          </button>
        </div>
      </div>

      <section className="mt-8 rounded-[24px] border border-slate-800 bg-slate-950/80 p-5">
        <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Input</p>
        {mode === "visitor" ? (
          <div className="mt-4 space-y-4">
            <label className="block">
              <span className="mb-2 block text-sm text-slate-300">IP address</span>
              <input
                className="w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm text-white outline-none ring-0 placeholder:text-slate-500"
                onChange={(event) => onChangeField("ip", event.target.value)}
                placeholder="34.201.12.88"
                value={formState.ip}
              />
            </label>
            <label className="block">
              <span className="mb-2 block text-sm text-slate-300">Pages visited</span>
              <textarea
                className="min-h-[120px] w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500"
                onChange={(event) => onChangeField("pages", event.target.value)}
                placeholder="/pricing, /ai-sales-agent, /case-studies"
                value={formState.pages}
              />
            </label>
            <div className="grid grid-cols-2 gap-3">
              <label className="block">
                <span className="mb-2 block text-sm text-slate-300">Dwell time</span>
                <input
                  className="w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500"
                  onChange={(event) =>
                    onChangeField("timeOnSiteSeconds", event.target.value)
                  }
                  placeholder="222"
                  value={formState.timeOnSiteSeconds}
                />
              </label>
              <label className="block">
                <span className="mb-2 block text-sm text-slate-300">
                  Visits this week
                </span>
                <input
                  className="w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500"
                  onChange={(event) =>
                    onChangeField("visitsThisWeek", event.target.value)
                  }
                  placeholder="3"
                  value={formState.visitsThisWeek}
                />
              </label>
            </div>
          </div>
        ) : (
          <label className="mt-4 block">
            <span className="mb-2 block text-sm text-slate-300">Company names</span>
            <textarea
              className="min-h-[224px] w-full rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500"
              onChange={(event) => onChangeCompanyList(event.target.value)}
              placeholder={"Keller Williams\nloanDepot\nCompass"}
              value={companyList}
            />
          </label>
        )}

        <div className="mt-5 grid grid-cols-3 gap-2">
          <button
            className="col-span-2 rounded-2xl bg-emerald-400 px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-emerald-300"
            onClick={onAnalyze}
            type="button"
          >
            {loading ? "Analyzing..." : "Analyze"}
          </button>
          <button
            className="rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-slate-300 transition hover:bg-slate-800"
            onClick={onReset}
            type="button"
          >
            Reset
          </button>
        </div>
      </section>

      <section className="mt-8">
        <div className="mb-4 flex items-center justify-between">
          <p className="text-xs uppercase tracking-[0.28em] text-slate-500">
            Recent Visitors
          </p>
          <span className="text-xs text-slate-500">Queue</span>
        </div>

        <div className="space-y-3">
          {recentVisitors.map((visitor) => (
            <button
              key={visitor.id}
              className="flex w-full items-center justify-between rounded-2xl border border-slate-800 bg-slate-900/70 px-4 py-4 text-left transition hover:border-slate-700 hover:bg-slate-900"
              onClick={() => onSelectVisitor(visitor)}
              type="button"
            >
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-white">
                  {visitor.label}
                </p>
                <p className="mt-1 text-xs text-slate-500">{visitor.ip}</p>
              </div>
              <span
                className={`h-3 w-3 flex-none rounded-full ${scoreTone(visitor.score)}`}
              />
            </button>
          ))}
        </div>
      </section>
    </aside>
  );
}
