// Card component for recommended sales follow-up actions.
export default function ActionsCard({
  actions = [
    "Send a tailored outbound note referencing pricing and case-study interest.",
    "Route the account to the regional AE covering broker-owner operations.",
    "Follow up with a workflow demo focused on seller conversion speed.",
  ],
}) {
  return (
    <div className="rounded-[28px] border border-slate-800 bg-slate-950/80 p-5">
      <p className="text-xs uppercase tracking-[0.28em] text-slate-500">
        Recommended actions
      </p>
      <div className="mt-4 space-y-3">
        {actions.map((action, index) => (
          <div
            key={action}
            className="flex gap-3 rounded-2xl border border-slate-800 bg-slate-900/70 px-4 py-3"
          >
            <span className="flex h-7 w-7 flex-none items-center justify-center rounded-full bg-emerald-400/15 text-sm font-semibold text-emerald-300">
              {index + 1}
            </span>
            <p className="text-sm leading-6 text-slate-300">{action}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
